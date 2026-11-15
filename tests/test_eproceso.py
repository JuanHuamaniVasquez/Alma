"""M6.1 · e-proceso: la teoría se comprueba en simulación (nula gaussiana) y el detector detecta un escalón. Semilla pública 20261113."""
import random

from src.motor.eproceso import ALFA, detecta, mezcla, regla_exacta


def test_ville_nula_gaussiana_fpr_bajo_alfa():
    rng = random.Random(20261113)
    n, k = 4000, 0
    for _ in range(n):
        if detecta([rng.gauss(0, 1) for _ in range(14)], 1.0) is not None:
            k += 1
    assert k / n <= ALFA            # Ville: P(alguna alarma en 14 d) ≤ α (en la práctica es mucho menor: la cota es conservadora)


def test_detecta_escalon_y_da_retardo():
    rng = random.Random(20261114)
    z = [rng.gauss(3.0, 1) for _ in range(14)]
    d = detecta(z, 1.0)
    assert d is not None and d <= 7


def test_mezcla_monotona_en_media_absoluta():
    assert mezcla([2.0] * 10)[-1] > mezcla([1.0] * 10)[-1] > mezcla([0.0] * 10)[-1]


def test_bilateral_simetrico():
    a, b = mezcla([1.5, 2, 2.5, 1, 2]), mezcla([-1.5, -2, -2.5, -1, -2])
    assert all(abs(x - y) < 1e-12 for x, y in zip(a, b))


def test_regla_exacta_imprimible():
    r = regla_exacta(7.5, 1.2, 1.25)
    assert "mu=7.5" in r and "ALARMA si M>=1/alfa" in r
