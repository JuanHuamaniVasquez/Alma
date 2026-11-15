"""MO-1 · Línea base personal, VERSIONADA y solo-anexar.

Una línea base nunca se sobrescribe: re-calibrar crea una versión nueva con su fecha y su motivo, y la
primera versión se conserva siempre. Así se puede medir la **deriva acumulada entre generaciones de línea
base** — la «rana hirviendo» de DOC-04 §6: cada cohorte normaliza un poco peor y nadie recuerda la
primera. Este es el ENCHUFE de M-L1 (Archivo de Generaciones, extensión multi-cohorte de MO-1): M-L1 no se
construye hoy (DOC-04 §10), pero lo construido aquí ya enchufa en él.

σ_efectiva = max(σ_sensor, s·√(1 + 1/n)): s·√(1+1/n) es la desviación típica de la predicción para UN dato
nuevo con media y SD estimadas con n días (intervalo de predicción); σ_sensor es el piso que impone el
instrumento. Honestidad: sin priors poblacionales reales (OSDR sin archivos) no se predice nada antes de
completar `DIAS_BASE` datos válidos: es el «modo aprendizaje honesto» de DOC-01.
"""
from __future__ import annotations

import math
import statistics
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date

DIAS_BASE = 14


@dataclass(frozen=True)
class LineaBase:
    persona_id: str
    indicador: str
    version: int
    n: int
    media: float
    sd: float
    sigma_sensor: float
    desde: date
    hasta: date
    motivo: str

    @property
    def sigma_efectiva(self) -> float:
        return max(self.sigma_sensor, self.sd * math.sqrt(1 + 1 / self.n))

    @property
    def manda_el_sensor(self) -> bool:
        """True si el piso del instrumento, y no la variabilidad de la persona, fija la σ."""
        return self.sigma_sensor >= self.sd * math.sqrt(1 + 1 / self.n)


def confianza(n_validos: int, dias: int = DIAS_BASE) -> float:
    return min(1.0, n_validos / dias)


def estimar_linea_base(persona_id: str, indicador: str, observaciones: Sequence[tuple[date, float | None]],
                       sigma_sensor: float, *, dias: int = DIAS_BASE, version: int = 1,
                       motivo: str = "línea base inicial") -> LineaBase | None:
    """None mientras no haya `dias` datos válidos (modo aprendizaje). Usa los PRIMEROS `dias` válidos."""
    validas = [(d, v) for d, v in observaciones if v is not None and math.isfinite(v)]
    if len(validas) < dias:
        return None
    base = validas[:dias]
    valores = [v for _, v in base]
    return LineaBase(persona_id, indicador, version, dias, statistics.fmean(valores), statistics.stdev(valores),
                     sigma_sensor, base[0][0], base[-1][0], motivo)


class HistorialLineasBase:
    """Solo-anexar: las versiones se numeran 1, 2, 3… y no se borran ni se editan."""

    def __init__(self) -> None:
        self._por_clave: dict[tuple[str, str], list[LineaBase]] = {}

    def registrar(self, lb: LineaBase) -> None:
        versiones = self._por_clave.setdefault((lb.persona_id, lb.indicador), [])
        if lb.version != len(versiones) + 1:
            raise ValueError(f"la versión de la línea base debe ser {len(versiones) + 1}, no {lb.version}: solo se anexa")
        if versiones and lb.desde <= versiones[-1].hasta:
            raise ValueError("una línea base nueva debe calcularse con datos posteriores a la anterior")
        versiones.append(lb)

    def versiones(self, persona_id: str, indicador: str) -> tuple[LineaBase, ...]:
        return tuple(self._por_clave.get((persona_id, indicador), ()))

    def vigente(self, persona_id: str, indicador: str) -> LineaBase | None:
        v = self._por_clave.get((persona_id, indicador))
        return v[-1] if v else None

    def deriva_entre_versiones(self, persona_id: str, indicador: str, v1: int, v2: int) -> float:
        """(media v2 − media v1) en σ efectivas de la v1."""
        vs = self.versiones(persona_id, indicador)
        a, b = vs[v1 - 1], vs[v2 - 1]
        return (b.media - a.media) / a.sigma_efectiva

    def deriva_acumulada(self, persona_id: str, indicador: str) -> float:
        """Distancia de la línea base VIGENTE a la PRIMERA, en σ de la primera: la «rana hirviendo»."""
        vs = self.versiones(persona_id, indicador)
        if len(vs) < 2:
            return 0.0
        return (vs[-1].media - vs[0].media) / vs[0].sigma_efectiva
