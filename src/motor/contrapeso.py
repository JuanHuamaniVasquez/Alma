"""MO-6 · El Contrapeso: cierre de conservación diario de un bucle (agua / aire / energía) → DC-08.

Método (en la tradición de la *conciliación de datos y detección de errores gruesos* de la
ingeniería de procesos — Narasimhan & Jordache; ver docs/evaluacion-paper.md §7):

    residuo = Σ entradas − Σ salidas − Δ almacén − pérdida declarada
    σ_propagada = √(Σ σᵢ²)                       (errores independientes: SUPUESTO declarado, GUM)
    CIERRA  ⇔  |residuo| ≤ K_CIERRE · σ_propagada          (mismo umbral 2σ que `dos_sigma`)

Reglas de honestidad:
  · **Si una pérdida no está declarada, no existe**: no se resta; aparece como residuo y NO CIERRA.
  · **Bilateral**: un residuo positivo (sale menos de lo que entró: pérdida/fuga no declarada) y uno
    negativo (sale más de lo que entró: fuente no declarada, el «octavo pasajero») son anomalías.
  · El banner se hereda de las corrientes: si alguna es SIMULADA, el cierre es SIMULADO.
  · Sin corrientes no hay libro: no se afirma un cierre (la ausencia es dato).
El umbral 2σ y la independencia son decisiones de diseño sin validar con datos reales (D-08, D-16).
"""
from __future__ import annotations

import math
from collections.abc import Sequence
from dataclasses import dataclass
from enum import StrEnum

from src.contratos.comunes import Banner, banner_heredado
from src.contratos.dc04_libro import K_CIERRE
from src.contratos.dc08_conservacion import Bucle, DC08Cierre, Veredicto


@dataclass(frozen=True)
class Corriente:
    """Una línea contabilizada del bucle: valor (kg o kWh), su σ del manifiesto y su banner."""
    nombre: str
    valor: float
    sigma: float
    banner: Banner

    def __post_init__(self) -> None:
        if not (math.isfinite(self.valor) and math.isfinite(self.sigma)) or self.sigma < 0:
            raise ValueError(f"{self.nombre}: valor finito y σ ≥ 0")


class Sentido(StrEnum):
    PERDIDA_NO_DECLARADA = "perdida_no_declarada"   # residuo > 0: entró más de lo que se explica
    FUENTE_NO_DECLARADA = "fuente_no_declarada"      # residuo < 0: salió más de lo que entró
    NINGUNO = "ninguno"


def _no_negativas(corrientes: Sequence[Corriente], lado: str) -> None:
    for c in corrientes:
        if c.valor < 0:
            raise ValueError(f"{lado} '{c.nombre}': una corriente de {lado} no puede ser negativa (usa delta_almacen)")


def cierre_de_conservacion(*, dia_habitat: int, bucle: Bucle, entradas: Sequence[Corriente],
                           salidas: Sequence[Corriente], delta_almacen: Corriente,
                           perdida_declarada: Corriente, k: float = K_CIERRE) -> DC08Cierre:
    if not entradas and not salidas:
        raise ValueError("sin corrientes no hay libro: no se afirma un cierre")
    _no_negativas(entradas, "entradas")
    _no_negativas(salidas, "salidas")
    if perdida_declarada.valor < 0:
        raise ValueError("perdida_declarada no puede ser negativa")
    todas = [*entradas, *salidas, delta_almacen, perdida_declarada]
    suma_in = sum(c.valor for c in entradas)
    suma_out = sum(c.valor for c in salidas)
    residuo = suma_in - suma_out - delta_almacen.valor - perdida_declarada.valor
    sigma = math.sqrt(sum(c.sigma ** 2 for c in todas))
    veredicto = Veredicto.CIERRA if abs(residuo) <= k * sigma else Veredicto.NO_CIERRA
    return DC08Cierre(
        dia_habitat=dia_habitat, bucle=bucle, entradas=suma_in, salidas=suma_out,
        delta_almacen=delta_almacen.valor, perdida_declarada=perdida_declarada.valor,
        residuo_conservacion=residuo, incertidumbre_propagada=sigma, veredicto=veredicto,
        banner=banner_heredado(*(c.banner for c in todas)))


def sentido(cierre: DC08Cierre, k: float = K_CIERRE) -> Sentido:
    if cierre.veredicto is Veredicto.CIERRA:
        return Sentido.NINGUNO
    return Sentido.PERDIDA_NO_DECLARADA if cierre.residuo_conservacion > 0 else Sentido.FUENTE_NO_DECLARADA


def abre_investigacion(cierre: DC08Cierre) -> bool:
    """NO CIERRA abre investigación D6 el mismo día (DOC-01, DC-08)."""
    return cierre.veredicto is Veredicto.NO_CIERRA
