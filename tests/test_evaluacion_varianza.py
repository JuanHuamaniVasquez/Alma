"""M2.20 · lógica de FB-020 con ruido SIMULADO (semilla pública): ventanas, FPR nominal, potencia y ceguera del CUSUM de media."""
import random
from datetime import date, timedelta

from src.motor.evaluacion_varianza import evaluar, ventanas, veredictos, wilson


def serie(n, semilla, hueco_en=None):
    rng, d, out = random.Random(semilla), date(2021, 6, 1), []
    for i in range(n):
        d += timedelta(days=100 if i == hueco_en else 1)
        out.append((d, 400 + 40 * rng.gauss(0, 1)))
    return out


def test_ventanas_cada_14_y_se_descartan_las_que_puentean_huecos():
    assert len(ventanas(serie(70, 1))) == 3                # 70 valores: inicios 0, 14, 28 (28+42=70)
    assert len(ventanas(serie(70, 1, hueco_en=30))) < 3    # un hueco de 100 días invalida las ventanas que lo cruzan
    assert all(len(b) == 28 and len(v) == 14 for b, v in ventanas(serie(70, 1)))


def test_wilson_es_un_intervalo_razonable():
    lo, hi = wilson(3, 100)
    assert 0.009 < lo < 0.03 < hi < 0.09


def test_con_ruido_gaussiano_el_fpr_es_nominal_y_el_canal_ve_lo_que_el_cusum_no():
    series = {f"p{i}": serie(14 * 30 + 28, 20261113 + i) for i in range(10)}
    r = evaluar(series)
    assert r["n_ventanas"] >= 250 and r["fpr"]["tasa"] < 0.03
    p = r["potencia"]
    assert p["3.0"]["canal_varianza"] >= 0.95 and p["2.0"]["canal_varianza"] >= 0.80
    assert p["2.0"]["cusum_media"] <= 0.10
    v = veredictos(r)
    assert v["H1"] == v["H2"] == v["H3"] == "SOSTENIDA" and v["H4_control_valido"]
