"""MP-8 · Prior empírico del error de un manifiesto de fallos: cociente MTBF estimado (MADS) / MTBF de vuelo (ISS ECLSS).

Datos REALES transcritos de Jones 2019 (NTRS 20190027319, Tablas 2-4) en `data/calibracion/jones2019_mtbf.json`.
Cociente > 1 = el manifiesto era optimista (el equipo falla más de lo estimado). Las filas con vida de vuelo CENSURADA
(70 000 h sin fallo) solo dan una cota y se separan de las medidas. Límites: ORU no aleatorias; ISS, no un hábitat nuevo.
"""
from __future__ import annotations

import json
import math
import random
from pathlib import Path

RUTA = Path(__file__).resolve().parents[2] / "data" / "calibracion" / "jones2019_mtbf.json"


def cargar(ruta: Path = RUTA) -> dict:
    return json.loads(ruta.read_text(encoding="utf-8"))


def cocientes(datos: dict, *, medidas: bool) -> list[float]:
    """MADS/vuelo por fila. medidas=True: solo vida de vuelo no censurada; False: solo las censuradas (cota)."""
    return [f["mtbf_mads_h"] / f["mtbf_vuelo_h"] for f in datos["filas"]
            if f["vuelo_censurado"] is (not medidas) and f["mtbf_mads_h"] != f["mtbf_vuelo_h"]]


def cuantil(valores: list[float], q: float) -> float:
    v = sorted(valores)
    i = q * (len(v) - 1)
    lo, hi = math.floor(i), math.ceil(i)
    return v[lo] + (v[hi] - v[lo]) * (i - lo)


def muestrear_log(datos: dict, rng: random.Random) -> float:
    """Un cociente muestreado (con reemplazo) del conjunto de filas MEDIDAS; el flujo de FB-005 usa su log10."""
    return rng.choice(cocientes(datos, medidas=True))
