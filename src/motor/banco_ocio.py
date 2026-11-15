"""IN-4 · Banco de Falsaciones — modelo SIMULADO del par ocio→ánimo (réplica independiente de FB-002, acta FB-015).

TODO lo de aquí es simulación etiquetada (docs/politica-de-datos.md X-08): un modelo MÍO, no el original de FB-002.
Especificación completa y congelada en docs/actas/FB-015.md (no se edita sin un acta -v2).
"""
from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass

DIAS, DIA_EROSION, VENTANA = 150, 30, 14
L0, SIGMA_L, K_CUSUM = 120.0, 20.0, 10.0
SIGMA_OBS, LAMBDA, L_EWMA = 1.0, 0.2, 3.0
H_FPR_OBJETIVO, DIAS_FPR = 0.018, 70


@dataclass(frozen=True)
class Corrida:
    dia_ocio: int | None
    dia_animo: int | None

    @property
    def preaviso(self) -> int | None:
        return None if self.dia_ocio is None or self.dia_animo is None else self.dia_animo - self.dia_ocio


def correr(rng: random.Random, gamma: float, tau: float, r: float, h: float, dias: int = DIAS) -> Corrida:
    """Una tripulación sintética de `dias` días; devuelve el día (1-indexado) de la primera alarma tras la erosión de cada detector."""
    m, L, y = 0.0, [], []
    for t in range(1, dias + 1):
        ocio = L0 - r * max(0, t - DIA_EROSION) + rng.gauss(0.0, SIGMA_L)
        m += (1.0 / tau) * (-gamma * (L0 - ocio) / 60.0 - m)
        L.append(ocio)
        y.append(m + rng.gauss(0.0, SIGMA_OBS))
    mu_l = statistics.fmean(L[:VENTANA])
    mu_y, sd_y = statistics.fmean(y[:VENTANA]), statistics.stdev(y[:VENTANA])
    umbral_z = mu_y - L_EWMA * sd_y * math.sqrt(LAMBDA / (2 - LAMBDA))
    s, z = 0.0, mu_y
    dia_ocio = dia_animo = None
    for t in range(VENTANA + 1, dias + 1):
        s = max(0.0, s + (mu_l - L[t - 1]) - K_CUSUM)
        z = LAMBDA * y[t - 1] + (1 - LAMBDA) * z
        if dia_ocio is None and t > DIA_EROSION and s > h:
            dia_ocio = t
        if dia_animo is None and t > DIA_EROSION and z < umbral_z:
            dia_animo = t
    return Corrida(dia_ocio, dia_animo)


def calibrar_h(semilla: int, n: int = 1000) -> tuple[int, float]:
    """Menor h entero (min) con falsas alarmas ≤ 1,8 % en 70 días sin erosión. Devuelve (h, FPR alcanzada)."""
    maximos = []
    for i in range(n):
        rng = random.Random(f"{semilla}-h-{i}")
        L = [L0 + rng.gauss(0.0, SIGMA_L) for _ in range(VENTANA + DIAS_FPR)]
        mu = statistics.fmean(L[:VENTANA])
        s, mx = 0.0, 0.0
        for x in L[VENTANA:]:
            s = max(0.0, s + (mu - x) - K_CUSUM)
            mx = max(mx, s)
        maximos.append(mx)
    maximos.sort()
    h = math.ceil(maximos[int((1 - H_FPR_OBJETIVO) * n) - 1])
    while sum(1 for v in maximos if v > h) / n > H_FPR_OBJETIVO:
        h += 1
    return h, sum(1 for v in maximos if v > h) / n


def mediana_preaviso(semilla: int, gamma: float, tau: float, r: float, h: float, n: int = 400) -> tuple[float | None, int, int]:
    """(mediana del preaviso, corridas con preaviso medible, corridas con alarma de ocio)."""
    pre, ocio = [], 0
    for i in range(n):
        c = correr(random.Random(f"{semilla}-{gamma}-{tau}-{i}"), gamma, tau, r, h)
        ocio += c.dia_ocio is not None
        if c.preaviso is not None:
            pre.append(c.preaviso)
    return (statistics.median(pre) if pre else None), len(pre), ocio


def ajustar_r(semilla: int, h: float, objetivo: float = 22.0, gamma: float = 0.06, tau: float = 7.0,
              lo: float = 0.5, hi: float = 30.0, pasos: int = 24) -> float:
    """Bisección de r: más erosión ⇒ ambos detectores saltan antes; se busca la r con mediana nominal = objetivo.
    La monotonía no se asume: se evalúa en cada paso y se sigue el signo de (mediana − objetivo)."""
    f_lo = (mediana_preaviso(semilla, gamma, tau, lo, h)[0] or 0.0) - objetivo
    for _ in range(pasos):
        mid = (lo + hi) / 2
        f_mid = (mediana_preaviso(semilla, gamma, tau, mid, h)[0] or 0.0) - objetivo
        if (f_mid > 0) == (f_lo > 0):
            lo, f_lo = mid, f_mid
        else:
            hi = mid
    return (lo + hi) / 2
