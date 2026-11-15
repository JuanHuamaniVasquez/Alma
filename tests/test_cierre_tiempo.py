"""M2.9 · compuerta de cierre del tiempo, con filas REALES de LifeSnaps (data/fixtures/lifesnaps_diario_extracto.csv)."""
import csv
from collections import Counter
from pathlib import Path

from src.contratos.dc04_libro import EstadoLinea
from src.libro.cierre_tiempo import evaluar_dia

FIX = Path(__file__).resolve().parent.parent / "data" / "fixtures" / "lifesnaps_diario_extracto.csv"
FILAS = list(csv.DictReader(FIX.open(encoding="utf-8")))


def test_dias_completos_reales_cierran_en_su_mayoria_y_los_que_no_se_marcan():
    cs = [evaluar_dia(f) for f in FILAS]
    completos = [c for c in cs if c.residuo_min is not None]
    assert len(completos) == 88 and sum(c.estado is EstadoLinea.LIMPIO for c in completos) == 79   # 79/88 = 89,8 % (fixture de un participante)
    assert sum(1 for c in cs if c.motivo.startswith("incompleto")) == 99                            # sin registro de sueño: la ausencia es dato
    assert all(c.estado is not EstadoLinea.CUARENTENA for c in cs)


def test_estado_coherente_con_el_residuo():
    for f in FILAS:
        c = evaluar_dia(f)
        if c.residuo_min is not None:
            assert (c.estado is EstadoLinea.LIMPIO) == (abs(c.residuo_min) <= 1)
        else:
            assert c.estado is EstadoLinea.SOSPECHOSO and c.motivo.startswith("incompleto")


def test_ausencia_es_dato_y_nunca_se_rellena():
    fila = dict(FILAS[0], minutesAsleep="")
    c = evaluar_dia(fila)
    assert c.estado is EstadoLinea.SOSPECHOSO and c.residuo_min is None and "minutesAsleep" in c.motivo


def test_tolerancia_exacta():
    base = {"sedentary_minutes": 700, "lightly_active_minutes": 100, "moderately_active_minutes": 20,
            "very_active_minutes": 20, "minutesAsleep": 420, "minutesAwake": 180}
    assert evaluar_dia(base).estado is EstadoLinea.LIMPIO                           # suma 1440
    assert evaluar_dia({**base, "minutesAwake": 181}).estado is EstadoLinea.LIMPIO  # +1 min: tolerado
    assert evaluar_dia({**base, "minutesAwake": 182}).estado is EstadoLinea.SOSPECHOSO
