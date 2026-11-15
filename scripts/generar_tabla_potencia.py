"""Genera data/calibracion/tabla_potencia.json (tabla de potencia del CUSUM, SIMULADA X-06, semilla pública).

Uso:  uv run python scripts/generar_tabla_potencia.py      (≈1 min)
La tabla es un artefacto de calibración reproducible: mismo código + misma semilla ⇒ mismo archivo.
"""
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.motor.cusum import K_REF, SEMILLA_CALIBRACION, calibrar_h  # noqa: E402
from src.motor.potencia import ARCHIVO_TABLA, DELTAS, VENTANA, calcular_tabla  # noqa: E402

N_SIM = 20000


def main() -> int:
    tabla = calcular_tabla(N_SIM, SEMILLA_CALIBRACION, K_REF)
    cuerpo = {"descripcion": "P(alarma de CAÍDA dentro de los primeros m días observados | caída sostenida de δ·σ_efectiva); "
                             "ruido gaussiano independiente; línea base de 14 datos estimada; CUSUM bilateral",
              "banner": "SIMULADO (X-06)", "n_sim": N_SIM, "semilla": SEMILLA_CALIBRACION, "k": K_REF, "h": calibrar_h(),
              "dias_base": 14, "ventana": VENTANA, "deltas": list(DELTAS),
              "tabla": {str(d): list(f) for d, f in tabla.items()}}
    ARCHIVO_TABLA.parent.mkdir(parents=True, exist_ok=True)
    ARCHIVO_TABLA.write_text(json.dumps(cuerpo, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(f"escrito {ARCHIVO_TABLA.relative_to(RAIZ)} sha256={hashlib.sha256(ARCHIVO_TABLA.read_bytes()).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
