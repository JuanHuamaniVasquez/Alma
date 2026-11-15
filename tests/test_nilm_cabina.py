"""M6.2 · NILM de cabina: identificable con turnos escalonados, no identificable con horarios idénticos (SIMULADO, X-17). Semilla pública 20261113."""
import random

from src.motor.nilm_cabina import N_TRIP, atribuir, exactitud, resolver, simular


def test_ruido_cero_recupera_al_tripulante_con_turnos():
    rng = random.Random(20261113)
    for k in range(N_TRIP):
        r, X = simular(4, 0.2, 0.0, k, 4, rng)
        d = resolver(r, X)
        assert max(range(N_TRIP), key=lambda i: d[i]) == k


def test_horarios_identicos_son_azar():
    e = exactitud(0, 0.2, 0.069, 300, 20261113)
    assert abs(e["exactitud"] - 1 / N_TRIP) < 0.09


def test_con_turnos_supera_al_azar():
    assert exactitud(4, 0.2, 0.069, 200, 20261113)["exactitud"] > 0.6


def test_empate_se_resuelve_entre_los_empatados():
    rng = random.Random(1)
    assert atribuir([1.0, 1.0, 0.0], rng) in (0, 1)
