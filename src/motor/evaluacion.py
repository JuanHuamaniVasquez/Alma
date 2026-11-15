"""M2.8 · Evaluación del motor sobre series reales (FB-009). Implementa EXACTAMENTE docs/actas/FB-009.md.

No cambiar ningún parámetro aquí sin un acta nueva (FB-009-v2): sería HARKing.
Unidad = bloque de 28 días válidos de una persona: 14 de línea base + 14 de monitoreo, con un ModeloNulo nuevo.
"""
from __future__ import annotations

import math
import random
import statistics
from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date

from src.contratos.comunes import Indicador

from .linea_base import DIAS_BASE, estimar_linea_base
from .modelo_nulo import ModeloNulo

BLOQUE = 2 * DIAS_BASE
H_FB009 = 10.011730842174083  # h fijado en el acta FB-009 (calibrar_h con semilla pública 20261113)
DELTAS = (1.0, 1.5, 2.0, 3.0)
SEMILLA_REMUESTREO = 20261114
UMBRAL_H1_ALFA = 0.05
UMBRAL_H2 = 0.80


def unidades(serie: Sequence[tuple[date, float]], bloque: int = BLOQUE) -> list[tuple[list[tuple[date, float]], list[tuple[date, float]]]]:
    """Bloques consecutivos de `bloque` días válidos ordenados por fecha → (base de 14, monitoreo de 14)."""
    ordenada = sorted(serie, key=lambda x: x[0])
    mitad = bloque // 2
    return [(ordenada[i:i + mitad], ordenada[i + mitad:i + bloque]) for i in range(0, len(ordenada) - bloque + 1, bloque)]


@dataclass(frozen=True)
class ResultadoUnidad:
    alarma: bool
    sentido: str | None
    dia_de_alarma: int | None  # 1…14 dentro de la ventana de monitoreo
    sigma_efectiva: float
    manda_el_sensor: bool


def ejecutar_unidad(persona: str, indicador: Indicador, sigma_sensor: float, base: list[tuple[date, float]],
                    monitoreo: list[tuple[date, float]], h: float = H_FB009, delta: float = 0.0) -> ResultadoUnidad:
    """Corre una unidad. `delta` > 0 RESTA delta·σ_efectiva (la de esta unidad) a todo el monitoreo (inyección SIMULADA, determinista)."""
    lb = estimar_linea_base(persona, indicador.value, base, sigma_sensor)
    assert lb is not None, "una unidad siempre tiene 14 datos de base"
    modelo = ModeloNulo(persona, indicador, sigma_sensor, h=h)
    for d, v in base:
        modelo.observar(d, v)
    for i, (d, v) in enumerate(monitoreo, start=1):
        o = modelo.observar(d, v - delta * lb.sigma_efectiva)
        if o.alarma:
            return ResultadoUnidad(True, o.alarma.sentido.value, i, lb.sigma_efectiva, lb.manda_el_sensor)
    return ResultadoUnidad(False, None, None, lb.sigma_efectiva, lb.manda_el_sensor)


# --- estadísticos (todos exactos o estándar; sin dependencias externas) ------------------------------
def wilson(x: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = x / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    margen = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centro - margen), min(1.0, centro + margen))


def cola_binomial(x: int, n: int, p: float) -> float:
    """P(X ≥ x) para X ~ Binomial(n, p), exacta."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x, n + 1))


def x_critico(n: int, p0: float = 0.01, alfa: float = UMBRAL_H1_ALFA) -> int:
    """Menor x tal que P(X ≥ x | n, p0) ≤ alfa (regla de refutación de H1 en FB-009)."""
    return next(x for x in range(n + 2) if cola_binomial(x, n, p0) <= alfa)


def remuestreo_por_persona(por_persona: dict[str, tuple[int, int]], semilla: int = SEMILLA_REMUESTREO,
                           n_rep: int = 5000) -> tuple[float, float]:
    """IC 95 % percentil de la tasa agrupada, remuestreando PERSONAS (cada una con sus (alarmas, unidades))."""
    personas = list(por_persona.values())
    if not personas:
        return (0.0, 0.0)
    rng = random.Random(semilla)
    tasas = []
    for _ in range(n_rep):
        muestra = [personas[rng.randrange(len(personas))] for _ in personas]
        n = sum(u for _, u in muestra)
        tasas.append(sum(a for a, _ in muestra) / n if n else 0.0)
    tasas.sort()
    return (tasas[int(0.025 * (n_rep - 1))], tasas[int(0.975 * (n_rep - 1))])


# --- la evaluación completa -----------------------------------------------------------------------------
def evaluar(series: dict[str, list[tuple[date, float]]], indicador: Indicador, sigma_sensor: float, *,
            filtro: Callable[[float], bool] | None = None, h: float = H_FB009, deltas: Sequence[float] = DELTAS) -> dict:
    por_persona_unidades: dict[str, list] = defaultdict(list)
    for persona, serie in series.items():
        valida = [(d, v) for d, v in serie if filtro is None or filtro(v)]
        us = unidades(valida)
        if us:
            por_persona_unidades[persona] = us
    todas = [(p, u) for p, us in por_persona_unidades.items() for u in us]
    n = len(todas)
    naturales = [ejecutar_unidad(p, indicador, sigma_sensor, b, m, h) for p, (b, m) in todas]
    x = sum(r.alarma for r in naturales)
    por_persona = {}
    for (p, _), r in zip(todas, naturales):
        a, u = por_persona.get(p, (0, 0))
        por_persona[p] = (a + r.alarma, u + 1)
    primeras = [ejecutar_unidad(p, indicador, sigma_sensor, *us[0], h) for p, us in por_persona_unidades.items()]
    potencia = {}
    for d in deltas:
        rs = [ejecutar_unidad(p, indicador, sigma_sensor, b, m, h, delta=d) for p, (b, m) in todas]
        dias = [r.dia_de_alarma for r in rs if r.alarma and r.sentido == "caída"]
        det = len(dias)
        potencia[str(d)] = {"detectadas": det, "de": n, "tasa": det / n if n else 0.0, "wilson95": wilson(det, n),
                            "mediana_dias": statistics.median(dias) if dias else None}
    return {
        "indicador": indicador.value, "n_personas": len(por_persona_unidades), "n_unidades": n,
        "M1": {"alarmas": x, "n": n, "tasa": x / n if n else 0.0, "wilson95": wilson(x, n),
               "remuestreo95": remuestreo_por_persona(por_persona), "x_critico": x_critico(n) if n else None,
               "p_valor_cola": cola_binomial(x, n, 0.01) if n else None},
        "M2": {"alarmas": sum(r.alarma for r in primeras), "n": len(primeras)},
        "M3": potencia,
        "M4": {"fraccion_manda_el_sensor": sum(r.manda_el_sensor for r in naturales) / n if n else 0.0,
               "alarmas_naturales_por_sentido": {s: sum(1 for r in naturales if r.alarma and r.sentido == s) for s in ("alza", "caída")}},
    }


def veredictos(resultado: dict) -> dict:
    """Aplica las reglas de FB-009 al resultado PRIMARIO (sueño, sin limpieza)."""
    m1, m3 = resultado["M1"], resultado["M3"]["2.0"]
    h1_refutada = m1["n"] > 0 and m1["alarmas"] >= m1["x_critico"]
    h2_sostenida = m3["de"] > 0 and m3["tasa"] >= UMBRAL_H2
    return {"H1": "REFUTADA" if h1_refutada else "NO REFUTADA", "H2": "SOSTENIDA" if h2_sostenida else "REFUTADA"}
