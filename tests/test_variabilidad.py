import random
from datetime import date, timedelta

from src.motor.variabilidad import barajar_dias, correlacion_entre, cv, ic_mediana, pearson, rho1


def _serie(vals, ini=date(2020, 1, 1)):
    return {ini + timedelta(days=i): v for i, v in enumerate(vals)}


def test_rho1_detecta_dependencia_y_barajar_la_destruye():
    s = _serie([float(i % 2 == 0) + 0.0 for i in range(60)])           # alterna: ρ1 ≈ -1
    assert rho1(s) < -0.9
    t = _serie([float(i) for i in range(60)])                           # tendencia: ρ1 ≈ +1
    assert rho1(t) > 0.9
    assert abs(rho1(barajar_dias(t, random.Random(20261113)))) < 0.4


def test_dia_no_observado_no_se_imputa():
    s = _serie([1.0, 2.0, 3.0] * 10)
    del s[date(2020, 1, 5)]
    pares = rho1(s, min_pares=1)
    assert pares is not None and len(s) == 29


def test_minimos_y_cv():
    assert rho1(_serie([1.0, 2.0, 3.0])) is None
    assert cv(_serie([5.0] * 30)) == 0.0
    assert cv(_serie([1.0] * 5)) is None


def test_correlacion_entre_hogares_solo_con_dias_comunes():
    a, b = _serie([float(i) for i in range(30)]), _serie([2.0 * i for i in range(30)])
    c = _serie([1.0] * 30, ini=date(2021, 1, 1))
    r = correlacion_entre([a, b, c])
    assert len(r) == 1 and r[0] > 0.99
    assert pearson([1, 2], [1, 2]) is None


def test_ic_mediana_contiene_mediana():
    m, lo, hi = ic_mediana([0.1, 0.2, 0.3, 0.4, 0.5], 20261113, n=500)
    assert lo <= m <= hi
