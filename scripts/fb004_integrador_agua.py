"""M2.5 · FB-004R: integrador lento del agua con normalización MP-3 (caudal REAL de Utah). Una sola ejecución."""
import hashlib
import json
import random
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.motor.integrador_agua import DIA_CAMBIO, FIXTURE, alarma, corrida, pool_volumenes, residuo  # noqa: E402

ACTA, BASE, N = "FB-004R", 20261113, 400
SHA = "a0ca143eee0784bcd608fe0dcea63ea12a39f0f6e718dd6bbcf34f458c085d23"


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    if hashlib.sha256(FIXTURE.read_bytes()).hexdigest() != SHA:
        print("fixture distinto del preregistrado"); return 2
    reg = RAIZ / "docs/actas/RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in reg.read_text(encoding="utf-8").splitlines() if l):
        print("ya ejecutada"); return 1
    pool = pool_volumenes()
    res = {}
    for delta in (0.0, 0.10, 0.20):
        det = {"R": [], "N": [], "N_barajado": []}
        for i in range(N):
            rng = random.Random(BASE + i)
            o, esp = corrida(rng, pool, delta)
            det["R"].append(alarma(o))
            det["N"].append(alarma(residuo(o, esp)))
            esp_malo = esp[:]
            random.Random(BASE + 10_000 + i).shuffle(esp_malo)         # caudal de otro día: rompe la corrección
            det["N_barajado"].append(alarma(residuo(o, esp_malo)))
        def tasa(a):
            return sum(1 for x in a if x is not None and (x >= DIA_CAMBIO if delta > 0 else True)) / N
        res[str(delta)] = {k: {"tasa": tasa(v), "mediana_dias": (statistics.median([x - DIA_CAMBIO for x in v if x is not None and x >= DIA_CAMBIO]) if delta > 0 and any(x is not None and x >= DIA_CAMBIO for x in v) else None)} for k, v in det.items()}
    for d, r in res.items():
        print(f"δ = {d}: " + " · ".join(f"{k}: {100 * v['tasa']:.1f} %" + (f" (mediana {v['mediana_dias']} d)" if v["mediana_dias"] is not None else "") for k, v in r.items()))
    f0, d10 = res["0.0"], res["0.1"]
    h1 = "SOSTENIDA" if d10["N"]["tasa"] >= 0.90 and f0["N"]["tasa"] <= 0.05 else "REFUTADA"
    h2 = "SOSTENIDA" if d10["N"]["tasa"] - d10["R"]["tasa"] >= 0.30 else "REFUTADA"
    h3 = "SOSTENIDA" if (d10["N"]["mediana_dias"] is not None and d10["N"]["mediana_dias"] <= 15) else "REFUTADA"
    h4 = "SOSTENIDA" if d10["N"]["tasa"] - d10["N_barajado"]["tasa"] >= 0.20 else "REFUTADA"
    print(f"H1 {h1} · H2 {h2} · H3 {h3} · H4 {h4}   (FPR de N = {100 * f0['N']['tasa']:.1f} %, de R = {100 * f0['R']['tasa']:.1f} %)")
    with reg.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256, "semillas": [BASE],
                            "banner": "SIMULADO (tanque, carga, ruido) + caudal REAL (Utah, S-12)", "fixture_sha256": SHA, "resultados": res,
                            "veredictos": {"H1": h1, "H2": h2, "H3": h3, "H4": h4}}, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
