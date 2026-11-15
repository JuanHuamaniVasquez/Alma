"""MO-4b · Consistencia física cruzada: ¿sensor roto o cuerpo cambiado? M6.3 / FB-022 (MP-18).

Idea: dos señales fisiológicamente acopladas (p. ej. rmssd y pulso en reposo) se mueven JUNTAS cuando cambia el cuerpo, y por separado cuando falla un
sensor. Con la pendiente b aprendida en la línea base personal, el residuo r_t = z_y − b·z_x debe quedarse en 0 si el cambio es coherente.
  · Acoplamiento: Spearman dentro de la persona, fuera de muestra (mitad de entrenamiento / mitad de prueba).
  · Clasificador de bloque (14 días): t = media(r)/(sd_r/√n);  |t| > T_CORTE ⇒ «incoherente» (sospecha de sensor);  si no, «coherente» (cuerpo).
LÍMITE DECLARADO: rmssd y pulso salen de la MISMA serie de latidos del mismo sensor óptico: un fallo del sensor corrompe a ambos. Esto solo detecta
fallos que afectan a una métrica derivada y no a la otra.
"""
from __future__ import annotations

import math
import statistics
from collections.abc import Sequence

BLOQUE = 14
T_CORTE = 3.0


def rangos(v: Sequence[float]) -> list[float]:
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


def spearman(x: Sequence[float], y: Sequence[float]) -> float | None:
    if len(x) < 5 or len(x) != len(y):
        return None
    a, b = rangos(x), rangos(y)
    ma, mb = statistics.fmean(a), statistics.fmean(b)
    num = sum((p - ma) * (q - mb) for p, q in zip(a, b))
    den = math.sqrt(sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b))
    return num / den if den else None


def ajustar(x: Sequence[float], y: Sequence[float]) -> dict | None:
    """Línea base: estandariza con media/sd de entrenamiento y ajusta z_y = b·z_x (MCO sin término libre, ya centradas)."""
    mx, my, sx, sy = statistics.fmean(x), statistics.fmean(y), statistics.pstdev(x), statistics.pstdev(y)
    if sx == 0 or sy == 0:
        return None
    zx, zy = [(p - mx) / sx for p in x], [(q - my) / sy for q in y]
    b = sum(p * q for p, q in zip(zx, zy)) / sum(p * p for p in zx)
    res = [q - b * p for p, q in zip(zx, zy)]
    sr = statistics.pstdev(res)
    return {"mx": mx, "my": my, "sx": sx, "sy": sy, "b": b, "sd_res": sr} if sr > 0 else None


def estadistico_t(aj: dict, x: Sequence[float], y: Sequence[float]) -> float:
    r = [((q - aj["my"]) / aj["sy"]) - aj["b"] * ((p - aj["mx"]) / aj["sx"]) for p, q in zip(x, y)]
    return statistics.fmean(r) / (aj["sd_res"] / math.sqrt(len(r)))


def incoherente(aj: dict, x: Sequence[float], y: Sequence[float], corte: float = T_CORTE) -> bool:
    return abs(estadistico_t(aj, x, y)) > corte
