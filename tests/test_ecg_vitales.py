"""M6.9 · ECG REAL (MIT-BIH registro 100, PhysioNet; no astronautas): el lector y el detector se MIDEN contra las anotaciones humanas. Fixture real o se omite."""
from pathlib import Path

import pytest

from src.ingesta import ecg_mitbih as E
from src.motor.ecg_vitales import comparar, detectar_r, pulso_lpm, rmssd_ms

CARPETA = Path(__file__).resolve().parent.parent / "data" / "externos" / "mitdb"
pytestmark = pytest.mark.skipif(not (CARPETA / "100.dat").exists(), reason="falta data/externos/mitdb (descarga PhysioNet, ver docs/politica-de-datos.md S-20)")


@pytest.fixture(scope="module")
def reg():
    return E.cargar(CARPETA)


def test_formato_y_duracion(reg):
    assert len(reg.mlii) == 650000 and abs(len(reg.mlii) / E.FS - 1805.6) < 1           # 30 min a 360 Hz
    assert 2200 < len(reg.latidos_ref) < 2300                                             # el registro 100 tiene ~2273 latidos anotados
    assert -5 < min(reg.mlii) and max(reg.mlii) < 5


def test_detector_contra_anotaciones_humanas(reg):
    m = comparar(detectar_r(list(reg.mlii)), list(reg.latidos_ref))
    assert m["sensibilidad"] >= 0.98 and m["ppv"] >= 0.98, m


def test_pulso_fisiologico_y_rmssd(reg):
    picos = detectar_r(list(reg.mlii))
    lpm = [v for _, v in pulso_lpm(picos)]
    assert 50 < sorted(lpm)[len(lpm) // 2] < 100                                          # reposo ambulatorio
    assert 5 < rmssd_ms(picos[:400]) < 200
