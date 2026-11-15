"""LB-1 · El libro contable: los 9 presupuestos sobre DC-04 y el cierre diario.

Una línea cierra si |residuo_contable| ≤ K_CIERRE·σ_manifiesto (DOC-01 v0.2.3). El libro del día
cierra si todas sus líneas contabilizables cierran. Reglas de honestidad:
  · un día sin líneas NO cierra (la ausencia es dato; no se afirma un cierre sin libro);
  · las líneas en `cuarentena` (GO-6) no se cuentan como cerradas ni se esconden: se listan aparte;
  · solo se anexa: una línea (día, presupuesto, sujeto) no se sobrescribe.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.contratos.comunes import Presupuesto
from src.contratos.dc04_libro import K_CIERRE, DC04Linea, EstadoLinea


class LineaDuplicada(ValueError):
    """Ya existe una línea para ese (día, presupuesto, sujeto): el libro es solo-anexar."""


@dataclass(frozen=True)
class CierreDelDia:
    dia_habitat: int
    cierra: bool
    lineas: int
    abiertas: tuple[DC04Linea, ...]       # contabilizables que NO cierran: la pregunta que hay que hacer
    en_cuarentena: tuple[DC04Linea, ...]  # excluidas del veredicto, nunca contadas como cerradas
    por_presupuesto: dict[Presupuesto, bool]


class Libro:
    def __init__(self) -> None:
        self._lineas: dict[tuple[int, Presupuesto, str], DC04Linea] = {}

    def anotar(self, linea: DC04Linea) -> None:
        clave = (linea.dia_habitat, linea.presupuesto_id, linea.sujeto)
        if clave in self._lineas:
            raise LineaDuplicada(f"día {clave[0]} · {clave[1].value} · {clave[2]} ya está anotada")
        self._lineas[clave] = linea

    def lineas_del_dia(self, dia: int) -> list[DC04Linea]:
        return [l for (d, _, _), l in self._lineas.items() if d == dia]

    def dias(self) -> list[int]:
        return sorted({d for d, _, _ in self._lineas})

    def cierre_del_dia(self, dia: int) -> CierreDelDia:
        todas = self.lineas_del_dia(dia)
        cuarentena = tuple(l for l in todas if l.estado_linea is EstadoLinea.CUARENTENA)
        contables = [l for l in todas if l.estado_linea is not EstadoLinea.CUARENTENA]
        abiertas = tuple(l for l in contables if not l.cierra)
        por_presupuesto: dict[Presupuesto, bool] = {}
        for l in contables:
            por_presupuesto[l.presupuesto_id] = por_presupuesto.get(l.presupuesto_id, True) and l.cierra
        return CierreDelDia(dia, cierra=bool(contables) and not abiertas, lineas=len(todas), abiertas=abiertas,
                            en_cuarentena=cuarentena, por_presupuesto=por_presupuesto)
