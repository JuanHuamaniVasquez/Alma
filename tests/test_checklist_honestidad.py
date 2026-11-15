"""M5.4 · Checklist de honestidad (mandamiento 3 + política de datos), ejecutable: si algo se rompe, el test lo dice.

1 · Toda respuesta con datos de la API lleva banner REAL/SIMULADO.   2 · Toda pantalla de la vitrina declara su banner o lo hereda.
3 · Toda línea de ALMA tiene fuente y banner, y su audio existe.     4 · Las actas siguen intactas (hash).
5 · Toda alarma persistida tiene recibo completo.                    6 · Toda cápsula declara límites.
7 · La UI no afirma lo que el proyecto no demostró (FB-002 10/10 NO replicó; D-35).
"""
import json
import re
from pathlib import Path

import pytest
from rest_framework.test import APIClient

from src.gobernanza.preregistro import verificar

RAIZ = Path(__file__).resolve().parent.parent
WEB = RAIZ / "web" / "src"


@pytest.mark.django_db
@pytest.mark.parametrize("url", ["/api/libro/dias/", "/api/alarmas/", "/api/residuo/", "/api/verdes/", "/api/tormenta/", "/api/tormenta/escenario/G2/", "/api/indicadores/"])
def test_1_toda_respuesta_con_datos_lleva_banner(url):
    d = APIClient().get(url).json()
    assert d["banner"] in ("REAL", "SIMULADO")


def test_1b_los_artefactos_de_actas_y_demo_declaran_su_banner():
    d = APIClient().get("/api/demo-kill/").json()
    assert "SIMULADO" in d["banner"]
    assert all(c["banner"] in ("REAL", "SIMULADO") for c in APIClient().get("/api/capsulas/").json()["capsulas"])
    assert all(a["banner"] is None or a["banner"] for a in APIClient().get("/api/actas/").json()["actas"] if a["ejecutada"])


def test_2_cada_pantalla_declara_o_hereda_su_banner():
    paginas = sorted((WEB / "app").rglob("page.tsx"))
    assert len(paginas) >= 8
    sin = [str(p.relative_to(WEB)) for p in paginas if not re.search(r"Stamp|banner|Banner|AlmaDock|Room", p.read_text(encoding="utf-8"))]
    assert sin == []
    # Room incluye AlmaDock (que imprime el sello de cada línea) y la barra superior sella las salas con libro
    assert "Stamp" in (WEB / "components" / "Alma.tsx").read_text(encoding="utf-8")
    sin_sello_propio = [str(p.parent.name) for p in paginas if "Stamp" not in p.read_text(encoding="utf-8") and p.parent.name not in ("app", "machine", "budget", "kill")]
    assert sin_sello_propio == []   # las salas con datos reales o mezclados llevan su sello propio; las del hábitat simulado lo heredan de la barra


def test_3_cada_linea_de_alma_tiene_fuente_banner_y_audio():
    m = json.loads((WEB.parent / "public" / "voice" / "manifest.json").read_text(encoding="utf-8"))
    assert {"tormenta", "demo_kill", "fundicion", "actas", "residuo", "indicadores"} <= set(m) and any(k.startswith("libro-") for k in m) and any(k.startswith("escenario-") for k in m)
    for k, e in m.items():
        assert e["fuente"] and e["banner"] in ("REAL", "SIMULADO"), k
        assert (WEB.parent / "public" / e["audio"].lstrip("/")).is_file(), k


def test_3b_el_narrador_no_usa_texto_libre():
    fuente = (RAIZ / "src" / "superficies" / "narrador.py").read_text(encoding="utf-8")
    assert "openai" not in fuente.lower() and "anthropic" not in fuente.lower() and "llm" not in fuente.lower().replace("not an llm", "")


def test_4_las_actas_estan_intactas():
    assert verificar(RAIZ) == []


@pytest.mark.django_db
def test_5_toda_alarma_persistida_tiene_recibo_completo():
    from apps.motor.models import Alarma
    for a in Alarma.objects.all():
        assert a.regla_exacta and a.semilla is not None and len(a.hash_preregistro) == 64


def test_6_toda_capsula_declara_limites():
    cs = APIClient().get("/api/capsulas/").json()["capsulas"]
    assert cs and all(c["limites"].strip() for c in cs)


def test_7_la_ui_no_afirma_lo_que_no_se_demostro():
    for p in list((WEB).rglob("*.tsx")) + list((WEB.parent / "public" / "voice").glob("manifest.json")):
        t = p.read_text(encoding="utf-8").lower()
        assert not re.search(r"10\s*/\s*10|10 out of 10|ten out of ten", t), p
        assert "proven" not in t and "guaranteed" not in t, p
