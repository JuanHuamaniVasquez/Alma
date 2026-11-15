"""M9 · el borrador del acta y la ejecución salen de la MISMA especificación: lo preregistrado y lo ejecutado no pueden divergir."""
from src.fabrica import generador as G


def test_el_borrador_lleva_los_umbrales_de_la_especificacion():
    t = G.borrador_acta("FB-X", ["sueno-fc", "carga-rmssd"], semilla=20261113, sha_csv="0" * 64, alfa=0.025, no_ceguera="n", predicciones="p")
    assert "S ≥ 0.5 lpm" in t and "S ≤ -0.05 sd" in t and "control placebo" in t and "α = 0.025" in t
    assert "PREREGISTRADA, sin ejecutar" in t and "`sueno-fc`" in t and "`carga-rmssd`" in t


def test_toda_hipotesis_con_especificacion_existe_en_la_biblioteca_y_esta_lista():
    claves = {m.clave for m in G.BIBLIOTECA}
    assert set(G.TEST_SPEC) <= claves
    assert all(sp["signo"] in (-1, 1) and sp["efecto_min"] > 0 for sp in G.TEST_SPEC.values())
