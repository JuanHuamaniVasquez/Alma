"""DC-09 · Forma diaria del hábitat — MO-7 (DOC-01 §3)."""
from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import Field, StringConstraints

from .comunes import Banner, Contrato, DiaHabitat, RefEvento, Real


class Curva(StrEnum):
    POTENCIA = "potencia"
    AGUA = "agua"
    AIRE = "aire"


HoraUtc = Annotated[str, StringConstraints(pattern=r"^([01]\d|2[0-3]):[0-5]\d$")]


class DC09Forma(Contrato):
    dia_habitat: DiaHabitat
    banner: Banner
    curva: Curva
    fase_valle_local: HoraUtc  # hh:mm UTC
    # razón pico/valle del día: por definición ≥ 1
    amplitud_relativa: Annotated[float, Field(ge=1, allow_inf_nan=False)]
    residuo_forma: Real  # σ, contra la ventana de calibración
    covariables: list[RefEvento] = Field(default_factory=list)  # refs DC-03 que explican desviaciones benignas
