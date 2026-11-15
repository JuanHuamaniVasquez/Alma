"""M2.10 · Tabla de potencia, MDE condicionado a días válidos y recibo de verde (DC-14).

La tabla es SIMULADA (X-06, semilla pública 20261113). La versión rápida de la simulación se comprueba contra el
`ModeloNulo` real; la tabla versionada, contra una re-simulación más pequeña con la misma semilla.
"""
import random
from datetime import UTC, date, datetime, timedelta

import pytest

from src.contratos import SEMILLAS_PUBLICAS, Banner
from src.contratos.comunes import Indicador
from src.contratos.dc14_recibo_verde import EstadoVerde
from src.motor.cusum import calibrar_h
from src.motor.evaluacion import ejecutar_unidad
from src.motor.linea_base import LineaBase
from src.motor.potencia import DELTAS, M_MIN, VENTANA, calcular_tabla, mde_sigma, metadatos_tabla, potencia, primer_cruce, tabla_potencia
from src.motor.verde import recibo_verde, reevaluar_verde

H = calibrar_h()
F0 = date(2026, 1, 1)
TS = datetime(2026, 11, 15, tzinfo=UTC)
LINEA = LineaBase("p-sim", "sueño", 1, 14, 400.0, 70.0, 102.0, F0, F0 + timedelta(days=13), "inicial")  # σ_efectiva ≈ 102
HASH = "c" * 64


def recibo(valores, **kw):
    return recibo_verde(recibo_id="rv", linea=LINEA, valores=valores, ts=TS, sujeto="p-sim", indicador=Indicador.SUENO,
                        unidad="min", semilla=SEMILLAS_PUBLICAS[0], hash_preregistro=HASH, banner=Banner.SIMULADO, h=H, **kw)


# --- la tabla ---------------------------------------------------------------------------------------------
def test_la_tabla_versionada_declara_como_se_genero_y_su_h_es_el_calibrado():
    md = metadatos_tabla()
    assert (md["n_sim"], md["semilla"], md["k"], md["ventana"]) == (20000, 20261113, 0.5, VENTANA)
    assert md["h"] == pytest.approx(H, abs=1e-12) and md["banner"] == "SIMULADO (X-06)"


def test_la_potencia_crece_con_el_cambio_y_con_los_dias_observados():
    tb = tabla_potencia()
    for d in DELTAS:
        assert all(a <= b + 1e-12 for a, b in zip(tb[d], tb[d][1:]))               # más días ⇒ ≥ potencia
    for m in range(VENTANA):
        col = [tb[d][m] for d in DELTAS]
        assert all(a <= b + 0.02 for a, b in zip(col, col[1:]))                    # más cambio ⇒ ≥ potencia (± ruido MC)
    assert potencia(2.0, 14) >= 0.95 and potencia(0.25, 14) < 0.15


def test_el_mde_baja_con_los_dias_validos_y_es_el_de_la_tabla():
    por_m = [mde_sigma(m) for m in range(M_MIN, VENTANA + 1)]
    assert all(a >= b for a, b in zip(por_m, por_m[1:]))                            # más datos ⇒ menor MDE
    assert mde_sigma(14) == 1.75 and mde_sigma(10) == 2.25 and mde_sigma(7) == 2.75
    assert mde_sigma(14, objetivo=0.99) > mde_sigma(14, objetivo=0.90) >= mde_sigma(14, objetivo=0.80)  # más potencia exigida ⇒ MDE no menor


def test_la_version_rapida_coincide_con_el_modelo_nulo_real():
    rng = random.Random(SEMILLAS_PUBLICAS[1])
    for sensor in (0.0, 8.0):
        for delta in (0.0, 1.0, 2.5, 4.0):
            for _ in range(25):
                base = [(F0 + timedelta(days=i), rng.gauss(100, 10)) for i in range(14)]
                mon = [(F0 + timedelta(days=14 + i), rng.gauss(100, 10)) for i in range(14)]
                real = ejecutar_unidad("p-sim", Indicador.SUENO, sensor, base, mon, H, delta=delta)
                rapido = primer_cruce([v for _, v in base], [v for _, v in mon], H, delta=delta, sigma_sensor=sensor)
                assert (rapido is not None) == real.alarma
                if rapido:
                    assert rapido == (real.dia_de_alarma, real.sentido)


def test_la_tabla_versionada_coincide_con_una_resimulacion_mas_pequena_misma_semilla():
    chica = calcular_tabla(n_sim=2000)
    grande = tabla_potencia()
    for d, m in ((1.0, 14), (1.75, 14), (2.0, 10), (2.75, 7), (3.0, 5)):
        assert abs(chica[d][m - 1] - grande[d][m - 1]) < 0.04, (d, m)


# --- el recibo de verde -----------------------------------------------------------------------------------
def test_un_verde_con_los_14_dias_declara_potencia_mde_en_sigma_y_en_minutos():
    r = recibo([400.0] * 14)
    assert r.estado is EstadoVerde.VERDE and r.dias_validos == 14 and r.cobertura == 1.0
    assert r.potencia_declarada == 0.9 and r.mde_sigma == 1.75
    assert r.mde_fisico == pytest.approx(1.75 * LINEA.sigma_efectiva) and r.unidad == "min" and r.mde_fisico > 170  # ≈ 3 h de sueño
    assert r.banner is Banner.SIMULADO and r.hash_preregistro == HASH and "CUSUM_BILATERAL" in r.regla_exacta


def test_con_menos_dias_validos_el_verde_es_mas_debil_y_con_muy_pocos_no_afirma_nada():
    r14, r10, r7 = recibo([400.0] * 14), recibo([400.0] * 10 + [None] * 4), recibo([400.0] * 7 + [None] * 7)
    assert r14.mde_sigma < r10.mde_sigma < r7.mde_sigma                      # la cobertura endurece el MDE
    assert (r10.dias_validos, r7.dias_validos) == (10, 7)
    pocos = recibo([400.0] * (M_MIN - 1) + [None] * (14 - (M_MIN - 1)))
    assert pocos.estado is EstadoVerde.SIN_DATOS
    assert (pocos.potencia_declarada, pocos.mde_sigma, pocos.mde_fisico) == (None, None, None)  # no hay base para declarar
    assert recibo([None] * 14).estado is EstadoVerde.SIN_DATOS


def test_si_hay_alarma_no_hay_verde():
    assert recibo([400.0 - 3 * LINEA.sigma_efectiva] * 14) is None


def test_el_verde_se_retira_solo_si_los_datos_corregidos_hacen_alarmar_la_regla():
    r = recibo([400.0] * 14)
    assert reevaluar_verde(r, [400.0] * 14).estado is EstadoVerde.VERDE
    assert reevaluar_verde(r, [400.0 - 3 * LINEA.sigma_efectiva] * 14).estado is EstadoVerde.RETIRADO
    sd = recibo([400.0] * 3 + [None] * 11)
    assert reevaluar_verde(sd, [400.0 - 3 * LINEA.sigma_efectiva] * 14).estado is EstadoVerde.SIN_DATOS  # no afirmaba nada: no hay qué retirar
