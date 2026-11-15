"""MO-3b · Alarma anytime-valid: e-proceso de mezcla gaussiana (Robbins) sobre residuos estandarizados. M6.1 / FB-021 (MP-16).

Idea (no es nuestra; ver docs/revision-literatura.md §M6.0): un e-proceso es una secuencia no negativa M_t con E[M_τ] ≤ 1 bajo la nula para
CUALQUIER tiempo de parada τ. Por la desigualdad de Ville, P(∃t: M_t ≥ 1/α) ≤ α: la tasa de falsas alarmas queda acotada por α aunque se
mire todos los días (el «problema de mirar varias veces» que rompe el p-valor clásico). Lo nuestro es la aplicación: línea base personal de
28 días, MDE declarado y recibo por alarma.

Estadístico (mezcla sobre λ ~ N(0, τ²); simétrica → bilateral sin partir α):
    S_t = Σ y_i,   y_i = clip(z_i, −c·s, +c·s),   z_i = (x_i − μ_base)/sd_base
    M_t = (1 + τ² s² t)^(−1/2) · exp( τ² S_t² / (2 (1 + τ² s² t)) ),     τ² = 1/(s²·T)
    ALARMA en el primer t con M_t ≥ 1/α.
Supuesto de la garantía: los incrementos y_i son, condicionalmente, s-subgaussianos de media 0 bajo «sin cambio». `s` es el factor de inflación
(s = 1 ⇒ varianza unitaria exacta). La autocorrelación y la estimación de μ, sd con 28 días lo violan: por eso FB-021 mide el FPR REAL y calibra
`s` en un conjunto y valida en otro, en vez de fiarse de la teoría.
"""
from __future__ import annotations

import math
from collections.abc import Sequence

T_HORIZONTE = 14        # días de vigilancia para los que se afina τ (fijado en el acta)
CLIP_C = 4.0            # recorte de los incrementos en ±c·s (fijado en el acta)
ALFA = 0.01             # falsa alarma máxima garantizada (misma que el CUSUM de 14 d del sistema)


def mezcla(z: Sequence[float], s: float = 1.0, *, t_horizonte: int = T_HORIZONTE, clip: float = CLIP_C) -> list[float]:
    """Trayectoria del e-proceso M_1..M_n (una por día de vigilancia)."""
    tau2 = 1.0 / (s * s * t_horizonte)
    suma, out = 0.0, []
    for t, x in enumerate(z, start=1):
        suma += max(-clip * s, min(clip * s, x))
        den = 1.0 + tau2 * s * s * t
        out.append(math.exp(tau2 * suma * suma / (2.0 * den) - 0.5 * math.log(den)))
    return out


def detecta(z: Sequence[float], s: float = 1.0, alfa: float = ALFA) -> int | None:
    """Día (1-based) de la primera alarma, o None."""
    for t, m in enumerate(mezcla(z, s), start=1):
        if m >= 1.0 / alfa:
            return t
    return None


def regla_exacta(mu: float, sd: float, s: float, alfa: float = ALFA) -> str:
    """Texto ejecutable e imprimible (recibo): reproduce el estadístico con repr de los floats."""
    return (f"E_PROCESO_MEZCLA mu={mu!r} sd={sd!r} s={s!r} alfa={alfa!r} T={T_HORIZONTE} clip={CLIP_C!r} :: z=(x-mu)/sd; y=clip(z,-clip*s,clip*s); "
            f"S=sum(y); M=(1+tau2*s^2*t)^(-1/2)*exp(tau2*S^2/(2*(1+tau2*s^2*t))), tau2=1/(s^2*T); ALARMA si M>=1/alfa (garantía: P(falsa alarma)<=alfa si y es s-subgaussiana de media 0)")
