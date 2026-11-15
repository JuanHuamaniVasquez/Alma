"""MO-10 · Línea base personal con intervalo de predicción sobre sangre REAL de astronautas (FB-024). Python puro.

Banda = media ± t·sd·√(1 + 1/n) con sd muestral y t de Student 97,5 % con n−1 g. l. (n = 3 → 4,3027; n = 2 → 12,7062). n < 2 → sin datos.
Con 3 puntos de base la banda es ANCHA: es el piso de detección del método y se declara, no se disimula.
"""
from __future__ import annotations

import math
import statistics

T975 = {1: 12.7062, 2: 4.3027}
ANALITOS = ("abs_lymphocytes", "abs_neutrophils", "nlr", "hb", "hct", "plt", "wbc")


def banda(base: list[float]) -> tuple[float, float, float] | None:
    n = len(base)
    if n < 2 or n - 1 not in T975:
        return None
    mu, sd = statistics.fmean(base), statistics.stdev(base)
    h = T975[n - 1] * sd * math.sqrt(1 + 1 / n)
    return mu, mu - h, mu + h


def evaluar(filas, pre, post, analitos=ANALITOS) -> dict:
    """{(persona, analito, t): estado}: 'dentro' | 'arriba' | 'abajo' | 'sin_datos' | 'sospechoso'; + media personal para el % de cambio."""
    res, personas = {}, sorted({f.persona for f in filas})
    for p in personas:
        for a in analitos:
            base = [f.v[a] for f in filas if f.persona == p and f.t in pre and f.v.get(a) is not None and a not in f.sospechosos]
            b = banda(base)
            for f in filas:
                if f.persona != p or f.t not in post:
                    continue
                x = f.v.get(a)
                if a in f.sospechosos:
                    res[(p, a, f.t)] = {"estado": "sospechoso", "cambio_pct": None}
                elif b is None or x is None:
                    res[(p, a, f.t)] = {"estado": "sin_datos", "cambio_pct": None}
                else:
                    mu, lo, hi = b
                    res[(p, a, f.t)] = {"estado": "arriba" if x > hi else "abajo" if x < lo else "dentro", "cambio_pct": 100.0 * (x - mu) / mu if mu else None}
    return res


T975_GL = {5: 2.5706, 6: 2.4469, 7: 2.3646, 8: 2.3060}


def evaluar_agrupada(filas, pre, post, analitos=ANALITOS) -> dict:
    """FB-025 · banda personal con la desviación intra-persona AGRUPADA entre personas (más grados de libertad). {(persona, analito, t): {estado, cambio_pct, semiancho_pct}}."""
    personas = sorted({f.persona for f in filas})
    res, info = {}, {}
    for a in analitos:
        bases = {p: [f.v[a] for f in filas if f.persona == p and f.t in pre and f.v.get(a) is not None and a not in f.sospechosos] for p in personas}
        gl = sum(max(len(b) - 1, 0) for b in bases.values())
        ss = sum(sum((x - statistics.fmean(b)) ** 2 for x in b) for b in bases.values() if len(b) >= 2)
        if gl not in T975_GL:
            continue
        sd, t = math.sqrt(ss / gl), T975_GL[gl]
        info[a] = {"gl": gl, "t": t, "sd": sd}
        for p in personas:
            b = bases[p]
            if len(b) < 1:
                continue
            mu = statistics.fmean(b)
            h = t * sd * math.sqrt(1 + 1 / len(b))
            for f in filas:
                if f.persona != p or f.t not in post:
                    continue
                x = f.v.get(a)
                if a in f.sospechosos or x is None:
                    res[(p, a, f.t)] = {"estado": "sospechoso" if a in f.sospechosos else "sin_datos", "cambio_pct": None, "semiancho_pct": 100 * h / mu if mu else None}
                else:
                    res[(p, a, f.t)] = {"estado": "arriba" if x > mu + h else "abajo" if x < mu - h else "dentro", "cambio_pct": 100 * (x - mu) / mu if mu else None,
                                        "semiancho_pct": 100 * h / mu if mu else None}
    return {"res": res, "info": info}
