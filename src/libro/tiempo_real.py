"""LB-1 · Línea `tiempo` del libro con filas REALES de LifeSnaps (S-07): 1440 min = actividad + sueño + vigilia.

Convención declarada: σ del manifiesto = 0,5 min, de modo que la regla de cierre del libro (|r| ≤ 2σ = 1 min) coincide con la
tolerancia de `cierre_tiempo` (redondeo a minuto del export). Un día incompleto (falta algún componente) NO genera línea:
la ausencia es dato y se cuenta aparte. `fuente_linea` = DC-01 del día de la persona (no se inventa otra trazabilidad).
"""
from __future__ import annotations

from src.contratos.comunes import Presupuesto
from src.contratos.dc04_libro import DC04Linea, EstadoLinea

from .cierre_tiempo import COMPONENTES, MINUTOS_DIA, evaluar_dia

SIGMA_MANIFIESTO_MIN = 0.5


def linea_tiempo(fila: dict, dia_habitat: int) -> DC04Linea | None:
    c = evaluar_dia(fila)
    if c.residuo_min is None:
        return None
    observada = MINUTOS_DIA + c.residuo_min
    assert all(fila.get(k) not in (None, "") for k in COMPONENTES)
    return DC04Linea(dia_habitat=dia_habitat, presupuesto_id=Presupuesto.TIEMPO, sujeto=fila["id"],
                     emision_esperada=MINUTOS_DIA, incertidumbre_del_manifiesto=SIGMA_MANIFIESTO_MIN, emision_observada=observada,
                     residuo_contable=c.residuo_min, fuente_linea=f"DC-01:lifesnaps-{fila['id']}-{fila['date']}",
                     estado_linea=EstadoLinea.LIMPIO if c.estado is EstadoLinea.LIMPIO else EstadoLinea.SOSPECHOSO)
