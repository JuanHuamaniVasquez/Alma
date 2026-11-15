"""MO-4 · Triangulación de 3 testigos (planta × chip × humano) y cuarta causa «modelo» (fuga vs almacén no modelado). SIMULADO (X-09).
Especificación congelada en docs/actas/FB-003.md."""
from __future__ import annotations

import math
import random
import statistics

H_CALIBRADO = 10.011730842174083  # h de MO-3 (1 % de falsas alarmas en 14 días), calibrado con la semilla 20261113

DIAS, VENTANA, DIA_EVENTO, K = 60, 14, 25, 0.5
CAUSAS = ("nada", "mundo", "sensor", "humano")
RUIDO = {"planta": 0.5, "chip": 0.5, "humano": 1.0}


def alarma(serie: list[float], h: float = H_CALIBRADO, k: float = K) -> int | None:
    """Primer día (1-indexado) > VENTANA con CUSUM bilateral por encima de h; la serie se estandariza con los días 1–VENTANA."""
    mu, sd = statistics.fmean(serie[:VENTANA]), statistics.stdev(serie[:VENTANA])
    sp = sm = 0.0
    for t in range(VENTANA, len(serie)):
        z = (serie[t] - mu) / sd
        sp, sm = max(0.0, sp + z - k), max(0.0, sm - z - k)
        if sp > h or sm > h:
            return t + 1
    return None


def mundo(rng: random.Random, causa: str, tasa: float = 0.15) -> dict[str, list[float]]:
    afectado = rng.choice(("planta", "chip")) if causa == "sensor" else None
    x, y = [], {n: [] for n in RUIDO}
    for t in range(1, DIAS + 1):
        deriva = -tasa * max(0, t - DIA_EVENTO + 1)
        xt = rng.gauss(0, 1) + (deriva if causa == "mundo" else 0.0)
        x.append(xt)
        for n, s in RUIDO.items():
            extra = deriva if (causa == "humano" and n == "humano") or (causa == "sensor" and n == afectado) else 0.0
            y[n].append(xt + extra + rng.gauss(0, s))
    return y


def diagnosticar(testigos: dict[str, list[float]]) -> tuple[str, set[str]]:
    A = {n for n, s in testigos.items() if alarma(s) is not None}
    if not A:
        return "nada", A
    if len(A) >= 2:
        return "mundo", A
    return ("humano" if "humano" in A else "sensor"), A


def ingenuo(A: set[str]) -> str:
    return "mundo" if A else "nada"


# --- cuarta causa: fuga (lineal) vs almacén no modelado (saturante) -------------------------------------
TAUS = (3, 5, 10, 20, 40)


def acumulado(rng: random.Random, causa: str, dias: int, a: float = 0.5, sigma: float = 0.3) -> list[float]:
    S = 0.6 * a * 60.0
    c, out = 0.0, []
    for t in range(1, dias + 1):
        tasa = a if causa == "fuga" else (S / 10.0) * math.exp(-(t - 1) / 10.0) / 1.0
        c += tasa + rng.gauss(0.0, sigma)
        out.append(c)
    return out


def _rss(y: list[float], f: list[float]) -> float:
    return sum((a - b) ** 2 for a, b in zip(y, f))


def diagnosticar_almacen(C: list[float]) -> str:
    """BIC de L (a·t; 1 parámetro) contra S (S·(1−e^{−t/τ}); S libre y τ de la rejilla; 2 parámetros). Devuelve 'fuga' o 'almacen'."""
    n = len(C)
    t = list(range(1, n + 1))
    a = sum(ti * ci for ti, ci in zip(t, C)) / sum(ti * ti for ti in t)
    bic_l = n * math.log(_rss(C, [a * ti for ti in t]) / n + 1e-12) + 1 * math.log(n)
    mejor = math.inf
    for tau in TAUS:
        g = [1 - math.exp(-ti / tau) for ti in t]
        s = sum(gi * ci for gi, ci in zip(g, C)) / sum(gi * gi for gi in g)
        mejor = min(mejor, n * math.log(_rss(C, [s * gi for gi in g]) / n + 1e-12) + 2 * math.log(n))
    return "fuga" if bic_l <= mejor else "almacen"
