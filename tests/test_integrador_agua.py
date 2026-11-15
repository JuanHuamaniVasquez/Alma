"""FB-004R · integrador lento del agua con el caudal REAL (fixture de Utah, S-12). Números fijados de la corrida publicada."""
import hashlib
import random

from src.motor.integrador_agua import FIXTURE, alarma, corrida, pool_volumenes, residuo


def test_fixture_real_es_el_preregistrado():
    assert hashlib.sha256(FIXTURE.read_bytes()).hexdigest() == "a0ca143eee0784bcd608fe0dcea63ea12a39f0f6e718dd6bbcf34f458c085d23"
    p = pool_volumenes()
    assert len(p) == 2115 and 0.9 < sum(p) / len(p) < 1.1            # normalizado por hogar: media ≈ 1


def test_la_normalizacion_por_caudal_es_lo_que_hace_util_la_senal():
    pool = pool_volumenes()
    n = 60
    cruda_sin_cambio = normal_con_cambio = normal_sin_cambio = 0
    for i in range(n):
        o0, e0 = corrida(random.Random(20261113 + i), pool, 0.0)
        o1, e1 = corrida(random.Random(20261113 + i), pool, 0.10)
        cruda_sin_cambio += alarma(o0) is not None
        normal_sin_cambio += alarma(residuo(o0, e0)) is not None
        normal_con_cambio += alarma(residuo(o1, e1)) is not None
    assert cruda_sin_cambio / n > 0.6                                 # el crudo se dispara solo por la dilución real
    assert normal_sin_cambio / n < 0.15 and normal_con_cambio / n > 0.95


def test_corrida_es_determinista():
    pool = pool_volumenes()
    assert corrida(random.Random(20261113), pool, 0.1) == corrida(random.Random(20261113), pool, 0.1)
