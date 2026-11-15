"""M6.4 · el libro de privacidad: composición, agotamiento, reproducibilidad y el ataque por diferencias (estructural, X-01)."""
import pytest

from src.superficies.privacidad import Libro, PresupuestoAgotado, laplace
import random


def test_el_libro_suma_epsilon_y_se_agota():
    L = Libro(total=1.0)
    L.liberar_conteo("a", 2, 5, 0.5)
    L.liberar_conteo("b", 1, 5, 0.5)
    assert L.gastado == 1.0 and L.restante == 0.0
    with pytest.raises(PresupuestoAgotado):
        L.liberar_conteo("c", 1, 5, 0.1)


def test_reproducible_por_semilla_y_etiqueta():
    a, b = Libro(), Libro()
    assert a.liberar_conteo("x", 2, 5, 0.5) == b.liberar_conteo("x", 2, 5, 0.5)


def test_ruido_laplace_tiene_escala_correcta():
    rng = random.Random(20261113)
    xs = [abs(laplace(2.0, rng)) for _ in range(40000)]
    assert abs(sum(xs) / len(xs) - 2.0) < 0.06          # E|X| = escala


def test_ataque_por_diferencias_exacto_vs_con_ruido():
    # Tripulación de 5; el atacante pide el conteo de «en alarma» de los 5 y de los otros 4 (sin VEGA). Exacto → recupera a VEGA siempre.
    rng = random.Random(20261113)
    exacto = fallos = 0
    ensayos = 2000
    for _ in range(ensayos):
        v = rng.random() < 0.15                       # estado oculto de VEGA
        otros = sum(rng.random() < 0.15 for _ in range(4))
        exacto += ((otros + v) - otros) == v
        L = Libro(total=10)
        d = L.liberar_conteo("t5", otros + v, 5, 0.5, semilla=rng.randrange(1 << 30)) - L.liberar_conteo("t4", otros, 4, 0.5, semilla=rng.randrange(1 << 30))
        fallos += (d >= 1) != v                       # mejor estrategia simple del atacante
    assert exacto == ensayos                          # sin ruido: reidentificación total
    assert fallos / ensayos > 0.12                    # con ε=0,5 por consulta el atacante se equivoca de verdad
