"""DC-04 · Libro GPV — los 9 presupuestos, el contrato central (DOC-01 §3; `estado_linea` desde v0.2)."""
from __future__ import annotations

from enum import StrEnum

from pydantic import model_validator

from .comunes import Contrato, DiaHabitat, Presupuesto, Real, RefFuenteLinea, SigmaPositiva, Sujeto, cerca

# Regla de cierre del libro (DOC-01 v0.2.3, decisión del humano 2026-11-15): una línea cierra si
# |residuo_contable| ≤ K_CIERRE · incertidumbre_del_manifiesto. 2σ es el mismo umbral que el
# detector `dos_sigma` de DC-05; no está validado con datos reales (ver docs/checklist-backend.md).
K_CIERRE = 2.0


class EstadoLinea(StrEnum):
    LIMPIO = "limpio"
    SOSPECHOSO = "sospechoso"
    CUARENTENA = "cuarentena"


class DC04Linea(Contrato):
    dia_habitat: DiaHabitat
    presupuesto_id: Presupuesto
    sujeto: Sujeto  # persona_id o "habitat": cuerpo o máquina, mismo libro
    emision_esperada: Real  # el manifiesto
    # El piso de detección (hallazgo v4): estrictamente positiva, una σ cero no es un manifiesto.
    incertidumbre_del_manifiesto: SigmaPositiva
    emision_observada: Real
    residuo_contable: Real
    fuente_linea: RefFuenteLinea  # trazabilidad de cada entrada (DC-01/02/03)
    estado_linea: EstadoLinea

    @model_validator(mode="after")
    def _residuo_contable(self):
        if not cerca(self.residuo_contable, self.emision_observada - self.emision_esperada):
            raise ValueError("residuo_contable debe ser emision_observada − emision_esperada")
        return self

    @property
    def cierra(self) -> bool:
        return abs(self.residuo_contable) <= K_CIERRE * self.incertidumbre_del_manifiesto
