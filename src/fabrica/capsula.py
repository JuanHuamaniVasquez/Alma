"""FA-3 · Cápsulas exportables (DC-07): el veredicto de una tarjeta ya resuelta, con su protocolo, sus números EXACTOS y sus límites.

Sin `limites` no hay cápsula (DC-07 lo exige). Los números se LEEN de `docs/actas/RESULTADOS.jsonl` (nunca se retipean) y el hash/semilla del
preregistro de `docs/actas/INDEX.jsonl`; el texto en inglés sale de `data/fundicion/en.json` (derivado) y los límites de las notas de cada acta.
Solo se exportan tarjetas con veredicto (sostenida/refutada): lo que está en prueba o sin datos no tiene cápsula.
"""
from __future__ import annotations

import json
from pathlib import Path

from src.contratos.comunes import Banner
from src.contratos.dc07_capsula import DC07Capsula, Preregistro

LIM_016 = ("Not astronauts: everyday people wearing consumer devices, one cohort (LifeSnaps), sleep and heart-rate sensors are proxies. "
           "Same row means same day, so the causal direction is not separated; tiredness is a binary self-report. ")
CAPS = {
    "f9af5667": ("FB-016", "Within-person shuffling test, one preregistered run (act FB-016, card A); the rule that would have killed the card was written before the data was read.",
                 LIM_016 + "A pass here only shows the pipeline can detect an expected effect (positive control); it is association, not mechanism."),
    "ca55ac22": ("FB-016", "Within-person shuffling test, one preregistered run (act FB-016, card B); the rule that would have killed the card was written before the data was read.",
                 LIM_016 + "Only 13 people have both rmssd and a same-day report, so power is low: a small effect is NOT ruled out. The sign is opposite to the prediction, not 'barely short'."),
    "f5ac1905": ("FB-014", "10,000 circular-shift nulls, Bonferroni alpha 0.0125, one preregistered run (act FB-014); the rule that would have killed the card was written before the data was read.",
                 "Not astronauts; global Kp; LifeSnaps time zone unknown; seasonality only partly mitigated by the circular shift. "
                 "With 16 days of Kp ≥ 5 and about 50 people the test could only see large average effects (|rho| ≳ 0.1): small effects are NOT ruled out."),
}


def _jsonl(ruta: Path) -> list[dict]:
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()]


def _numeros(acta: str, tarjeta: str, r: dict) -> dict:
    if acta == "FB-016":
        x = r["A" if tarjeta == "f9af5667" else "B"]
        return {"statistic_S": x["S"], "people": x["n_personas"], "p_one_sided": x["p_unilateral"], "data_sha256": r["csv_sha256"]}
    out: dict = {"nulls": 10000, "alpha_bonferroni": 0.0125}
    for k, nombre in (("minutesAsleep", "sleep"), ("rmssd", "hrv")):
        d = r["resultados"][k]
        out |= {f"{nombre}_mean_rho": d["S1_obs"], f"{nombre}_p": d["p_S1_bilateral"], f"{nombre}_people": d["n_personas"]}
    return out | {"data_sha256": json.dumps(r["datos_sha256"], sort_keys=True)}


def capsulas(raiz: Path) -> list[DC07Capsula]:
    en = json.loads((raiz / "data/fundicion/en.json").read_text(encoding="utf-8"))["tarjetas"]
    tarjetas = {json.loads(l)["tarjeta"]["tarjeta_id"][:8]: json.loads(l)["tarjeta"] for l in (raiz / "data/fundicion/tarjetas.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    resultados = {d["acta"]: d for d in _jsonl(raiz / "docs/actas/RESULTADOS.jsonl")}
    indice = {d["acta"]: d for d in _jsonl(raiz / "docs/actas/INDEX.jsonl")}
    out = []
    for corto, (acta, protocolo, limites) in CAPS.items():
        t = tarjetas[corto]
        e = en[t["tarjeta_id"]]
        out.append(DC07Capsula(
            version="1", banner=Banner.REAL, hipotesis=e["prediction"], prueba_protocolo=protocolo,
            preregistro=Preregistro(hash=indice[acta]["hash_sha256"], semilla=indice[acta]["semillas"][0]),
            numeros=_numeros(acta, corto, resultados[acta]), senal_refutadora=e["refuter"],
            veredicto=e["result"], limites=limites))
    return out
