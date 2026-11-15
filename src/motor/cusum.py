"""MO-3 · CUSUM bilateral y su regla exacta ejecutable (recibo de DC-05).

Estadístico (z = residuo / σ_efectiva):   S⁺ₜ = máx(0, S⁺ₜ₋₁ + zₜ − k)    S⁻ₜ = máx(0, S⁻ₜ₋₁ − zₜ − k)
Alarma cuando S⁺ ≥ h (alza) o S⁻ ≥ h (caída). Bilateral obligatorio: el CUSUM unilateral era ciego a las caídas
(falsación v4, DOC-01).

El umbral h NO es artesanal: se **calibra** por Monte Carlo con semilla pública para que la probabilidad de
alarmar en `dias_ventana` días sin cambio real sea `fpr` (1 % en 14 d, DOC-01), simulando el procedimiento
COMPLETO — incluida la incertidumbre de estimar la línea base con solo 14 días. Esa simulación es un utensilio
estadístico (registro X-06), no un dato.
"""
from __future__ import annotations

import math
import random
import re
import statistics
from dataclasses import dataclass
from functools import lru_cache

K_REF = 0.5
SEMILLA_CALIBRACION = 20261113  # semilla pública (CLAUDE.md §2)


def paso(s_alza: float, s_caida: float, z: float, k: float = K_REF) -> tuple[float, float]:
    return max(0.0, s_alza + z - k), max(0.0, s_caida - z - k)


@lru_cache(maxsize=16)
def calibrar_h(k: float = K_REF, dias_base: int = 14, dias_ventana: int = 14, fpr: float = 0.01,
               semilla: int = SEMILLA_CALIBRACION, n_sim: int = 20000) -> float:
    rng = random.Random(semilla)
    maximos = []
    for _ in range(n_sim):
        base = [rng.gauss(0.0, 1.0) for _ in range(dias_base)]
        mu, sigma = statistics.fmean(base), statistics.stdev(base) * math.sqrt(1 + 1 / dias_base)
        s_alza = s_caida = mejor = 0.0
        for _ in range(dias_ventana):
            s_alza, s_caida = paso(s_alza, s_caida, (rng.gauss(0.0, 1.0) - mu) / sigma, k)
            mejor = max(mejor, s_alza, s_caida)
        maximos.append(mejor)
    maximos.sort()
    return maximos[min(n_sim - 1, math.ceil((1 - fpr) * n_sim) - 1)] + 1e-9


def regla_exacta(k: float, h: float, mu: float, sigma: float) -> str:
    """Texto ejecutable e imprimible; usa repr de los floats para que el recibo reproduzca exactamente."""
    return (f"CUSUM_BILATERAL k={k!r} h={h!r} mu={mu!r} sigma={sigma!r} :: z=(x-mu)/sigma; "
            "S+=max(0,S+ + z-k); S-=max(0,S- - z-k); ALARMA si S+>=h (alza) o S->=h (caída)")


_PATRON = re.compile(r"^CUSUM_BILATERAL k=(\S+) h=(\S+) mu=(\S+) sigma=(\S+) ::")


@dataclass(frozen=True)
class ResultadoRegla:
    alarma: bool
    indice: int | None
    sentido: str | None
    s_cruzado: float | None


def ejecutar_regla(texto: str, valores: list[float]) -> ResultadoRegla:
    """Re-ejecuta la regla sobre los valores observados desde el último reinicio. Si ya no se cumple, la
    alarma se retira sola (mandamiento 3)."""
    m = _PATRON.match(texto)
    if not m:
        raise ValueError("regla_exacta no interpretable")
    k, h, mu, sigma = (float(x) for x in m.groups())
    s_alza = s_caida = 0.0
    for i, x in enumerate(valores):
        s_alza, s_caida = paso(s_alza, s_caida, (x - mu) / sigma, k)
        if s_alza >= h or s_caida >= h:
            alza = s_alza >= s_caida
            return ResultadoRegla(True, i, "alza" if alza else "caída", s_alza if alza else s_caida)
    return ResultadoRegla(False, None, None, None)
