"""IN-4 · Banco de Falsaciones materializado (M2.6): fachada única de los escenarios SIMULADOS del proyecto.

Toda corrida imprime el banner `UNIVERSO SIMULADO — DÍA N · semilla S` (CLAUDE.md §3, mandamiento 3). Tres clases de anomalía:
  · deriva_coherente        — cambio lento de un indicador colectivo; lo caza el CUSUM (MO-3) antes que la regla diaria de 2σ.
  · flujo_no_contabilizado  — pérdida que NO está en el manifiesto: el detector contra el manifiesto es ciego, el Contrapeso (ley) alarma
                              (FB-005-D1, el «demo kill»).
  · fuga_fisica             — pérdida real que además deja firma en testigos físicos independientes: los tres testigos de MO-4 se mueven
                              y la triangulación la clasifica como `mundo` (no como fallo de sensor ni de humano).
Más: `replay_real` (series REALES con caída inyectada SIMULADA, vía `evaluacion.evaluar`), `monte_carlo` (n corridas con semillas
consecutivas a partir de una pública) y `modo_adversario` (FB-018). La interpretación de «fuga física» es un supuesto declarado (X-09).
"""
from __future__ import annotations

import math
import random
import statistics

from .adversario import tasas as _tasas_adversario
from .cusum import K_REF, paso
from .fb005_demo import ejecutar as _fb005
from .triangulacion import diagnosticar, mundo

H = 10.011730842174083


def banner(dia: int, semilla: int) -> str:
    return f"UNIVERSO SIMULADO — DÍA {dia} · semilla {semilla}"


def deriva_coherente(semilla: int, tasa_sigma_dia: float = 0.3, dias: int = 60, dia_deriva: int = 15) -> dict:
    rng = random.Random(semilla)
    x = [rng.gauss(0, 1) - tasa_sigma_dia * max(0, t - dia_deriva + 1) for t in range(1, dias + 1)]
    mu, sd = statistics.fmean(x[:14]), statistics.stdev(x[:14]) * math.sqrt(1 + 1 / 14)
    sa = sc = 0.0
    dia_cusum = dia_2s = None
    for t in range(14, dias):
        z = (x[t] - mu) / sd
        sa, sc = paso(sa, sc, z, K_REF)
        if dia_cusum is None and (sa >= H or sc >= H):
            dia_cusum = t + 1
        if dia_2s is None and abs(z) > 2.0 and t + 1 >= dia_deriva:
            dia_2s = t + 1
    return {"escenario": "deriva_coherente", "banner": banner(dia_deriva, semilla), "dia_cusum": dia_cusum, "dia_regla_2sigma": dia_2s,
            "detecta": dia_cusum is not None}


def flujo_no_contabilizado(semilla: int) -> dict:
    r = _fb005(semilla)
    return {"escenario": "flujo_no_contabilizado", "banner": r["banner"] + f" · semilla {semilla}",
            "manifiesto_alarma": r["fuga"]["A_manifiesto"]["alarma"], "ley_veredicto": r["fuga"]["B_ley"]["veredicto"],
            "detecta": r["fuga"]["B_ley"]["veredicto"] == "NO CIERRA" and not r["fuga"]["A_manifiesto"]["alarma"]}


def fuga_fisica(semilla: int) -> dict:
    causa, alarmantes = diagnosticar(mundo(random.Random(semilla), "mundo"))
    return {"escenario": "fuga_fisica", "banner": banner(25, semilla), "testigos_con_alarma": sorted(alarmantes), "diagnostico": causa,
            "detecta": causa == "mundo"}


ESCENARIOS = {"deriva_coherente": deriva_coherente, "flujo_no_contabilizado": flujo_no_contabilizado, "fuga_fisica": fuga_fisica}


def monte_carlo(escenario: str, semilla: int, n: int = 100) -> dict:
    """n corridas con semillas semilla, semilla+1, … Devuelve la tasa de detección y el banner de la primera."""
    f = ESCENARIOS[escenario]
    res = [f(semilla + i) for i in range(n)]
    return {"escenario": escenario, "semilla": semilla, "n": n, "banner": res[0]["banner"], "tasa_deteccion": sum(r["detecta"] for r in res) / n}


def replay_real(series, indicador, sigma_sensor, deltas=(2.0,)) -> dict:
    """Series REALES (p. ej. de LifeSnaps) con caída inyectada SIMULADA de δ·σ: potencia por δ. Banner híbrido."""
    from .evaluacion import evaluar
    r = evaluar(series, indicador, sigma_sensor, deltas=deltas)
    return {"banner": "REAL (series) + SIMULADO (caída inyectada)", "potencia": {d: v["tasa"] for d, v in r["M3"].items()},
            "fpr_natural": r["M1"]["tasa"], "n_unidades": r["M1"]["n"]}


def modo_adversario(perfil: str, dano: float, semilla: int, n: int, hv: float) -> dict:
    return {"banner": banner(14, semilla), **_tasas_adversario(perfil, dano, semilla, n, hv)}
