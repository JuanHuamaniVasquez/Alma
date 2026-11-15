"""Exposición diaria a Kp y contraste por desplazamiento circular (FB-014). Puro Python."""
from __future__ import annotations

import random
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path
from statistics import fmean, pstdev


def kp_max_por_dia(ruta: Path) -> dict[date, float]:
    """Máximo diario de Kp (8 intervalos de 3 h) del archivo de GFZ; ignora Kp = −1 (ausente)."""
    por: dict[date, list[float]] = defaultdict(list)
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.startswith("#") or not linea.strip():
            continue
        p = linea.split()
        kp = float(p[7])
        if kp >= 0:
            por[date(int(p[0]), int(p[1]), int(p[2]))].append(kp)
    return {d: max(v) for d, v in por.items()}


def exposicion(kpmax: list[float]) -> list[float]:
    """exposición[i] = max(Kp_max[i−1], Kp_max[i]); el primer día usa solo el suyo."""
    return [kpmax[0]] + [max(kpmax[i - 1], kpmax[i]) for i in range(1, len(kpmax))]


def _rangos(x: list[float]) -> list[float]:
    orden = sorted(range(len(x)), key=lambda i: x[i])
    r = [0.0] * len(x)
    i = 0
    while i < len(orden):
        j = i
        while j + 1 < len(orden) and x[orden[j + 1]] == x[orden[i]]:
            j += 1
        for k in range(i, j + 1):
            r[orden[k]] = (i + j) / 2 + 1
        i = j + 1
    return r


def spearman(x: list[float], y: list[float]) -> float | None:
    if len(x) < 3:
        return None
    a, b = _rangos(x), _rangos(y)
    ma, mb = fmean(a), fmean(b)
    sa = sum((u - ma) ** 2 for u in a)
    sb = sum((v - mb) ** 2 for v in b)
    return None if sa == 0 or sb == 0 else sum((u - ma) * (v - mb) for u, v in zip(a, b)) / (sa * sb) ** 0.5


def estadisticos(personas: dict[str, list[tuple[int, float]]], expo: list[float], desfase: int = 0) -> tuple[float, float] | None:
    """(S1 = media, S2 = desviación típica) de los ρ de Spearman por persona; `personas[p]` = (índice de día, valor).
    `desfase` desplaza circularmente la exposición."""
    n = len(expo)
    rhos = []
    for pares in personas.values():
        r = spearman([expo[(i - desfase) % n] for i, _ in pares], [v for _, v in pares])
        if r is not None:
            rhos.append(r)
    return (fmean(rhos), pstdev(rhos)) if len(rhos) >= 2 else None


def contraste(personas: dict[str, list[tuple[int, float]]], expo: list[float], semilla: int, n: int = 10_000,
              minimo: int = 14) -> dict:
    obs = estadisticos(personas, expo)
    assert obs is not None
    rng = random.Random(semilla)
    maximo = len(expo) - minimo
    nulos = [estadisticos(personas, expo, rng.randint(minimo, maximo)) for _ in range(n)]
    s1 = [a for a, _ in nulos]
    s2 = [b for _, b in nulos]
    p1 = (1 + sum(1 for v in s1 if abs(v) >= abs(obs[0]))) / (n + 1)
    p2 = (1 + sum(1 for v in s2 if v >= obs[1])) / (n + 1)
    return {"S1_obs": obs[0], "S2_obs": obs[1], "p_S1_bilateral": p1, "p_S2_unilateral": p2,
            "S1_nulo_q025_q975": [sorted(s1)[int(0.025 * n)], sorted(s1)[int(0.975 * n) - 1]],
            "S2_nulo_media": fmean(s2), "n_personas": len(personas)}
