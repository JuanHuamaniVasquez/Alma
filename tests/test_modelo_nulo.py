"""M2.1 / M2.2 · MO-1 modelo nulo + MO-2 residuo + MO-3 CUSUM bilateral + DC-05 con recibo.

Comportamiento sobre DATOS REALES: sueño del participante de LifeSnaps (88 días válidos; NO astronautas; σ de
sensor = proxy declarado). La calibración del umbral y las inyecciones usan SIMULACIÓN etiquetada (registro X-06
de docs/politica-de-datos.md: ruido gaussiano con semillas públicas): son utensilios estadísticos, no datos.
"""
import math
import random
import statistics
from datetime import date, timedelta
from pathlib import Path

import pytest

from src.contratos import SEMILLAS_PUBLICAS
from src.contratos.comunes import Indicador, IndicadorSensor
from src.contratos.dc01_sensores import CalidadDato
from src.contratos.dc05_alarma import EstadoAlarma, Sentido
from src.ingesta.incertidumbre import sigma_de
from src.ingesta.lifesnaps import cargar
from src.motor.alertas import a_dc05, presupuesto_de, reevaluar
from src.motor.cusum import calibrar_h, ejecutar_regla, paso, regla_exacta
from src.motor.linea_base import DIAS_BASE, HistorialLineasBase, LineaBase, estimar_linea_base
from src.motor.modelo_nulo import ModeloNulo

RAIZ = Path(__file__).resolve().parent.parent
EXTRACTO = RAIZ / "data" / "fixtures" / "lifesnaps_diario_extracto.csv"
HASH = "b" * 64  # un SHA-256 de ejemplo; en una corrida real es el del acta registrada (GO-2)
SIGMA_SUENO = sigma_de(IndicadorSensor.SUENO).sigma


def serie_real_sueno():
    regs = [r for r in cargar(EXTRACTO).registros if r.indicador is IndicadorSensor.SUENO]
    regs.sort(key=lambda r: r.ts_utc)
    return [(r.ts_utc.date(), r.valor if r.calidad is CalidadDato.OK else None) for r in regs]


def correr(modelo, serie):
    return [modelo.observar(d, v) for d, v in serie]


def serie_sim(rng, n, media=500.0, sd=10.0, desplazamiento=0.0, desde=None):
    """SIMULADA (X-06): n días de ruido gaussiano; desde el día `desde` se suma un cambio sostenido."""
    f0 = date(2026, 1, 1)
    return [(f0 + timedelta(days=i), rng.gauss(media, sd) + (desplazamiento if desde is not None and i >= desde else 0.0))
            for i in range(n)]


# --- MO-1: línea base honesta ----------------------------------------------------------------
def test_modo_aprendizaje_no_finge_prediccion_ni_confianza():
    obs = correr(ModeloNulo("p-real", Indicador.SUENO, SIGMA_SUENO), serie_real_sueno())
    validos = [o for o in obs if o.estado != "ausente"]
    assert [o.estado for o in validos[:DIAS_BASE]] == ["aprendizaje"] * DIAS_BASE
    assert all(o.residuo is None and o.alarma is None for o in validos[:DIAS_BASE])
    assert validos[0].confianza == pytest.approx(1 / DIAS_BASE) and validos[DIAS_BASE - 1].confianza == 1.0
    assert all(o.estado == "activo" for o in validos[DIAS_BASE:])


def test_la_linea_base_es_la_de_los_primeros_14_datos_validos_y_su_sigma_respeta_el_piso_del_sensor():
    serie = serie_real_sueno()
    m = ModeloNulo("p-real", Indicador.SUENO, SIGMA_SUENO)
    correr(m, serie)
    primeros = [v for _, v in serie if v is not None][:DIAS_BASE]
    lb = m.linea_base
    assert lb.n == DIAS_BASE and lb.media == pytest.approx(statistics.fmean(primeros)) and lb.sd == pytest.approx(statistics.stdev(primeros))
    assert lb.sigma_efectiva == pytest.approx(max(SIGMA_SUENO, lb.sd * math.sqrt(1 + 1 / 14)))
    assert lb.sigma_efectiva >= SIGMA_SUENO  # el piso del instrumento nunca se baja


def test_corrida_real_cada_residuo_es_observado_menos_predicho_y_la_ausencia_no_se_rellena():
    serie = serie_real_sueno()
    m = ModeloNulo("p-real", Indicador.SUENO, SIGMA_SUENO)
    obs = correr(m, serie)
    validos = sum(1 for _, v in serie if v is not None)
    r = [o.residuo for o in obs if o.residuo is not None]
    assert len(r) == validos - DIAS_BASE and m.ausencias == len(serie) - validos > 0
    assert all(x.residuo == pytest.approx(x.observado - x.predicho) and x.sigma_efectiva > 0 for x in r)
    assert all(o.residuo is None for o in obs if o.estado == "ausente")  # sin dato no hay residuo inventado


