"""M2.20 · FB-020: evaluación del canal de varianza en series reales. Especificación congelada en docs/actas/FB-020.md."""
from __future__ import annotations

import math
import statistics
from collections.abc import Sequence
from datetime import date

from .adversario import H_MEDIA, detecta_media
from .canal_varianza import BASE, VIG, calibrar_critico, razon_f

PASO, MAX_DIAS = 14, 60
HS = (1.5, 1.75, 2.0, 3.0)


def ventanas(serie: Sequence[tuple[date, float]]) -> list[tuple[list[float], list[float]]]:
    """Ventanas (línea base 28, vigilancia 14) cada 14 valores válidos; se descartan las que abarcan > 60 días."""
    s = sorted(serie)
    out = []
    for i in range(0, len(s) - (BASE + VIG) + 1, PASO):
        w = s[i:i + BASE + VIG]
        if (w[-1][0] - w[0][0]).days > MAX_DIAS:
            continue
        v = [x for _, x in w]
        out.append((v[:BASE], v[BASE:]))
    return out


def zigzag(vig: Sequence[float], h: float, sd_base: float) -> list[float]:
    return [x + ((-1) ** j) * h * sd_base for j, x in enumerate(vig, start=1)]


def wilson(k: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (math.nan, math.nan)
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    m = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return (c - m, c + m)


def evaluar(series: dict[str, list[tuple[date, float]]], hs: Sequence[float] = HS) -> dict:
    c = calibrar_critico()
    todas = [(p, b, v) for p, s in sorted(series.items()) for b, v in ventanas(s)]
    n = len(todas)
    alarmas = [razon_f(b, v) > c for _, b, v in todas]
    res = {"n_ventanas": n, "n_personas_con_ventana": len({p for p, _, _ in todas}), "critico_f": c,
           "fpr": {"k": sum(alarmas), "n": n, "tasa": sum(alarmas) / n if n else None, "wilson95": wilson(sum(alarmas), n),
                   "personas_con_alarma": len({p for (p, _, _), a in zip(todas, alarmas) if a})}, "potencia": {}}
    for h in hs:
        kf = km = 0
        for _, b, v in todas:
            sd, mu = statistics.stdev(b), statistics.fmean(b)
            if sd == 0:
                continue
            vz = zigzag(v, h, sd)
            kf += razon_f(b, vz) > c
            km += detecta_media([(x - mu) / sd for x in vz], H_MEDIA)
        res["potencia"][str(h)] = {"canal_varianza": kf / n if n else None, "cusum_media": km / n if n else None, "k_varianza": kf, "k_media": km}
    return res


def veredictos(r: dict) -> dict:
    p = r["potencia"]
    h1 = r["fpr"]["tasa"] is not None and r["fpr"]["tasa"] <= 0.03
    lo, hi = r["fpr"]["wilson95"]
    return {"H1": "SOSTENIDA" if h1 else "REFUTADA", "H1_intervalo_contiene_0.03": bool(lo <= 0.03 <= hi),
            "H2": "SOSTENIDA" if p["2.0"]["canal_varianza"] >= 0.80 else "REFUTADA",
            "H3": "SOSTENIDA" if p["2.0"]["cusum_media"] <= 0.10 else "REFUTADA",
            "H4_control_valido": bool(p["3.0"]["canal_varianza"] >= 0.95)}
