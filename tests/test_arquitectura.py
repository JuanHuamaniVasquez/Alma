"""Reglas de arquitectura: el dominio (src/) es Python puro y las apps Django
son un adaptador por módulo. Flujo unidireccional (mandamiento 1):
ingesta -> libro -> motor -> fabrica -> superficies. Nadie escribe hacia atrás."""
import ast
from pathlib import Path

import pytest
from django.apps import apps

RAIZ = Path(__file__).resolve().parent.parent
APPS = ["ingesta", "libro", "motor", "fabrica", "superficies", "gobernanza"]
# Orden del flujo; un módulo solo puede importar de los anteriores.
ORDEN = ["contratos", "ingesta", "libro", "motor", "fabrica", "superficies"]


def _importados(ruta: Path) -> set[str]:
    arbol = ast.parse(ruta.read_text(encoding="utf-8"))
    nombres: set[str] = set()
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Import):
            nombres.update(a.name for a in nodo.names)
        elif isinstance(nodo, ast.ImportFrom) and nodo.module:
            nombres.add(nodo.module)
    return nombres


def test_dominio_no_importa_django_ni_drf():
    for py in (RAIZ / "src").rglob("*.py"):
        for mod in _importados(py):
            assert mod.split(".")[0] not in {"django", "rest_framework"}, f"{py} importa {mod}"


def test_flujo_unidireccional_en_el_dominio():
    for py in (RAIZ / "src").rglob("*.py"):
        propio = py.relative_to(RAIZ / "src").parts[0]
        if propio not in ORDEN:
            continue
        for mod in _importados(py):
            partes = mod.split(".")
            destino = partes[1] if partes[0] == "src" and len(partes) > 1 else None
            if destino in ORDEN:
                assert ORDEN.index(destino) <= ORDEN.index(propio), (
                    f"{py} ({propio}) importa hacia adelante: {mod}"
                )


@pytest.mark.parametrize("app", APPS)
def test_una_app_django_por_modulo(app):
    assert apps.get_app_config(app).name == f"apps.{app}"
    assert (RAIZ / "backend" / "apps" / app).is_dir()