def test_la_corrida_real_es_determinista():
    a = [o.residuo for o in correr(ModeloNulo("p-real", Indicador.SUENO, SIGMA_SUENO), serie_real_sueno())]
    b = [o.residuo for o in correr(ModeloNulo("p-real", Indicador.SUENO, SIGMA_SUENO), serie_real_sueno())]
    assert a == b


# --- MO-3: el umbral es calibrado, no artesanal -------------------------------------------------
def test_h_calibrado_da_un_fpr_cercano_al_1_por_ciento_en_14_dias_con_otra_semilla():
    h = calibrar_h()
    rng = random.Random(SEMILLAS_PUBLICAS[1])  # semilla distinta de la de calibración
    corridas, alarmas = 3000, 0
    for _ in range(corridas):
        m = ModeloNulo("p-sim", Indicador.SUENO, 0.0, h=h)
        obs = correr(m, serie_sim(rng, 2 * DIAS_BASE))
        alarmas += any(o.alarma for o in obs)
    assert 0.004 <= alarmas / corridas <= 0.018, f"FPR empírico {alarmas / corridas:.4f}"


def test_el_cusum_es_bilateral_caidas_y_alzas_se_detectan():
    h = calibrar_h()
    for signo, sentido in ((-1, Sentido.CAIDA), (+1, Sentido.ALZA)):
        rng = random.Random(SEMILLAS_PUBLICAS[2])
        detectadas = 0
        for _ in range(100):
            m = ModeloNulo("p-sim", Indicador.SUENO, 0.0, h=h)
            obs = correr(m, serie_sim(rng, DIAS_BASE + 20, sd=10.0, desplazamiento=signo * 40.0, desde=DIAS_BASE))  # ±4σ
            detectadas += any(o.alarma and o.alarma.sentido is sentido for o in obs)
        assert detectadas >= 95, f"{sentido.value}: solo {detectadas}/100"


def test_un_cambio_pequeno_no_se_detecta_en_14_dias_el_precio_honesto_de_una_base_de_14_dias():
    h = calibrar_h()
    rng = random.Random(SEMILLAS_PUBLICAS[3])
    detectadas = 0
    for _ in range(200):
        m = ModeloNulo("p-sim", Indicador.SUENO, 0.0, h=h)
        obs = correr(m, serie_sim(rng, 2 * DIAS_BASE, sd=10.0, desplazamiento=-5.0, desde=DIAS_BASE))  # −0.5σ
        detectadas += any(o.alarma for o in obs)
    assert detectadas / 200 < 0.25  # medio sigma no se ve en 14 días: se dice, no se esconde


# --- MO-2/MO-3: bandera y reinicio -------------------------------------------------------------
def test_bandera_sorpresa_y_deriva_y_el_cusum_se_reinicia_tras_alarmar():
    m = ModeloNulo("p-sim", Indicador.SUENO, 0.0, h=3.0)
    rng = random.Random(SEMILLAS_PUBLICAS[0])
    base = serie_sim(rng, DIAS_BASE, sd=10.0)
    correr(m, base)
    f = base[-1][0]
    sorpresa = m.observar(f + timedelta(days=1), m.linea_base.media - 3 * m.linea_base.sigma_efectiva)
    assert sorpresa.residuo.bandera.value in {"sorpresa", "deriva"}
    obs = [m.observar(f + timedelta(days=2 + i), m.linea_base.media - 2.0 * m.linea_base.sigma_efectiva) for i in range(6)]
    cruce = next(o for o in obs if o.alarma)
    assert cruce.residuo.bandera.value == "deriva" and cruce.residuo.cusum_acumulado < 0  # firmado: caída
    despues = m.observar(f + timedelta(days=20), m.linea_base.media)
    assert abs(despues.residuo.cusum_acumulado) < 3.0  # reiniciado


# --- DC-05 con recibo ejecutable ---------------------------------------------------------------
def _alarma_de_caida():
    m = ModeloNulo("p-sim", Indicador.SUENO, 0.0, h=3.0)
    rng = random.Random(SEMILLAS_PUBLICAS[0])
    base = serie_sim(rng, DIAS_BASE, sd=10.0)
    correr(m, base)
    f = base[-1][0]
    for i in range(20):
        o = m.observar(f + timedelta(days=1 + i), m.linea_base.media - 2.0 * m.linea_base.sigma_efectiva)
        if o.alarma:
            return o.alarma
    raise AssertionError("no hubo alarma")


def test_la_alarma_sale_con_recibo_completo_y_la_regla_la_reproduce():
    a = _alarma_de_caida()
    dc05 = a_dc05(a, indicador=Indicador.SUENO, alarma_id="al-1", semilla=SEMILLAS_PUBLICAS[0], hash_preregistro=HASH)
    assert dc05.regla_exacta.startswith("CUSUM_BILATERAL") and dc05.semilla == 20261113 and dc05.hash_preregistro == HASH
    assert dc05.presupuesto_id.value == "ritmo" and dc05.sentido is Sentido.CAIDA and dc05.estado is EstadoAlarma.ACTIVA
    r = ejecutar_regla(dc05.regla_exacta, list(a.valores))
    assert r.alarma and r.sentido == "caída" and r.indice == len(a.valores) - 1  # cruza exactamente en el último dato
    assert reevaluar(dc05, list(a.valores)).estado is EstadoAlarma.ACTIVA


