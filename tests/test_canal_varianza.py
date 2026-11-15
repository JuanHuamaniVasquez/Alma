"""MP-15 · canal de varianza (DC-14 `canal`, detector `f_varianza`). Ruido SIMULADO (X-12) con semillas públicas."""
import random
from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from src.contratos import CONTRATOS, Banner
from src.contratos.comunes import Indicador
from src.contratos.dc14_recibo_verde import Canal, EstadoVerde
from src.motor import canal_varianza as cv

T = datetime(2026, 11, 15, tzinfo=UTC)
H64 = "f" * 64


def ruido(n, semilla, zigzag=0.0):
    rng = random.Random(semilla)
    return [100 + 10 * (rng.gauss(0, 1) + ((-1) ** j) * zigzag) for j in range(1, n + 1)]


def recibo(base, vig):
    return cv.recibo_varianza(recibo_id="rv-var", base=base, vig=vig, ts=T, sujeto="astro-01", indicador=Indicador.SUENO, unidad="min",
                              semilla=20261113, hash_preregistro=H64, banner=Banner.SIMULADO)


def test_tabla_x12_fpr_nominal_y_mde():
    t = cv.tabla()
    assert t["banner"].startswith("SIMULADO") and 0.005 <= t["fpr_nulo"] <= 0.015   # α=1 %
    assert cv.mde_sigma() == 1.75 and t["potencia_zigzag"]["2.0"] >= 0.95            # coincide con FB-019 (95 % a 2σ con base 28)


def test_el_critico_es_reproducible_y_cercano_al_teorico():
    assert cv.calibrar_critico() == cv.calibrar_critico(20261113, 20000, 0.01)
    assert 2.6 < cv.calibrar_critico() < 3.1                                          # F(13;27) al 99 % ≈ 2,8


def test_verde_con_recibo_en_unidades_fisicas():
    r = recibo(ruido(28, 1), ruido(14, 2))
    assert r.canal is Canal.VARIANZA and r.estado is EstadoVerde.VERDE and r.detector.value == "f_varianza"
    assert r.potencia_declarada == 0.80 and r.mde_sigma == 1.75 and 8 < r.mde_fisico < 30   # sd≈10 min → ≈17 min
    assert "F_VARIANZA" in r.regla_exacta and r.hash_preregistro == H64


def test_con_menos_de_28_dias_de_base_no_hay_verde_ni_alarma():
    r = recibo(ruido(27, 1), ruido(14, 2))
    assert r.estado is EstadoVerde.SIN_DATOS and r.mde_sigma is None and r.potencia_declarada is None
    assert recibo(ruido(28, 1), ruido(13, 2)).estado is EstadoVerde.SIN_DATOS
    assert recibo([None] * 40, ruido(14, 2)).estado is EstadoVerde.SIN_DATOS          # ausencias no cuentan como datos


def test_un_zigzag_de_3_sigma_alarma_y_no_hay_verde():
    assert recibo(ruido(28, 1), ruido(14, 2, zigzag=3.0)) is None


def test_el_verde_se_retira_solo_si_la_regla_alarma_con_datos_corregidos():
    base = ruido(28, 1)
    r = recibo(base, ruido(14, 2))
    assert cv.reevaluar(r, base, ruido(14, 2)).estado is EstadoVerde.VERDE
    assert cv.reevaluar(r, base, ruido(14, 2, zigzag=3.0)).estado is EstadoVerde.RETIRADO


def test_el_cusum_de_media_es_ciego_al_zigzag_que_este_canal_ve():
    from src.motor.adversario import _z, detecta_media, perfil
    vistos_media = vistos_var = 0
    for i in range(200):
        rng = random.Random(20261113 + i)
        b = [rng.gauss(0, 1) for _ in range(28)]
        v = [rng.gauss(0, 1) + d for d in perfil("zigzag", 2.5)]
        vistos_var += cv.razon_f(b, v) > cv.calibrar_critico()
        vistos_media += detecta_media(_z(random.Random(20261113 + i), perfil("zigzag", 2.5)))
    assert vistos_var / 200 > 0.95 and vistos_media / 200 < 0.10


def test_dc14_exige_coherencia_canal_detector():
    r = recibo(ruido(28, 1), ruido(14, 2))
    with pytest.raises(ValidationError):
        CONTRATOS["DC-14"].model_validate({**r.model_dump(), "detector": "cusum"})        # canal varianza con detector de media
    with pytest.raises(ValidationError):
        CONTRATOS["DC-14"].model_validate({**r.model_dump(), "canal": "media"})           # f_varianza fuera del canal de varianza


@pytest.mark.django_db
def test_persistencia_canal_y_detectores_largos():
    from apps.motor.models import Alarma, ReciboVerde
    from apps.motor.repositorio import guardar_alarma, guardar_recibo_verde
    guardar_recibo_verde(recibo(ruido(28, 1), ruido(14, 2)))
    assert ReciboVerde.objects.get().canal == "varianza"
    a = CONTRATOS["DC-05"].model_validate(dict(alarma_id="a-up", ts_utc=T, indicador="sueño", detector="umbral_personal", sentido="caída",
                                               umbral=1.0, valor_cruzado=0.5, regla_exacta="noche < mediana", semilla=20261113,
                                               hash_preregistro=H64, estado="activa"))
    guardar_alarma(a, Banner.REAL)
    assert Alarma.objects.get().detector == "umbral_personal"     # 15 caracteres: no cabía en max_length=12
