"""M0.4 · IN-3: loader de SWPC (Kp, rayos X, alertas) con fixtures REALES archivados en data/lecturas/.

Los casos de fallo (404, red caída, vacío, JSON roto) y las filas sin valor son entradas
construidas a propósito (registro X-01 de docs/politica-de-datos.md): no son datos de salud.
"""
import json
import shutil
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.contratos import SEMILLAS_PUBLICAS, Banner
from src.contratos.dc03_eventos import DC03Evento
from src.ingesta.archivo import archivar, sha256_hex
from src.ingesta.cliente import FEEDS, Respuesta, ingestar
from src.ingesta.compuerta import RegistroRechazado, admitir, cargar_ficha_os892
from src.ingesta.swpc import alertas_a_registros, kp_a_eventos, normalizar_tabla

RAIZ = Path(__file__).resolve().parent.parent
AHORA = datetime(2026, 11, 15, 12, 0, 0, tzinfo=UTC)


def _real(nombre: str) -> bytes:
    """Última respuesta cruda REAL de ese feed, tal como la archivó el loader en vivo."""
    lineas = [json.loads(l) for l in (RAIZ / "data" / "lecturas" / "manifiesto.jsonl").read_text(encoding="utf-8").splitlines() if l]
    e = [x for x in lineas if x["fuente"] == "swpc" and f"_{nombre}_" in x["archivo"]][-1]
    cuerpo = (RAIZ / "data" / "lecturas" / e["archivo"]).read_bytes()
    assert sha256_hex(cuerpo) == e["hash_sha256"]  # el fixture es exactamente lo que llegó
    return cuerpo


def servir(cuerpo: bytes):
    return lambda url: Respuesta(200, cuerpo)


# --- lecturas reales ------------------------------------------------------------------------
def test_kp_real_entra_con_banner_real_y_hash(tmp_path):
    cuerpo = _real("kp")
    r = ingestar(FEEDS["kp"], fetch=servir(cuerpo), ahora=AHORA, raiz=tmp_path)
    assert r.intento.resultado.value == "ok" and r.intento.banner is Banner.REAL
    assert r.intento.hash_lectura_cruda == sha256_hex(cuerpo)
    assert len(r.eventos) == r.filas > 50 and r.omitidas == 0
    assert all(e.banner is Banner.REAL and e.tipo.value == "lectura_clima_espacial" for e in r.eventos)
    assert all(e.hash_lectura_cruda == r.intento.hash_lectura_cruda for e in r.eventos)
    assert all(0 <= e.parametros["kp"] <= 9 for e in r.eventos)
    assert r.archivo.read_bytes() == cuerpo  # MP-3: el crudo queda archivado tal cual


def test_xrays_reales(tmp_path):
    r = ingestar(FEEDS["xrays"], fetch=servir(_real("xrays")), ahora=AHORA, raiz=tmp_path)
    assert r.intento.resultado.value == "ok" and len(r.eventos) > 2000
    assert all(e.parametros["flujo_x_w_m2"] > 0 for e in r.eventos)
    assert len({e.evento_id for e in r.eventos}) == len(r.eventos)  # ids únicos (satélite+banda+tiempo)


def test_alertas_reales_se_archivan_sin_clasificar(tmp_path):
    cuerpo = _real("alertas")
    r = ingestar(FEEDS["alertas"], fetch=servir(cuerpo), ahora=AHORA, raiz=tmp_path)
    assert r.intento.resultado.value == "ok" and r.eventos == () and r.filas > 0
    alertas, omitidas = alertas_a_registros(normalizar_tabla(json.loads(cuerpo)))
    assert omitidas == 0 and all(a.emitida_utc.tzinfo is not None and a.mensaje for a in alertas)


def test_archivo_es_solo_anexar_y_deja_manifiesto(tmp_path):
    ingestar(FEEDS["kp"], fetch=servir(_real("kp")), ahora=AHORA, raiz=tmp_path)
    linea = json.loads((tmp_path / "data" / "lecturas" / "manifiesto.jsonl").read_text().splitlines()[-1])
    assert linea["fuente"] == "swpc" and linea["banner"] == "REAL" and len(linea["hash_sha256"]) == 64
    with pytest.raises(FileExistsError):  # archivar nunca reescribe un archivo existente
        archivar(b"otro contenido", fuente="swpc", nombre="kp", url="https://x.test", ts=AHORA, raiz=tmp_path)


# --- el fallo del feed es dato (DC-13) -----------------------------------------------------
@pytest.mark.parametrize("resp, resultado, status", [
    (Respuesta(404, b"", "HTTP 404"), "fallo", 404),
    (Respuesta(None, b"", "URLError: sin red"), "fallo", None),
    (Respuesta(200, b"<html>no json</html>"), "fallo", 200),
    (Respuesta(200, b"[]"), "vacio", 200),
])
def test_un_feed_caido_o_vacio_se_registra_y_nunca_se_rellena(tmp_path, resp, resultado, status):
    r = ingestar(FEEDS["kp"], fetch=lambda u: resp, ahora=AHORA, raiz=tmp_path)
    assert r.intento.resultado.value == resultado and r.intento.http_status == status
    assert r.eventos == () and r.archivo is None
    assert r.intento.hash_lectura_cruda is None
    assert not (tmp_path / "data" / "lecturas").exists()  # sin lectura no hay archivo


