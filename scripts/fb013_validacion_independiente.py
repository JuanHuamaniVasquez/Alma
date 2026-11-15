"""M2.15 · FB-013: validación INDEPENDIENTE de FB-009/FB-010 en Zenodo 8018238 (sanos; REAL, no astronautas). Una sola ejecución.
Uso: uv run python scripts/fb013_validacion_independiente.py
"""
import hashlib
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.contratos.comunes import Indicador, IndicadorSensor  # noqa: E402
from src.contratos.dc01_sensores import CalidadDato  # noqa: E402
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.ingesta.fatiga_zenodo import cargar, sanos  # noqa: E402
from src.ingesta.incertidumbre import sigma_de  # noqa: E402
from src.motor.evaluacion import H_FB009, estimar_phi, evaluar  # noqa: E402

ACTA = "FB-013"
D = RAIZ / "data/externos/zenodo_8018238"
SHAS = {"day_activity_features.csv": "004c31d0875782088d7351f500189c06d700dd707f8a20e24c397159036515f3",
        "screener_survey.csv": "01b0ea479577db1d4aa8afad8e7b5540632979352acfbb26405e360b8ae01eac"}
PHI = {"fc": 0.18226445093426857, "sueño": -0.05597460167904739}  # congelados de FB-010 (entrenamiento LifeSnaps)


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    for n, h in SHAS.items():
        if hashlib.sha256((D / n).read_bytes()).hexdigest() != h:
            print("dataset distinto del preregistrado:", n); return 2
    registro = RAIZ / "docs" / "actas" / "RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in registro.read_text(encoding="utf-8").splitlines() if l):
        print(f"{ACTA} ya se ejecutó: una sola vez."); return 1
    regs = cargar(D / "day_activity_features.csv", sanos(D / "screener_survey.csv"))
    out = {}
    for ie, ind in ((IndicadorSensor.FC, Indicador.FC), (IndicadorSensor.SUENO, Indicador.SUENO)):
        por = defaultdict(list)
        for r in regs:
            if r.indicador is ie and r.calidad is CalidadDato.OK:
                por[r.persona_id].append((r.ts_utc.date(), r.valor))
        series, sigma, phi = {p: sorted(s) for p, s in por.items()}, sigma_de(ie).sigma, PHI[ind.value]
        out[ind.value] = {"phi_congelado": phi, "phi_propio_descriptivo": estimar_phi(series, filtro_personas=lambda p: True),
                          "base": evaluar(series, ind, sigma, phi=0.0), "blanqueado": evaluar(series, ind, sigma, phi=phi)}
        b, w = out[ind.value]["base"], out[ind.value]["blanqueado"]
        print(f"\n== {ind.value.upper()} · {b['n_personas']} personas / {b['n_unidades']} unidades · φ congelado {phi:.4f} · φ propio {out[ind.value]['phi_propio_descriptivo']:.4f} ==")
        for nombre, r in (("sin blanquear", b), ("blanqueado φ congelado", w)):
            m = r["M1"]
            pot = " · ".join(f"{d}σ:{100 * v['tasa']:.0f}%" for d, v in r["M3"].items())
            print(f"{nombre:24} FPR {m['alarmas']}/{m['n']} = {100 * m['tasa']:.2f} % Wilson95=[{100 * m['wilson95'][0]:.1f},{100 * m['wilson95'][1]:.1f}] x_crít={m['x_critico']} · potencia {pot}")
    b, w = out["fc"]["base"], out["fc"]["blanqueado"]
    xc = b["M1"]["x_critico"]
    h1 = "SOSTENIDA" if b["M1"]["alarmas"] >= xc else "REFUTADA"
    h2 = ("SOSTENIDA" if (w["M1"]["alarmas"] < xc and w["M1"]["alarmas"] <= b["M1"]["alarmas"]) else "REFUTADA") if h1 == "SOSTENIDA" else "NO CONCLUYENTE"
    h3 = "SOSTENIDA" if w["M3"]["2.0"]["tasa"] >= 0.80 else "REFUTADA"
    print(f"\nVEREDICTOS (pulso) → H1 (el problema replica): {h1} (x_base={b['M1']['alarmas']}, x_crít={xc}) · H2 (la corrección generaliza): {h2} (x_pw={w['M1']['alarmas']}) · H3 (potencia δ=2σ ≥ 80 %): {h3} ({100 * w['M3']['2.0']['tasa']:.1f} %)")
    print("Límites: no son astronautas; ventana de ~1 mes; σ proxy; φ y h congelados de LifeSnaps; potencia de H1 declarada ≈ 65 % si el FPR real fuera 5 %.")
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256,
             "acta_registrada_utc": acta.registrada_utc, "semillas": list(acta.semillas), "datos_sha256": SHAS,
             "banner": "REAL (Zenodo 8018238, sanos, no astronautas) + inyección SIMULADA", "h": H_FB009, "resultados": out,
             "veredictos": {"H1": h1, "H2": h2, "H3": h3}}
    with registro.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
