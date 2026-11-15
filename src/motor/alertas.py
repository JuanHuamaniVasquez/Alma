"""MO-3 → SU-1 · De la alarma detectada al DC-05 con RECIBO completo, y su reevaluación (retiro automático).

Recibo = regla exacta ejecutable + semilla pública + hash del preregistro (GO-2). Si al reevaluar con los datos
la regla ya no se cumple, la alarma se RETIRA sola.

DC-05 lleva `presupuesto_id` O `indicador` (DOC-01 v0.2.5, D-30). Solo `sueño → ritmo` está documentado (DOC-02 §0.6):
si el indicador tiene presupuesto documentado se emite por presupuesto; si no (p. ej. `fc`), por indicador. Nunca se
inventa un presupuesto.
"""
from __future__ import annotations

from datetime import UTC, datetime

from src.contratos.comunes import Indicador, Presupuesto
from src.contratos.dc05_alarma import DC05Alarma, Detector, EstadoAlarma

from .cusum import ejecutar_regla
from .modelo_nulo import AlarmaDetectada

PRESUPUESTO_DOCUMENTADO = {Indicador.SUENO: Presupuesto.RITMO}


def presupuesto_de(indicador: Indicador) -> Presupuesto | None:
    """El presupuesto documentado del indicador, o None si DOC-01/02 no lo mapean (entonces el DC-05 lleva el indicador)."""
    return PRESUPUESTO_DOCUMENTADO.get(indicador)


def a_dc05(alarma: AlarmaDetectada, *, indicador: Indicador, alarma_id: str, semilla: int, hash_preregistro: str) -> DC05Alarma:
    presupuesto = presupuesto_de(indicador)
    return DC05Alarma(
        alarma_id=alarma_id, ts_utc=datetime.combine(alarma.fecha, datetime.min.time(), tzinfo=UTC),
        presupuesto_id=presupuesto, indicador=None if presupuesto else indicador, detector=Detector.CUSUM, sentido=alarma.sentido, umbral=alarma.h,
        valor_cruzado=alarma.s_cruzado, regla_exacta=alarma.regla_exacta, semilla=semilla,
        hash_preregistro=hash_preregistro, estado=EstadoAlarma.ACTIVA)


def reevaluar(alarma: DC05Alarma, valores: list[float]) -> DC05Alarma:
    """La alarma se retira sola si la regla ya no se cumple (o se cumple en el sentido contrario)."""
    r = ejecutar_regla(alarma.regla_exacta, valores)
    if r.alarma and r.sentido == alarma.sentido.value:
        return alarma
    return alarma.model_copy(update={"estado": EstadoAlarma.RETIRADA})
