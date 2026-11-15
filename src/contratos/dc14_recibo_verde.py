"""DC-14 · Recibo de verde — «el verde sin recibo no aparece» (DOC-01 v0.2.6, MP-5 / M2.10).

Un «sin anomalías» NO es evidencia de ausencia (Altman & Bland 1995, BMJ, doi:10.1136/bmj.311.7003.485): solo dice qué
habría visto el detector. El recibo declara el efecto mínimo detectable (MDE) y la potencia **dados los días válidos
realmente observados** (la cobertura importa), en σ y en **unidades físicas**, más el supuesto estadístico. Con pocos
datos el estado es `sin_datos_suficientes`: ni verde ni alarma — la ausencia es dato.
"""
from __future__ import annotations

from enum import StrEnum
from typing import Annotated

from pydantic import Field, model_validator

from .comunes import Banner, Contrato, Indicador, Presupuesto, Real, Sha256, SigmaPositiva, Sujeto, Texto, TsUtc


class EstadoVerde(StrEnum):
    VERDE = "verde"
    SIN_DATOS = "sin_datos_suficientes"
    RETIRADO = "retirado"  # la regla ya no se cumple al reevaluar con datos corregidos


class Detector(StrEnum):
    """Detectores admitidos en un recibo de verde (DOC-01 v0.2.7): solo los estadísticos; `umbral_personal` es de contexto y NO sustenta un verde."""
    DOS_SIGMA = "dos_sigma"
    CUSUM = "cusum"


class DC14ReciboVerde(Contrato):
    recibo_id: Texto
    ts_utc: TsUtc  # fin de la ventana
    sujeto: Sujeto
    presupuesto_id: Presupuesto | None = None   # exactamente uno, como DC-05 (v0.2.5)
    indicador: Indicador | None = None
    estado: EstadoVerde
    ventana_dias: Annotated[int, Field(ge=1)]
    dias_validos: Annotated[int, Field(ge=0)]    # la cobertura (dias_validos / ventana_dias) viaja con el recibo
    detector: Detector
    k: Real
    h: SigmaPositiva
    potencia_declarada: Annotated[float, Field(gt=0, lt=1, allow_inf_nan=False)] | None  # None si sin_datos
    mde_sigma: SigmaPositiva | None
    mde_fisico: SigmaPositiva | None
    unidad: Texto
    supuesto: Texto                              # p. ej. «ruido independiente; calibrado en simulación X-06 …»
    regla_exacta: Texto                          # verde ⇔ la regla NO alarma sobre los datos de la ventana
    semilla: int
    hash_preregistro: Sha256
    banner: Banner

    @model_validator(mode="after")
    def _coherencia(self):
        if (self.presupuesto_id is None) == (self.indicador is None):
            raise ValueError("exactamente uno de presupuesto_id o indicador")
        if self.dias_validos > self.ventana_dias:
            raise ValueError("dias_validos no puede superar la ventana")
        declara = (self.potencia_declarada, self.mde_sigma, self.mde_fisico)
        if self.estado is EstadoVerde.SIN_DATOS:
            if any(x is not None for x in declara):
                raise ValueError("sin_datos_suficientes no declara potencia ni MDE: no hay base para afirmarlos")
        elif any(x is None for x in declara):
            raise ValueError("un verde declara potencia, MDE en σ y MDE físico: sin ellos no hay recibo")
        return self

    @property
    def cobertura(self) -> float:
        return self.dias_validos / self.ventana_dias
