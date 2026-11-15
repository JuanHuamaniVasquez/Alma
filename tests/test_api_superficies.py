"""M1.3 · API REST de solo lectura (DC-04/05/06/08) contra la BD real.

Los registros son ESTRUCTURALES y SIMULADOS (X-01): valores distintivos (4242.4242, ids «astro-…») para
poder demostrar que el contenido individual jamás aparece en una respuesta.
"""
from datetime import UTC, datetime

import pytest
from rest_framework.test import APIClient

from apps.libro.repositorio import guardar_linea
from apps.motor.repositorio import guardar_alarma, guardar_cierre, guardar_residuo
from src.contratos import CONTRATOS, Banner
from src.motor.contrapeso import Corriente, cierre_de_conservacion
from src.contratos.dc05_alarma import EstadoAlarma
from src.contratos.dc08_conservacion import Bucle

SIM, REAL = Banner.SIMULADO, Banner.REAL
H = "a" * 64
T = datetime(2026, 11, 15, 12, 0, tzinfo=UTC)
PERSONAS = ("astro-01", "astro-02")
VALOR_SECRETO = 4242.4242


def linea(pres, sujeto, esperada, observada, sigma=0.2, estado="limpio"):
    return CONTRATOS["DC-04"].model_validate(dict(
        dia_habitat=3, presupuesto_id=pres, sujeto=sujeto, emision_esperada=esperada, incertidumbre_del_manifiesto=sigma,
        emision_observada=observada, residuo_contable=observada - esperada, fuente_linea="DC-03:ev-1", estado_linea=estado))


@pytest.fixture
def datos(db):
    guardar_linea(linea("aire", "habitat", 10.0, 10.1), SIM)
    guardar_linea(linea("agua", "habitat", 10.0, 12.0), SIM)                          # abierta: |2.0| > 0.4
    guardar_linea(linea("ritmo", PERSONAS[0], VALOR_SECRETO, VALOR_SECRETO + 0.05), SIM)  # cierra
    guardar_linea(linea("ritmo", PERSONAS[1], VALOR_SECRETO, VALOR_SECRETO + 5.0), SIM)   # abierta
    a = CONTRATOS["DC-05"].model_validate(dict(
        alarma_id="al-1", ts_utc=T, presupuesto_id="agua", detector="cusum", sentido="alza", umbral=5.0, valor_cruzado=5.4,
        regla_exacta="cusum_bilateral(h=5.0) cruza al alza", semilla=20261113, hash_preregistro=H, estado="activa"))
    guardar_alarma(a, SIM)
    guardar_alarma(a.model_copy(update={"alarma_id": "al-2", "estado": EstadoAlarma.RETIRADA}), SIM)
    r = lambda sujeto, **kw: CONTRATOS["DC-06"].model_validate(dict(  # noqa: E731
        sujeto=sujeto, ts_utc=T, observado=VALOR_SECRETO, predicho=VALOR_SECRETO - 1.0, residuo=1.0, sigma_efectiva=0.5,
        cusum_acumulado=2.0, bandera="sorpresa", **kw))
    guardar_residuo(r("habitat", presupuesto_id="aire"), SIM)
    guardar_residuo(r(PERSONAS[0], indicador="sueño"), SIM)
    guardar_residuo(r(PERSONAS[1], indicador="fc"), SIM)
    ok = Corriente("x", 1.0, 0.1, SIM)
    cero = Corriente("0", 0.0, 0.0, SIM)
    guardar_cierre(cierre_de_conservacion(dia_habitat=3, bucle=Bucle.AIRE, entradas=[Corriente("in", 1.5, 0.1, SIM)],
                                          salidas=[ok], delta_almacen=cero, perdida_declarada=cero))
    return APIClient()


def texto(resp) -> str:
    return resp.content.decode("utf-8")


def sin_individuales(resp):
    t = texto(resp)
    for p in PERSONAS:
        assert p not in t, f"el id {p} se coló en la respuesta"
    assert "4242" not in t, "un valor individual se coló en la respuesta"


@pytest.mark.django_db
def test_libro_del_dia_resume_por_presupuesto_y_nunca_expone_al_individuo(datos):
    r = datos.get("/api/libro/dia/3/")
    assert r.status_code == 200 and r["Content-Type"].startswith("application/json")
    j = r.json()
    assert j["banner"] == "SIMULADO" and j["dia_habitat"] == 3 and j["cierra"] is False
    assert j["presupuestos"]["aire"] == {"lineas": 1, "abiertas": 0, "cierra": True}
    assert j["presupuestos"]["agua"]["cierra"] is False and j["presupuestos"]["ritmo"]["abiertas"] == 1
    assert {l["presupuesto_id"] for l in j["habitat"]} == {"aire", "agua"}  # el hábitat sí va en detalle
    assert j["cuerpo_agregado"] == {"personas": 2, "con_linea_abierta": 1}   # el cuerpo, solo agregado
    sin_individuales(r)


