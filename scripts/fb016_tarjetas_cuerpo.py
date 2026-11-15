"""M4.2 · FB-016: tarjetas A (sueño corto→cansancio) y B (tensión→HRV), LifeSnaps REAL. Una sola ejecución."""
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

ACTA, SEMILLA, ALFA = "FB-016", 20261113, 0.025
CSV = RAIZ / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"
SHA = "82c84ee495be4b0ff636a8a44271ffb124e2358d9dd52012b529b897f3d54963"


def num(x):
    try:
        v = float(x)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    if hashlib.sha256(CSV.read_bytes()).hexdigest() != SHA:
        print("CSV distinto del preregistrado"); return 2
    reg = RAIZ / "docs/actas/RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in reg.read_text(encoding="utf-8").splitlines() if l):
        print("ya ejecutada"); return 1
    filas = list(csv.DictReader(CSV.read_text(encoding="utf-8").splitlines()))
    A, B = defaultdict(list), defaultdict(list)
    for r in filas:
        s, t, tense, hrv = num(r["minutesAsleep"]), num(r["TIRED"]), num(r["TENSE/ANXIOUS"]), num(r["rmssd"])
        if s is not None and t is not None:
            A[r["id"]].append((s, t))
        if tense is not None and hrv is not None:
            B[r["id"]].append((int(tense), hrv))
    A = {p: v for p, v in A.items() if len(v) >= 30}
    B = {p: v for p, v in B.items() if len(v) >= 30}
    A = {p: [(1 if s < statistics.median([x for x, _ in v]) else 0, t) for s, t in v] for p, v in A.items()}
    ra = contraste(A, False, SEMILLA, +1)
    rb = contraste(B, True, SEMILLA, -1)
    va = "SOSTENIDA" if ra["p_unilateral"] <= ALFA and ra["S"] >= 0.03 else "REFUTADA"
    vb = "SOSTENIDA" if rb["p_unilateral"] <= ALFA and rb["S"] <= -0.05 else "REFUTADA"
    print(f"A sueño corto→TIRED: {ra['n_personas']} personas · S_A = {ra['S']:+.4f} · p = {ra['p_unilateral']:.4f} → {va}")
    print(f"B tensión→rmssd:     {rb['n_personas']} personas · S_B = {rb['S']:+.4f} sd · p = {rb['p_unilateral']:.4f} → {vb}")
    with reg.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256,
                            "semillas": [SEMILLA], "csv_sha256": SHA, "banner": "REAL (LifeSnaps, no astronautas)",
                            "A": {**ra, "veredicto": va}, "B": {**rb, "veredicto": vb}}, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
