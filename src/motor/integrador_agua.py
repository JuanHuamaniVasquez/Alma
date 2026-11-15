"""MO-5 · Integrador lento del agua (TOC como censo colectivo) con normalización por caudal (MP-3). SIMULADO salvo el caudal (REAL, Utah).
Especificación congelada en docs/actas/FB-004R.md. X-10."""
from __future__ import annotations

import csv
import random
import statistics
from pathlib import Path

from .triangulacion import H_CALIBRADO, K

M, DIAS, VENTANA, DIA_CAMBIO, SIGMA_MED = 10.0, 100, 28, 40, 0.03
FIXTURE = Path(__file__).resolve().parents[2] / "data" / "fixtures" / "utah_volumen_diario_normalizado.csv"


def pool_volumenes(ruta: Path = FIXTURE) -> list[float]:
    with ruta.open(encoding="utf-8", newline="") as f:
        return [float(r["volumen_interior_relativo"]) for r in csv.DictReader(f)]


def corrida(rng: random.Random, pool: list[float], delta: float) -> tuple[list[float], list[float]]:
    """(observado o_t, esperado Ĉ_t con la carga base y el caudal conocido) de DIAS días."""
    V = [rng.choice(pool) for _ in range(DIAS)]
    c = chat = 1.0
    o, esperado = [], []
    for t in range(1, DIAS + 1):
        carga = 1.0 + (delta if t >= DIA_CAMBIO else 0.0)
        c = (1 - V[t - 1] / M) * c + carga / M
        chat = (1 - V[t - 1] / M) * chat + 1.0 / M
        o.append(c * (1 + rng.gauss(0.0, SIGMA_MED)))
        esperado.append(chat)
    return o, esperado


def alarma(serie: list[float], h: float = H_CALIBRADO, k: float = K) -> int | None:
    mu, sd = statistics.fmean(serie[:VENTANA]), statistics.stdev(serie[:VENTANA])
    sp = sm = 0.0
    for t in range(VENTANA, len(serie)):
        z = (serie[t] - mu) / sd
        sp, sm = max(0.0, sp + z - k), max(0.0, sm - z - k)
        if sp > h or sm > h:
            return t + 1
    return None


def residuo(o: list[float], esperado: list[float]) -> list[float]:
    return [a - b for a, b in zip(o, esperado)]
