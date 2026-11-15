"""FB-027 · contraste por correlación con nulo circular: detecta un acoplamiento real y no inventa uno en ruido (estructural, X-01; semilla pública)."""
import random

from src.motor.correlacion_intrapersona import mediana_rho_prueba


def _gen(n_pers=12, n=80, b=-0.7, seed=20261113):
    r = random.Random(seed)
    out = {}
    for p in range(n_pers):
        xs = [r.gauss(0, 1) for _ in range(n)]
        out[f"p{p}"] = [(x, b * x + r.gauss(0, 1)) for x in xs]
    return out


def test_acoplamiento_real_sale_significativo_y_con_su_signo():
    r = mediana_rho_prueba(_gen(b=-0.8), 20261113, n_perm=400)
    assert r["S"] < -0.3 and r["p_neg"] < 0.01 and r["n_personas"] == 12


def test_ruido_no_da_significancia():
    r = mediana_rho_prueba(_gen(b=0.0, seed=1), 20261113, n_perm=400)
    assert abs(r["S"]) < 0.2 and r["p_bilateral"] > 0.05


def test_pocas_pruebas_no_cuentan():
    assert mediana_rho_prueba({"a": [(1.0, 2.0)] * 10}, 1)["n_personas"] == 0
