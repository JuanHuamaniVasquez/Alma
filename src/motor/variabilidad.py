"""Estadísticos de variabilidad de una corriente diaria (FB-012): ρ1, CV y correlación entre hogares.
Puro Python (sin Django). Un día sin datos es NO observado: no se imputa."""
from __future__ import annotations

import math
import random
from datetime import date, timedelta
from statistics import mean, median, stdev


def pearson(x: list[float], y: list[float]) -> float | None:
    if len(x) < 3 or len(x) != len(y):
        return None
    mx, my = mean(x), mean(y)
    sxx = sum((a - mx) ** 2 for a in x)
    syy = sum((b - my) ** 2 for b in y)
    if sxx == 0 or syy == 0:
        return None
    return sum((a - mx) * (b - my) for a, b in zip(x, y)) / math.sqrt(sxx * syy)


def rho1(serie: dict[date, float], min_pares: int = 20) -> float | None:
    """Autocorrelación lag-1 sobre pares de días calendario consecutivos ambos observados."""
    x, y = [], []
    for d, v in serie.items():
        w = serie.get(d + timedelta(days=1))
        if w is not None:
            x.append(v)
            y.append(w)
    return pearson(x, y) if len(x) >= min_pares else None


def cv(serie: dict[date, float], min_dias: int = 20) -> float | None:
    if len(serie) < min_dias:
        return None
    m = mean(serie.values())
    return stdev(serie.values()) / m if m > 0 else None


def correlacion_entre(series: list[dict[date, float]], min_comunes: int = 20) -> list[float]:
    out = []
    for i in range(len(series)):
        for j in range(i + 1, len(series)):
            comunes = sorted(set(series[i]) & set(series[j]))
            if len(comunes) >= min_comunes:
                r = pearson([series[i][d] for d in comunes], [series[j][d] for d in comunes])
                if r is not None:
                    out.append(r)
    return out


def barajar_dias(serie: dict[date, float], rng: random.Random) -> dict[date, float]:
    fechas = sorted(serie)
    valores = [serie[d] for d in fechas]
    rng.shuffle(valores)
    return dict(zip(fechas, valores))


def ic_mediana(valores: list[float], semilla: int, n: int = 10_000) -> tuple[float, float, float]:
    rng = random.Random(semilla)
    meds = sorted(median(rng.choices(valores, k=len(valores))) for _ in range(n))
    return median(valores), meds[int(0.025 * n)], meds[int(0.975 * n) - 1]
