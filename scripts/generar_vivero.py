"""M8 · Ejecuta el generador de hipótesis de LA FUNDICIÓN sobre los datos REALES cargados y escribe data/fundicion/vivero.json (la API lo lee).
Uso:  uv run python scripts/generar_vivero.py"""
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.fabrica import generador as G  # noqa: E402

CSV = RAIZ / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"


def main() -> int:
    cand = G.generar(CSV)
    out = {"generado_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "n_mecanismos": len(G.BIBLIOTECA), "fuente_datos": "LifeSnaps (Zenodo 7229547), conteos de pares REALES",
           "n_listos": sum(c["estado"] == "listo" for c in cand), "n_bloqueados": sum(c["estado"] == "bloqueado" for c in cand), "n_ya_probadas": sum(c["estado"] == "ya_probada" for c in cand), "candidatos": cand}
    (RAIZ / "data/fundicion/vivero.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print({k: out[k] for k in ("n_mecanismos", "n_listos", "n_bloqueados", "n_ya_probadas")})
    for c in cand:
        print(f"  {c['estado']:10s} {c['clave']:18s} pares={c['datos']['pares']:5d} personas≥40d={c['datos']['personas_con_40_dias']:3d}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
