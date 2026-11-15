"""DC-08 · Cierre de conservación — El Contrapeso, MO-6 (DOC-01 §3).

El schema fija el residuo = entradas − salidas − Δalmacén − pérdida declarada. El umbral que
convierte el residuo en CIERRA / NO CIERRA es lógica de MO-6 (M1.2), no del schema.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import Field, model_validator

from .comunes import Banner, Contrato, DiaHabitat, Real, Sigma, cerca


class Bucle(StrEnum):
    AGUA = "agua"
    AIRE = "aire"
    ENERGIA = "energia"


class Veredicto(StrEnum):
    CIERRA = "CIERRA"
    NO_CIERRA = "NO CIERRA"


class DC08Cierre(Contrato):
    dia_habitat: DiaHabitat
    bucle: Bucle  # un cierre por bucle y día
    entradas: Real  # kg / kWh
    salidas: Real
    delta_almacen: Real
    perdida_declarada: Annotated[float, Field(ge=0, allow_inf_nan=False)]  # si no está declarada, no existe
    residuo_conservacion: Real
    incertidumbre_propagada: Sigma
    veredicto: Veredicto
    banner: Banner

    @model_validator(mode="after")
    def _formula(self):
        esperado = self.entradas - self.salidas - self.delta_almacen - self.perdida_declarada
        if not cerca(self.residuo_conservacion, esperado):
            raise ValueError("residuo_conservacion = entradas − salidas − delta_almacen − perdida_declarada")
        return self
