"""FB-003 (SIMULADO, semillas públicas): fija el comportamiento de MO-4 y de la cuarta causa."""
import random

from src.motor.triangulacion import CAUSAS, acumulado, diagnosticar, diagnosticar_almacen, ingenuo, mundo


def _exactitud(causa, j, n=40):
    return sum(diagnosticar(mundo(random.Random(20261113 + 1000 * j + i), causa))[0] == causa for i in range(n)) / n


def test_mo4_distingue_mundo_de_fallos_de_fuente():
    assert _exactitud("mundo", 1) >= 0.9
    assert _exactitud("sensor", 2) >= 0.75 and _exactitud("humano", 3) >= 0.75


def test_corrida_publica_es_determinista():
    a = diagnosticar(mundo(random.Random(20261113 + 2000), "sensor"))
    b = diagnosticar(mundo(random.Random(20261113 + 2000), "sensor"))
    assert a == b


def test_comparador_ingenuo_no_puede_diagnosticar_fuente():
    assert ingenuo({"humano"}) == "mundo" and ingenuo(set()) == "nada"


def test_cuarta_causa_distingue_fuga_de_almacen():
    ok = lambda causa, j: sum(diagnosticar_almacen(acumulado(random.Random(20261113 + 77 + 1000 * j + i), causa, 60)) == causa for i in range(60)) / 60
    assert ok("fuga", 0) >= 0.9 and ok("almacen", 1) >= 0.9


def test_causas_declaradas():
    assert CAUSAS == ("nada", "mundo", "sensor", "humano")
