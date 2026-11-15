"""M2.17 · FB-012: variabilidad REAL de la demanda de agua (Utah, S-12). Una sola ejecución; exige acta e intacto el manifiesto.
Uso: uv run python scripts/fb012_variabilidad_agua.py
"""
import csv
import hashlib
import json
import random
import sys
from collections import defaultdict
from datetime import UTC, date, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.motor.variabilidad import barajar_dias, correlacion_entre, cv, ic_mediana, rho1  # noqa: E402

ACTA, SEMILLA = "FB-012", 20261113
D = RAIZ / "data/externos/utah_agua"
SHA_MANIFIESTO = "f03f189ef61aad1477a49163a245cc51cc85c98e82715ba8ea4227a55a4c44c7"


def veredicto(lo, hi, umbral, tipo):
    if tipo == "mayor":   # H: mediana > umbral
        return "SOSTENIDA" if lo > umbral else ("REFUTADA" if hi <= umbral else "INCONCLUSA")
    return "SOSTENIDA" if hi < umbral else ("REFUTADA" if lo >= umbral else "INCONCLUSA")  # H: mediana < umbral


def main() -> int:
    exigir_preregistro(RAIZ, ACTA, ahora=datetime.now(UTC))
    if hashlib.sha256((D / "MANIFIESTO.sha256.json").read_bytes()).hexdigest() != SHA_MANIFIESTO:
        print("manifiesto distinto del preregistrado"); return 2
    man = json.loads((D / "MANIFIESTO.sha256.json").read_text())
    series, observados = {}, {}
    for n, h in sorted(man.items()):
        if not n.startswith("LabelledEvents_site_"):
            continue
        b = (D / n).read_bytes()
        if hashlib.sha256(b).hexdigest() != h:
            print("archivo alterado:", n); return 2
        interior, vistos = defaultdict(float), set()
        for r in csv.DictReader(b.decode().splitlines()):
            dia = date.fromisoformat(r["StartTime"][:10])
            vistos.add(dia)
            if r["Label"] != "irrigation":
                interior[dia] += float(r["OriginalVolume"])
        series[n[20:23]] = {d: interior.get(d, 0.0) for d in vistos}
    rhos = {k: rho1(s) for k, s in series.items()}
    cvs = {k: cv(s) for k, s in series.items()}
    r_ok = [v for v in rhos.values() if v is not None]
    c_ok = [v for v in cvs.values() if v is not None]
    rng = random.Random(SEMILLA)
    barajados = [rho1(barajar_dias(s, rng)) for s in series.values()]
    b_ok = [v for v in barajados if v is not None]
    entre = correlacion_entre(list(series.values()))
    m1, l1, h1 = ic_mediana(r_ok, SEMILLA)
    m2, l2, h2 = ic_mediana(c_ok, SEMILLA)
    m3, l3, h3 = ic_mediana(entre, SEMILLA) if entre else (float("nan"),) * 3
    mb = sorted(b_ok)[len(b_ok) // 2]
    control_ok = -0.05 <= mb <= 0.05
    res = {
        "acta": ACTA, "sitios": len(series), "dias_observados_total": sum(len(s) for s in series.values()),
        "H1": {"n_hogares": len(r_ok), "mediana_rho1": m1, "ic95": [l1, h1], "umbral": 0.10,
               "veredicto": veredicto(l1, h1, 0.10, "mayor") if control_ok else "NO EVALUADA (control falla)"},
        "H2": {"n_hogares": len(c_ok), "mediana_cv": m2, "ic95": [l2, h2], "umbral": 0.25, "veredicto": veredicto(l2, h2, 0.25 - 1e-12, "mayor")},
        "H3": {"n_pares": len(entre), "mediana_corr_entre_hogares": m3, "ic95": [l3, h3], "umbral": 0.10, "veredicto": veredicto(l3, h3, 0.10, "menor") if entre else "SIN PARES"},
        "control": {"mediana_rho1_barajado": mb, "n": len(b_ok), "dentro_de_[-0.05,0.05]": control_ok},
        "rho1_por_hogar": {k: v for k, v in rhos.items()}, "cv_por_hogar": cvs,
    }
    print(json.dumps({k: v for k, v in res.items() if not k.endswith("por_hogar")}, indent=1, ensure_ascii=False))
    with (RAIZ / "docs/actas/RESULTADOS.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps({**res, "ejecutada_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")}, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
