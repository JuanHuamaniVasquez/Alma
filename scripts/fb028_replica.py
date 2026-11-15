"""M9 · FB-028: réplica de sueño corto → pulso en reposo más alto en la cohorte independiente Zenodo 8018238. Una sola ejecución.
Uso:  uv run python scripts/fb028_replica.py"""
import csv
import hashlib
import json
import statistics
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.motor.intrapersona import contraste  # noqa: E402

ACTA, SEMILLA, ALFA, MIN_DIAS, DESPLAZ = "FB-028", 20261113, 0.025, 25, 10
CSV = RAIZ / "data/externos/zenodo_8018238/day_activity_features.csv"
SHA = "004c31d0875782088d7351f500189c06d700dd707f8a20e24c397159036515f3"


def num(t):
    try:
        v = float(t)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def personas(filas, desplazar=0):
    por = defaultdict(list)
    for r in sorted(filas, key=lambda r: r["date"]):
        x, y = num(r["sleep__asleep__sum"]), num(r["heart_rate__resting_heart_rate"])
        if x is not None and y is not None:
            por[r["user_id"]].append((x, y))
    out = {}
    for p, v in por.items():
        if len(v) < MIN_DIAS:
            continue
        med = statistics.median(x for x, _ in v)
        et = [1 if x < med else 0 for x, _ in v]
        k = desplazar % len(et)
        et = et[k:] + et[:k]
        out[p] = [(e, y) for e, (_, y) in zip(et, v)]
    return out


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    if hashlib.sha256(CSV.read_bytes()).hexdigest() != SHA:
        print("CSV distinto del preregistrado"); return 2
    reg = RAIZ / "docs/actas/RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in reg.read_text(encoding="utf-8").splitlines() if l):
        print(f"{ACTA} ya se ejecutó: una sola vez."); return 1
    filas = list(csv.DictReader(CSV.read_text(encoding="utf-8").splitlines()))
    print(f"*** {ACTA} · acta sha256={acta.hash_sha256} · REAL (Zenodo 8018238, no astronautas) ***")
    r = contraste(personas(filas), False, SEMILLA, 1)
    rp = contraste(personas(filas, DESPLAZ), False, SEMILLA, 1)
    h1 = "SOSTENIDA" if r["S"] >= 0.5 and r["p_unilateral"] <= ALFA else "REFUTADA"
    h2 = "SOSTENIDA" if r["S"] >= 0.2 and r["p_unilateral"] <= ALFA else "REFUTADA"
    h3 = "VÁLIDO" if not (rp["S"] >= 0.2 and rp["p_unilateral"] <= ALFA) else "INVÁLIDO"
    print(f"  {r['n_personas']} personas · S = {r['S']:+.4f} lpm · p = {r['p_unilateral']:.4f}\n  H1 (≥0,5) {h1} · H2 (≥0,2) {h2}\n  placebo ({DESPLAZ} d): S = {rp['S']:+.4f} · p = {rp['p_unilateral']:.4f} → H3 {h3}")
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256, "acta_registrada_utc": acta.registrada_utc, "semillas": [SEMILLA],
             "csv_sha256": SHA, "banner": "REAL (Zenodo 8018238, no astronautas)", "alfa": ALFA, "resultado": r, "placebo": {**rp, "desplazamiento": DESPLAZ},
             "veredictos": {"H1_regla_original": h1, "H2_tamano_observado": h2, "H3_control_placebo": h3}}
    with reg.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")
    print("Límites: no son astronautas; mismo dispositivo; 36 días; asociación, no causalidad.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
