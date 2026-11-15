"""Exploración (no es un ítem de la cola): ¿cierra el «presupuesto del tiempo» (1440 min/día) en LifeSnaps?

Datos REALES (Zenodo 7229547, CC-BY 4.0; ver docs/politica-de-datos.md S-07). Requiere extraer antes
`daily_fitbit_sema_df_unprocessed.csv` a data/externos/lifesnaps/. Resultado del 2026-11-15 en
docs/ideas-extremas.md I-02. OJO: es una identidad contable del export de Fitbit, no una ley fisiológica.
Uso:  uv run python scripts/cierre_tiempo_lifesnaps.py
"""
import collections
import csv
import statistics
from pathlib import Path

CSV = Path(__file__).resolve().parent.parent / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main() -> int:
    filas = list(csv.DictReader(CSV.open(encoding="utf-8")))
    res, sin_sueno = [], []
    for r in filas:
        act = [num(r[k]) for k in ("sedentary_minutes", "lightly_active_minutes", "moderately_active_minutes", "very_active_minutes")]
        if None in act:
            continue
        dormido, despierto = num(r["minutesAsleep"]), num(r["minutesAwake"])
        if dormido is None or despierto is None:
            sin_sueno.append(sum(act))
        else:
            res.append(sum(act) + dormido + despierto - 1440)
    ok = sum(1 for x in res if abs(x) <= 1)
    print(f"días con actividad y sueño: {len(res)} · cierran a 1440 (|r|≤1 min): {ok} ({100 * ok / len(res):.1f} %)")
    print(f"residuo: mediana {statistics.median(res)} · mín {min(res)} · máx {max(res)} · más frecuentes {collections.Counter(round(x) for x in res).most_common(5)}")
    print(f"por debajo de 1440: {sum(1 for x in res if x < -1)} · por encima: {sum(1 for x in res if x > 1)}")
    print(f"días sin registro de sueño: {len(sin_sueno)} · mediana de la suma de actividad: {statistics.median(sin_sueno)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
