"""Contraste intrapersonal binario→numérico con nulo por barajado de etiquetas DENTRO de cada persona (FB-016). Puro Python."""
from __future__ import annotations

import random
from statistics import fmean, stdev


def diferencia(pares: list[tuple[int, float]], estandarizar: bool, minimo: int = 5) -> float | None:
    """media(y | x=1) − media(y | x=0) de una persona; None si algún grupo tiene < `minimo` días."""
    a = [y for x, y in pares if x == 1]
    b = [y for x, y in pares if x == 0]
    if len(a) < minimo or len(b) < minimo:
        return None
    d = fmean(a) - fmean(b)
    if estandarizar:
        sd = stdev([y for _, y in pares])
        return d / sd if sd > 0 else None
    return d


def estadistico(personas: dict[str, list[tuple[int, float]]], estandarizar: bool) -> tuple[float, int] | None:
    ds = [d for d in (diferencia(p, estandarizar) for p in personas.values()) if d is not None]
    return (fmean(ds), len(ds)) if ds else None


def contraste(personas: dict[str, list[tuple[int, float]]], estandarizar: bool, semilla: int, signo: int, n: int = 10_000) -> dict:
    """signo=+1: se espera S>0; signo=−1: se espera S<0. p unilateral por barajado intrapersona."""
    obs = estadistico(personas, estandarizar)
    assert obs is not None
    rng = random.Random(semilla)
    xs = {p: [x for x, _ in v] for p, v in personas.items()}
    ext = 0
    for _ in range(n):
        barajado = {}
        for p, v in personas.items():
            x = xs[p][:]
            rng.shuffle(x)
            barajado[p] = [(xi, y) for xi, (_, y) in zip(x, v)]
        s = estadistico(barajado, estandarizar)
        if s is not None and signo * s[0] >= signo * obs[0]:
            ext += 1
    return {"S": obs[0], "n_personas": obs[1], "p_unilateral": (1 + ext) / (n + 1)}
