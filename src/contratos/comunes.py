"""Tipos y reglas comunes de los contratos DC-01…DC-12 (DOC-01 §3 es la única fuente).

Convenciones (DOC-01 §3, CLAUDE.md §3): timestamps ISO 8601 en UTC; `persona_id` siempre
pseudónimo; floats finitos; campos desconocidos prohibidos (un contrato no se improvisa).
"""
from __future__ import annotations

import math
import re
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Annotated

from pydantic import AfterValidator, BaseModel, ConfigDict, Field, StringConstraints

# Semillas públicas del proyecto (CLAUDE.md §2). Sin semilla pública no hay fila nueva.
SEMILLAS_PUBLICAS = (20261113, 20261114, 20261115, 20261111, 20261112)

HABITAT = "habitat"
_PERSONA_RE = re.compile(r"^[A-Za-z0-9_-]{3,64}$")


class Banner(StrEnum):
    REAL = "REAL"
    SIMULADO = "SIMULADO"


class IndicadorSensor(StrEnum):
    """Los 5 indicadores del Canal A (el ánimo vive en DC-02)."""
    PRESION = "presión"
    FC = "fc"
    GLUCOSA = "glucosa"
    TEMPERATURA = "temperatura"
    SUENO = "sueño"


class Indicador(StrEnum):
    """Los 6 indicadores oficiales del reto (5 de sensor + ánimo)."""
    PRESION = "presión"
    FC = "fc"
    GLUCOSA = "glucosa"
    TEMPERATURA = "temperatura"
    SUENO = "sueño"
    ANIMO = "ánimo"


class Presupuesto(StrEnum):
    """Los 9 presupuestos del libro (DC-04): el vocabulario común."""
    AIRE = "aire"
    AGUA = "agua"
    ENERGIA = "energia"
    DOSIS = "dosis"
    RITMO = "ritmo"
    CARGA = "carga"
    INMUNIDAD = "inmunidad"
    CONDUCTA = "conducta"
    TIEMPO = "tiempo"


def _a_utc(v: datetime) -> datetime:
    if v.tzinfo is None or v.utcoffset() != timedelta(0):
        raise ValueError("el timestamp debe ser ISO 8601 con zona UTC (p. ej. 2026-11-15T00:00:00Z)")
    return v


def _sujeto(v: str) -> str:
    if v == HABITAT or _PERSONA_RE.fullmatch(v):
        return v
    raise ValueError("sujeto: 'habitat' o un persona_id pseudónimo ([A-Za-z0-9_-]{3,64})")


TsUtc = Annotated[datetime, AfterValidator(_a_utc)]
Real = Annotated[float, Field(allow_inf_nan=False)]
Sigma = Annotated[float, Field(ge=0, allow_inf_nan=False)]
SigmaPositiva = Annotated[float, Field(gt=0, allow_inf_nan=False)]
Texto = Annotated[str, StringConstraints(strip_whitespace=True, min_length=1)]
Sha256 = Annotated[str, StringConstraints(pattern=r"^[0-9a-f]{64}$")]
PersonaId = Annotated[str, StringConstraints(pattern=_PERSONA_RE.pattern)]
Sujeto = Annotated[str, AfterValidator(_sujeto)]
DiaHabitat = Annotated[int, Field(ge=0)]
# Referencias a líneas/eventos de otros contratos: "DC-01:<id>".
RefFuenteLinea = Annotated[str, StringConstraints(pattern=r"^DC-0[1-3]:\S+$")]
RefNodo = Annotated[str, StringConstraints(pattern=r"^DC-0[1-4]:\S+$")]
RefEvento = Annotated[str, StringConstraints(pattern=r"^DC-03:\S+$")]


class Contrato(BaseModel):
    """Base de todos los contratos: inmutable y sin campos fuera de DOC-01 §3."""
    model_config = ConfigDict(extra="forbid", frozen=True)


def cerca(a: float, b: float) -> bool:
    return math.isclose(a, b, rel_tol=1e-9, abs_tol=1e-9)
