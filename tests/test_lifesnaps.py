"""M2.7 · IN-1: adaptador de LifeSnaps → DC-01 con filas REALES del dataset (extracto CC BY 4.0).

Las filas «imposibles» o sin valor son construidas a propósito (registro X-01); el resto es real.
"""
import csv
import datetime as dt
import math
from pathlib import Path

import pytest

from src.contratos import Banner
from src.contratos.comunes import IndicadorSensor
from src.contratos.dc01_sensores import CalidadDato
from src.ingesta import incertidumbre
from src.ingesta.incertidumbre import SinIncertidumbreVerificada, sigma_de
from src.ingesta.lifesnaps import cargar, fila_a_registros, leer_diario

RAIZ = Path(__file__).resolve().parent.parent
EXTRACTO = RAIZ / "data" / "fixtures" / "lifesnaps_diario_extracto.csv"
COMPLETO = RAIZ / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"


def test_el_extracto_real_se_carga_completo_y_valida_contra_dc01():
    r = cargar(EXTRACTO)
    assert r.filas == 187 and len(r.registros) == 2 * 187  # fc y sueño por cada día
    assert all(x.banner is Banner.REAL and x.fuente == "fitbit_sense" for x in r.registros)
    assert len({x.persona_id for x in r.registros}) == 1  # un participante pseudonimizado


def test_la_ausencia_es_dato_no_se_rellena():
    filas = leer_diario(EXTRACTO)
    esperados = {"bpm": sum(1 for f in filas if not f["bpm"]), "minutesAsleep": sum(1 for f in filas if not f["minutesAsleep"])}
    assert esperados["bpm"] > 0 and esperados["minutesAsleep"] > 0  # el fixture real SÍ tiene huecos
    r = cargar(EXTRACTO)
    ausentes = [x for x in r.registros if x.calidad is CalidadDato.AUSENTE]
    assert len(ausentes) == sum(esperados.values())
    assert all(x.valor is None and x.incertidumbre_sensor is None for x in ausentes)
    assert r.por_calidad.get("ok", 0) + len(ausentes) + r.por_calidad.get("sospechoso", 0) == len(r.registros)


def test_la_incertidumbre_viaja_con_el_dato_y_viene_de_limites_publicados():
    s_fc, s_sueno = sigma_de(IndicadorSensor.FC), sigma_de(IndicadorSensor.SUENO)
    assert s_fc.sigma == pytest.approx((8.6 + 6.9) / (2 * 1.96)) and s_fc.unidad == "lpm"
    assert s_sueno.sigma == pytest.approx((196.3 + 204.3) / (2 * 1.96)) and s_sueno.unidad == "min"
    assert s_fc.es_proxy and "PROXY" in s_fc.nota and "PMC8527385" in s_fc.enlace + s_fc.fuente
    for x in cargar(EXTRACTO).registros:
        if x.calidad is CalidadDato.OK:
            assert x.incertidumbre_sensor == pytest.approx(sigma_de(x.indicador).sigma)


def test_sin_sigma_verificada_no_se_emite_el_indicador():
    for ind in (IndicadorSensor.TEMPERATURA, IndicadorSensor.PRESION, IndicadorSensor.GLUCOSA):
        with pytest.raises(SinIncertidumbreVerificada, match="no se emite"):
            sigma_de(ind)


def test_hay_al_menos_14_dias_reales_consecutivos_con_pulso_y_sueno():
    por_dia = {}
    for x in cargar(EXTRACTO).registros:
        por_dia.setdefault(x.ts_utc.date(), []).append(x.calidad is CalidadDato.OK)
    buenos = sorted(d for d, v in por_dia.items() if len(v) == 2 and all(v))
    racha = mejor = 1
    for a, b in zip(buenos, buenos[1:]):
        racha = racha + 1 if (b - a).days == 1 else 1
        mejor = max(mejor, racha)
    assert mejor >= 14  # fixture real para el libro de 14 días de M1.1 (la racha real es de 88)


def test_valores_fisicamente_imposibles_se_marcan_sospechosos_y_el_texto_basura_es_ausencia():
    base = {"id": "p-test-001", "date": "2026-01-01", "bpm": "72", "minutesAsleep": "420"}
    ok = fila_a_registros(base)
    assert [x.calidad for x in ok] == [CalidadDato.OK, CalidadDato.OK]
    imposible = fila_a_registros({**base, "bpm": "0", "minutesAsleep": "1500"})
    assert [x.calidad for x in imposible] == [CalidadDato.SOSPECHOSO, CalidadDato.SOSPECHOSO]
    basura = fila_a_registros({**base, "bpm": "nan", "minutesAsleep": "n/a"})
    assert [x.calidad for x in basura] == [CalidadDato.AUSENTE, CalidadDato.AUSENTE]
    assert all(x.ts_utc.tzinfo is not None and x.ts_utc.hour == 0 for x in ok)


def test_la_atribucion_cc_by_acompana_al_extracto():
    t = (RAIZ / "data" / "fixtures" / "LIFESNAPS-ATRIBUCION.md").read_text(encoding="utf-8")
    assert "10.1038/s41597-022-01764-x" in t and "CC BY 4.0" in t
    assert "no de astronautas" in t.lower()  # el aviso de que NO son astronautas viaja con los datos


@pytest.mark.skipif(not COMPLETO.exists(), reason="el dataset completo (615 MB) no está en este equipo")
def test_el_extracto_es_un_subconjunto_literal_del_dataset_completo():
    completo = {(r["id"], r["date"]): r for r in csv.DictReader(COMPLETO.open(encoding="utf-8"))}
    for fila in leer_diario(EXTRACTO):
        assert completo[(fila["id"], fila["date"])] == fila