def test_si_la_regla_ya_no_se_cumple_la_alarma_se_retira_sola():
    a = _alarma_de_caida()
    dc05 = a_dc05(a, indicador=Indicador.SUENO, alarma_id="al-1", semilla=SEMILLAS_PUBLICAS[0], hash_preregistro=HASH)
    corregidos = [x + 80.0 for x in a.valores]  # datos corregidos: el sueño «no cayó»
    assert reevaluar(dc05, corregidos).estado is EstadoAlarma.RETIRADA
    assert reevaluar(dc05, list(a.valores)[:-1]).estado is EstadoAlarma.RETIRADA  # sin el dato del cruce tampoco


def test_el_recibo_es_texto_que_se_puede_leer_y_ejecutar_sin_el_codigo_original():
    texto = regla_exacta(0.5, 4.0, 100.0, 10.0)
    assert ejecutar_regla(texto, [100.0] * 30).alarma is False
    r = ejecutar_regla(texto, [70.0] * 10)  # z = −3 → S⁻ sube 2.5 por día → cruza 4.0 al 2.º día
    assert r.alarma and r.sentido == "caída" and r.indice == 1
    assert ejecutar_regla(texto, [130.0] * 10).sentido == "alza"
    with pytest.raises(ValueError):
        ejecutar_regla("regla inventada", [1.0])


def test_sin_presupuesto_documentado_la_alarma_lleva_el_indicador_y_no_se_inventa_un_presupuesto():
    assert presupuesto_de(Indicador.SUENO).value == "ritmo"
    a = _alarma_de_caida()
    ritmo = a_dc05(a, indicador=Indicador.SUENO, alarma_id="a1", semilla=SEMILLAS_PUBLICAS[0], hash_preregistro=HASH)
    assert ritmo.presupuesto_id.value == "ritmo" and ritmo.indicador is None
    for ind in (Indicador.FC, Indicador.TEMPERATURA, Indicador.ANIMO):
        assert presupuesto_de(ind) is None
        dc05 = a_dc05(a, indicador=ind, alarma_id="a2", semilla=SEMILLAS_PUBLICAS[0], hash_preregistro=HASH)
        assert dc05.indicador is ind and dc05.presupuesto_id is None  # recibo completo, sin presupuesto inventado


# --- el enchufe de M-L1: líneas base versionadas, solo-anexar, memoria de la primera ----------------
def _lb(version, media, desde, hasta):
    return LineaBase("p-sim", "sueño", version, 14, media, 10.0, 0.0, desde, hasta, "recalibración" if version > 1 else "inicial")


def test_las_lineas_base_son_solo_anexar_y_miden_la_deriva_acumulada_la_rana_hirviendo():
    h = HistorialLineasBase()
    h.registrar(_lb(1, 500.0, date(2026, 1, 1), date(2026, 1, 14)))
    h.registrar(_lb(2, 490.0, date(2026, 3, 1), date(2026, 3, 14)))
    h.registrar(_lb(3, 480.0, date(2026, 6, 1), date(2026, 6, 14)))
    assert [v.version for v in h.versiones("p-sim", "sueño")] == [1, 2, 3]
    sigma1 = h.versiones("p-sim", "sueño")[0].sigma_efectiva
    assert h.deriva_entre_versiones("p-sim", "sueño", 1, 2) == pytest.approx(-10.0 / sigma1)
    # cada cohorte «normaliza» solo −1σ respecto a la anterior, pero la primera línea base recuerda −2σ acumulados
    assert h.deriva_acumulada("p-sim", "sueño") == pytest.approx(-20.0 / sigma1)
    assert h.vigente("p-sim", "sueño").version == 3
    with pytest.raises(ValueError, match="solo se anexa"):
        h.registrar(_lb(2, 400.0, date(2026, 8, 1), date(2026, 8, 14)))  # no se reescribe una versión
    with pytest.raises(ValueError, match="posteriores"):
        h.registrar(_lb(4, 470.0, date(2026, 6, 10), date(2026, 6, 23)))  # datos solapados con la anterior


def test_estimar_linea_base_devuelve_none_mientras_aprende():
    f0 = date(2026, 1, 1)
    obs = [(f0 + timedelta(days=i), 100.0 + i) for i in range(13)]
    assert estimar_linea_base("p", "sueño", obs, 1.0) is None
    assert estimar_linea_base("p", "sueño", obs + [(f0 + timedelta(days=13), 113.0)], 1.0).n == 14
    assert estimar_linea_base("p", "sueño", [(f0, None)] * 40, 1.0) is None  # solo ausencias: nunca hay base
