"""M0.14 · clasificación de alertas oficiales de SWPC → DC-03 tormenta_solar, con el archivo REAL archivado."""
import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.contratos.comunes import Banner
from src.contratos.dc03_eventos import TipoEvento
from src.ingesta.swpc import AlertaSwpc, alerta_a_evento, alertas_a_registros

ARCHIVO = Path(__file__).resolve().parent.parent / "data" / "lecturas" / "swpc_alertas_20261115T051917Z.json"
CRUDO = ARCHIVO.read_bytes()
H = hashlib.sha256(CRUDO).hexdigest()
ALERTAS, _ = alertas_a_registros(json.loads(CRUDO))


def test_solo_alert_kp_5_o_mas_es_tormenta():
    eventos = [(a, alerta_a_evento(a, H)) for a in ALERTAS]
    tormentas = [e for _, e in eventos if e is not None]
    assert tormentas, "el archivo real contiene alertas K05A/K06A observadas"
    assert {a.product_id for a, e in eventos if e} == {"K05A", "K06A"}
    assert all(e.tipo is TipoEvento.TORMENTA_SOLAR and e.banner is Banner.REAL and e.parametros["kp"] >= 5 for e in tormentas)


def test_avisos_electrones_radio_y_k04_no_son_tormenta():
    nulos = {a.product_id for a in ALERTAS if alerta_a_evento(a, H) is None}
    assert {"K05W", "K06W", "K04A", "K04W", "A20F", "EF3A", "TIIA", "TIVA", "BHIS"} <= nulos


def test_umbral_alcanzado_es_el_inicio():
    a = next(x for x in ALERTAS if x.product_id == "K05A" and "Threshold Reached: 2026 Nov 08 0203 UTC" in x.mensaje)
    e = alerta_a_evento(a, H)
    assert e.ts_utc_inicio == datetime(2026, 11, 8, 2, 3, tzinfo=UTC) and e.parametros == {"kp": 5.0}


def test_escala_g_inconsistente_se_rechaza_no_se_adivina():
    base = next(x for x in ALERTAS if x.product_id == "K05A")
    malo = AlertaSwpc(base.product_id, base.emitida_utc, base.mensaje.replace("Noaa Scale: G1", "Noaa Scale: G3"))
    with pytest.raises(ValueError, match="escala G"):
        alerta_a_evento(malo, H)
