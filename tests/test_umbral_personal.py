"""M4.5 · detector `umbral_personal` con noches REALES de LifeSnaps (fixture) y la regla exacta de FB-016."""
import csv
from datetime import UTC, datetime
from pathlib import Path

import pytest

from src.contratos.dc05_alarma import Detector
from src.motor.umbral_personal import alarma, ejecutar_regla, regla_exacta

FILAS = sorted((f for f in csv.DictReader((Path(__file__).resolve().parent.parent / "data/fixtures/lifesnaps_diario_extracto.csv").open(encoding="utf-8"))
                if f["minutesAsleep"] not in ("", "nan")), key=lambda f: f["date"])
SUENO = [float(f["minutesAsleep"]) for f in FILAS]
H = "ec4a82e04f4343a56974030f03f3148e9145fdcc3d82777a6afadc8d3dd8ae87"   # acta FB-016
TS = datetime(2026, 11, 15, tzinfo=UTC)


def test_alarma_con_recibo_en_noche_corta_real_y_ninguna_en_larga():
    base = SUENO[:14]
    corta, larga = min(SUENO[14:]), max(SUENO[14:])
    a = alarma("p1-corta", TS, corta, base, 20261113, H)
    assert a is not None and a.detector is Detector.UMBRAL_PERSONAL and a.hash_preregistro == H and a.valor_cruzado == corta
    assert alarma("p1-larga", TS, larga, base, 20261113, H) is None


def test_la_regla_exacta_es_ejecutable_y_se_retira_sola():
    a = alarma("p1", TS, 200.0, [400.0] * 14, 20261113, H)
    assert ejecutar_regla(a.regla_exacta, a.valor_cruzado) is True
    assert ejecutar_regla(a.regla_exacta, 450.0) is False        # con otro dato la regla no se cumple: la alarma se retira
    with pytest.raises(ValueError):
        ejecutar_regla("cualquier cosa", 1.0)


def test_limite_declarado_marca_cerca_de_la_mitad_de_las_noches():
    base = SUENO[:14]
    med = sorted(base)[len(base) // 2 - 1: len(base) // 2 + 1]
    marcadas = sum(alarma(f"n{i}", TS, x, base, 20261113, H) is not None for i, x in enumerate(SUENO[14:]))
    assert 0.2 < marcadas / len(SUENO[14:]) < 0.8 and regla_exacta(sum(med) / 2).startswith("UMBRAL_PERSONAL")
