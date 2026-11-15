"""M8 · El generador de hipótesis de LA FUNDICIÓN: parte de mecanismos con fuente, cuenta pares REALES y nunca simula el dato que falta."""
from pathlib import Path

import pytest

from src.fabrica import generador as G

CSV = Path(__file__).resolve().parent.parent / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"


def test_toda_hipotesis_tiene_fuente_con_identificador_y_umbral_que_la_mata():
    for m in G.BIBLIOTECA:
        assert m.fuentes and all(f["id"] and f["tipo"] in {"DOI", "PMID", "NTRS"} for f in m.fuentes) and m.mata and m.mecanismo


def test_sin_dato_en_vuelo_es_bloqueado_y_dice_que_falta():
    sin = [m for m in G.BIBLIOTECA if G.CATALOGO.get(m.causa) is None or G.CATALOGO.get(m.efecto) is None]
    assert {m.clave for m in sin} == {"hf-en-vuelo", "sueno-en-vuelo", "retardo-estres"}


@pytest.mark.skipif(not CSV.exists(), reason="falta LifeSnaps local (S-07)")
def test_con_datos_reales_hay_listos_bloqueados_y_ya_probadas():
    c = G.generar(CSV)
    e = {x["clave"]: x for x in c}
    assert e["temp-eficiencia"]["estado"] == "listo" and e["temp-eficiencia"]["datos"]["pares"] > 1000
    assert e["sueno-fc"]["estado"] == "ya_probada" and e["sueno-fc"]["ya_probada_en"] == "FB-026"
    assert e["hf-en-vuelo"]["estado"] == "bloqueado" and e["hf-en-vuelo"]["datos"]["pares"] == 0 and e["hf-en-vuelo"]["precio"]["dias"] is None
    assert e["temp-fc"]["estado"] == "ya_probada" and e["temp-fc"]["ya_probada_en"] == "FB-022"
    assert [x["estado"] for x in c] == sorted((x["estado"] for x in c), key=["listo", "ya_probada", "bloqueado"].index)


@pytest.mark.skipif(not CSV.exists(), reason="falta LifeSnaps local (S-07)")
def test_cada_candidato_trae_su_texto_en_ingles_para_la_vitrina():
    for c in G.generar(CSV):
        assert all(c["en"][k] for k in ("mechanism", "kill", "price", "compute", "next")) and "á" not in c["en"]["mechanism"] + c["en"]["kill"]
