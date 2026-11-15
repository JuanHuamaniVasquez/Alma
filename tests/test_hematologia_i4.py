"""M7.2 · Hemograma REAL de astronautas (Inspiration4, OSD-569): lector, conciliación interna y banda personal. Fixture real o se omite."""
from pathlib import Path

import pytest

from src.ingesta import osdr_cbc as O
from src.motor.hematologia import banda, evaluar

RUTA = Path(__file__).resolve().parent.parent / "data" / "externos" / "osdr569" / "cbc_transformed.csv"
pytestmark = pytest.mark.skipif(not RUTA.exists(), reason="falta data/externos/osdr569 (descarga OSDR, ver docs/politica-de-datos.md S-24)")


@pytest.fixture(scope="module")
def filas():
    return O.cargar(RUTA)


def test_forma_4_personas_7_extracciones(filas):
    assert len(filas) == 28 and {f.persona for f in filas} == {"C001", "C002", "C003", "C004"}
    assert {f.t for f in filas} == set(O.PRE) | set(O.POST)


def test_la_fila_que_no_cierra_se_marca(filas):
    g = next(x for x in filas if x.persona == "C003" and x.t == "L-92")
    assert "abs_neutrophils" in g.sospechosos                                       # 10,1 cél/µL con 6 826 linfocitos: no concilia con su propio porcentaje


def test_banda_conocida():
    mu, lo, hi = banda([10.0, 12.0, 14.0])                                           # sd=2 → h = 4,3027·2·√(4/3)
    assert mu == 12.0 and abs((hi - mu) - 9.9366) < 1e-3
    assert banda([5.0]) is None


def test_sin_datos_si_la_base_queda_en_uno(filas):
    r = evaluar(filas, O.PRE, O.POST)
    assert all(v["estado"] in {"dentro", "arriba", "abajo", "sin_datos", "sospechoso"} for v in r.values())
