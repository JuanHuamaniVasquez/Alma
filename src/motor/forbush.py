"""FB-029 · ¿el MISMO motor (CUSUM, MO-3) que vigila cuerpos y hábitat ve un decaimiento Forbush en el monitor de neutrones? Puro Python.

Serie horaria de Oulu (NMDB, corregida por presión). Línea base CAUSAL: cada día a las 00:00 UTC se recalcula mediana y MAD (×1,4826 = σ robusta) de los `base_dias`
días completos anteriores; z = (x − mediana)/σ; se acumula la rama de caída S⁻ con `cusum.paso` (k = 0,5); alarma cuando S⁻ ≥ h, con periodo refractario.
Eventos de referencia: tormentas geomagnéticas del índice Kp (GFZ): inicio = primer intervalo de 3 h con Kp ≥ 5 en las 48 h previas al primer intervalo con Kp ≥ umbral.
"""
from __future__ import annotations

import random
import statistics
from bisect import bisect_left, bisect_right
from datetime import UTC, datetime, timedelta
from pathlib import Path

from .cusum import K_REF, paso

HORA = timedelta(hours=1)


def leer_oulu(ruta: Path) -> list[tuple[datetime, float]]:
    out = []
    for l in ruta.read_text(encoding="utf-8").splitlines()[1:]:
        t, v = l.split(",")
        out.append((datetime.strptime(t, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC), float(v)))
    return out


def leer_kp(ruta: Path) -> list[tuple[datetime, float]]:
    out = []
    for l in ruta.read_text(encoding="utf-8").splitlines():
        if l.startswith("#") or not l.strip():
            continue
        p = l.split()
        k = float(p[7])
        if k >= 0:
            out.append((datetime(int(p[0]), int(p[1]), int(p[2]), int(float(p[3])), tzinfo=UTC), k))
    return out


def eventos_kp(kp: list[tuple[datetime, float]], umbral: float, desde: datetime, hasta: datetime, separacion_dias: int = 3) -> list[datetime]:
    """Inicio (primer intervalo con Kp ≥ 5 en las 48 h previas) de cada tormenta cuyo primer intervalo con Kp ≥ `umbral` cae en [desde, hasta); eventos separados ≥ `separacion_dias`."""
    out, ultimo = [], None
    for i, (t, k) in enumerate(kp):
        if not (desde <= t < hasta) or k < umbral:
            continue
        if ultimo is not None and (t - ultimo) < timedelta(days=separacion_dias):
            ultimo = t
            continue
        ultimo = t
        ini = t
        j = i
        while j > 0 and (t - kp[j - 1][0]) <= timedelta(hours=48) and kp[j - 1][1] >= 5:
            j -= 1
        ini = kp[j][0] if kp[j][1] >= 5 else t
        out.append(ini)
    return out


def alarmas(serie: list[tuple[datetime, float]], h: float, k: float = K_REF, base_dias: int = 27, refractario_h: int = 72, min_base: int = 12 * 24) -> list[datetime]:
    """Alarmas de CAÍDA (S⁻ ≥ h). Causal: la línea base de cada día solo usa los `base_dias` días completos anteriores; sin al menos `min_base` horas de base no hay juicio."""
    ts = [t for t, _ in serie]
    vs = [v for _, v in serie]
    out: list[datetime] = []
    s_alza = s_caida = 0.0
    mu = sigma = None
    dia_base = None
    bloqueo_hasta = None
    for i, (t, v) in enumerate(serie):
        d = t.date()
        if d != dia_base:
            dia_base = d
            ini = datetime(d.year, d.month, d.day, tzinfo=UTC)
            a, b = bisect_left(ts, ini - timedelta(days=base_dias)), bisect_left(ts, ini)
            base = vs[a:b]
            if len(base) >= min_base:
                mu = statistics.median(base)
                mad = statistics.median(abs(x - mu) for x in base)
                sigma = 1.4826 * mad or None
            else:
                mu = sigma = None
        if mu is None or sigma is None:
            s_alza = s_caida = 0.0
            continue
        s_alza, s_caida = paso(s_alza, s_caida, (v - mu) / sigma, k)
        if s_caida >= h and (bloqueo_hasta is None or t >= bloqueo_hasta):
            out.append(t)
            s_caida = s_alza = 0.0
            bloqueo_hasta = t + timedelta(hours=refractario_h)
        elif bloqueo_hasta is not None and t < bloqueo_hasta:
            s_caida = 0.0
    return out


def alarmas_falsas(al: list[datetime], kp: list[tuple[datetime, float]], desde: datetime, hasta: datetime, margen_dias: int = 3, kp_min: float = 5.0) -> list[datetime]:
    """Alarmas en [desde, hasta) que no caen a ±`margen_dias` de ningún intervalo con Kp ≥ `kp_min` (no hay tormenta que las explique)."""
    tormenta = [t for t, k in kp if k >= kp_min]
    m = timedelta(days=margen_dias)
    out = []
    for a in al:
        if not (desde <= a < hasta):
            continue
        i = bisect_left(tormenta, a - m)
        if not (i < len(tormenta) and tormenta[i] <= a + m):
            out.append(a)
    return out


def evaluar(al: list[datetime], eventos: list[datetime], antes_h: int = 24, despues_h: int = 24) -> dict:
    """Un evento está detectado si hay alguna alarma en [inicio − antes_h, inicio + despues_h]; adelanto = inicio − primera alarma de esa ventana (horas; negativo = tarde)."""
    ts = sorted(al)
    adelantos, hits = [], 0
    for e in eventos:
        a = bisect_left(ts, e - timedelta(hours=antes_h))
        if a < len(ts) and ts[a] <= e + timedelta(hours=despues_h):
            hits += 1
            adelantos.append((e - ts[a]).total_seconds() / 3600)
    return {"n_eventos": len(eventos), "detectados": hits, "sensibilidad": hits / len(eventos) if eventos else None, "adelantos_h": adelantos,
            "adelanto_mediano_h": statistics.median(adelantos) if adelantos else None}


def placebo(al: list[datetime], eventos: list[datetime], desde: datetime, hasta: datetime, semilla: int, n: int = 1000, min_desp_dias: int = 15) -> dict:
    """Desplaza TODOS los inicios de evento una misma cantidad aleatoria (circular dentro del periodo, ≥ `min_desp_dias`): ¿cuántos «detecta» el motor por azar? p = (1 + #{tasa ≥ observada})/(n + 1)."""
    rng = random.Random(semilla)
    span = (hasta - desde).total_seconds()
    obs = evaluar(al, eventos)["sensibilidad"]
    tasas = []
    for _ in range(n):
        d = rng.uniform(min_desp_dias * 86400, span - min_desp_dias * 86400)
        sh = [desde + timedelta(seconds=((e - desde).total_seconds() + d) % span) for e in eventos]
        tasas.append(evaluar(al, sh)["sensibilidad"])
    return {"observada": obs, "media_placebo": statistics.fmean(tasas), "p_unilateral": (1 + sum(t >= obs for t in tasas)) / (n + 1), "n": n}
