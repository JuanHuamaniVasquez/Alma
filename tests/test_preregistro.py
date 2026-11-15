"""M0.5 · GO-2: preregistro con hash de los bytes exactos, solo-anexar, y compuerta para runners.

Las actas de prueba de tmp_path son entradas construidas (X-01); las actas reales FB-005…FB-008
de docs/actas/ se verifican tal cual. FB-001…FB-004 NO están registradas: no hay acta (ver README).
"""
import hashlib
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pytest

from src.contratos import SEMILLAS_PUBLICAS
from src.gobernanza.preregistro import PreregistroInvalido, exigir_preregistro, hash_acta, leer_indice, registrar, verificar

RAIZ = Path(__file__).resolve().parent.parent
T0 = datetime(2026, 11, 15, 12, 0, tzinfo=UTC)


def _acta(tmp_path, nombre="FB-900", texto="Hipótesis: x. Muerte: y.\n"):
    (tmp_path / "docs" / "actas").mkdir(parents=True, exist_ok=True)
    (tmp_path / "docs" / "actas" / f"{nombre}.md").write_text(texto, encoding="utf-8")
    return nombre


# --- actas reales del repo -----------------------------------------------------------------
def test_actas_reales_registradas_e_intactas():
    entradas = {e.acta: e for e in leer_indice(RAIZ)}
    assert set(entradas) >= {"FB-005", "FB-006", "FB-007", "FB-008"}
    assert verificar(RAIZ) == []
    for e in entradas.values():
        crudo = (RAIZ / "docs" / "actas" / e.archivo).read_bytes()
        assert hashlib.sha256(crudo).hexdigest() == e.hash_sha256  # reproducible por cualquiera
        assert all(s in SEMILLAS_PUBLICAS for s in e.semillas)
        if e.acta in {"FB-005", "FB-006", "FB-007", "FB-008"}:  # las re-registradas conservan el hash del 11-nov
            assert len(e.hash_publicado_origen or "") == 64
        assert exigir_preregistro(RAIZ, e.acta, ahora=T0 + timedelta(days=1)).acta == e.acta


def test_las_actas_aun_no_escritas_no_estan_registradas():
    registradas = {e.acta for e in leer_indice(RAIZ)}
    for sin_acta in ("FB-001", "FB-002", "FB-003", "FB-004"):
        assert sin_acta not in registradas  # no se inventan preregistros


# --- la herramienta --------------------------------------------------------------------------
def test_registra_con_el_hash_de_los_bytes_exactos(tmp_path):
    a = _acta(tmp_path)
    e = registrar(tmp_path, a, semillas=(20261113,), ahora=T0)
    assert e.hash_sha256 == hash_acta(tmp_path / "docs" / "actas" / f"{a}.md")
    assert verificar(tmp_path) == []


def test_rechaza_semillas_no_publicas_o_ausentes_y_archivo_inexistente(tmp_path):
    a = _acta(tmp_path)
    with pytest.raises(PreregistroInvalido):
        registrar(tmp_path, a, semillas=(42,), ahora=T0)
    with pytest.raises(PreregistroInvalido):
        registrar(tmp_path, a, semillas=(), ahora=T0)
    with pytest.raises(PreregistroInvalido):
        registrar(tmp_path, "FB-999", semillas=(20261113,), ahora=T0)


def test_un_acta_registrada_no_se_re_registra(tmp_path):
    a = _acta(tmp_path)
    registrar(tmp_path, a, semillas=(20261113,), ahora=T0)
    with pytest.raises(PreregistroInvalido, match="v2"):
        registrar(tmp_path, a, semillas=(20261113,), ahora=T0)


def test_editar_el_acta_despues_de_registrarla_se_detecta(tmp_path):  # anti-HARKing
    a = _acta(tmp_path)
    registrar(tmp_path, a, semillas=(20261113,), ahora=T0)
    (tmp_path / "docs" / "actas" / f"{a}.md").write_text("Hipótesis: cambiada tras ver datos.\n", encoding="utf-8")
    assert verificar(tmp_path) and "cambió" in verificar(tmp_path)[0]
    with pytest.raises(PreregistroInvalido, match="hash"):
        exigir_preregistro(tmp_path, a, ahora=T0 + timedelta(hours=1))


# --- la compuerta de los runners ---------------------------------------------------------------
def test_sin_preregistro_no_se_corre(tmp_path):
    with pytest.raises(PreregistroInvalido, match="no está preregistrada"):
        exigir_preregistro(tmp_path, "FB-900", ahora=T0)


def test_registrada_despues_de_la_ejecucion_no_vale(tmp_path):
    a = _acta(tmp_path)
    registrar(tmp_path, a, semillas=(20261113,), ahora=T0)
    with pytest.raises(PreregistroInvalido, match="después"):
        exigir_preregistro(tmp_path, a, ahora=T0 - timedelta(minutes=1))
    assert exigir_preregistro(tmp_path, a, ahora=T0 + timedelta(minutes=1)).acta == a
