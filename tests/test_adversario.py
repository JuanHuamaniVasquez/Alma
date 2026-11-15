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


def test_fb019_techo_de_informacion_f_mejora_con_linea_base_larga():
    import random
    import statistics

    from src.motor.adversario import perfil

    def potencia(nbase, H, crit, n=300):
        ok = 0
        for i in range(n):
            r = random.Random(20261113 + i)
            base = [r.gauss(0, 1) for _ in range(nbase)]
            vig = [r.gauss(0, 1) + d for d in perfil("zigzag", H)]
            ok += statistics.variance(vig) / statistics.variance(base) > crit
        return ok / n

    # críticos al 99 % publicados en NOTA-FB-019 (F14: 3,947; F28: 2,846)
    assert potencia(28, 2.0, 2.846) > potencia(14, 2.0, 3.947) + 0.10
    assert potencia(14, 1.5, 3.947) < 0.60
