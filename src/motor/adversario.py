"""M4.4 · El Adversario: perfiles de cambio de igual «daño» que buscan evadir al CUSUM bilateral, y el CUSUM de varianza (contramedida).
SIMULADO (X-11). Especificación congelada en docs/actas/FB-018.md."""
from __future__ import annotations

import math
import random
import statistics
from functools import lru_cache

from .cusum import K_REF, paso

H_MEDIA = 10.011730842174083
PERFILES = ("escalon", "rampa", "zigzag", "pulsos")
BASE, VIG = 14, 14
KV = 0.5


def perfil(nombre: str, h: float) -> list[float]:
    j = range(1, VIG + 1)
    if nombre == "escalon":
        return [h] * VIG
    if nombre == "rampa":
        return [h / 7.5 * x for x in j]
    if nombre == "zigzag":
        return [((-1) ** x) * h for x in j]
    if nombre == "pulsos":
        return [3.5 * h if x % 3 == 0 else 0.0 for x in j]
    raise ValueError(nombre)


def _z(rng: random.Random, desv: list[float]) -> list[float]:
    base = [rng.gauss(0.0, 1.0) for _ in range(BASE)]
    mu, sigma = statistics.fmean(base), statistics.stdev(base) * math.sqrt(1 + 1 / BASE)
    return [(rng.gauss(0.0, 1.0) + d - mu) / sigma for d in desv]


def detecta_media(z: list[float], h: float = H_MEDIA) -> bool:
    sa = sc = 0.0
    for v in z:
        sa, sc = paso(sa, sc, v, K_REF)
        if sa >= h or sc >= h:
            return True
    return False


def maximo_varianza(z: list[float]) -> float:
    s = mejor = 0.0
    for v in z:
        s = max(0.0, s + (v * v - 1.0) - KV)
        mejor = max(mejor, s)
    return mejor


@lru_cache(maxsize=4)
def calibrar_hv(semilla: int = 20261113, n: int = 20000, fpr: float = 0.01) -> float:
    rng = random.Random(semilla)
    m = sorted(maximo_varianza(_z(rng, [0.0] * VIG)) for _ in range(n))
    return m[min(n - 1, math.ceil((1 - fpr) * n) - 1)] + 1e-9


def tasas(nombre: str, h: float, semilla: int, n: int, hv: float) -> dict:
    d = dv = du = 0
    for i in range(n):
        z = _z(random.Random(semilla + i), perfil(nombre, h) if nombre != "nulo" else [0.0] * VIG)
        a, b = detecta_media(z), maximo_varianza(z) > hv
        d += a
        dv += b
        du += a or b
    return {"media": d / n, "varianza": dv / n, "union": du / n}
