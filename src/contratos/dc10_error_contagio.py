"""DC-10 · Casos de error y contagio — Sistema Inmune, GO-6 (DOC-01 §3)."""
from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import Field, model_validator

from .comunes import Contrato, RefNodo, Texto, TsUtc


class ClaseError(StrEnum):
    FALTANTE = "faltante"
    TIMESTAMP = "timestamp"
    UNIDAD = "unidad"
    SENSOR_MUERTO = "sensor_muerto"
    DUPLICADO = "duplicado"


class EstadoCaso(StrEnum):
    ABIERTO = "abierto"
    EN_CUARENTENA = "en_cuarentena"
    CERRADO = "cerrado"
    CORREGIDO_ESTRUCTURAL = "corregido_estructural"  # inmunidad adquirida


class DC10Caso(Contrato):
    caso_id: Texto
    ts_utc_deteccion: TsUtc
    nodo_origen: RefNodo  # dónde nació el error (DC-01/02/03/04)
    clase_error: ClaseError
    descendientes: list[RefNodo]  # líneas que consumieron el dato corrupto
    estado: EstadoCaso
    r0_fuente: Annotated[float, Field(ge=0, allow_inf_nan=False)]
    brote: bool
    k_brote: Annotated[int, Field(ge=0)]  # el k declarado: brote ⇔ más de k descendientes

    @model_validator(mode="after")
    def _brote(self):
        if self.brote != (len(self.descendientes) > self.k_brote):
            raise ValueError("brote debe ser verdadero exactamente cuando hay más de k_brote descendientes")
        return self
