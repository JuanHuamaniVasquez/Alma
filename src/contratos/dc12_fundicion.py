"""DC-12 · Contrato de Fundición — la tarjeta del lab (DOC-01 §3, DOC-04).

La puerta de LA FUNDICIÓN vive aquí: sin mecanismo, sin fuente con identificador válido o sin
precio, la tarjeta no existe. Interpretaciones que el DOC no fija (a confirmar con el humano):
  · `precio` = {datos: texto, computo: texto, dias: entero ≥ 0}.
  · `valor_si_cierta` = lista no vacía de referencias "DC-xx".
  · `preregistro_hash` es obligatorio desde `en_prueba` (el hash va ANTES de ejecutar, GO-2,
    DOC-01 v0.2.1) y también en `sin_datos`; en `vivero` es opcional (preregistrar antes es válido).
"""
from __future__ import annotations

import re
from enum import StrEnum
from typing import Annotated
from uuid import UUID

from pydantic import Field, StringConstraints, model_validator

from .comunes import Contrato, Sha256, Texto, TsUtc

_OSDR = re.compile(r"^OSD?-\d+$")
_DOI = re.compile(r"^10\.\d{4,9}/\S+$")


class TipoFuente(StrEnum):
    ACCESION_OSDR = "accesión OSDR"
    DOI = "DOI"
    LOTE = "lote"


class Fuente(Contrato):
    id: Texto
    tipo: TipoFuente
    semilla: int | None = None  # los lotes llevan semilla

    @model_validator(mode="after")
    def _identificador(self):
        if self.tipo is TipoFuente.ACCESION_OSDR and not _OSDR.fullmatch(self.id):
            raise ValueError("accesión OSDR con forma OS-NNN u OSD-NNN")
        if self.tipo is TipoFuente.DOI and not _DOI.fullmatch(self.id):
            raise ValueError("DOI con forma 10.NNNN/…")
        if self.tipo is TipoFuente.LOTE and self.semilla is None:
            raise ValueError("un lote exige semilla")
        return self


class TipoPar(StrEnum):
    CUERPO = "cuerpo"
    HABITAT = "habitat"
    RELATO = "relato"


class ParVariables(Contrato):
    senal_cuerpo: Texto
    otra_senal: Texto
    tipo_otra_senal: TipoPar


class Precio(Contrato):
    datos: Texto
    computo: Texto
    dias: Annotated[int, Field(ge=0)]


class EstadoTarjeta(StrEnum):
    VIVERO = "vivero"
    EN_PRUEBA = "en_prueba"
    REFUTADA = "refutada"
    SOSTENIDA = "sostenida"
    SIN_DATOS = "sin_datos"


RefDetector = Annotated[str, StringConstraints(pattern=r"^DC-(0[1-9]|1[0-9]|2[0-9])$")]


class DC12Tarjeta(Contrato):
    tarjeta_id: UUID
    par_variables: ParVariables
    mecanismo: Texto  # ref biblioteca FA; "correlación sin mecanismo" no pasa la puerta
    prediccion: Texto  # qué observar, cuándo, con qué efecto mínimo
    senal_refutadora: Texto  # escrita antes de probar
    fuentes: Annotated[list[Fuente], Field(min_length=1)]  # sin fuente cargada, la tarjeta no existe
    precio: Precio
    valor_si_cierta: Annotated[list[RefDetector], Field(min_length=1)]  # detectores DC-xx nuevos
    estado: EstadoTarjeta
    preregistro_hash: Sha256 | None = None
    vencimiento: TsUtc | None = None  # preguntas perecederas (M-L3)

    @model_validator(mode="after")
    def _preregistro(self):
        if self.estado is not EstadoTarjeta.VIVERO and self.preregistro_hash is None:
            raise ValueError("desde en_prueba el preregistro_hash es obligatorio (se hashea ANTES de ejecutar)")
        return self
