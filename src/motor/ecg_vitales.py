"""MO-9 · Constantes desde un ECG REAL: detección de onda R (tipo Pan–Tompkins simplificado), pulso instantáneo y RMSSD. M6.9.

Detector: derivada → cuadrado → integración móvil (150 ms) → umbral adaptativo (media de los máximos recientes × 0,5) con período refractario de 200 ms; cada pico se
reubica en el máximo de |señal| en ±60 ms. Sin dependencias (Python puro). La calidad se MIDE contra las anotaciones humanas (tests/test_ecg_vitales.py), no se asume.
"""
from __future__ import annotations

import math
import statistics
from collections.abc import Sequence

FS = 360


def detectar_r(x: Sequence[float], fs: int = FS) -> list[int]:
    n = len(x)
    d = [0.0] + [x[i] - x[i - 1] for i in range(1, n)]
    e = [v * v for v in d]
    w = int(0.15 * fs)
    acc, integ = 0.0, [0.0] * n
    for i in range(n):
        acc += e[i] - (e[i - w] if i >= w else 0.0)
        integ[i] = acc / w
    umbral_pico = max(integ[: 5 * fs]) * 0.5                         # arranque: 5 s iniciales
    picos, ult, medias = [], -10 * fs, [max(integ[: 5 * fs])]
    refrac, ventana = int(0.2 * fs), int(0.06 * fs)
    i = 1
    while i < n - 1:
        if integ[i] > umbral_pico and integ[i] >= integ[i - 1] and integ[i] >= integ[i + 1] and i - ult > refrac:
            lo, hi = max(0, i - 2 * ventana - w // 2), min(n, i + ventana)
            r = max(range(lo, hi), key=lambda j: abs(x[j]))            # reubica en el pico real de la onda R
            picos.append(r); ult = i
            medias.append(integ[i]); umbral_pico = 0.5 * statistics.fmean(medias[-8:])
            i += refrac
        else:
            i += 1
    return picos


def comparar(picos: Sequence[int], ref: Sequence[int], tol: int = int(0.15 * FS)) -> dict:
    """Sensibilidad y valor predictivo positivo frente a la referencia humana (tolerancia ±150 ms, emparejamiento 1:1 voraz)."""
    usado, tp = set(), 0
    j = 0
    pk = sorted(picos)
    for r in ref:
        cand = [k for k in range(len(pk)) if k not in usado and abs(pk[k] - r) <= tol]
        if cand:
            k = min(cand, key=lambda q: abs(pk[q] - r)); usado.add(k); tp += 1
    fn, fp = len(ref) - tp, len(pk) - tp
    return {"referencia": len(ref), "detectados": len(pk), "tp": tp, "fn": fn, "fp": fp, "sensibilidad": tp / len(ref) if ref else None, "ppv": tp / len(pk) if pk else None}


def pulso_lpm(picos: Sequence[int], fs: int = FS) -> list[tuple[float, float]]:
    """(segundo del latido, lpm instantáneo) para cada intervalo RR fisiológico (0,3–2,0 s)."""
    out = []
    for a, b in zip(picos, picos[1:]):
        rr = (b - a) / fs
        if 0.3 <= rr <= 2.0:
            out.append((b / fs, 60.0 / rr))
    return out


def rmssd_ms(picos: Sequence[int], fs: int = FS) -> float | None:
    rr = [(b - a) * 1000.0 / fs for a, b in zip(picos, picos[1:]) if 300 <= (b - a) * 1000.0 / fs <= 2000]
    dif = [(y - x) ** 2 for x, y in zip(rr, rr[1:])]
    return math.sqrt(sum(dif) / len(dif)) if dif else None
