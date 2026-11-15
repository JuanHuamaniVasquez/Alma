"""M2.19 · API de lectura de la vitrina: Fundición, actas, demo kill, tormenta. Lee los archivos reales del repo (sin datos inventados)."""
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from rest_framework.test import APIClient

from apps.ingesta.models import EventoClimaEspacial

RAIZ = Path(__file__).resolve().parent.parent
H = "e" * 64


def get(url):
    return APIClient().get(url)


def test_fundicion_expone_tablero_tarjetas_detector_y_faro():
    r = get("/api/fundicion/")
    assert r.status_code == 200
    d = r.json()
    assert d["tablero"]["nacidas"] == len(d["tarjetas"]) == 5
    assert d["tablero"]["detectores_nuevos"] == len(d["detectores"]) == 1
    assert all(t["senal_refutadora"] and t["fuentes"] for t in d["tarjetas"])  # sin fuente o sin señal refutadora no existe
    assert len(d["faro"]) == 1
    assert all(t["en"] and t["en"]["refuter"] for t in d["tarjetas"]) and d["detectores"][0]["en"] and d["faro"][0]["en"]  # nada sin su versión en inglés


def test_actas_publica_refutadas_y_hash_de_cada_una():
    d = get("/api/actas/").json()["actas"]
    assert len(d) == len(open(RAIZ / "docs/actas/INDEX.jsonl").read().splitlines())
    assert all(len(a["hash_sha256"]) == 64 for a in d)
    assert any(a["ejecutada"] for a in d) and any(not a["ejecutada"] for a in d)


def test_demo_kill_dos_columnas_y_hash_antes_de_correr():
    d = get("/api/demo-kill/").json()
    assert d["acta_registrada_utc"] < d["ts_ejecucion_utc"]          # el hash precede a la ejecución
    assert d["fuga"]["A_manifiesto"]["alarma"] is False                # ciego
    assert d["fuga"]["B_ley"]["veredicto"] == "NO CIERRA"             # alarma
    assert d["control"]["B_ley"]["veredicto"] == "CIERRA"             # el control puede fallar y no falla
    assert "SIMULADO" in d["banner"]


@pytest.mark.django_db
def test_tormenta_hereda_banner_simulado():
    t = datetime(2026, 11, 15, 12, tzinfo=UTC)
    base = dict(ts_utc_inicio=t, ts_utc_fin=t, tipo="lectura_clima_espacial", parametros={"kp": 3.33}, hash_lectura_cruda=H)
    EventoClimaEspacial.objects.create(evento_id="e1", fuente="swpc", banner="REAL", **base)
    assert get("/api/tormenta/").json()["banner"] == "REAL"
    EventoClimaEspacial.objects.create(evento_id="e2", fuente="simulador", banner="SIMULADO", **base)
    d = get("/api/tormenta/").json()
    assert d["banner"] == "SIMULADO" and len(d["eventos"]) == 2
    assert len(get("/api/tormenta/?tipo=otro").json()["eventos"]) == 0


def test_solo_lectura():
    for u in ("fundicion", "actas", "demo-kill", "tormenta"):
        assert APIClient().post(f"/api/{u}/", {}).status_code == 405


@pytest.mark.django_db
def test_sembrar_demo_es_simulado_reproducible_y_la_fuga_abre_solo_el_aire_del_dia_11():
    from django.core.management import call_command
    call_command("sembrar_demo")
    call_command("sembrar_demo")                                       # idempotente (solo-anexar)
    d = get("/api/libro/dias/").json()
    assert d["dias"] == list(range(1, 15)) and d["ultimo"] == 14 and d["banner"] == "SIMULADO"
    dia11, dia3 = get("/api/libro/dia/11/").json(), get("/api/libro/dia/3/").json()
    assert dia11["presupuestos"]["aire"]["cierra"] is False and dia11["presupuestos"]["agua"]["cierra"] is True
    assert dia3["cierra"] is True and set(dia3["presupuestos"]) == {"aire", "agua"}   # los otros 7 no existen: ausencia = dato


@pytest.mark.django_db
def test_libro_vacio_no_inventa_dias():
    d = get("/api/libro/dias/").json()
    assert d["dias"] == [] and d["ultimo"] is None


@pytest.mark.django_db
def test_sembrar_demo_siembra_el_residuo_dc06_y_la_fuga_es_la_unica_sorpresa():
    from django.core.management import call_command
    call_command("sembrar_demo")
    call_command("sembrar_demo")
    d = get("/api/residuo/").json()
    assert d["banner"] == "SIMULADO" and len(d["habitat"]) == 28
    sorpresas = [r for r in d["habitat"] if r["bandera"] != "normal"]
    assert [(r["presupuesto_id"], r["ts_utc"][:10]) for r in sorpresas] == [("aire", "2026-11-12")]   # día 11 = 2 nov + 10 días
    from src.superficies import narrador
    texto = narrador.residuo(d).texto
    assert "air on 2026-11-12" in texto and "not an alarm" in texto


def test_narrador_residuo_sin_datos_dice_la_ausencia():
    from src.superficies import narrador
    assert "absence" in narrador.residuo({"banner": "REAL", "habitat": []}).texto
