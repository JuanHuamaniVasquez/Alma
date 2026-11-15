"""FB-018 (SIMULADO): el zigzag evade al CUSUM de media; el escalón de igual daño no. Regresión de la corrida publicada."""
import statistics

from src.motor.adversario import PERFILES, calibrar_hv, perfil, tasas


def test_todos_los_perfiles_tienen_el_mismo_dano():
    for p in PERFILES:
        assert abs(statistics.fmean(abs(x) for x in perfil(p, 1.5)) - 1.5) < 0.06, p
    assert abs(statistics.fmean(perfil("zigzag", 1.0))) < 0.08            # media ≈ 0: el CUSUM de media no la ve


def test_zigzag_evade_y_escalon_no():
    hv = calibrar_hv(n=3000)
    assert tasas("zigzag", 2.0, 20261113, 120, hv)["media"] <= 0.10
    assert tasas("escalon", 2.0, 20261113, 120, hv)["media"] >= 0.85
    assert tasas("nulo", 0.0, 20261113, 120, hv)["union"] <= 0.06


def test_la_contramedida_de_varianza_ve_algo_pero_no_basta():
    hv = calibrar_hv(n=3000)
    t = tasas("zigzag", 2.0, 20261113, 120, hv)
    assert t["varianza"] > t["media"] and t["varianza"] < 0.80          # H2 de FB-018 refutada: no llega al 80 %
