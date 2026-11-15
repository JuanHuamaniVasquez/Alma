"""M6.3 · consistencia: el clasificador distingue un cambio coherente de un fallo de una sola señal (datos sintéticos estructurales, X-01)."""
import random

from src.motor.consistencia import ajustar, incoherente, spearman


def _par(n=60, b=-0.6, seed=20261113):
    r = random.Random(seed)
    x = [r.gauss(60, 4) for _ in range(n)]
    y = [40 + b * 0.5 * (p - 60) + r.gauss(0, 3) for p in x]
    return x, y


def test_spearman_negativo_en_par_acoplado():
    x, y = _par()
    assert spearman(x, y) < -0.3


def test_fisiologico_coherente_y_fallo_incoherente():
    x, y = _par()
    aj = ajustar(x, y)
    bx, by = x[:14], y[:14]
    coher = incoherente(aj, [p + 2 * aj["sx"] for p in bx], [q + aj["b"] * 2 * aj["sy"] for q in by])
    fallo = incoherente(aj, [p + 2 * aj["sx"] for p in bx], by)
    assert not coher and fallo


def test_sin_cambio_no_alarma_casi_nunca():
    x, y = _par(seed=1)
    aj = ajustar(x, y)
    assert not incoherente(aj, x[:14], y[:14])
