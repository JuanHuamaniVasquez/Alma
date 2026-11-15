"""MO-3 → SU-1 · De la alarma detectada al DC-05 con RECIBO completo, y su reevaluación (retiro automático).

Recibo = regla exacta ejecutable + semilla pública + hash del preregistro (GO-2). Si al reevaluar con los datos
la regla ya no se cumple, la alarma se RETIRA sola.

HUECO DE CONTRATO (decisión pendiente, D-27): DC-05 pide `presupuesto_id` y no `indicador`. Solo `sueño → ritmo`
está documentado (DOC-02 §0.6). Para los demás indicadores (p. ej. `fc`) no hay presupuesto documentado: NO se
inventa uno — se lanza `SinPresupuestoDocumentado`. Sus residuos siguen viajando en DC-06 (que admite `indicador`).
"""
from __future__ import annotations

from datetime import UTC, datetime

from src.contratos.comunes import Indicador, Presupuesto
from src.contratos.dc05_alarma import DC05Alarma, Detector, EstadoAlarma

from .cusum import ejecutar_regla
from .modelo_nulo import AlarmaDetectada

PRESUPUESTO_DOCUMENTADO = {Indicador.SUENO: Presupuesto.RITMO}


class SinPresupuestoDocumentado(ValueError):
    """DOC-02/DOC-01 no mapean ese indicador a un presupuesto: no se emite un DC-05 inventado."""


def presupuesto_de(indicador: Indicador) -> Presupuesto:
    try:
        return PRESUPUESTO_DOCUMENTADO[indicador]
    except KeyError:
        raise SinPresupuestoDocumentado(
            f"no hay presupuesto documentado para '{indicador.value}' (DC-05 no lleva `indicador`): decisión D-27") from None


def a_dc05(alarma: AlarmaDetectada, *, indicador: Indicador, alarma_id: str, semilla: int, hash_preregistro: str) -> DC05Alarma:
    return DC05Alarma(
        alarma_id=alarma_id, ts_utc=datetime.combine(alarma.fecha, datetime.min.time(), tzinfo=UTC),
        presupuesto_id=presupuesto_de(indicador), detector=Detector.CUSUM, sentido=alarma.sentido, umbral=alarma.h,
        valor_cruzado=alarma.s_cruzado, regla_exacta=alarma.regla_exacta, semilla=semilla,
        hash_preregistro=hash_preregistro, estado=EstadoAlarma.ACTIVA)


def reevaluar(alarma: DC05Alarma, valores: list[float]) -> DC05Alarma:
    """La alarma se retira sola si la regla ya no se cumple (o se cumple en el sentido contrario)."""
    r = ejecutar_regla(alarma.regla_exacta, valores)
    if r.alarma and r.sentido == alarma.sentido.value:
        return alarma
    return alarma.model_copy(update={"estado": EstadoAlarma.RETIRADA})