# --- formatos y filas sin valor --------------------------------------------------------------
def test_acepta_lista_de_listas_con_encabezado():
    tabla = [["time_tag", "Kp", "a_running", "station_count"], ["2026-11-15T00:00:00", "2.00", "7", "8"]]
    assert normalizar_tabla(tabla) == [{"time_tag": "2026-11-15T00:00:00", "Kp": "2.00", "a_running": "7", "station_count": "8"}]
    eventos, omitidas = kp_a_eventos(normalizar_tabla(tabla), "a" * 64)
    assert omitidas == 0 and eventos[0].parametros == {"kp": 2.0}


def test_fila_sin_valor_se_omite_y_se_cuenta_no_se_inventa():
    filas = [{"time_tag": "2026-11-15T00:00:00", "Kp": None}, {"time_tag": "2026-11-15T03:00:00", "Kp": 3.0}]
    eventos, omitidas = kp_a_eventos(filas, "a" * 64)
    assert omitidas == 1 and [e.parametros["kp"] for e in eventos] == [3.0]


def test_feed_que_no_es_lista_no_se_interpreta():
    with pytest.raises(ValueError):
        normalizar_tabla({"no": "lista"})


# --- la compuerta: los 3 casos negativos de TASKS.md M0.4 -----------------------------------
def _registro(**cambios):
    base = dict(evento_id="swpc-kp-x", ts_utc_inicio="2026-11-15T00:00:00Z", ts_utc_fin="2026-11-15T00:00:00Z",
                tipo="lectura_clima_espacial", fuente="swpc", parametros={"kp": 2.0},
                hash_lectura_cruda="a" * 64, banner="REAL")
    return {**base, **cambios}


def test_compuerta_rechaza_registro_sin_banner():
    datos = _registro(); del datos["banner"]
    with pytest.raises(RegistroRechazado, match="banner"):
        admitir(datos)


def test_compuerta_rechaza_registro_sin_fuente_con_id():
    datos = _registro(); del datos["fuente"]
    with pytest.raises(RegistroRechazado, match="fuente"):
        admitir(datos)
    with pytest.raises(RegistroRechazado):
        admitir(_registro(hash_lectura_cruda="no-es-un-hash"))


def test_compuerta_rechaza_simulado_sin_semilla_publica():
    sim = _registro(tipo="inyeccion_escenario", fuente="simulador", banner="SIMULADO")
    with pytest.raises(RegistroRechazado, match="semilla"):
        admitir(sim)
    with pytest.raises(RegistroRechazado, match="semilla"):
        admitir(sim, semilla=12345)  # no es una semilla pública del proyecto


def test_compuerta_acepta_lo_valido():
    assert isinstance(admitir(_registro()), DC03Evento)
    sim = _registro(tipo="inyeccion_escenario", fuente="simulador", banner="SIMULADO")
    assert admitir(sim, semilla=SEMILLAS_PUBLICAS[0]).banner is Banner.SIMULADO


# --- ficha de verdad OS-892 (fixture real) ---------------------------------------------------
def test_ficha_os892_real_se_carga():
    ficha = cargar_ficha_os892(RAIZ)
    assert ficha["id"] == "OS-892" and ficha["banner"] == "REAL" and ficha["archivos_publicos"] == 0


def test_ficha_os892_se_rechaza_si_su_lectura_cruda_no_cuadra(tmp_path):
    shutil.copytree(RAIZ / "data", tmp_path / "data")
    ficha = json.loads((tmp_path / "data" / "OS-892-extracto.json").read_text(encoding="utf-8"))
    (tmp_path / ficha["respuesta_cruda"]).write_bytes(b"{}")  # crudo alterado
    with pytest.raises(RegistroRechazado, match="hash"):
        cargar_ficha_os892(tmp_path)


def test_la_misma_lectura_no_se_archiva_dos_veces(tmp_path):
    cuerpo = _real("kp")
    a = ingestar(FEEDS["kp"], fetch=servir(cuerpo), ahora=AHORA, raiz=tmp_path)
    b = ingestar(FEEDS["kp"], fetch=servir(cuerpo), ahora=AHORA.replace(hour=15), raiz=tmp_path)
    assert b.archivo == a.archivo and b.intento.hash_lectura_cruda == a.intento.hash_lectura_cruda
    assert len(list((tmp_path / "data" / "lecturas").glob("swpc_kp_*.json"))) == 1  # sin duplicar
    assert len((tmp_path / "data" / "lecturas" / "manifiesto.jsonl").read_text().splitlines()) == 1
