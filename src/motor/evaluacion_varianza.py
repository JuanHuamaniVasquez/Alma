"""M2.20 · FB-020: evaluación del canal de varianza en series reales. Especificación congelada en docs/actas/FB-020.md."""
from __future__ import annotations

import math
import statistics
from collections.abc import Sequence
from datetime import date

from .adversario import H_MEDIA, detecta_media
import random
from functools import lru_cache

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


def _mad(x: Sequence[float]) -> float:
    m = statistics.median(x)
    return statistics.median(abs(v - m) for v in x)


def razon_mad(base: Sequence[float], vig: Sequence[float]) -> float:
    """FB-020-v2: razón de desviaciones absolutas medianas (vigilancia / línea base): robusta a colas pesadas y a días atípicos."""
    mb = _mad(base)
    return _mad(vig) / mb if mb > 0 else math.inf


@lru_cache(maxsize=4)
def calibrar_critico_mad(semilla: int = 20261113, n: int = 20000, alfa: float = 0.01) -> float:
    rng = random.Random(semilla)
    f = sorted(razon_mad([rng.gauss(0, 1) for _ in range(BASE)], [rng.gauss(0, 1) for _ in range(VIG)]) for _ in range(n))
    return f[math.ceil((1 - alfa) * n) - 1]


def critico_empirico(series_varias: Sequence[dict[str, list[tuple[date, float]]]], estadistico, q: float = 0.98) -> float:
    """Percentil q del estadístico sobre las ventanas SIN inyección de los conjuntos dados (índice ceil(q·n) − 1)."""
    v = sorted(estadistico(b, w) for series in series_varias for s in series.values() for b, w in ventanas(s))
    return v[math.ceil(q * len(v)) - 1]


def evaluar(series: dict[str, list[tuple[date, float]]], hs: Sequence[float] = HS, estadistico=razon_f, critico: float | None = None) -> dict:
    c = calibrar_critico() if critico is None else critico
    todas = [(p, b, v) for p, s in sorted(series.items()) for b, v in ventanas(s)]
    n = len(todas)
    alarmas = [estadistico(b, v) > c for _, b, v in todas]
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
            kf += estadistico(b, vz) > c
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


# --- FB-020-v2: candidatos, selección en entrenamiento (LifeSnaps) y congelado ---------------------------------
CANDIDATOS = ("C2", "C3", "C4")  # C2: MAD + crítico normal · C3: F + crítico empírico · C4: MAD + crítico empírico
PREFERENCIA = ("C2", "C4", "C3")  # desempate (potencia a ≤ 2 pp): el que tiene menos parámetros ajustados a datos


def candidato(nombre: str, entrenamiento: Sequence[dict]) -> tuple:
    if nombre == "C2":
        return razon_mad, calibrar_critico_mad()
    est = razon_f if nombre == "C3" else razon_mad
    return est, critico_empirico(entrenamiento, est)


def seleccionar(ls_sueno: dict, ls_pulso: dict, fpr_max: float = 0.03, potencia_min: float = 0.80, empate: float = 0.02) -> dict:
    """Entrena con LifeSnaps (sueño + pulso para FPR y crítico empírico; sueño para potencia a H=2,0). Devuelve la tabla y el elegido (o None)."""
    tabla = {}
    for nombre in CANDIDATOS:
        est, c = candidato(nombre, (ls_sueno, ls_pulso))
        rs, rp = evaluar(ls_sueno, (2.0,), est, c), evaluar(ls_pulso, (), est, c)
        k = rs["fpr"]["k"] + rp["fpr"]["k"]
        n = rs["fpr"]["n"] + rp["fpr"]["n"]
        tabla[nombre] = {"critico": c, "fpr_entrenamiento": k / n, "k": k, "n": n, "potencia_h2": rs["potencia"]["2.0"]["canal_varianza"]}
    aptos = {k: v for k, v in tabla.items() if v["fpr_entrenamiento"] <= fpr_max and v["potencia_h2"] >= potencia_min}
    elegido = None
    if aptos:
        mejor = max(v["potencia_h2"] for v in aptos.values())
        elegido = next(k for k in PREFERENCIA if k in aptos and aptos[k]["potencia_h2"] >= mejor - empate)
    return {"tabla": tabla, "elegido": elegido}


def veredictos_v2(sueno: dict, pulso: dict, h_primaria: str = "2.5") -> dict:
    f = sueno["fpr"]
    lo, hi = f["wilson95"]
    p = sueno["potencia"]
    h1 = "REFUTADA" if f["tasa"] > 0.03 else ("SOSTENIDA" if hi <= 0.06 else "NO CONCLUYENTE")
    return {"H1_fpr_sueno": h1, "H2_potencia": "SOSTENIDA" if p[h_primaria]["canal_varianza"] >= 0.80 else "REFUTADA",
            "H3_cusum_ciego": "SOSTENIDA" if p[h_primaria]["cusum_media"] <= 0.10 else "REFUTADA",
            "H4_control_valido": bool(p["3.0"]["canal_varianza"] >= 0.95),
            "H5_fpr_pulso": "SOSTENIDA" if pulso["fpr"]["tasa"] <= 0.03 else "REFUTADA"}
