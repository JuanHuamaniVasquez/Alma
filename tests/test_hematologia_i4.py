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


def test_sin_datos_si_la_base_queda_en_uno_y_alarma_si_sale_de_la_banda():
    """Con 2 de las 3 extracciones previas sospechosas la base queda en 1 punto → `sin_datos`; con base buena, un valor lejano sale de la banda y uno cercano no."""
    from src.ingesta.osdr_cbc import Fila
    mk = lambda t, x, sosp=(): Fila("P", t, {"hb": x}, frozenset(sosp))                                  # noqa: E731
    pobre = [mk("L-92", 14.0, ("hb",)), mk("L-44", 14.2, ("hb",)), mk("L-3", 14.1), mk("R+1", 14.1)]
    assert evaluar(pobre, ("L-92", "L-44", "L-3"), ("R+1",), analitos=("hb",))[("P", "hb", "R+1")]["estado"] == "sin_datos"
    buena = lambda x: [mk("L-92", 14.0), mk("L-44", 14.2), mk("L-3", 14.4), mk("R+1", x)]               # noqa: E731
    assert evaluar(buena(14.3), ("L-92", "L-44", "L-3"), ("R+1",), analitos=("hb",))[("P", "hb", "R+1")]["estado"] == "dentro"
    assert evaluar(buena(20.0), ("L-92", "L-44", "L-3"), ("R+1",), analitos=("hb",))[("P", "hb", "R+1")]["estado"] == "arriba"
