"""MO-3 · estado de un indicador por persona: verde con recibo, sin datos suficientes o alarma con recibo; sin σ verificada no se emite."""
import random
from datetime import date, timedelta

import pytest

from src.contratos.comunes import Indicador, IndicadorSensor
from src.contratos.dc14_recibo_verde import EstadoVerde
from src.ingesta.incertidumbre import SinIncertidumbreVerificada
from src.motor.estado_indicadores import evaluar_persona

H64 = "1" * 64
D0 = date(2021, 6, 1)


def serie(n, semilla, delta_final=0.0, huecos=()):
    rng = random.Random(semilla)
    out = []
    for i in range(n):
        if i in huecos:
            continue
        v = 420 + 30 * rng.gauss(0, 1) + (delta_final if i >= 14 else 0.0)
        out.append((D0 + timedelta(days=i), v))
    return out


def ev(obs, ind=Indicador.SUENO, sensor=IndicadorSensor.SUENO):
    return evaluar_persona("persona-01", ind, sensor, obs, H64)


def test_menos_de_14_dias_es_modo_aprendizaje_y_no_afirma_nada():
    assert ev(serie(13, 1)) is None and ev([]) is None


def test_dia_normal_da_verde_con_recibo_y_banner_real():
    e = ev(serie(28, 1))
    assert e.alarma is None and e.recibo.estado is EstadoVerde.VERDE and e.recibo.banner.value == "REAL"
    assert e.recibo.dias_validos == 14 and e.recibo.hash_preregistro == H64 and e.recibo.potencia_declarada > 0


def test_pocos_dias_validos_en_la_ventana_no_declaran_potencia():
    e = ev(serie(28, 1, huecos=range(15, 28)))       # solo 1 día de monitoreo válido
    assert e.recibo.estado is EstadoVerde.SIN_DATOS and e.recibo.potencia_declarada is None


def test_una_caida_grande_alarma_con_recibo_y_no_hay_verde():
    e = ev(serie(28, 1, delta_final=-400))
    assert e.recibo is None and e.alarma.sentido.value == "caída" and "CUSUM_BILATERAL" in e.alarma.regla_exacta
    assert e.alarma.hash_preregistro == H64 and e.alarma.semilla == 20261113 and e.alarma.valor_cruzado >= e.alarma.umbral


def test_sin_sigma_verificada_el_indicador_no_se_emite():
    with pytest.raises(SinIncertidumbreVerificada):
        ev(serie(28, 1), Indicador.TEMPERATURA, IndicadorSensor.TEMPERATURA)
