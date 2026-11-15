"""M1.4 · FB-005-D1 (demo «kill» del Contrapeso): regresión permanente. UNIVERSO SIMULADO — DÍA 7.

Verifica que el resultado registrado se reproduce con la semilla pública, que el acta no cambió después
de registrarse y que se registró ANTES de ejecutar (mandamiento 2). La ceguera del detector A es por
construcción: esto es una demostración de lógica, no una prueba estadística (esa es FB-005, M2.6).
"""
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.gobernanza.preregistro import PreregistroInvalido, exigir_preregistro, hash_acta
from src.motor.fb005_demo import ejecutar

RAIZ = Path(__file__).resolve().parent.parent
ACTA = "FB-005-D1"


def _registro():
    lineas = (RAIZ / "docs" / "actas" / "RESULTADOS.jsonl").read_text(encoding="utf-8").splitlines()
    return [json.loads(l) for l in lineas if l and json.loads(l)["acta"] == ACTA]


def test_se_ejecuto_una_sola_vez_con_la_semilla_publica():
    r = _registro()
    assert len(r) == 1 and r[0]["semilla"] == 20261113


def test_el_resultado_registrado_se_reproduce_exactamente():
    r = _registro()[0]
    de_nuevo = ejecutar(r["semilla"])
    for k in ("control", "fuga", "prediccion_confirmada", "reglas_de_muerte_cumplidas", "banner"):
        assert de_nuevo[k] == r[k]


def test_el_acta_no_cambio_y_se_registro_antes_de_ejecutar():
    r = _registro()[0]
    assert hash_acta(RAIZ / "docs" / "actas" / f"{ACTA}.md") == r["hash_acta"]
    registrada = datetime.strptime(r["acta_registrada_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    ejecutada = datetime.strptime(r["ts_ejecucion_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
    assert registrada < ejecutada
    assert exigir_preregistro(RAIZ, ACTA, ahora=ejecutada).hash_sha256 == r["hash_acta"]


def test_columna_a_ciega_y_columna_b_alarmada_en_el_mismo_escenario():
    r = _registro()[0]
    assert r["banner"] == "UNIVERSO SIMULADO — DÍA 7"
    fuga, control = r["fuga"], r["control"]
    assert fuga["A_manifiesto"]["alarma"] is False                     # el manifiesto no ve la fuga
    assert fuga["B_ley"]["veredicto"] == "NO CIERRA" and fuga["B_ley"]["abre_investigacion_D6"] is True
    assert fuga["B_ley"]["sentido"] == "perdida_no_declarada"
    assert control["A_manifiesto"]["alarma"] is False and control["B_ley"]["veredicto"] == "CIERRA"  # sin falsas alarmas
    assert r["prediccion_confirmada"] is True and r["reglas_de_muerte_cumplidas"] == []


def test_sin_acta_registrada_el_runner_no_puede_correr(tmp_path):
    with pytest.raises(PreregistroInvalido, match="no está preregistrada"):
        exigir_preregistro(tmp_path, ACTA, ahora=datetime.now(UTC))


def test_el_diseno_es_sensible_a_la_semilla_pero_conserva_la_estructura():
    otra = ejecutar(20261114)  # no forma parte del acta: solo comprueba que el runner usa la semilla
    assert otra["control"]["B_ley"]["residuo_kg"] != _registro()[0]["control"]["B_ley"]["residuo_kg"]
    assert otra["fuga"]["fuga_kg"] == 0.30 and otra["control"]["fuga_kg"] == 0.0
