"""MO-3 → SU · Recibo de verde (DC-14): «sin anomalías» + qué habría visto el detector, dados los días realmente observados.

Un verde es `ejecutar_regla(...)` SIN alarma sobre los datos de la ventana. Si hay alarma no hay verde (devuelve None).
La potencia/MDE se leen de la tabla versionada y se CONDICIONAN a los días válidos m; con m < M_MIN el estado es
`sin_datos_suficientes` y no se declara nada. Si al reevaluar con datos corregidos la regla alarma, el verde se RETIRA.
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from datetime import datetime

from src.contratos.comunes import Banner, Indicador
from src.contratos.dc05_alarma import Detector
from src.contratos.dc14_recibo_verde import DC14ReciboVerde, EstadoVerde

from .cusum import K_REF, calibrar_h, ejecutar_regla, regla_exacta
from .linea_base import LineaBase
from .potencia import M_MIN, POTENCIA_OBJETIVO, VENTANA, mde_sigma, metadatos_tabla

SUPUESTO = ("Ruido independiente y gaussiano; potencia de la tabla simulada X-06 (data/calibracion/tabla_potencia.json, semilla pública "
            "20261113). Contrastada en datos reales en FB-009 (sueño: potencia real ≥ simulada a 2σ) y FB-011; donde hay "
            "autocorrelación (pulso) la tabla es OPTIMISTA. σ_efectiva incluye el piso del sensor (proxy).")


def _validos(valores: Sequence[float | None]) -> list[float]:
    return [v for v in valores if v is not None and math.isfinite(v)]


def recibo_verde(*, recibo_id: str, linea: LineaBase, valores: Sequence[float | None], ts: datetime, sujeto: str,
                 indicador: Indicador, unidad: str, semilla: int, hash_preregistro: str, banner: Banner,
                 k: float = K_REF, h: float | None = None, ventana_dias: int = VENTANA,
                 objetivo: float = POTENCIA_OBJETIVO, m_min: int = M_MIN) -> DC14ReciboVerde | None:
    h = calibrar_h(k=k) if h is None else h
    regla = regla_exacta(k, h, linea.media, linea.sigma_efectiva)
    validos = _validos(valores)
    if ejecutar_regla(regla, validos).alarma:
        return None  # hay alarma: no hay verde que recibir
    m = len(validos)
    mde = mde_sigma(m, objetivo) if m >= m_min else None
    comun = dict(recibo_id=recibo_id, ts_utc=ts, sujeto=sujeto, indicador=indicador, ventana_dias=ventana_dias, dias_validos=m,
                 detector=Detector.CUSUM, k=k, h=h, unidad=unidad, supuesto=SUPUESTO, regla_exacta=regla, semilla=semilla,
                 hash_preregistro=hash_preregistro, banner=banner)
    if mde is None:
        return DC14ReciboVerde(**comun, estado=EstadoVerde.SIN_DATOS, potencia_declarada=None, mde_sigma=None, mde_fisico=None)
    return DC14ReciboVerde(**comun, estado=EstadoVerde.VERDE, potencia_declarada=objetivo, mde_sigma=mde,
                           mde_fisico=mde * linea.sigma_efectiva)


def reevaluar_verde(recibo: DC14ReciboVerde, valores: Sequence[float | None]) -> DC14ReciboVerde:
    """Si con los datos (corregidos) la regla ahora alarma, el verde se retira solo (mandamiento 3)."""
    if recibo.estado is EstadoVerde.VERDE and ejecutar_regla(recibo.regla_exacta, _validos(valores)).alarma:
        return recibo.model_copy(update={"estado": EstadoVerde.RETIRADO})
    return recibo


def tabla_vigente() -> dict:
    return metadatos_tabla()
