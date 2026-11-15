"""MO-6 · El Contrapeso: cierre de conservación diario de un bucle (agua / aire / energía) → DC-08.

Método (en la tradición de la *conciliación de datos y detección de errores gruesos* de la
ingeniería de procesos — Narasimhan & Jordache; ver docs/evaluacion-paper.md §7):

    residuo = Σ entradas − Σ salidas − Δ almacén − pérdida declarada
    σ_propagada² = Σ aᵢ²σᵢ² + 2 Σ_{i<j} aᵢaⱼ ρᵢⱼ σᵢσⱼ   (aᵢ=+1 entradas, −1 el resto; ρ=0 por defecto = independientes)
    CIERRA  ⇔  |residuo| ≤ K_CIERRE · σ_propagada          (mismo umbral 2σ que `dos_sigma`)

Reglas de honestidad:
  · **Si una pérdida no está declarada, no existe**: no se resta; aparece como residuo y NO CIERRA.
  · **Bilateral**: un residuo positivo (sale menos de lo que entró: pérdida/fuga no declarada) y uno
    negativo (sale más de lo que entró: fuente no declarada, el «octavo pasajero») son anomalías.
  · El banner se hereda de las corrientes: si alguna es SIMULADA, el cierre es SIMULADO.
  · Sin corrientes no hay libro: no se afirma un cierre (la ausencia es dato).
Por defecto se asume independencia (supuesto declarado, GUM); si hay errores compartidos se declaran con `correlaciones`:
  · entre una ENTRADA y una SALIDA con ρ>0 (error común, p. ej. mismo tipo de sensor) los errores se CANCELAN en el residuo;
  · entre dos SALIDAS (o dos entradas) con ρ>0 (p. ej. el mismo modelo de manifiesto para todos los astronautas) se SUMAN:
    la cuadratura independiente SUBESTIMA la σ y provoca falsas alarmas. Hallazgo del red teaming (docs/red-team.md).
El umbral 2σ y los ρ son decisiones de diseño sin validar con datos reales (D-08, D-16, D-23).
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


def _sigma_propagada(entradas, salidas, delta, perdida, correlaciones) -> float:
    lineas = [(c, +1.0) for c in entradas] + [(c, -1.0) for c in (*salidas, delta, perdida)]
    por_nombre = {c.nombre: (c, a) for c, a in lineas}
    if correlaciones and len(por_nombre) != len(lineas):
        raise ValueError("para declarar correlaciones los nombres de las corrientes deben ser únicos")
    varianza = sum((a * c.sigma) ** 2 for c, a in lineas)
    vistos: set[frozenset[str]] = set()
    for n1, n2, rho in correlaciones:
        if n1 not in por_nombre or n2 not in por_nombre or n1 == n2:
            raise ValueError(f"correlación entre corrientes inexistentes o iguales: {n1!r}, {n2!r}")
        if not -1.0 <= rho <= 1.0 or not math.isfinite(rho):
            raise ValueError("ρ debe estar en [−1, 1]")
        par = frozenset((n1, n2))
        if par in vistos:
            raise ValueError(f"correlación repetida: {n1!r}, {n2!r}")
        vistos.add(par)
        (c1, a1), (c2, a2) = por_nombre[n1], por_nombre[n2]
        varianza += 2 * a1 * a2 * rho * c1.sigma * c2.sigma
    if varianza < -1e-12:
        raise ValueError("las correlaciones declaradas son inconsistentes (varianza negativa)")
    return math.sqrt(max(varianza, 0.0))


def cierre_de_conservacion(*, dia_habitat: int, bucle: Bucle, entradas: Sequence[Corriente],
                           salidas: Sequence[Corriente], delta_almacen: Corriente,
                           perdida_declarada: Corriente, k: float = K_CIERRE,
                           correlaciones: Sequence[tuple[str, str, float]] = ()) -> DC08Cierre:
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
    sigma = _sigma_propagada(entradas, salidas, delta_almacen, perdida_declarada, correlaciones)
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


def sensibilidad_rho(*, rhos: Sequence[float], pares: Sequence[tuple[str, str]], **cierre) -> list[dict]:
    """M2.17b · ρ como supuesto SENSIBLE: recalcula el cierre con la misma correlación ρ en todos los `pares` para cada ρ del barrido.

    Devuelve por ρ la σ propagada, la razón σ(ρ)/σ(0) y el veredicto, para que se vea cuándo el veredicto depende del supuesto.
    El soporte empírico de ρ≈0,1–0,15 es la demanda de agua real de Utah (FB-012, S-12: ρ entre hogares 0,126, INCONCLUSA):
    es un orden de magnitud, no un valor medido en un hábitat. Sin `correlaciones` en `cierre` (se declaran aquí).
    """
    if "correlaciones" in cierre:
        raise ValueError("las correlaciones se declaran con `rhos` y `pares`")
    base = cierre_de_conservacion(**cierre).incertidumbre_propagada
    filas = []
    for rho in rhos:
        c = cierre_de_conservacion(**cierre, correlaciones=[(a, b, rho) for a, b in pares])
        filas.append({"rho": rho, "sigma": c.incertidumbre_propagada,
                      "razon_vs_independiente": c.incertidumbre_propagada / base if base else math.inf, "veredicto": c.veredicto})
    return filas