@pytest.mark.django_db
def test_dia_sin_libro_es_404_no_un_cierre_inventado(datos):
    assert datos.get("/api/libro/dia/99/").status_code == 404
    assert datos.get("/api/cierres/dia/99/").status_code == 404


@pytest.mark.django_db
def test_alarmas_llevan_su_recibo_completo_y_se_filtran_por_estado(datos):
    j = datos.get("/api/alarmas/?estado=activa").json()
    assert j["banner"] == "SIMULADO" and [a["alarma_id"] for a in j["alarmas"]] == ["al-1"]
    a = j["alarmas"][0]
    assert a["regla_exacta"] and a["semilla"] == 20261113 and a["hash_preregistro"] == H and a["banner"] == "SIMULADO"
    assert len(datos.get("/api/alarmas/").json()["alarmas"]) == 2


@pytest.mark.django_db
def test_residuo_da_detalle_del_habitat_y_solo_conteos_del_cuerpo(datos):
    r = datos.get("/api/residuo/")
    j = r.json()
    assert j["banner"] == "SIMULADO" and len(j["habitat"]) == 1 and j["habitat"][0]["presupuesto_id"] == "aire"
    assert j["cuerpo_agregado"] == {"registros": 2, "por_bandera": {"sorpresa": 2}}
    t = texto(r)
    for p in PERSONAS:
        assert p not in t
    assert "sueño" not in t and '"fc"' not in t  # ni siquiera qué indicador de qué persona


@pytest.mark.django_db
def test_cierres_del_dia_con_veredicto_y_banner(datos):
    j = datos.get("/api/cierres/dia/3/").json()
    assert j["banner"] == "SIMULADO" and j["cierres"][0]["bucle"] == "aire" and j["cierres"][0]["veredicto"] == "NO CIERRA"


@pytest.mark.django_db
@pytest.mark.parametrize("url", ["/api/libro/dia/3/", "/api/alarmas/", "/api/residuo/", "/api/cierres/dia/3/"])
def test_toda_respuesta_lleva_banner_y_solo_se_puede_leer(datos, url):
    assert "banner" in datos.get(url).json()
    for metodo in ("post", "put", "patch", "delete"):
        assert getattr(datos, metodo)(url, {}, format="json").status_code == 405


@pytest.mark.django_db
def test_una_sola_fila_simulada_hace_simulada_toda_la_respuesta(db):
    guardar_linea(linea("aire", "habitat", 10.0, 10.1), REAL)
    guardar_linea(linea("agua", "habitat", 10.0, 10.1), SIM)
    assert APIClient().get("/api/libro/dia/3/").json()["banner"] == "SIMULADO"  # jamás REAL en silencio


@pytest.mark.django_db
def test_la_base_rechaza_una_alarma_sin_regla_y_dos_lineas_iguales(datos):
    from django.db import IntegrityError, transaction

    from apps.motor.models import Alarma
    with pytest.raises(IntegrityError), transaction.atomic():
        Alarma.objects.create(alarma_id="x", ts_utc=T, presupuesto_id="aire", detector="cusum", sentido="alza", umbral=1.0,
                              valor_cruzado=2.0, regla_exacta="", semilla=1, hash_preregistro=H, estado="activa", banner="SIMULADO")
    with pytest.raises(IntegrityError), transaction.atomic():
        guardar_linea(linea("aire", "habitat", 10.0, 10.1), SIM)  # el libro es solo-anexar


@pytest.mark.django_db
def test_una_alarma_por_indicador_sin_presupuesto_inventado_sale_con_recibo_y_la_bd_exige_uno_solo(datos):
    from django.db import IntegrityError, transaction

    from apps.motor.models import Alarma
    a = CONTRATOS["DC-05"].model_validate(dict(
        alarma_id="al-fc", ts_utc=T, indicador="fc", detector="cusum", sentido="alza", umbral=10.0, valor_cruzado=10.4,
        regla_exacta="CUSUM_BILATERAL k=0.5 h=10.0 mu=70.0 sigma=5.0 :: ...", semilla=20261113, hash_preregistro=H, estado="activa"))
    guardar_alarma(a, SIM)
    por_ind = [x for x in datos.get("/api/alarmas/").json()["alarmas"] if x["alarma_id"] == "al-fc"][0]
    assert por_ind["indicador"] == "fc" and por_ind["presupuesto_id"] is None and por_ind["regla_exacta"] and por_ind["hash_preregistro"] == H
    base = dict(alarma_id="x", ts_utc=T, detector="cusum", sentido="alza", umbral=1.0, valor_cruzado=2.0, regla_exacta="r",
                semilla=1, hash_preregistro=H, estado="activa", banner="SIMULADO")
    with pytest.raises(IntegrityError), transaction.atomic():
        Alarma.objects.create(**base)                                           # ninguno
    with pytest.raises(IntegrityError), transaction.atomic():
        Alarma.objects.create(**{**base, "presupuesto_id": "aire", "indicador": "fc"})  # los dos
