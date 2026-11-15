"""DC-05 · Evento de alarma con recibo (DOC-01 §3). Sin `regla_exacta` no hay alarma."""
from __future__ import annotations

from enum import StrEnum

from .comunes import Contrato, Presupuesto, Real, Sha256, Texto, TsUtc


class Detector(StrEnum):
    DOS_SIGMA = "dos_sigma"
    CUSUM = "cusum"


class Sentido(StrEnum):
    ALZA = "alza"
    CAIDA = "caída"  # bilateral obligatorio: el CUSUM unilateral era ciego a las caídas (v4)


class EstadoAlarma(StrEnum):
    ACTIVA = "activa"
    RETIRADA = "retirada"
    APELADA = "apelada"


class DC05Alarma(Contrato):
    alarma_id: Texto
    ts_utc: TsUtc
    presupuesto_id: Presupuesto
    detector: Detector
    sentido: Sentido
    umbral: Real
    valor_cruzado: Real
    regla_exacta: Texto  # texto ejecutable; si la regla no se cumple, la alarma se retira sola
    semilla: int
    hash_preregistro: Sha256  # enlace a GO-2
    estado: EstadoAlarma
