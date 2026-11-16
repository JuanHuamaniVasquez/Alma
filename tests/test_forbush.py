"""FB-029 · el detector de caída (CUSUM de MO-3) sobre una serie horaria: ve un decaimiento Forbush inyectado, no inventa alarmas en ruido, es causal y evalúa/pone placebo con reglas puras.
Estructural (X-01): serie sintética con semilla pública; no es un resultado."""
import random
from datetime import UTC, datetime, timedelta

from src.motor import forbush as F

T0 = datetime(2020, 1, 1, tzinfo=UTC)


def _serie(dias=120, caida=None, seed=20261113):
    r = random.Random(seed)
    out = []
    for i in range(dias * 24):
        v = 100 + r.gauss(0, 0.4)
        if caida and caida[0] <= i < caida[1]:
            v -= caida[2]
        out.append((T0 + timedelta(hours=i), v))
    return out


def test_ruido_no_alarma_con_h_calibrado_y_la_caida_si():
    assert F.alarmas(_serie(), h=30) == []
    s = _serie(caida=(80 * 24, 80 * 24 + 36, 6.0))                         # −6 % durante 36 h, tras 80 días de base
    al = F.alarmas(s, h=30)
    assert len(al) >= 1 and T0 + timedelta(days=80) <= al[0] <= T0 + timedelta(days=80, hours=6)      # la alarma llega en las primeras horas


def test_es_causal_el_futuro_no_cambia_las_alarmas_pasadas():
    s = _serie(dias=100, caida=(70 * 24, 70 * 24 + 30, 5.0))
    corto = F.alarmas(s[: 75 * 24], h=20)
    largo = F.alarmas(s, h=20)
    assert corto == [a for a in largo if a < T0 + timedelta(days=75)]


def test_sin_base_suficiente_no_hay_juicio():
    s = _serie(dias=8, caida=(6 * 24, 6 * 24 + 30, 8.0))
    assert F.alarmas(s, h=10) == []                                        # menos de 12 días de base


def test_eventos_kp_inicio_y_separacion():
    kp = [(T0 + timedelta(hours=3 * i), 2.0) for i in range(80)]
    kp[20] = (kp[20][0], 5.3); kp[21] = (kp[21][0], 7.0); kp[22] = (kp[22][0], 6.0)
    ev = F.eventos_kp(kp, 7.0, T0, T0 + timedelta(days=30))
    assert ev == [kp[20][0]]                                              # el inicio es el primer Kp ≥ 5 de las 48 h previas
    assert F.eventos_kp(kp, 7.0, T0 + timedelta(days=30), T0 + timedelta(days=40)) == []


def test_evaluar_ventana_adelanto_y_placebo_puro():
    ev = [T0 + timedelta(days=10), T0 + timedelta(days=40)]
    al = [T0 + timedelta(days=10) - timedelta(hours=5)]
    r = F.evaluar(al, ev)
    assert r["detectados"] == 1 and r["sensibilidad"] == 0.5 and r["adelantos_h"] == [5.0] and r["adelanto_mediano_h"] == 5.0
    assert F.evaluar([T0 + timedelta(days=10, hours=30)], ev)["detectados"] == 0          # fuera de la ventana de 24 h
    p = F.placebo(al, ev, T0, T0 + timedelta(days=100), 20261113, n=200)
    assert 0 < p["p_unilateral"] <= 1 and p["n"] == 200


def test_alarmas_falsas_excluyen_las_explicadas_por_tormenta():
    kp = [(T0 + timedelta(days=10), 6.0)]
    al = [T0 + timedelta(days=11), T0 + timedelta(days=30)]
    assert F.alarmas_falsas(al, kp, T0, T0 + timedelta(days=60)) == [T0 + timedelta(days=30)]
