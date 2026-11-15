"""IN-4 · CLI del Banco de Falsaciones. Uso: uv run python scripts/banco.py <escenario|todos> [--semilla 20261113] [--n 100]"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from src.contratos.comunes import SEMILLAS_PUBLICAS  # noqa: E402
from src.motor.banco import ESCENARIOS, monte_carlo  # noqa: E402

p = argparse.ArgumentParser()
p.add_argument("escenario", choices=[*ESCENARIOS, "todos"])
p.add_argument("--semilla", type=int, default=20261113)
p.add_argument("--n", type=int, default=100)
a = p.parse_args()
if a.semilla not in SEMILLAS_PUBLICAS:
    sys.exit(f"semilla no pública: sin semilla pública no hay fila nueva (DOC-01). Públicas: {sorted(SEMILLAS_PUBLICAS)}")
for e in (ESCENARIOS if a.escenario == "todos" else [a.escenario]):
    print(json.dumps(monte_carlo(e, a.semilla, a.n), ensure_ascii=False))
