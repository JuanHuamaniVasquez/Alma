"""M2.8 · evaluador de FB-009. Estadísticos exactos y estructura de unidades; SIN tocar el dataset de la evaluación.

La verificación contra el resultado registrado (cuando exista) está en la última sección. Las series simuladas son X-06.
"""
import json
import math
import random
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest

from src.contratos import SEMILLAS_PUBLICAS
from src.contratos.comunes import Indicador, IndicadorSensor
from src.contratos.dc01_sensores import CalidadDato
from src.gobernanza.preregistro import exigir_preregistro, hash_acta
from src.ingesta.incertidumbre import sigma_de
from src.ingesta.lifesnaps import cargar
from src.motor.cusum import calibrar_h
from src.motor.evaluacion import (BLOQUE, H_FB009, ejecutar_unidad, evaluar, cola_binomial, remuestreo_por_persona,
                                  unidades, veredictos, wilson, x_critico)

RAIZ = Path(__file__).resolve().parent.parent
EXTRACTO = RAIZ / "data" / "fixtures" / "lifesnaps_diario_extracto.csv"
F0 = date(2026, 1, 1)


def serie(valores):
    return [(F0 + timedelta(days=i), v) for i, v in enumerate(valores)]


def test_el_h_del_acta_es_el_calibrado():
    assert calibrar_h() == pytest.approx(H_FB009, rel=0, abs=1e-12)


def test_unidades_son_bloques_de_28_dias_validos_14_de_base_y_14_de_monitoreo():
    assert unidades(serie(range(27))) == []
    u = unidades(serie(range(56)))
    assert len(u) == 2 and all(len(b) == 14 and len(m) == 14 for b, m in u)
    assert u[0][0][0][1] == 0 and u[0][1][-1][1] == 27 and u[1][0][0][1] == 28  # bloques disjuntos y consecutivos
    assert len(unidades(serie(range(83)))) == 2 and len(unidades(serie(range(84)))) == 3
    desordenada = list(reversed(serie(range(28))))
    assert unidades(desordenada)[0][0][0][1] == 0  # se ordena por fecha


def test_estadisticos_exactos():
    assert wilson(0, 10) == pytest.approx((0.0, 0.27753), abs=1e-4)
    lo, hi = wilson(5, 50)
    assert lo < 0.1 < hi
    assert sum(math.comb(7, i) * 0.3 ** i * 0.7 ** (7 - i) for i in range(8)) == pytest.approx(1.0)
    assert cola_binomial(0, 20, 0.5) == pytest.approx(1.0) and cola_binomial(21, 20, 0.5) == 0.0
    # los x críticos que el acta declara
    assert x_critico(97) == 4 and x_critico(51) == 3
    assert cola_binomial(4, 97, 0.01) <= 0.05 < cola_binomial(3, 97, 0.01)


def test_remuestreo_es_determinista_y_degenerado_sin_alarmas():
    datos = {"a": (1, 2), "b": (0, 2), "c": (0, 3), "d": (0, 1)}
    r1, r2 = remuestreo_por_persona(datos, n_rep=500), remuestreo_por_persona(datos, n_rep=500)
    assert r1 == r2 and r1[0] <= 1 / 8 <= r1[1] + 0.2
    assert remuestreo_por_persona({"a": (0, 3), "b": (0, 2)}, n_rep=200) == (0.0, 0.0)


def _unidad_sim(rng, sd=10.0):
    base = serie([rng.gauss(500, sd) for _ in range(14)])
    mon = [(F0 + timedelta(days=14 + i), rng.gauss(500, sd)) for i in range(14)]
    return base, mon


def test_la_inyeccion_es_determinista_y_restar_cae_en_el_sentido_caida():
    rng = random.Random(SEMILLAS_PUBLICAS[0])
    base, mon = _unidad_sim(rng)
    a = ejecutar_unidad("p-sim", Indicador.SUENO, 0.0, base, mon, delta=3.0)
    b = ejecutar_unidad("p-sim", Indicador.SUENO, 0.0, base, mon, delta=3.0)
    assert a == b and a.alarma and a.sentido == "caída" and 1 <= a.dia_de_alarma <= 14
    media = sum(v for _, v in base) / 14
    quieta = ejecutar_unidad("p-sim", Indicador.SUENO, 0.0, base, [(d, media) for d, _ in mon])
    assert quieta.alarma is False  # monitoreo = media de la base ⇒ residuo 0 ⇒ el CUSUM no sube


def test_a_mayor_cambio_inyectado_menor_latencia():
    rng = random.Random(SEMILLAS_PUBLICAS[1])
    base, mon = _unidad_sim(rng)
    r2 = ejecutar_unidad("p-sim", Indicador.SUENO, 0.0, base, mon, delta=2.0)
    r4 = ejecutar_unidad("p-sim", Indicador.SUENO, 0.0, base, mon, delta=4.0)
    assert r4.alarma and (not r2.alarma or r4.dia_de_alarma <= r2.dia_de_alarma)


