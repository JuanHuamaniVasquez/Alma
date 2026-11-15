"""DC-01 · Canal A — sensores automáticos (DOC-01 §3)."""
from __future__ import annotations

from enum import StrEnum

from pydantic import model_validator

from .comunes import Banner, Contrato, IndicadorSensor, PersonaId, Real, Sigma, Texto, TsUtc


class CalidadDato(StrEnum):
    OK = "ok"
    SOSPECHOSO = "sospechoso"
    AUSENTE = "ausente"


class DC01Sensor(Contrato):
    persona_id: PersonaId
    ts_utc: TsUtc
    indicador: IndicadorSensor
    # None solo si calidad == ausente: «la ausencia es dato» (MNAR) y se registra, no se ignora.
    valor: Real | None
    unidad: Texto
    incertidumbre_sensor: Sigma
    calidad: CalidadDato
    fuente: Texto  # device_id
    banner: Banner

    @model_validator(mode="after")
    def _la_ausencia_es_dato(self):
        ausente = self.calidad is CalidadDato.AUSENTE
        if ausente and self.valor is not None:
            raise ValueError("calidad=ausente no lleva valor")
        if not ausente and self.valor is None:
            raise ValueError("sin valor solo se admite calidad=ausente")
        return self
