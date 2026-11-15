"""FA-3 · cápsulas DC-07: números LEÍDOS de las actas (no retipeados), hash del preregistro del índice, límites obligatorios."""
import json
from pathlib import Path

import pytest
from pydantic import ValidationError
from rest_framework.test import APIClient

from src.contratos.dc07_capsula import DC07Capsula
from src.fabrica.capsula import capsulas

RAIZ = Path(__file__).resolve().parent.parent


def test_tres_capsulas_validas_con_limites_y_veredicto_de_la_tarjeta():
    cs = capsulas(RAIZ)
    assert len(cs) == 3 and all(c.limites and c.senal_refutadora and c.preregistro.semilla == 20261113 for c in cs)
    assert sorted(c.veredicto.split(" ")[0].strip(":").upper() for c in cs) == ["REFUTED", "REFUTED", "SUSTAINED"]
    assert all("NOT" in c.limites or "Not astronauts" in c.limites for c in cs)


def test_los_numeros_y_el_hash_son_los_de_las_actas():
    res = {json.loads(l)["acta"]: json.loads(l) for l in (RAIZ / "docs/actas/RESULTADOS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    idx = {json.loads(l)["acta"]: json.loads(l) for l in (RAIZ / "docs/actas/INDEX.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    a = next(c for c in capsulas(RAIZ) if c.veredicto.startswith("Sustained"))
    assert a.numeros["statistic_S"] == res["FB-016"]["A"]["S"] and a.numeros["people"] == 27 and a.preregistro.hash == idx["FB-016"]["hash_sha256"]
    k = next(c for c in capsulas(RAIZ) if "sleep_p" in c.numeros)
    assert k.numeros["sleep_p"] == res["FB-014"]["resultados"]["minutesAsleep"]["p_S1_bilateral"] and k.preregistro.hash == idx["FB-014"]["hash_sha256"]


def test_sin_limites_no_hay_capsula():
    c = capsulas(RAIZ)[0].model_dump()
    c["limites"] = ""
    with pytest.raises(ValidationError):
        DC07Capsula.model_validate(c)


def test_api_capsulas():
    r = APIClient().get("/api/capsulas/")
    assert r.status_code == 200 and len(r.json()["capsulas"]) == 3 and APIClient().post("/api/capsulas/", {}).status_code == 405
