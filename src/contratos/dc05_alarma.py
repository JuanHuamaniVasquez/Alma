"""DC-05 · Evento de alarma con recibo (DOC-01 §3). Sin `regla_exacta` no hay alarma."""
from __future__ import annotations

from enum import StrEnum

from pydantic import model_validator

from .comunes import Contrato, Indicador, Presupuesto, Real, Sha256, Texto, TsUtc


class Detector(StrEnum):
    DOS_SIGMA = "dos_sigma"
    CUSUM = "cusum"
    UMBRAL_PERSONAL = "umbral_personal"  # v0.2.7 (MP-14): regla fija contra una referencia personal


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
    # Exactamente uno (DOC-01 v0.2.5, D-30): `presupuesto_id` si el indicador tiene presupuesto documentado; si no, `indicador`.
    # Mismo patrón que DC-06 (`indicador`/`presupuesto_id`). No se inventa un presupuesto para el pulso o la temperatura.
    presupuesto_id: Presupuesto | None = None
    indicador: Indicador | None = None
    detector: Detector
    sentido: Sentido
    umbral: Real
    valor_cruzado: Real
    regla_exacta: Texto  # texto ejecutable; si la regla no se cumple, la alarma se retira sola
    semilla: int
    hash_preregistro: Sha256  # enlace a GO-2
    estado: EstadoAlarma

    @model_validator(mode="after")
    def _presupuesto_o_indicador(self):
        if (self.presupuesto_id is None) == (self.indicador is None):
            raise ValueError("exactamente uno de presupuesto_id o indicador")
        return self
