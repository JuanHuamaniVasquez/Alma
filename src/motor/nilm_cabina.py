"""MO-6b · NILM metabólico de cabina: ¿a QUIÉN pertenece un exceso de CO₂ en el libro de aire? M6.2 / FB-023 (MP-17). SIMULADO (X-17).

Idea: la cabina mide la SUMA de lo que emiten 5 cuerpos; si un tripulante emite un d % más (fiebre, hipermetabolismo) que su manifiesto, el residuo del libro lo
dice, pero no QUIÉN. Con los horarios de vigilia de cada persona (que SÍ conocemos: ritmo, turnos) la columna de cada uno es distinta, y una regresión
sobre el residuo reparte el exceso. Si todos duermen y despiertan a la vez, las columnas son idénticas y el problema es NO identificable (azar = 1/n).
Producción de referencia: 1,01 kg CO₂/persona/día (Ewert & Stromgren, ICES 2021, protocolo corto; docs/parametros-publicos.md P-03).
Supuestos declarados: p_i(t) = c·(0,8 + 0,6·despierto_i(t)), c tal que 24 h suman 1,01 kg; el exceso es multiplicativo sobre p_i(t); ruido del libro = σ_rel × total horario.
"""
from __future__ import annotations

import random
from collections.abc import Sequence

N_TRIP = 5
HORAS = 24 * 14
CO2_DIA = 1.01                                   # kg/persona/día, P-03 (protocolo corto)
C = CO2_DIA / (24 * 0.8 + 0.6 * 16)              # kg/h para que un día de 16 h despierto sume CO2_DIA
VIGILIA = 16


def despierto(i: int, t: int, paso: int) -> int:
    """1 si la persona i está despierta en la hora t; la vigilia de cada una se corre `paso` horas respecto de la anterior."""
    h = (t - i * paso) % 24
    return 1 if h < VIGILIA else 0


def esperado(i: int, t: int, paso: int) -> float:
    return C * (0.8 + 0.6 * despierto(i, t, paso))


def simular(paso: int, delta: float, sigma_rel: float, k: int, inicio_dia: int, rng: random.Random) -> tuple[list[float], list[list[float]]]:
    """Libro de aire observado menos el esperado (residuo r_t) y las columnas esperadas X[t][i]. El tripulante k emite `delta` más desde `inicio_dia`."""
    X = [[esperado(i, t, paso) for i in range(N_TRIP)] for t in range(HORAS)]
    r = []
    for t in range(HORAS):
        total = sum(X[t])
        extra = delta * X[t][k] if t >= inicio_dia * 24 else 0.0
        r.append(extra + rng.gauss(0.0, sigma_rel * total))
    return r, X


def resolver(r: Sequence[float], X: Sequence[Sequence[float]], ridge: float = 1e-9) -> list[float]:
    """Mínimos cuadrados (ecuaciones normales con ridge mínimo; eliminación gaussiana). Columnas idénticas → reparto igual (no identificable)."""
    n = len(X[0])
    A = [[sum(X[t][a] * X[t][b] for t in range(len(r))) + (ridge if a == b else 0.0) for b in range(n)] for a in range(n)]
    y = [sum(X[t][a] * r[t] for t in range(len(r))) for a in range(n)]
    for c in range(n):
        p = max(range(c, n), key=lambda i: abs(A[i][c]))
        A[c], A[p], y[c], y[p] = A[p], A[c], y[p], y[c]
        for i in range(c + 1, n):
            f = A[i][c] / A[c][c]
            for j in range(c, n):
                A[i][j] -= f * A[c][j]
            y[i] -= f * y[c]
    d = [0.0] * n
    for i in range(n - 1, -1, -1):
        d[i] = (y[i] - sum(A[i][j] * d[j] for j in range(i + 1, n))) / A[i][i]
    return d


def atribuir(d: Sequence[float], rng: random.Random) -> int:
    """Persona con mayor exceso estimado; los empates (≤ 1e-9 de diferencia) se resuelven al azar, como haría un lector honesto."""
    m = max(d)
    return rng.choice([i for i, v in enumerate(d) if m - v <= 1e-9])


def exactitud(paso: int, delta: float, sigma_rel: float, n: int, semilla: int, inicio_dia: int = 4) -> dict:
    rng = random.Random(semilla * 1000 + paso * 100 + int(delta * 1000))
    ok = 0
    for _ in range(n):
        k = rng.randrange(N_TRIP)
        r, X = simular(paso, delta, sigma_rel, k, inicio_dia, rng)
        ok += atribuir(resolver(r, X), rng) == k
    return {"paso_h": paso, "delta": delta, "n": n, "aciertos": ok, "exactitud": ok / n}
