"""DC-11 · Ficha de vida de sensor — MO-8 (DOC-01 §3)."""
from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import Field, model_validator

from .comunes import Contrato, SigmaPositiva, Texto, TsUtc


class EstadoSensor(StrEnum):
    VIVO = "vivo"
    CONVALECIENTE = "convaleciente"
    MUERTO = "muerto"


class DC11Sensor(Contrato):
    device_id: Texto
    clase_sensor: Texto  # la clase define la curva de supervivencia
    nacimiento: TsUtc  # primera línea del instrumento en el libro
    calibraciones: list[TsUtc]  # vacía o vencida = hazard sube
    edad_dias: Annotated[int, Field(ge=0)]
    dias_desde_calibracion: Annotated[int, Field(ge=0)] | None  # None ⇔ nunca calibrado
    hazard_dia: Annotated[float, Field(ge=0, le=1, allow_inf_nan=False)]  # probabilidad instantánea (Weibull por clase)
    sigma_manifiesto_recomendada: SigmaPositiva
    estado: EstadoSensor

    @model_validator(mode="after")
    def _coherencia(self):
        if (not self.calibraciones) != (self.dias_desde_calibracion is None):
            raise ValueError("dias_desde_calibracion es None exactamente cuando no hay calibraciones")
        if any(c < self.nacimiento for c in self.calibraciones):
            raise ValueError("una calibración no puede ser anterior al nacimiento del sensor")
        return self