def test_el_piso_del_sensor_manda_cuando_la_persona_es_muy_estable():
    rng = random.Random(SEMILLAS_PUBLICAS[2])
    base, mon = _unidad_sim(rng, sd=1.0)
    assert ejecutar_unidad("p-sim", Indicador.SUENO, 100.0, base, mon).manda_el_sensor is True
    base, mon = _unidad_sim(rng, sd=50.0)
    assert ejecutar_unidad("p-sim", Indicador.SUENO, 1.0, base, mon).manda_el_sensor is False


def test_evaluar_sobre_el_extracto_real_devuelve_la_estructura_del_acta():
    regs = [r for r in cargar(EXTRACTO).registros if r.indicador is IndicadorSensor.SUENO and r.calidad is CalidadDato.OK]
    series = {"p-real": [(r.ts_utc.date(), r.valor) for r in regs]}
    res = evaluar(series, Indicador.SUENO, sigma_de(IndicadorSensor.SUENO).sigma)
    assert res["n_unidades"] == len(regs) // BLOQUE == 3 and res["n_personas"] == 1
    assert set(res) >= {"M1", "M2", "M3", "M4"} and set(res["M3"]) == {"1.0", "1.5", "2.0", "3.0"}
    assert res["M1"]["x_critico"] == x_critico(3) and 0 <= res["M1"]["tasa"] <= 1
    assert res["M3"]["3.0"]["tasa"] >= res["M3"]["1.0"]["tasa"]  # más cambio, al menos tanta detección
    assert set(veredictos(res)) == {"H1", "H2"}


def test_las_reglas_de_veredicto_son_las_del_acta():
    base = {"M1": {"alarmas": 3, "n": 97, "x_critico": 4}, "M3": {"2.0": {"tasa": 0.9, "de": 97}}}
    assert veredictos(base) == {"H1": "NO REFUTADA", "H2": "SOSTENIDA"}
    base["M1"]["alarmas"] = 4
    base["M3"]["2.0"]["tasa"] = 0.79
    assert veredictos(base) == {"H1": "REFUTADA", "H2": "REFUTADA"}
    base["M3"]["2.0"]["tasa"] = 0.80
    assert veredictos(base)["H2"] == "SOSTENIDA"  # ≥ 80 % cuenta


def test_el_acta_fb009_esta_registrada_intacta_y_antes_de_correr_nada():
    e = exigir_preregistro(RAIZ, "FB-009", ahora=datetime.now(UTC))
    assert e.hash_sha256 == hash_acta(RAIZ / "docs" / "actas" / "FB-009.md")
    texto = (RAIZ / "docs" / "actas" / "FB-009.md").read_text(encoding="utf-8")
    assert "10,011730842174083" in texto and "82c84ee495be4b0ff636a8a44271ffb124e2358d9dd52012b529b897f3d54963" in texto


