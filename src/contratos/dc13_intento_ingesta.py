"""DC-13 · Registro de intento de ingesta (DOC-01 v0.2.2, MP-4 aceptada 2026-11-15).

«La ausencia es dato» aplicada al propio feed: distingue *sin evento* (sol tranquilo) de
*no pudimos mirar* (feed caído, vacío o movido). Cada intento de leer una fuente externa
deja un registro, también el fallido — jamás se rellena una lectura que no llegó.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import Field, StringConstraints, model_validator

from .comunes import Banner, Contrato, Sha256, Texto, TsUtc
from .dc03_eventos import FuenteEvento


class ResultadoIntento(StrEnum):
    OK = "ok"
    FALLO = "fallo"
    VACIO = "vacio"


Url = Annotated[str, StringConstraints(pattern=r"^https?://\S+$")]


class DC13Intento(Contrato):
    intento_id: Texto
    ts_utc: TsUtc
    fuente: FuenteEvento
    url: Url
    resultado: ResultadoIntento
    http_status: Annotated[int, Field(ge=100, le=599)] | None  # None si ni siquiera hubo respuesta HTTP
    hash_lectura_cruda: Sha256 | None = None  # solo si resultado == ok
    error: Texto | None = None  # solo si resultado == fallo
    banner: Banner  # REAL en operación; SIMULADO en replay/adversario

    @model_validator(mode="after")
    def _coherencia(self):
        r = self.resultado
        if r is ResultadoIntento.OK:
            if self.hash_lectura_cruda is None:
                raise ValueError("resultado=ok exige hash_lectura_cruda (la lectura cruda se archiva)")
            if self.error is not None:
                raise ValueError("resultado=ok no lleva error")
            if self.http_status is None or not 200 <= self.http_status < 300:
                raise ValueError("resultado=ok exige http_status 2xx")
        if r is ResultadoIntento.FALLO:
            if self.error is None:
                raise ValueError("resultado=fallo exige error (el fallo se registra con su causa)")
            if self.hash_lectura_cruda is not None:
                raise ValueError("resultado=fallo no puede llevar hash: no hubo lectura")
        if r is ResultadoIntento.VACIO:
            if self.hash_lectura_cruda is not None or self.error is not None:
                raise ValueError("resultado=vacio no lleva hash ni error")
            if self.http_status is None or not 200 <= self.http_status < 300:
                raise ValueError("resultado=vacio exige http_status 2xx (respondió, pero sin registros)")
        if self.fuente is FuenteEvento.SIMULADOR and self.banner is not Banner.SIMULADO:
            raise ValueError("fuente=simulador exige banner=SIMULADO")
        if self.fuente is not FuenteEvento.SIMULADOR and self.banner is not Banner.REAL:
            raise ValueError("una fuente real (swpc/donki/osdr) exige banner=REAL")
        return self
