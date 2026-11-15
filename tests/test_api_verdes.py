"""M2.10 · persistencia y API de DC-14. Registros ESTRUCTURALES (X-01) con valores distintivos para probar la privacidad."""
from datetime import UTC, datetime

import pytest
from django.db import IntegrityError, transaction
from rest_framework.test import APIClient

from apps.motor.models import ReciboVerde
from apps.motor.repositorio import guardar_recibo_verde
from src.contratos import CONTRATOS

T = datetime(2026, 11, 15, 12, 0, tzinfo=UTC)
H = "d" * 64
SECRETO = 4242.4242


def dc14(sujeto="astro-01", **kw):
    base = dict(recibo_id=f"rv-{sujeto}-{kw.get('indicador', 'x')}", ts_utc=T, sujeto=sujeto, indicador="sueño", estado="verde",
                ventana_dias=14, dias_validos=14, detector="cusum", k=0.5, h=10.0117, potencia_declarada=0.9, mde_sigma=1.75,
                mde_fisico=SECRETO, unidad="min", supuesto="ruido independiente; tabla simulada", regla_exacta="CUSUM_BILATERAL k=0.5 ...",
                semilla=20261113, hash_preregistro=H, banner="SIMULADO")
    return CONTRATOS["DC-14"].model_validate({**base, **kw})


@pytest.mark.django_db
def test_ida_y_vuelta_de_un_recibo_de_verde():
    guardar_recibo_verde(dc14())
    f = ReciboVerde.objects.get()
    assert CONTRATOS["DC-14"].model_validate(dict(
        recibo_id=f.recibo_id, ts_utc=f.ts_utc, sujeto=f.sujeto, indicador=f.indicador, estado=f.estado, ventana_dias=f.ventana_dias,
        dias_validos=f.dias_validos, detector=f.detector, k=f.k, h=f.h, potencia_declarada=f.potencia_declarada, mde_sigma=f.mde_sigma,
        mde_fisico=f.mde_fisico, unidad=f.unidad, supuesto=f.supuesto, regla_exacta=f.regla_exacta, semilla=f.semilla,
        hash_preregistro=f.hash_preregistro, banner=f.banner)).mde_sigma == 1.75


@pytest.mark.django_db
def test_la_bd_hace_cumplir_el_contrato_aunque_se_escriba_directo():
    base = dict(recibo_id="x", ts_utc=T, sujeto="p-1", indicador="fc", estado="verde", ventana_dias=14, dias_validos=14, detector="cusum",
                k=0.5, h=10.0, potencia_declarada=0.9, mde_sigma=1.75, mde_fisico=9.3, unidad="lpm", supuesto="s", regla_exacta="r",
                semilla=1, hash_preregistro=H, banner="REAL")
    for malo in (dict(potencia_declarada=None), dict(estado="sin_datos_suficientes"), dict(dias_validos=15),
                 dict(presupuesto_id="ritmo"), dict(indicador=None), dict(hash_preregistro="no-es-sha")):
        with pytest.raises(IntegrityError), transaction.atomic():
            ReciboVerde.objects.create(**{**base, **malo})
    ReciboVerde.objects.create(**{**base, "estado": "sin_datos_suficientes", "potencia_declarada": None, "mde_sigma": None, "mde_fisico": None})


@pytest.mark.django_db
def test_la_api_da_detalle_del_habitat_y_solo_agregados_del_cuerpo_sin_ids_ni_valores_fisicos():
    guardar_recibo_verde(dc14("habitat", indicador=None, presupuesto_id="agua", mde_fisico=7.5))
    guardar_recibo_verde(dc14("astro-01", indicador="sueño"))
    guardar_recibo_verde(dc14("astro-02", indicador="fc", estado="sin_datos_suficientes", dias_validos=4,
                              potencia_declarada=None, mde_sigma=None, mde_fisico=None))
    r = APIClient().get("/api/verdes/")
    t, j = r.content.decode("utf-8"), r.json()
    assert r.status_code == 200 and j["banner"] == "SIMULADO"
    assert [h["presupuesto_id"] for h in j["habitat"]] == ["agua"] and j["habitat"][0]["mde_fisico"] == 7.5 and j["habitat"][0]["hash_preregistro"] == H
    assert j["cuerpo_agregado"]["recibos"] == 2 and j["cuerpo_agregado"]["por_estado"] == {"verde": 1, "sin_datos_suficientes": 1}
    assert j["cuerpo_agregado"]["cobertura_media"] == pytest.approx((1.0 + 4 / 14) / 2)
    for prohibido in ("astro-01", "astro-02", "4242"):
        assert prohibido not in t, f"{prohibido} se coló en la respuesta"
    for metodo in ("post", "put", "patch", "delete"):
        assert getattr(APIClient(), metodo)("/api/verdes/", {}, format="json").status_code == 405
