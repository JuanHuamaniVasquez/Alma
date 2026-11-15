"""M8.7 · DOC-01 v0.2.9: el entorno en vivo entra como DC-03 (con hash de lectura cruda) y los fallos como DC-13; las reglas de coherencia nuevas se aplican."""
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.contratos.comunes import Banner
from src.contratos.dc03_eventos import DC03Evento, FuenteEvento, TipoEvento
from src.contratos.dc05_alarma import DC05Alarma, Detector
from src.ingesta import entorno as E
from src.motor.eproceso import regla_exacta

F = Path(__file__).resolve().parent / "fixtures" / "entorno"
H = "a" * 64


def _env():
    E.ULTIMOS_HASHES.update({E.URL_ISS: "1" * 64, E.URL_PROT: "2" * 64, E.URL_XR: "3" * 64})
    E.ARCHIVADOS_NUEVOS.update({E.URL_ISS, E.URL_PROT, E.URL_XR})
    return {"iss": E.iss(json.loads((F / "iss.json").read_text())), "protones": E.protones(json.loads((F / "protones.json").read_text())), "rayosx": E.rayosx(json.loads((F / "rayosx.json").read_text()))}


def test_lecturas_reales_se_vuelven_eventos_dc03_validos_con_su_hash():
    ev = E.a_eventos(_env())
    assert {e.tipo for e in ev} == {TipoEvento.POSICION_ESTACION, TipoEvento.LECTURA_PROTONES, TipoEvento.LECTURA_RAYOSX}
    assert {e.fuente for e in ev} == {FuenteEvento.WHERETHEISS, FuenteEvento.SWPC} and all(e.banner is Banner.REAL and len(e.hash_lectura_cruda) == 64 for e in ev)
    iss = next(e for e in ev if e.tipo is TipoEvento.POSICION_ESTACION)
    assert set(iss.parametros) == {"latitud_deg", "longitud_deg", "altitud_km", "velocidad_kms", "luz_solar"} and iss.parametros["luz_solar"] in (0.0, 1.0)
    E.ARCHIVADOS_NUEVOS.clear()


def test_sin_archivar_no_hay_evento_y_un_fallo_siempre_es_intento_dc13():
    E.ARCHIVADOS_NUEVOS.clear()
    env = _env(); E.ARCHIVADOS_NUEVOS.clear()
    assert E.a_eventos(env) == []
    env["iss"] = {"disponible": False, "fuente": E.URL_ISS, "error": "TimeoutError"}
    intentos = E.a_intentos(env)
    assert len(intentos) == 1 and intentos[0].resultado.value == "fallo" and intentos[0].hash_lectura_cruda is None


def test_reglas_de_coherencia_nuevas():
    ok = dict(evento_id="x", ts_utc_inicio="2026-11-15T00:00:00Z", ts_utc_fin="2026-11-15T00:00:00Z", parametros={"flujo_protones_pfu": 0.3}, hash_lectura_cruda=H, banner=Banner.REAL)
    DC03Evento(tipo=TipoEvento.LECTURA_PROTONES, fuente=FuenteEvento.SWPC, **ok)
    with pytest.raises(ValidationError):
        DC03Evento(tipo=TipoEvento.LECTURA_PROTONES, fuente=FuenteEvento.WHERETHEISS, **ok)          # protones solo de GOES/SWPC
    with pytest.raises(ValidationError):
        DC03Evento(tipo=TipoEvento.POSICION_ESTACION, fuente=FuenteEvento.SWPC, **ok)               # la ISS solo de wheretheiss


def test_dc05_acepta_e_proceso_con_su_regla_que_declara_el_supuesto():
    r = regla_exacta(7.5, 1.2, 1.5)
    a = DC05Alarma(alarma_id="al-1", ts_utc="2026-11-15T00:00:00Z", indicador="fc", detector=Detector.E_PROCESO, sentido="alza", umbral=100.0, valor_cruzado=117.2, regla_exacta=r,
                   semilla=20261113, hash_preregistro=H, estado="activa")
    assert a.detector is Detector.E_PROCESO and "subgaussiana" in a.regla_exacta
