"""DC-04 · Libro GPV — los 9 presupuestos, el contrato central (DOC-01 §3; `estado_linea` desde v0.2)."""
from __future__ import annotations

from enum import StrEnum

from .comunes import Contrato, DiaHabitat, Presupuesto, Real, RefFuenteLinea, SigmaPositiva, Sujeto


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
