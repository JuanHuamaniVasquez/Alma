"""MO-1 / MO-2 / MO-3 · Modelo nulo personal → residuo (DC-06) → CUSUM bilateral → alarma detectada.

Para UNA persona y UN indicador, día a día:
  · los primeros DIAS_BASE datos válidos son aprendizaje (sin predicción: no se finge confianza);
  · después, la línea base se CONGELA (para poder detectar deriva) y cada día se emite un DC-06:
        residuo = observado − predicho (media de la línea base);  σ_efectiva de `linea_base.py`;
        bandera: «deriva» si el CUSUM cruzó h, «sorpresa» si |z| > 2, «normal» si no;
        `cusum_acumulado` = S⁺ si domina la alza, −S⁻ si domina la caída (contrato de un solo número);
  · un dato ausente NO se rellena: no mueve el CUSUM y se cuenta (la ausencia es dato);
  · al cruzar h se emite la alarma detectada (con su regla exacta) y el CUSUM se reinicia.
Los DC-05 con recibo completo (semilla + hash de preregistro) los construye `alertas.py`.
"""
from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import UTC, date, datetime

from src.contratos.comunes import Indicador
from src.contratos.dc05_alarma import Sentido
from src.contratos.dc06_residuo import Bandera, DC06Residuo

from .cusum import K_REF, calibrar_h, paso, regla_exacta
from .linea_base import DIAS_BASE, HistorialLineasBase, LineaBase, confianza, estimar_linea_base

UMBRAL_SORPRESA = 2.0  # |z| > 2σ (MO-2)


@dataclass(frozen=True)
class AlarmaDetectada:
    fecha: date
    sentido: Sentido
    s_cruzado: float
    h: float
    regla_exacta: str
    valores: tuple[float, ...]  # observados desde el último reinicio hasta el cruce, inclusive (auditoría del recibo)


@dataclass(frozen=True)
class Observacion:
    fecha: date
    estado: str  # "aprendizaje" | "activo" | "ausente"
    confianza: float
    residuo: DC06Residuo | None = None
    alarma: AlarmaDetectada | None = None


def _ts(d: date) -> datetime:
    return datetime.combine(d, datetime.min.time(), tzinfo=UTC)


class ModeloNulo:
    def __init__(self, persona_id: str, indicador: Indicador, sigma_sensor: float, *, dias_base: int = DIAS_BASE,
                 k: float = K_REF, h: float | None = None) -> None:
        self.persona_id, self.indicador, self.sigma_sensor = persona_id, indicador, sigma_sensor
        self.dias_base, self.k = dias_base, k
        self.h = h if h is not None else calibrar_h(k=k, dias_base=dias_base)
        self.historial = HistorialLineasBase()
        self.ausencias = 0
        self._base: list[tuple[date, float]] = []
        self._linea: LineaBase | None = None
        self._s_alza = self._s_caida = 0.0
        self._desde_reinicio: list[float] = []

    @property
    def linea_base(self) -> LineaBase | None:
        return self._linea

    def observar(self, fecha: date, valor: float | None) -> Observacion:
        if valor is None or not math.isfinite(valor):
            self.ausencias += 1
            return Observacion(fecha, "ausente", confianza(len(self._base), self.dias_base))
        if self._linea is None:
            self._base.append((fecha, valor))
            lb = estimar_linea_base(self.persona_id, self.indicador.value, self._base, self.sigma_sensor, dias=self.dias_base)
            if lb is not None:
                self._linea = lb
                self.historial.registrar(lb)
            return Observacion(fecha, "aprendizaje", confianza(len(self._base), self.dias_base))
        lb = self._linea
        residuo = valor - lb.media
        z = residuo / lb.sigma_efectiva
        self._s_alza, self._s_caida = paso(self._s_alza, self._s_caida, z, self.k)
        self._desde_reinicio.append(valor)
        cruzo = max(self._s_alza, self._s_caida) >= self.h
        bandera = Bandera.DERIVA if cruzo else Bandera.SORPRESA if abs(z) > UMBRAL_SORPRESA else Bandera.NORMAL
        acumulado = self._s_alza if self._s_alza >= self._s_caida else -self._s_caida
        dc06 = DC06Residuo(sujeto=self.persona_id, ts_utc=_ts(fecha), indicador=self.indicador, observado=valor,
                           predicho=lb.media, residuo=residuo, sigma_efectiva=lb.sigma_efectiva,
                           cusum_acumulado=acumulado, bandera=bandera)
        alarma = None
        if cruzo:
            alza = self._s_alza >= self._s_caida
            alarma = AlarmaDetectada(fecha, Sentido.ALZA if alza else Sentido.CAIDA, self._s_alza if alza else self._s_caida,
                                     self.h, regla_exacta(self.k, self.h, lb.media, lb.sigma_efectiva), tuple(self._desde_reinicio))
            self._s_alza = self._s_caida = 0.0
            self._desde_reinicio = []
        return Observacion(fecha, "activo", 1.0, dc06, alarma)
