"""MP-15 · genera data/calibracion/tabla_potencia_varianza.json (SIMULADO X-12): crítico de F y potencia frente al zigzag. Semilla 20261113.
Uso: uv run python scripts/generar_tabla_potencia_varianza.py"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.motor.canal_varianza import ALFA, BASE, TABLA, VIG, calibrar_critico, simular_potencia  # noqa: E402

SEMILLA, N = 20261113, 2000
HS = [1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0]
datos = {"banner": "SIMULADO (X-12)", "semilla": SEMILLA, "n_por_celda": N, "base_dias": BASE, "vig_dias": VIG, "alfa": ALFA,
         "critico_f": calibrar_critico(SEMILLA), "fpr_nulo": simular_potencia(0.0, N, SEMILLA + 10_000),
         "potencia_zigzag": {str(h): simular_potencia(h, N, SEMILLA) for h in HS}}
TABLA.write_text(json.dumps(datos, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print(json.dumps(datos, ensure_ascii=False, indent=1))
