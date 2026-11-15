"""M4.1-M4.3 · la puerta de LA FUNDICIÓN, las 5 tarjetas reales y El Faro."""
import copy
import json
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from src.fabrica import faro, mesa
from src.fabrica.faro import Prediccion, calificar, osdr_tiene_archivos
from src.gobernanza.preregistro import leer_indice

RAIZ = Path(__file__).resolve().parent.parent
TARJETAS = mesa.leer(RAIZ / "data/fundicion/tarjetas.jsonl")
BASE = json.loads(TARJETAS[0].model_dump_json())


def test_las_doce_tarjetas_pasan_la_puerta_y_tienen_hash_de_un_acta_registrada():
    assert len(TARJETAS) == 16                                                # 5 de M4.2 + 2 con astronautas REALES (M7.6/M7.7)
    hashes = {e.hash_sha256 for e in leer_indice(RAIZ)}
    assert all(t.preregistro_hash in hashes for t in TARJETAS)          # el hash es de un acta realmente registrada
    assert all(t.fuentes and t.mecanismo and t.precio and t.valor_si_cierta for t in TARJETAS)


def test_tablero_cuenta_nacidas_refutadas_sostenidas():
    t = mesa.tablero(TARJETAS)
    assert (t["nacidas"], t["refutada"], t["sostenida"], t["sin_datos"], t["en_prueba"]) == (16, 10, 4, 1, 1)
    assert t["detectores_nuevos"] == 0 and t["listas_para_detector"] == 4   # sin registro, una sostenida NO es un detector
    det = mesa.leer_detectores(RAIZ / "data/fundicion/detectores.jsonl")
    assert mesa.tablero(TARJETAS, det)["detectores_nuevos"] == 1            # M4.5: circuló como detector `umbral_personal`
    assert det[0]["detector"] == "umbral_personal" and det[0]["hash_preregistro"] == TARJETAS[1].preregistro_hash


def test_solo_una_tarjeta_sostenida_puede_circular(tmp_path):
    with pytest.raises(ValueError, match="sostenida"):
        mesa.registrar_detector(tmp_path / "d.jsonl", TARJETAS[0], "umbral_personal", "r")   # kp-sueno-hrv está refutada


@pytest.mark.parametrize("campo", ["mecanismo", "fuentes", "precio", "valor_si_cierta"])
def test_la_puerta_rechaza_tarjeta_incompleta(campo):
    malo = copy.deepcopy(BASE)
    malo[campo] = [] if isinstance(malo[campo], list) else ""
    if campo == "precio":
        malo[campo] = {"datos": "", "computo": "", "dias": -1}
    with pytest.raises(ValidationError):
        mesa.acunar(malo)


def test_la_puerta_rechaza_fuente_sin_identificador_valido_y_estado_sin_hash():
    malo = copy.deepcopy(BASE)
    malo["fuentes"] = [{"id": "un blog", "tipo": "DOI"}]
    with pytest.raises(ValidationError):
        mesa.acunar(malo)
    sin_hash = copy.deepcopy(BASE)
    sin_hash["preregistro_hash"] = None
    with pytest.raises(ValidationError):
        mesa.acunar(sin_hash)


def test_faro_f001_registrada_con_hash_y_calificacion():
    d = json.loads((RAIZ / "data/faro/predicciones.jsonl").read_text(encoding="utf-8").splitlines()[0])
    p = Prediccion(**{k: d[k] for k in Prediccion.__dataclass_fields__})
    assert p.hash() == d["sha256"] and p.emitida_utc < "2026-11-16"
    payload = json.loads(next((RAIZ / "data/lecturas").glob("osdr_OS-892_*.json")).read_text(encoding="utf-8"))
    assert osdr_tiene_archivos(payload) is False                         # hoy 0 archivos: pendiente
    assert calificar(p, False, date(2026, 11, 15))["estado"] == "pendiente"
    assert calificar(p, True, date(2027, 3, 1)) == {"id": "F-001", "estado": "calificada", "ocurrio": True, "brier": pytest.approx(0.5625)}
    assert calificar(p, False, date(2028, 1, 1))["brier"] == pytest.approx(0.0625)
    assert osdr_tiene_archivos({"fields": [{"files": [{"nombre": "a.csv"}]}]}) is True


def test_faro_no_se_edita_y_exige_probabilidad_valida(tmp_path):
    p = Prediccion("X", "e", "r", 0.5, "2026-11-15T00:00:00Z", "2027-01-01", "u")
    f = tmp_path / "f.jsonl"
    faro.registrar(f, p)
    with pytest.raises(ValueError, match="ya está registrada"):
        faro.registrar(f, p)
    with pytest.raises(ValueError, match="estrictamente"):
        faro.registrar(tmp_path / "g.jsonl", Prediccion("Y", "e", "r", 1.0, "2026-11-15T00:00:00Z", "2027-01-01", "u"))
