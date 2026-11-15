"""SU · vocabulario hablado del buscador: ids hablables y únicos, claves completas, nada fuera del vocabulario."""
import json
from pathlib import Path

from src.superficies.busqueda import RESULTADOS, clips, hablar_id

RAIZ = Path(__file__).resolve().parent.parent
IDS = [json.loads(l)["acta"] for l in (RAIZ / "docs/actas/INDEX.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]


def test_ids_se_hablan_letra_a_letra_y_son_unicos():
    assert hablar_id("FB-005") == "F B zero zero five" and hablar_id("FB-005-D1") == "F B zero zero five, D one"
    assert hablar_id("FB-020-v2") == "F B zero two zero, version two" and hablar_id("FB-003R") == "F B zero zero three R"
    hablados = [hablar_id(a) for a in IDS]
    assert len(set(hablados)) == len(IDS) == 24


def test_clips_cubren_numeros_veredictos_salas_e_ids_y_los_resultados_del_resumen_son_hablables():
    c = clips(IDS)
    assert all(f"id_{a}" in c for a in IDS) and all(f"o_{k}" in c for k in RESULTADOS) and all(f"n_{i}" in c for i in range(0, 22))
    en = json.loads((RAIZ / "data/actas_en.json").read_text(encoding="utf-8"))["actas"]
    assert {e["outcome"] for e in en.values()} <= set(RESULTADOS)          # todo veredicto que muestra la vitrina se puede decir
    assert all(len(t) < 140 for t in c.values())                            # clips cortos: se encadenan, no se leen párrafos
