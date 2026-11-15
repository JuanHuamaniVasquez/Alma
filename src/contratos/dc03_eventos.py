"""DC-03 · Canal C — eventos con firma física (DOC-01 §3).

`banner` se añade por la convención general de DOC-01 §3 y CLAUDE.md §3 (obligatorio en todo registro).
Unidades en el nombre del campo de `parametros`: se exige la forma `magnitud_unidad`
(≥2 segmentos) salvo adimensionales conocidos. Es una heurística: no puede verificar la unidad.
"""
from __future__ import annotations

import re
from enum import StrEnum

from pydantic import model_validator

from .comunes import Banner, Contrato, Real, Sha256, Texto, TsUtc

ADIMENSIONALES = frozenset({"kp"})
_CLAVE_CON_UNIDAD = re.compile(r"^[a-z][a-z0-9]*(_[a-z0-9]+)+$")


class TipoEvento(StrEnum):
    TORMENTA_SOLAR = "tormenta_solar"  # solo eventos declarados oficialmente (alerts.json / DONKI)
    LECTURA_CLIMA_ESPACIAL = "lectura_clima_espacial"  # lectura continua de SWPC/DONKI (v0.2.1)
    EVA = "eva"
    ECLSS = "eclss"
    INYECCION_ESCENARIO = "inyeccion_escenario"
    BROTE_SIMULADO = "brote_simulado"


class FuenteEvento(StrEnum):
    SWPC = "swpc"
    DONKI = "donki"
    OSDR = "osdr"
    SIMULADOR = "simulador"


_SIMULADOS = {TipoEvento.INYECCION_ESCENARIO, TipoEvento.BROTE_SIMULADO}


class DC03Evento(Contrato):
    evento_id: Texto
    ts_utc_inicio: TsUtc
    ts_utc_fin: TsUtc
    tipo: TipoEvento
    fuente: FuenteEvento
    parametros: dict[str, Real]
    hash_lectura_cruda: Sha256
    banner: Banner

    @model_validator(mode="after")
    def _coherencia(self):
        if self.ts_utc_fin < self.ts_utc_inicio:
            raise ValueError("ts_utc_fin anterior a ts_utc_inicio")
        if not self.parametros:
            raise ValueError("parametros no puede estar vacío")
        for k in self.parametros:
            if k not in ADIMENSIONALES and not _CLAVE_CON_UNIDAD.fullmatch(k):
                raise ValueError(f"parametro '{k}': la unidad va en el nombre del campo (p. ej. flujo_protones_pfu)")
        if self.tipo in _SIMULADOS and self.fuente is not FuenteEvento.SIMULADOR:
            raise ValueError(f"{self.tipo.value} solo puede venir de fuente=simulador")
        if self.fuente is FuenteEvento.SIMULADOR and self.banner is not Banner.SIMULADO:
            raise ValueError("fuente=simulador exige banner=SIMULADO")
        if self.fuente is not FuenteEvento.SIMULADOR and self.banner is not Banner.REAL:
            raise ValueError("una fuente real (swpc/donki/osdr) exige banner=REAL")
        if self.tipo is TipoEvento.LECTURA_CLIMA_ESPACIAL and self.fuente not in {FuenteEvento.SWPC, FuenteEvento.DONKI}:
            raise ValueError("lectura_clima_espacial solo viene de swpc o donki")
        return self
