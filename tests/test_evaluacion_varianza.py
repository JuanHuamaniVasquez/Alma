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


def test_mad_es_robusto_a_un_dia_atipico_donde_f_no_lo_es():
    from src.motor.canal_varianza import razon_f
    from src.motor.evaluacion_varianza import razon_mad
    rng = random.Random(20261113)
    base = [rng.gauss(0, 1) for _ in range(28)]
    vig = [rng.gauss(0, 1) for _ in range(14)]
    vig_atipico = vig[:-1] + [15.0]       # una noche de 15σ (p. ej. sueño de 0 min por no llevar el reloj)
    assert razon_f(base, vig_atipico) > 3 * razon_f(base, vig)
    assert abs(razon_mad(base, vig_atipico) - razon_mad(base, vig)) < 0.25


def test_seleccion_en_entrenamiento_y_critico_empirico_sobre_ruido_con_colas_pesadas():
    from src.motor.evaluacion_varianza import candidato, critico_empirico, razon_f, seleccionar
    def pesadas(semilla):  # t de 3 g.l. escalada: colas más pesadas que la normal
        rng, d, out = random.Random(semilla), date(2021, 6, 1), []
        for i in range(14 * 30 + 28):
            d += timedelta(days=1)
            out.append((d, 400 + 40 * rng.gauss(0, 1) / max(0.3, (sum(rng.gauss(0, 1) ** 2 for _ in range(3)) / 3) ** 0.5)))
        return out
    ls = {f"p{i}": pesadas(20261113 + i) for i in range(8)}
    c = critico_empirico([ls], razon_f)
    assert c > 2.85                                           # con colas pesadas el crítico normal se queda corto
    s = seleccionar(ls, ls)
    assert set(s["tabla"]) == {"C2", "C3", "C4"} and s["tabla"]["C3"]["fpr_entrenamiento"] <= 0.03
    assert s["elegido"] in (None, "C2", "C3", "C4")
    est, cc = candidato("C3", (ls, ls))
    assert est is razon_f and cc == c
