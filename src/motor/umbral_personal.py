"""M4.5 · Detector `umbral_personal` (DC-05, DOC-01 v0.2.7): circula la tarjeta DC-12 `sueno-corto-cansancio` (FB-016 A, sostenida).

Regla EXACTA probada en FB-016: la noche cuenta como «corta» si `minutesAsleep` es estrictamente menor que la MEDIANA PERSONAL.
Límite declarado: esa regla marca ≈ la mitad de las noches; la alarma es de CONTEXTO (hay +7,9 puntos de probabilidad de cansancio
autorreportado esas noches, no un diagnóstico). Un umbral más selectivo exige un acta nueva. La alarma se retira sola si la regla no se cumple.
"""
from __future__ import annotations

import re
import statistics
from datetime import datetime

from src.contratos.comunes import Indicador
from src.contratos.dc05_alarma import DC05Alarma, Detector, EstadoAlarma, Sentido

_PATRON = re.compile(r"^UMBRAL_PERSONAL mediana=(\S+) :: ALARMA si x < mediana$")


def mediana_personal(linea_base: list[float]) -> float:
    return statistics.median(linea_base)


def regla_exacta(mediana: float) -> str:
    return f"UMBRAL_PERSONAL mediana={mediana!r} :: ALARMA si x < mediana"


def ejecutar_regla(texto: str, x: float) -> bool:
    m = _PATRON.fullmatch(texto)
    if not m:
        raise ValueError("regla UMBRAL_PERSONAL mal formada")
    return x < float(m.group(1))


def alarma(persona_dia: str, ts_utc: datetime, x: float, linea_base: list[float], semilla: int, hash_preregistro: str) -> DC05Alarma | None:
    """Alarma con recibo si la noche es corta frente a la mediana personal; None si no."""
    med = mediana_personal(linea_base)
    regla = regla_exacta(med)
    if not ejecutar_regla(regla, x):
        return None
    return DC05Alarma(alarma_id=f"UP-{persona_dia}", ts_utc=ts_utc, indicador=Indicador.SUENO, detector=Detector.UMBRAL_PERSONAL,
                      sentido=Sentido.CAIDA, umbral=med, valor_cruzado=x, regla_exacta=regla, semilla=semilla,
                      hash_preregistro=hash_preregistro, estado=EstadoAlarma.ACTIVA)
