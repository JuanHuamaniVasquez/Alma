"""Contraste intrapersonal por CORRELACIÓN en la mitad de PRUEBA con nulo por desplazamiento circular (FB-027). Puro Python.

Por persona: serie ordenada de pares (x, y); mitad de entrenamiento = primera, mitad de PRUEBA = segunda (nada se ajusta: solo se separa lo que se mira). Estadístico S = mediana, entre
personas con ≥ `minimo` pares de prueba, del ρ de Spearman. Nulo: se desplaza CIRCULARMENTE y dentro de cada persona (desplazamiento aleatorio ≥ 5 posiciones) la serie y respecto de la x,
lo que conserva la autocorrelación de cada serie y rompe solo la coincidencia temporal.
"""
from __future__ import annotations

import random
from collections.abc import Sequence
from statistics import median


def _rangos(v: Sequence[float]) -> list[float]:
    orden = sorted(range(len(v)), key=lambda i: v[i])
    r = [0.0] * len(v)
    i = 0
    while i < len(orden):
        j = i
        while j + 1 < len(orden) and v[orden[j + 1]] == v[orden[i]]:
            j += 1
        for k in range(i, j + 1):
            r[orden[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def _rho(rx: list[float], ry: list[float], k: int = 0) -> float | None:
    n = len(rx)
    mx = my = (n + 1) / 2
    num = sx = sy = 0.0
    for i in range(n):
        a, b = rx[i] - mx, ry[(i + k) % n] - my
        num += a * b; sx += a * a; sy += b * b
    return num / (sx * sy) ** 0.5 if sx > 0 and sy > 0 else None


def mediana_rho_prueba(personas: dict[str, list[tuple[float, float]]], semilla: int, n_perm: int = 2000, minimo: int = 20, desplazamiento_min: int = 5) -> dict:
    prep = {}
    for p, s in personas.items():
        prueba = s[len(s) // 2:]
        if len(prueba) < minimo:
            continue
        prep[p] = (_rangos([x for x, _ in prueba]), _rangos([y for _, y in prueba]))
    obs = [r for rx, ry in prep.values() if (r := _rho(rx, ry)) is not None]
    if not obs:
        return {"n_personas": 0, "S": None, "p_neg": None, "p_pos": None, "p_bilateral": None}
    S = median(obs)
    rng = random.Random(semilla)
    ge = le = abs_ge = 0
    for _ in range(n_perm):
        rs = []
        for rx, ry in prep.values():
            n = len(rx)
            k = rng.randrange(desplazamiento_min, n - desplazamiento_min + 1)
            r = _rho(rx, ry, k)
            if r is not None:
                rs.append(r)
        m = median(rs)
        ge += m >= S; le += m <= S; abs_ge += abs(m) >= abs(S)
    n1 = n_perm + 1
    return {"n_personas": len(obs), "S": S, "p_neg": (le + 1) / n1, "p_pos": (ge + 1) / n1, "p_bilateral": (abs_ge + 1) / n1, "n_perm": n_perm}
