"""M2.8 · Evaluación del motor sobre series reales (FB-009). Implementa EXACTAMENTE docs/actas/FB-009.md.

No cambiar ningún parámetro aquí sin un acta nueva (FB-009-v2): sería HARKing.
Unidad = bloque de 28 días válidos de una persona: 14 de línea base + 14 de monitoreo, con un ModeloNulo nuevo.
"""
from __future__ import annotations

import math
import random
import statistics
from collections import defaultdict
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import date

from src.contratos.comunes import Indicador

from .linea_base import DIAS_BASE, estimar_linea_base
from .modelo_nulo import ModeloNulo

BLOQUE = 2 * DIAS_BASE
H_FB009 = 10.011730842174083  # h fijado en el acta FB-009 (calibrar_h con semilla pública 20261113)
DELTAS = (1.0, 1.5, 2.0, 3.0)
SEMILLA_REMUESTREO = 20261114
UMBRAL_H1_ALFA = 0.05
UMBRAL_H2 = 0.80


def unidades(serie: Sequence[tuple[date, float]], bloque: int = BLOQUE) -> list[tuple[list[tuple[date, float]], list[tuple[date, float]]]]:
    """Bloques consecutivos de `bloque` días válidos ordenados por fecha → (base de 14, monitoreo de 14)."""
    ordenada = sorted(serie, key=lambda x: x[0])
    mitad = bloque // 2
    return [(ordenada[i:i + mitad], ordenada[i + mitad:i + bloque]) for i in range(0, len(ordenada) - bloque + 1, bloque)]


@dataclass(frozen=True)
class ResultadoUnidad:
    alarma: bool
    sentido: str | None
    dia_de_alarma: int | None  # 1…14 dentro de la ventana de monitoreo
    sigma_efectiva: float
    manda_el_sensor: bool


def ejecutar_unidad(persona: str, indicador: Indicador, sigma_sensor: float, base: list[tuple[date, float]],
                    monitoreo: list[tuple[date, float]], h: float = H_FB009, delta: float = 0.0, phi: float = 0.0) -> ResultadoUnidad:
    """Corre una unidad. `delta` > 0 RESTA delta·σ_efectiva (la de esta unidad) a todo el monitoreo (inyección SIMULADA, determinista)."""
    lb = estimar_linea_base(persona, indicador.value, base, sigma_sensor)
    assert lb is not None, "una unidad siempre tiene 14 datos de base"
    modelo = ModeloNulo(persona, indicador, sigma_sensor, h=h, phi=phi)
    for d, v in base:
        modelo.observar(d, v)
    for i, (d, v) in enumerate(monitoreo, start=1):
        o = modelo.observar(d, v - delta * lb.sigma_efectiva)
        if o.alarma:
            return ResultadoUnidad(True, o.alarma.sentido.value, i, lb.sigma_efectiva, lb.manda_el_sensor)
    return ResultadoUnidad(False, None, None, lb.sigma_efectiva, lb.manda_el_sensor)


# --- estadísticos (todos exactos o estándar; sin dependencias externas) ------------------------------
def wilson(x: int, n: int, z: float = 1.959964) -> tuple[float, float]:
    if n == 0:
        return (0.0, 1.0)
    p = x / n
    den = 1 + z * z / n
    centro = (p + z * z / (2 * n)) / den
    margen = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return (max(0.0, centro - margen), min(1.0, centro + margen))


