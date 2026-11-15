"""DC-02 · Canal B — autorreporte en 3 toques (DOC-01 §3). El contenido nunca; el tiempo de respuesta sí."""
from __future__ import annotations

from enum import StrEnum

from pydantic import model_validator

from .comunes import Banner, Contrato, PersonaId, Texto, TsUtc
from pydantic import Field
from typing import Annotated


class TipoAutorreporte(StrEnum):
    ANIMO = "ánimo"
    SINTOMA = "síntoma"


class DC02Autorreporte(Contrato):
    persona_id: PersonaId
    ts_utc: TsUtc
    banner: Banner
    tipo: TipoAutorreporte
    escala: Texto  # declarada por tarjeta (p. ej. "Likert 1-5")
    # valor y duración son None solo cuando nadie respondió (registro_ausencia): el faltante es dato.
    valor: int | None
    duracion_respuesta_s: Annotated[float, Field(ge=0, allow_inf_nan=False)] | None
    registro_ausencia: bool

    @model_validator(mode="after")
    def _la_ausencia_es_dato(self):
        vacio = self.valor is None and self.duracion_respuesta_s is None
        lleno = self.valor is not None and self.duracion_respuesta_s is not None
        if self.registro_ausencia and not vacio:
            raise ValueError("registro_ausencia=True no lleva valor ni duración")
        if not self.registro_ausencia and not lleno:
            raise ValueError("una respuesta lleva valor y duracion_respuesta_s")
        return self
