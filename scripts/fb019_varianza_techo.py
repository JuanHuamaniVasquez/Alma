"""M2.18 · FB-019: techo de información de la detección de varianza frente al zigzag. SIMULADO. Una sola ejecución."""
import json
import math
import random
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.motor.adversario import perfil  # noqa: E402

ACTA, BASE, N, VIG = "FB-019", 20261113, 400, 14


def percentil(valores, p):
    v = sorted(valores)
    return v[min(len(v) - 1, math.ceil(p * len(v)) - 1)]


def muestra(rng, nbase, desv):
    return [rng.gauss(0, 1) for _ in range(nbase)], [rng.gauss(0, 1) + d for d in desv]


def estadistico_f(base, vig):
    return statistics.variance(vig) / statistics.variance(base)


def estadistico_oraculo(base, vig):
    return sum(v * v for v in vig)


def cusum_abs(base, vig, k=0.6):
    mu, sd = statistics.fmean(base), statistics.stdev(base)
    s = mejor = 0.0
    for v in vig:
        s = max(0.0, s + abs((v - mu) / sd) - 0.8 - k)  # |z| centrado en su media nula ≈ 0,8
        mejor = max(mejor, s)
    return mejor


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    reg = RAIZ / "docs/actas/RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in reg.read_text(encoding="utf-8").splitlines() if l):
        print("ya ejecutada"); return 1
    print("*** UNIVERSO SIMULADO — FB-019 · acta", acta.hash_sha256, "***")
    pruebas = {"F14": (14, estadistico_f), "F28": (28, estadistico_f), "oraculo": (14, estadistico_oraculo), "abs_cusum": (14, cusum_abs)}
    crit = {}
    for nombre, (nb, f) in pruebas.items():
        rng = random.Random(BASE)
        crit[nombre] = percentil([f(*muestra(rng, nb, [0.0] * VIG)) for _ in range(20000)], 0.99)
    out = {"criticos": crit, "fpr": {}, "potencia": {}}
    for nombre, (nb, f) in pruebas.items():
        out["fpr"][nombre] = sum(f(*muestra(random.Random(BASE + i), nb, [0.0] * VIG)) > crit[nombre] for i in range(N)) / N
        for H in (1.0, 1.5, 2.0):
            out["potencia"][f"{nombre}|{H}"] = sum(f(*muestra(random.Random(BASE + i), nb, perfil("zigzag", H))) > crit[nombre] for i in range(N)) / N
    print("criterios al 99 %:", {k: round(v, 3) for k, v in crit.items()})
    print("FPR (400 nulas):", out["fpr"])
    for k, v in out["potencia"].items():
        print(f"  {k:14} potencia {100 * v:5.1f} %")
    p = out["potencia"]
    h1 = "SOSTENIDA" if p["F14|1.5"] < 0.80 else "REFUTADA"
    h2 = "SOSTENIDA" if p["oraculo|1.5"] >= 0.80 else "REFUTADA"
    h3 = "SOSTENIDA" if p["F28|2.0"] >= 0.80 else "REFUTADA"
    h4 = "SOSTENIDA" if p["abs_cusum|1.5"] < 0.80 else "REFUTADA"
    valido = {k: v <= 0.02 for k, v in out["fpr"].items()}
    print(f"H1 {h1} · H2 {h2} · H3 {h3} · H4 {h4} · pruebas con FPR ≤ 2 %: {valido}")
    with reg.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256, "semillas": [BASE],
                            "banner": "SIMULADO", **out, "fpr_valido": valido, "veredictos": {"H1": h1, "H2": h2, "H3": h3, "H4": h4}}, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
