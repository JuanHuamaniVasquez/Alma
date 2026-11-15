"""M0.13 · Persistencia de DC-03 y DC-13 en PostgreSQL (BD real), con lecturas SWPC REALES archivadas.

Los registros inválidos que se intentan escribir a mano son construidos (X-01).
"""
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from django.db import IntegrityError, transaction

from apps.ingesta.models import EventoClimaEspacial, IntentoIngesta
from apps.ingesta.repositorio import a_dominio_evento, a_dominio_intento, guardar_eventos, guardar_intento, guardar_resultado
from src.ingesta.archivo import sha256_hex
from src.ingesta.cliente import FEEDS, Respuesta, ingestar

RAIZ = Path(__file__).resolve().parent.parent
AHORA = datetime(2026, 11, 15, 12, 0, tzinfo=UTC)


def _kp_real() -> bytes:
    lineas = [json.loads(l) for l in (RAIZ / "data" / "lecturas" / "manifiesto.jsonl").read_text(encoding="utf-8").splitlines() if l]
    e = [x for x in lineas if x["fuente"] == "swpc" and "_kp_" in x["archivo"]][-1]
    return (RAIZ / "data" / "lecturas" / e["archivo"]).read_bytes()


@pytest.fixture
def resultado_kp(tmp_path):
    return ingestar(FEEDS["kp"], fetch=lambda u: Respuesta(200, _kp_real()), ahora=AHORA, raiz=tmp_path)


@pytest.mark.django_db
def test_ida_y_vuelta_de_dc03_conserva_el_hash_del_crudo(resultado_kp):
    nuevos, intento = guardar_resultado(resultado_kp)
    assert nuevos == len(resultado_kp.eventos) > 50
    fila = EventoClimaEspacial.objects.order_by("-ts_utc_inicio").first()
    ev = a_dominio_evento(fila)  # se re-valida con el contrato al leer
    assert ev.parametros == {"kp": fila.parametros["kp"]} and ev.banner.value == "REAL"
    assert ev.hash_lectura_cruda == sha256_hex(_kp_real()) == intento.hash_lectura_cruda


@pytest.mark.django_db
def test_la_ingesta_es_idempotente(resultado_kp):
    guardar_eventos(resultado_kp.eventos)
    assert guardar_eventos(resultado_kp.eventos) == 0  # el mismo feed otra vez no duplica
    assert EventoClimaEspacial.objects.count() == len(resultado_kp.eventos)


@pytest.mark.django_db
def test_un_intento_fallido_tambien_se_guarda(tmp_path):
    r = ingestar(FEEDS["kp"], fetch=lambda u: Respuesta(404, b"", "HTTP 404"), ahora=AHORA, raiz=tmp_path)
    nuevos, intento = guardar_resultado(r)
    assert nuevos == 0
    di = a_dominio_intento(IntentoIngesta.objects.get(pk=intento.pk))
    assert di.resultado.value == "fallo" and di.http_status == 404 and di.error and di.hash_lectura_cruda is None


@pytest.mark.django_db
def test_intento_ok_se_guarda_con_su_hash(resultado_kp):
    guardar_intento(resultado_kp.intento)
    di = a_dominio_intento(IntentoIngesta.objects.get())
    assert di.resultado.value == "ok" and di.hash_lectura_cruda == sha256_hex(_kp_real())


# --- la BD también hace cumplir los contratos (aunque se escriba directo) -----------------------
@pytest.mark.django_db
@pytest.mark.parametrize("campos", [
    dict(resultado="ok", hash_lectura_cruda=None, error=None),          # ok sin hash
    dict(resultado="ok", hash_lectura_cruda="a" * 64, error="boom"),    # ok con error
    dict(resultado="fallo", hash_lectura_cruda="a" * 64, error="x"),    # fallo con hash
    dict(resultado="fallo", hash_lectura_cruda=None, error=None),       # fallo sin error
    dict(resultado="vacio", hash_lectura_cruda="a" * 64, error=None),   # vacío con hash
])
def test_bd_rechaza_intentos_incoherentes(campos):
    base = dict(intento_id="x", ts_utc=AHORA, fuente="swpc", url="https://x.test", http_status=200, banner="REAL")
    with pytest.raises(IntegrityError), transaction.atomic():
        IntentoIngesta.objects.create(**{**base, **campos})


@pytest.mark.django_db
def test_bd_rechaza_banner_incoherente_con_la_fuente_y_fin_antes_de_inicio():
    base = dict(evento_id="e1", ts_utc_inicio=AHORA, ts_utc_fin=AHORA, tipo="lectura_clima_espacial",
                fuente="swpc", parametros={"kp": 2.0}, hash_lectura_cruda="a" * 64, banner="REAL")
    with pytest.raises(IntegrityError), transaction.atomic():
        EventoClimaEspacial.objects.create(**{**base, "banner": "SIMULADO"})  # fuente real ⇒ REAL
    with pytest.raises(IntegrityError), transaction.atomic():
        EventoClimaEspacial.objects.create(**{**base, "evento_id": "e2", "ts_utc_fin": datetime(2026, 11, 14, tzinfo=UTC)})
    with pytest.raises(IntegrityError), transaction.atomic():
        EventoClimaEspacial.objects.create(**{**base, "evento_id": "e3", "hash_lectura_cruda": ""})