# --- FB-009: el resultado REGISTRADO (regresión permanente) --------------------------------------------
def _registro_fb009():
    lineas = (RAIZ / "docs" / "actas" / "RESULTADOS.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(l) for l in lineas if l and json.loads(l)["acta"] == "FB-009"]


COMPLETO = RAIZ / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"


def test_fb009_se_ejecuto_una_sola_vez_despues_de_registrar_el_acta_y_con_el_csv_preregistrado():
    (r,) = _registro_fb009()
    assert r["hash_acta"] == hash_acta(RAIZ / "docs" / "actas" / "FB-009.md")
    registrada = datetime.strptime(r["acta_registrada_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    ejecutada = datetime.strptime(r["ts_ejecucion_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    assert registrada < ejecutada
    assert r["csv_sha256"] in (RAIZ / "docs" / "actas" / "FB-009.md").read_text(encoding="utf-8")
    assert r["h"] == H_FB009 and r["semillas"] == [20261113, 20261114] and "no astronautas" in r["banner"].lower()


def test_fb009_el_numero_de_unidades_coincide_con_lo_que_el_acta_esperaba_y_los_veredictos_salen_de_sus_reglas():
    (r,) = _registro_fb009()
    assert (r["primario"]["n_unidades"], r["primario"]["n_personas"]) == (97, 51)  # el acta lo declaró antes de correr
    assert r["primario"]["M1"]["x_critico"] == 4
    assert veredictos(r["primario"]) == r["veredictos"] == {"H1": "NO REFUTADA", "H2": "SOSTENIDA"}


def test_fb009_la_sensibilidad_de_pulso_muestra_una_descalibracion_que_no_se_esconde():
    (r,) = _registro_fb009()
    s2 = r["S2"]["M1"]
    assert (s2["alarmas"], s2["n"]) == (7, 144) and s2["alarmas"] >= s2["x_critico"]  # 4,9 %: habría sido REFUTADA como primaria
    assert s2["wilson95"][0] > 0.01  # el 1 % nominal queda fuera del IC


@pytest.mark.skipif(not COMPLETO.exists(), reason="el dataset completo no está en este equipo")
def test_fb009_el_resultado_primario_se_reproduce_exactamente_desde_el_dataset():
    (r,) = _registro_fb009()
    por = {}
    for x in cargar(COMPLETO).registros:
        if x.indicador is IndicadorSensor.SUENO and x.calidad is CalidadDato.OK:
            por.setdefault(x.persona_id, []).append((x.ts_utc.date(), x.valor))
    de_nuevo = evaluar(por, Indicador.SUENO, sigma_de(IndicadorSensor.SUENO).sigma)
    for k in ("n_unidades", "n_personas", "M2", "M4"):
        assert de_nuevo[k] == r["primario"][k]
    assert de_nuevo["M1"]["alarmas"] == r["primario"]["M1"]["alarmas"]
    assert {d: v["detectadas"] for d, v in de_nuevo["M3"].items()} == {d: v["detectadas"] for d, v in r["primario"]["M3"].items()}


# --- FB-010 (MP-11): el resultado REGISTRADO --------------------------------------------------------------
def _registro_fb010():
    lineas = (RAIZ / "docs" / "actas" / "RESULTADOS.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(l) for l in lineas if l and json.loads(l)["acta"] == "FB-010"]


def test_fb010_se_ejecuto_una_sola_vez_tras_registrar_el_acta():
    (r,) = _registro_fb010()
    assert r["hash_acta"] == hash_acta(RAIZ / "docs" / "actas" / "FB-010.md")
    reg = datetime.strptime(r["acta_registrada_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    eje = datetime.strptime(r["ts_ejecucion_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    assert reg < eje and r["csv_sha256"] in (RAIZ / "docs" / "actas" / "FB-010.md").read_text(encoding="utf-8")


def test_fb010_los_tamanos_de_particion_son_los_que_el_acta_declaro_antes_de_correr():
    (r,) = _registro_fb010()
    fc, sueno = r["resultados"]["fc"], r["resultados"]["sueño"]
    assert (fc["prueba_base"]["n_unidades"], fc["entrenamiento_base"]["n_unidades"]) == (77, 67)
    assert (sueno["prueba_base"]["n_unidades"], sueno["entrenamiento_base"]["n_unidades"]) == (51, 46)
    assert fc["prueba_base"]["M1"]["x_critico"] == 3  # el acta lo declaró


def test_fb010_los_veredictos_salen_de_las_reglas_del_acta_y_la_prueba_no_discrimina():
    (r,) = _registro_fb010()
    pw, base = r["resultados"]["fc"]["prueba_blanqueado"], r["resultados"]["fc"]["prueba_base"]
    h1 = pw["M1"]["alarmas"] < pw["M1"]["x_critico"] and pw["M1"]["alarmas"] <= base["M1"]["alarmas"]
    h2 = pw["M3"]["2.0"]["tasa"] >= 0.80
    assert r["veredictos"] == {"H1p": "SOSTENIDA" if h1 else "REFUTADA", "H2p": "SOSTENIDA" if h2 else "REFUTADA"}
    # HECHO REGISTRADO (defecto de diseño del acta): en las personas de prueba el control sin blanquear TAMBIÉN pasó la regla,
    # y blanquear no cambió el número de falsas alarmas: esta prueba no demuestra mejora fuera de muestra.
    assert base["M1"]["alarmas"] < base["M1"]["x_critico"] and pw["M1"]["alarmas"] == base["M1"]["alarmas"]
    # coste del blanqueado en potencia a cambios pequeños (declarado)
    assert pw["M3"]["1.0"]["tasa"] < base["M3"]["1.0"]["tasa"]


def test_fb010_la_mejora_solo_se_ve_en_muestra_y_phi_viene_solo_de_entrenamiento():
    (r,) = _registro_fb010()
    fc = r["resultados"]["fc"]
    assert 0 < fc["phi_estimado_en_entrenamiento"] < 0.5
    assert fc["entrenamiento_blanqueado"]["M1"]["alarmas"] < fc["entrenamiento_base"]["M1"]["alarmas"]  # 5 → 2 (en muestra: sugestivo, no evidencia)


@pytest.mark.skipif(not COMPLETO.exists(), reason="el dataset completo no está en este equipo")
def test_fb010_el_resultado_de_pulso_se_reproduce_exactamente():
    from src.motor.evaluacion import estimar_phi, particion
    (r,) = _registro_fb010()
    por = {}
    for x in cargar(COMPLETO).registros:
        if x.indicador is IndicadorSensor.FC and x.calidad is CalidadDato.OK:
            por.setdefault(x.persona_id, []).append((x.ts_utc.date(), x.valor))
    entrena = {p for p in por if particion(p) == "entrenamiento"}
    prueba = {p for p in por if particion(p) == "prueba"}
    phi = estimar_phi(por, filtro_personas=lambda p: p in entrena)
    assert phi == pytest.approx(r["resultados"]["fc"]["phi_estimado_en_entrenamiento"])
    nuevo = evaluar(por, Indicador.FC, sigma_de(IndicadorSensor.FC).sigma, personas=prueba, phi=phi)
    assert nuevo["M1"]["alarmas"] == r["resultados"]["fc"]["prueba_blanqueado"]["M1"]["alarmas"]