def cola_binomial(x: int, n: int, p: float) -> float:
    """P(X ≥ x) para X ~ Binomial(n, p), exacta."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(x, n + 1))


def x_critico(n: int, p0: float = 0.01, alfa: float = UMBRAL_H1_ALFA) -> int:
    """Menor x tal que P(X ≥ x | n, p0) ≤ alfa (regla de refutación de H1 en FB-009)."""
    return next(x for x in range(n + 2) if cola_binomial(x, n, p0) <= alfa)


def remuestreo_por_persona(por_persona: dict[str, tuple[int, int]], semilla: int = SEMILLA_REMUESTREO,
                           n_rep: int = 5000) -> tuple[float, float]:
    """IC 95 % percentil de la tasa agrupada, remuestreando PERSONAS (cada una con sus (alarmas, unidades))."""
    personas = list(por_persona.values())
    if not personas:
        return (0.0, 0.0)
    rng = random.Random(semilla)
    tasas = []
    for _ in range(n_rep):
        muestra = [personas[rng.randrange(len(personas))] for _ in personas]
        n = sum(u for _, u in muestra)
        tasas.append(sum(a for a, _ in muestra) / n if n else 0.0)
    tasas.sort()
    return (tasas[int(0.025 * (n_rep - 1))], tasas[int(0.975 * (n_rep - 1))])


# --- la evaluación completa -----------------------------------------------------------------------------
def evaluar(series: dict[str, list[tuple[date, float]]], indicador: Indicador, sigma_sensor: float, *,
            filtro: Callable[[float], bool] | None = None, h: float = H_FB009, deltas: Sequence[float] = DELTAS,
            phi: float = 0.0, personas: set[str] | None = None) -> dict:
    por_persona_unidades: dict[str, list] = defaultdict(list)
    for persona, serie in series.items():
        if personas is not None and persona not in personas:
            continue
        valida = [(d, v) for d, v in serie if filtro is None or filtro(v)]
        us = unidades(valida)
        if us:
            por_persona_unidades[persona] = us
    todas = [(p, u) for p, us in por_persona_unidades.items() for u in us]
    n = len(todas)
    naturales = [ejecutar_unidad(p, indicador, sigma_sensor, b, m, h, phi=phi) for p, (b, m) in todas]
    x = sum(r.alarma for r in naturales)
    por_persona = {}
    for (p, _), r in zip(todas, naturales):
        a, u = por_persona.get(p, (0, 0))
        por_persona[p] = (a + r.alarma, u + 1)
    primeras = [ejecutar_unidad(p, indicador, sigma_sensor, *us[0], h, phi=phi) for p, us in por_persona_unidades.items()]
    potencia = {}
    for d in deltas:
        rs = [ejecutar_unidad(p, indicador, sigma_sensor, b, m, h, delta=d, phi=phi) for p, (b, m) in todas]
        dias = [r.dia_de_alarma for r in rs if r.alarma and r.sentido == "caída"]
        det = len(dias)
        potencia[str(d)] = {"detectadas": det, "de": n, "tasa": det / n if n else 0.0, "wilson95": wilson(det, n),
                            "mediana_dias": statistics.median(dias) if dias else None}
    return {
        "indicador": indicador.value, "n_personas": len(por_persona_unidades), "n_unidades": n,
        "M1": {"alarmas": x, "n": n, "tasa": x / n if n else 0.0, "wilson95": wilson(x, n),
               "remuestreo95": remuestreo_por_persona(por_persona), "x_critico": x_critico(n) if n else None,
               "p_valor_cola": cola_binomial(x, n, 0.01) if n else None},
        "M2": {"alarmas": sum(r.alarma for r in primeras), "n": len(primeras)},
        "M3": potencia,
        "M4": {"fraccion_manda_el_sensor": sum(r.manda_el_sensor for r in naturales) / n if n else 0.0,
               "alarmas_naturales_por_sentido": {s: sum(1 for r in naturales if r.alarma and r.sentido == s) for s in ("alza", "caída")}},
    }


def veredictos(resultado: dict) -> dict:
    """Aplica las reglas de FB-009 al resultado PRIMARIO (sueño, sin limpieza)."""
    m1, m3 = resultado["M1"], resultado["M3"]["2.0"]
    h1_refutada = m1["n"] > 0 and m1["alarmas"] >= m1["x_critico"]
    h2_sostenida = m3["de"] > 0 and m3["tasa"] >= UMBRAL_H2
    return {"H1": "REFUTADA" if h1_refutada else "NO REFUTADA", "H2": "SOSTENIDA" if h2_sostenida else "REFUTADA"}


# --- MP-11 / FB-010: partición por personas y φ poblacional -----------------------------------------------
PHI_MAX = 0.5


def particion(persona_id: str) -> str:
    """Partición determinista y fijada en FB-010: paridad de los primeros 8 hex de sha256(persona_id)."""
    import hashlib
    return "entrenamiento" if int(hashlib.sha256(persona_id.encode()).hexdigest()[:8], 16) % 2 == 0 else "prueba"


def lag1(valores: Sequence[float]) -> float:
    m = statistics.fmean(valores)
    den = sum((v - m) ** 2 for v in valores)
    return sum((valores[i] - m) * (valores[i + 1] - m) for i in range(len(valores) - 1)) / den if den else 0.0


def estimar_phi(series: dict[str, list[tuple[date, float]]], *, filtro_personas: Callable[[str], bool]) -> float:
    """φ poblacional: media de la autocorrelación lag-1 de las unidades de 28 días de las personas elegidas, acotada a ±PHI_MAX."""
    ac = [lag1([v for _, v in b + m]) for p, serie in series.items() if filtro_personas(p) for b, m in unidades(serie)]
    return max(-PHI_MAX, min(PHI_MAX, statistics.fmean(ac))) if ac else 0.0


# --- M2.10 / FB-011: contraste del recibo de verde en datos reales --------------------------------------
MS_FB011 = (14, 10, 7)
ALFA_H1 = 0.05 / 3  # Bonferroni sobre los tres m


def cola_baja(k: int, n: int, p: float) -> float:
    """P(X ≤ k) para X ~ Binomial(n, p), exacta."""
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def k_critico_potencia(n: int, p: float = 0.90, alfa: float = ALFA_H1) -> int:
    """Mayor k con P(X ≤ k | n, p) ≤ alfa: con ≤ k detecciones se REFUTA «potencia ≥ p» (regla de H1 de FB-011)."""
    return max((k for k in range(n + 1) if cola_baja(k, n, p) <= alfa), default=-1)


def submuestras(n_unidades: int, semilla: int = 20261113) -> list[dict[int, list[int]]]:
    """Índices de los días de monitoreo que se conservan, EN EL ORDEN fijado por el acta FB-011:
    un único generador; por unidad, primero m=10 y luego m=7; m=14 usa todos."""
    rng = random.Random(semilla)
    out = []
    for _ in range(n_unidades):
        i10 = sorted(rng.sample(range(14), 10))
        i7 = sorted(rng.sample(range(14), 7))
        out.append({14: list(range(14)), 10: i10, 7: i7})
    return out


def evaluar_verde(series: dict[str, list[tuple[date, float]]], indicador: Indicador, sigma_sensor: float, *,
                  h: float = H_FB009, ms: Sequence[int] = MS_FB011) -> dict:
    from .potencia import mde_sigma  # evita ciclo de importación al cargar el paquete
    ordenadas = [(p, u) for p in sorted(series) for u in unidades(series[p])]
    cortes = submuestras(len(ordenadas))
    por_m = {}
    for m in ms:
        mde = mde_sigma(m)
        det = ctrl = 0
        fisicos = []
        for (p, (base, mon)), idx in zip(ordenadas, cortes):
            sub = [mon[i] for i in idx[m]]
            r = ejecutar_unidad(p, indicador, sigma_sensor, base, sub, h, delta=mde)
            rc = ejecutar_unidad(p, indicador, sigma_sensor, base, sub, h, delta=mde / 2)
            det += bool(r.alarma and r.sentido == "caída")
            ctrl += bool(rc.alarma and rc.sentido == "caída")
            fisicos.append(mde * r.sigma_efectiva)
        n = len(ordenadas)
        por_m[str(m)] = {"mde_sigma": mde, "n": n, "detecciones": det, "tasa": det / n if n else 0.0, "wilson95": wilson(det, n),
                         "control_detecciones": ctrl, "control_tasa": ctrl / n if n else 0.0,
                         "mediana_mde_fisico": statistics.median(fisicos) if fisicos else None,
                         "k_critico_H1": k_critico_potencia(n) if n else None}
    return {"indicador": indicador.value, "n_unidades": len(ordenadas), "por_m": por_m}


def veredictos_verde(sueno: dict, pulso: dict) -> dict:
    """Aplica las reglas de FB-011: H1 (sueño), H2 (control), H3 (predicción de fallo en pulso, m = 14)."""
    ms = sueno["por_m"]
    h1 = all(v["detecciones"] > v["k_critico_H1"] for v in ms.values())
    h2 = all(v["control_tasa"] < 0.90 for v in ms.values())
    p14 = pulso["por_m"]["14"]
    return {"H1": "SOSTENIDA" if h1 else "REFUTADA", "H2": "CONTROL VÁLIDO" if h2 else "CONTROL INVÁLIDO",
            "H3": "SOSTENIDA" if p14["tasa"] < 0.90 else "REFUTADA",
            "H3_significativamente_menor": p14["detecciones"] <= k_critico_potencia(p14["n"], alfa=0.05)}
