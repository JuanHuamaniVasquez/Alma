"""MP-15 · Canal de varianza: razón de varianzas (vigilancia / línea base) con recibo propio. DOC-01 v0.2.8, DC-05/DC-14 `f_varianza`.

Por qué existe (FB-018/FB-019, SIMULADO X-11/X-12): un zigzag de la misma media escapa al CUSUM de media (1,8 %); el techo es de
INFORMACIÓN: con 14 días de base ni la mejor prueba pasa del 40 % a H=1,5σ; con 28 días F detecta el 95 % del zigzag de 2σ.
Reglas:
  · Línea base = los últimos 28 días válidos; vigilancia = los últimos 14 válidos. Con menos → `sin_datos_suficientes` (la ausencia es dato).
  · Regla (ejecutable): F = var(vigilancia)/var(base) > c, con c = percentil 99 % del nulo normal, calibrado por simulación (no tablas).
  · Unilateral al alza (más varianza). Una caída de varianza no se alarma: es un límite declarado.
  · Supuesto: ruido independiente y gaussiano. La autocorrelación y las colas reales los mide FB-020.
"""
from __future__ import annotations

import json
import math
import random
import re
import statistics
from collections.abc import Sequence
from datetime import datetime
from functools import lru_cache
from pathlib import Path

from src.contratos.comunes import Banner, Indicador
from src.contratos.dc14_recibo_verde import Canal, DC14ReciboVerde, Detector, EstadoVerde

BASE, VIG, ALFA = 28, 14, 0.01
POTENCIA_OBJETIVO = 0.80
TABLA = Path(__file__).resolve().parent.parent.parent / "data" / "calibracion" / "tabla_potencia_varianza.json"
SUPUESTO = ("Ruido independiente y gaussiano; crítico de F y potencia de la tabla SIMULADA X-12 (data/calibracion/tabla_potencia_varianza.json, "
            "semilla pública 20261113). Unilateral al alza. MDE = amplitud en σ de un zigzag de la misma media. La autocorrelación real "
            "empeora la estimación de la varianza (FB-019): el FPR real se mide en FB-020.")


def _validos(v: Sequence[float | None]) -> list[float]:
    return [x for x in v if x is not None and math.isfinite(x)]


def razon_f(base: Sequence[float], vig: Sequence[float]) -> float:
    vb = statistics.variance(base)
    return statistics.variance(vig) / vb if vb > 0 else math.inf


@lru_cache(maxsize=8)
def calibrar_critico(semilla: int = 20261113, n: int = 20000, alfa: float = ALFA) -> float:
    rng = random.Random(semilla)
    f = sorted(razon_f([rng.gauss(0, 1) for _ in range(BASE)], [rng.gauss(0, 1) for _ in range(VIG)]) for _ in range(n))
    return f[math.ceil((1 - alfa) * n) - 1]


def regla_exacta(c: float, media_base: float, sd_base: float) -> str:
    return (f"F_VARIANZA base={BASE}d vig={VIG}d c={c!r} · alarma ⇔ var(últimos {VIG} válidos) / var(últimos {BASE} válidos antes) > c "
            f"(referencia: media_base={media_base:.6g}, sd_base={sd_base:.6g})")


def ejecutar_regla(regla: str, base: Sequence[float | None], vig: Sequence[float | None]) -> dict:
    """Aplica la regla impresa a los datos. {'estado': 'sin_datos'|'ok', 'alarma': bool, 'F': float|None}."""
    c = float(re.search(r"c=([0-9.e+-]+) ", regla).group(1))
    b, v = _validos(base), _validos(vig)
    if len(b) < BASE or len(v) < VIG:
        return {"estado": "sin_datos", "alarma": False, "F": None}
    f = razon_f(b[-BASE:], v[-VIG:])
    return {"estado": "ok", "alarma": f > c, "F": f}


@lru_cache(maxsize=1)
def tabla() -> dict:
    return json.loads(TABLA.read_text(encoding="utf-8"))


def mde_sigma() -> float | None:
    """Menor H (σ) de la rejilla con potencia ≥ objetivo en la tabla simulada; None si ninguna llega."""
    for h, p in sorted((float(h), p) for h, p in tabla()["potencia_zigzag"].items()):
        if p >= POTENCIA_OBJETIVO:
            return h
    return None


def recibo_varianza(*, recibo_id: str, base: Sequence[float | None], vig: Sequence[float | None], ts: datetime, sujeto: str,
                    indicador: Indicador, unidad: str, semilla: int, hash_preregistro: str, banner: Banner) -> DC14ReciboVerde | None:
    """Verde del canal de varianza; None si la regla alarma (no hay verde que recibir)."""
    b, v = _validos(base), _validos(vig)
    c = calibrar_critico()
    media, sd = (statistics.fmean(b[-BASE:]), statistics.stdev(b[-BASE:])) if len(b) >= BASE else (math.nan, math.nan)
    regla = regla_exacta(c, media if len(b) >= BASE else 0.0, sd if len(b) >= BASE else 0.0)
    r = ejecutar_regla(regla, b, v)
    if r["alarma"]:
        return None
    comun = dict(recibo_id=recibo_id, ts_utc=ts, sujeto=sujeto, indicador=indicador, canal=Canal.VARIANZA, ventana_dias=VIG,
                 dias_validos=min(len(v), VIG), detector=Detector.F_VARIANZA, k=0.0, h=c, unidad=unidad, supuesto=SUPUESTO,
                 regla_exacta=regla, semilla=semilla, hash_preregistro=hash_preregistro, banner=banner)
    mde = mde_sigma()
    if r["estado"] == "sin_datos" or mde is None or sd == 0:
        return DC14ReciboVerde(**comun, estado=EstadoVerde.SIN_DATOS, potencia_declarada=None, mde_sigma=None, mde_fisico=None)
    return DC14ReciboVerde(**comun, estado=EstadoVerde.VERDE, potencia_declarada=POTENCIA_OBJETIVO, mde_sigma=mde, mde_fisico=mde * sd)


def reevaluar(recibo: DC14ReciboVerde, base: Sequence[float | None], vig: Sequence[float | None]) -> DC14ReciboVerde:
    """El verde se retira solo si con los datos corregidos la regla alarma (mandamiento 3)."""
    if recibo.estado is EstadoVerde.VERDE and ejecutar_regla(recibo.regla_exacta, base, vig)["alarma"]:
        return recibo.model_copy(update={"estado": EstadoVerde.RETIRADO})
    return recibo


def simular_potencia(h: float, n: int, semilla: int) -> float:
    """Potencia del canal frente a un zigzag de amplitud h·σ sobre ruido normal (SIMULADO). Corrida i usa semilla+i."""
    c, hits = calibrar_critico(), 0
    for i in range(n):
        rng = random.Random(semilla + i)
        b = [rng.gauss(0, 1) for _ in range(BASE)]
        v = [rng.gauss(0, 1) + ((-1) ** j) * h for j in range(1, VIG + 1)]
        hits += razon_f(b, v) > c
    return hits / n
