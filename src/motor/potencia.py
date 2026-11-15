"""MO-3 · Potencia del detector: tabla de potencia y efecto mínimo detectable (MDE) CONDICIONADOS a los días válidos.

Para el procedimiento COMPLETO (línea base de 14 datos estimada, σ_efectiva = s·√(1+1/14), CUSUM bilateral con el h
calibrado) se simula una caída sostenida de δ·σ_efectiva y se mide P(alarma de caída dentro de los primeros m días
observados). Una sola pasada por δ da la potencia para todos los m (el CUSUM es secuencial y los datos faltantes
simplemente no se observan). Ruido gaussiano independiente, semilla pública (registro X-06): es una TABLA DE
CALIBRACIÓN; su validez en datos reales se contrasta en FB-011 y, donde hay autocorrelación, es optimista (FB-009).
"""
from __future__ import annotations

import json
import math
import random
import statistics
from collections.abc import Sequence
from functools import lru_cache
from pathlib import Path

from .cusum import K_REF, SEMILLA_CALIBRACION, calibrar_h, paso

DELTAS = tuple(round(0.25 * i, 2) for i in range(1, 21))  # 0.25σ … 5σ
POTENCIA_OBJETIVO = 0.90
VENTANA = 14
M_MIN = 7  # menos de 7 días válidos de 14: no hay base para declarar potencia (sin_datos_suficientes)
ARCHIVO_TABLA = Path(__file__).resolve().parent.parent.parent / "data" / "calibracion" / "tabla_potencia.json"


def primer_cruce(base: Sequence[float], monitoreo: Sequence[float], h: float, k: float = K_REF, delta: float = 0.0,
                 sigma_sensor: float = 0.0) -> tuple[int, str] | None:
    """Versión rápida de `ModeloNulo` + inyección de −δ·σ_efectiva: (día 1…, sentido) del primer cruce, o None."""
    mu = statistics.fmean(base)
    sigma = max(sigma_sensor, statistics.stdev(base) * math.sqrt(1 + 1 / len(base)))
    s_alza = s_caida = 0.0
    for i, x in enumerate(monitoreo, start=1):
        s_alza, s_caida = paso(s_alza, s_caida, (x - delta * sigma - mu) / sigma, k)
        if s_alza >= h or s_caida >= h:
            return i, "alza" if s_alza >= s_caida else "caída"
    return None


def calcular_tabla(n_sim: int = 20000, semilla: int = SEMILLA_CALIBRACION, k: float = K_REF) -> dict[float, tuple[float, ...]]:
    """{δ: (potencia con m=1 día, …, m=VENTANA días)} — detección de CAÍDA, ruido gaussiano independiente.

    Cara (≈1 min con n_sim=20 000): por eso la tabla oficial se genera UNA vez (`scripts/generar_tabla_potencia.py`),
    se versiona con sus metadatos y `tabla_potencia()` solo la lee.
    """
    h = calibrar_h(k=k)
    rng = random.Random(semilla)
    muestras = [([rng.gauss(0, 1) for _ in range(14)], [rng.gauss(0, 1) for _ in range(VENTANA)]) for _ in range(n_sim)]
    tabla: dict[float, tuple[float, ...]] = {}
    for d in DELTAS:
        cuentas = [0] * VENTANA
        for base, mon in muestras:
            r = primer_cruce(base, mon, h, k, delta=d)
            if r and r[1] == "caída":
                cuentas[r[0] - 1] += 1
        acumulado, fila = 0, []
        for c in cuentas:
            acumulado += c
            fila.append(acumulado / n_sim)
        tabla[d] = tuple(fila)
    return tabla


@lru_cache(maxsize=1)
def tabla_potencia() -> dict[float, tuple[float, ...]]:
    datos = json.loads(ARCHIVO_TABLA.read_text(encoding="utf-8"))
    return {float(d): tuple(fila) for d, fila in datos["tabla"].items()}


def metadatos_tabla() -> dict:
    datos = json.loads(ARCHIVO_TABLA.read_text(encoding="utf-8"))
    return {k: v for k, v in datos.items() if k != "tabla"}


def potencia(delta: float, m: int) -> float:
    """Potencia tabulada en el δ de la rejilla más cercano por debajo (conservador), con m días válidos."""
    tabla = tabla_potencia()
    m = max(1, min(m, VENTANA))
    candidatos = [d for d in DELTAS if d <= delta + 1e-9]
    return tabla[candidatos[-1]][m - 1] if candidatos else 0.0


def mde_sigma(m: int, objetivo: float = POTENCIA_OBJETIVO) -> float | None:
    """Menor δ de la rejilla con potencia ≥ objetivo usando m días válidos; None si ninguno la alcanza (ni 5σ)."""
    tabla = tabla_potencia()
    m = max(1, min(m, VENTANA))
    return next((d for d in DELTAS if tabla[d][m - 1] >= objetivo), None)
