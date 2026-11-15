"""DC-06 · Stream de residuo (DOC-01 §3). Residuo = observado − predicho (definición del motor, MO-2)."""
from __future__ import annotations

from enum import StrEnum

from pydantic import model_validator

from .comunes import Contrato, Indicador, Presupuesto, Real, SigmaPositiva, Sujeto, TsUtc, cerca


class Bandera(StrEnum):
    NORMAL = "normal"
    SORPRESA = "sorpresa"
    DERIVA = "deriva"


class DC06Residuo(Contrato):
    sujeto: Sujeto
    ts_utc: TsUtc
    indicador: Indicador | None = None
    presupuesto_id: Presupuesto | None = None
    observado: Real
    predicho: Real
    residuo: Real
    sigma_efectiva: SigmaPositiva
    cusum_acumulado: Real
    bandas: tuple[Real, Real] | None = None  # opcional: bandas calibradas (MP-1, si se acepta)
    bandera: Bandera

    @model_validator(mode="after")
    def _coherencia(self):
        if (self.indicador is None) == (self.presupuesto_id is None):
            raise ValueError("exactamente uno de indicador o presupuesto_id")
        if not cerca(self.residuo, self.observado - self.predicho):
            raise ValueError("residuo debe ser observado − predicho")
        if self.bandas is not None and self.bandas[0] > self.bandas[1]:
            raise ValueError("bandas: el límite inferior no puede superar al superior")
        return self
