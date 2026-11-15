"""IN-4 · Banco de Falsaciones — modelo SIMULADO ocio→ánimo, versión FB-015-v2 (docs/actas/FB-015-v2.md). SIMULADO (X-08).

Igual que `banco_ocio` salvo: σ_L = 14, k = 7, σ_obs es parámetro, censura de corridas sin alarma de ánimo y rejilla de ajuste.
"""
from __future__ import annotations

import math
import random
import statistics

from .banco_ocio import DIA_EROSION, DIAS, DIAS_FPR, H_FPR_OBJETIVO, L0, LAMBDA, L_EWMA, VENTANA

SIGMA_L, K_CUSUM = 14.0, 7.0
RS = (6, 9, 12, 16, 20, 25, 30, 40, 50)
SIGMAS_OBS = (0.2, 0.3, 0.4, 0.5, 0.7, 1.0)


def correr(rng: random.Random, gamma: float, tau: float, r: float, h: float, sigma_obs: float) -> tuple[int | None, int | None]:
    m, L, y = 0.0, [], []
    for t in range(1, DIAS + 1):
        ocio = L0 - r * max(0, t - DIA_EROSION) + rng.gauss(0.0, SIGMA_L)
        m += (1.0 / tau) * (-gamma * (L0 - ocio) / 60.0 - m)
        L.append(ocio)
        y.append(m + rng.gauss(0.0, sigma_obs))
    mu_l = statistics.fmean(L[:VENTANA])
    mu_y, sd_y = statistics.fmean(y[:VENTANA]), statistics.stdev(y[:VENTANA])
    umbral_z = mu_y - L_EWMA * sd_y * math.sqrt(LAMBDA / (2 - LAMBDA))
    s, z, d_o, d_a = 0.0, mu_y, None, None
    for t in range(VENTANA + 1, DIAS + 1):
        s = max(0.0, s + (mu_l - L[t - 1]) - K_CUSUM)
        z = LAMBDA * y[t - 1] + (1 - LAMBDA) * z
        if d_o is None and t > DIA_EROSION and s > h:
            d_o = t
        if d_a is None and t > DIA_EROSION and z < umbral_z:
            d_a = t
    return d_o, d_a


def preaviso(d_o: int | None, d_a: int | None) -> int | None:
    """Preaviso con censura: sin alarma de ocio → None (excluida); sin alarma de ánimo → cota inferior DIAS − d_o."""
    if d_o is None:
        return None
    return (d_a if d_a is not None else DIAS) - d_o


def calibrar_h(semilla: int, n: int = 1000) -> tuple[int, float]:
    mx = []
    for i in range(n):
        rng = random.Random(f"{semilla}-h2-{i}")
        L = [L0 + rng.gauss(0.0, SIGMA_L) for _ in range(VENTANA + DIAS_FPR)]
        mu, s, m = statistics.fmean(L[:VENTANA]), 0.0, 0.0
        for x in L[VENTANA:]:
            s = max(0.0, s + (mu - x) - K_CUSUM)
            m = max(m, s)
        mx.append(m)
    h = math.ceil(sorted(mx)[int((1 - H_FPR_OBJETIVO) * n) - 1])
    while sum(1 for v in mx if v > h) / n > H_FPR_OBJETIVO:
        h += 1
    return h, sum(1 for v in mx if v > h) / n


def mediana(semilla: int, gamma: float, tau: float, r: float, h: float, so: float, n: int) -> tuple[float | None, int]:
    pre, con_ocio = [], 0
    for i in range(n):
        d_o, d_a = correr(random.Random(f"{semilla}-{gamma}-{tau}-{r}-{so}-{i}"), gamma, tau, r, h, so)
        con_ocio += d_o is not None
        p = preaviso(d_o, d_a)
        if p is not None:
            pre.append(p)
    return (statistics.median(pre) if pre else None), con_ocio


def ajustar(semilla: int, h: float, n: int = 200) -> tuple[float, float, float]:
    """Rejilla (r, σ_obs) minimizando la pérdida en las celdas (0,06;7)→22 y (0,20;7)→3. Empate: menor r, luego menor σ_obs."""
    mejor = None
    for r in RS:
        for so in SIGMAS_OBS:
            a = mediana(semilla, 0.06, 7, r, h, so, n)[0]
            b = mediana(semilla, 0.20, 7, r, h, so, n)[0]
            if a is None or b is None:
                continue
            perdida = (a - 22.0) ** 2 + (b - 3.0) ** 2
            if mejor is None or perdida < mejor[0]:
                mejor = (perdida, r, so)
    assert mejor is not None
    return mejor[1], mejor[2], mejor[0]
