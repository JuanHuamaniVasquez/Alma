"""Coherencia documento ⇄ código, comprobada por máquina (no por mi palabra).

1. Cada contrato DC-xx de DOC-01 §3: los CAMPOS y los VALORES DE ENUM de sus tablas coinciden con el schema.
2. Cada módulo del registro de DOC-01 §2 (IN-, LB-, MO-, FA-, SU-, GO-, K-) está en el mapa `docs/checklist-backend.md`.
Si el documento y el código se contradicen, este test falla y obliga a decidir cuál cambia (D-xx).
"""
import enum
import re
import typing
from pathlib import Path

import pytest

from src.contratos import CONTRATOS

RAIZ = Path(__file__).resolve().parent.parent
DOC01 = (RAIZ / "docs" / "DOC-01_MAP-S1-mapa-maestro-sistema-v0.2.md").read_text(encoding="utf-8")

# Campos que el código añade o que el DOC declara fuera de la tabla, con su razón (decisión registrada).
EXTRAS_DEL_CODIGO = {
    "DC-04": {"estado_linea"},   # el DOC lo declara en una nota bajo la tabla (columna añadida en v0.2, P10)
    "DC-05": {"sentido"},        # el DOC dice «detector … Y el sentido (alza/caída — bilateral obligatorio)»
    "DC-10": {"k_brote"},        # el DOC dice «brote | bool (+ k declarado)»: el k se guarda en su propio campo
}


def _bloque(dc: str) -> str:
    m = re.search(rf"### {dc} ·.*?(?=\n### DC-|\n---\n)", DOC01, re.S)
    assert m, f"{dc} no aparece en DOC-01 §3"
    return m.group(0)


def _filas(dc: str):
    for linea in _bloque(dc).splitlines():
        if linea.startswith("|") and not linea.startswith("|---") and "| Campo |" not in linea:
            celdas = [c.strip() for c in linea.strip().strip("|").split("|")]
            yield celdas


def _campos_doc(dc: str) -> set[str]:
    out: set[str] = set()
    for celdas in _filas(dc):
        out.update(re.findall(r"`([a-z_0-9]+)(?:\[\])?`", celdas[0]))  # `fuentes[]` es el campo `fuentes`
    return out


def _enums_doc(dc: str) -> dict[str, list[str]]:
    out = {}
    for celdas in _filas(dc):
        if len(celdas) >= 2 and celdas[1].startswith("enum:"):
            campo = re.findall(r"`([a-z_0-9]+)`", celdas[0])[0]
            valores = [v.strip() for v in celdas[1][len("enum:"):].split("·")]
            out[campo] = [re.sub(r"\s*\(.*$", "", v).strip() for v in valores]
    return out


def _enum_de(anotacion) -> type[enum.Enum] | None:
    pila = [anotacion]
    while pila:
        a = pila.pop()
        if isinstance(a, type) and issubclass(a, enum.Enum):
            return a
        pila.extend(typing.get_args(a))
    return None


@pytest.mark.parametrize("dc", sorted(CONTRATOS))
def test_los_campos_del_schema_son_los_de_doc01(dc):
    codigo = set(CONTRATOS[dc].model_fields)
    doc = _campos_doc(dc)
    extras = EXTRAS_DEL_CODIGO.get(dc, set())
    assert doc - codigo == set(), f"{dc}: campos del DOC que el código no tiene: {doc - codigo}"
    assert codigo - doc - extras == set(), f"{dc}: campos del código que el DOC no declara: {codigo - doc - extras}"


@pytest.mark.parametrize("dc", sorted(CONTRATOS))
def test_los_valores_de_enum_son_los_de_doc01(dc):
    campos = CONTRATOS[dc].model_fields
    for campo, valores in _enums_doc(dc).items():
        assert campo in campos, f"{dc}.{campo} no existe en el schema"
        enum_cls = _enum_de(campos[campo].annotation)
        assert enum_cls is not None, f"{dc}.{campo}: el DOC dice enum y el schema no lo es"
        permitidos = {m.value for m in enum_cls}
        sin_acento = {v for v in valores}
        # `sentido` del DOC se escribe «alza/caída»; el resto debe coincidir exacto
        assert sin_acento == permitidos, f"{dc}.{campo}: DOC {sorted(sin_acento)} ≠ código {sorted(permitidos)}"


def test_el_doc_declara_exactamente_14_contratos():
    assert sorted(re.findall(r"### (DC-\d\d) ·", DOC01)) == sorted(CONTRATOS)


def test_cada_modulo_del_registro_de_doc01_esta_en_el_mapa_del_backend():
    seccion = DOC01[DOC01.index("## §2 · Registro oficial de módulos"):DOC01.index("## §3 · Contratos")]
    ids = sorted(set(re.findall(r"^\| ((?:IN|LB|MO|FA|SU|GO|K)-\d) \|", seccion, re.M)))
    assert len(ids) >= 30, f"el parser solo halló {len(ids)} módulos"
    mapa = (RAIZ / "docs" / "checklist-backend.md").read_text(encoding="utf-8")
    faltan = [i for i in ids if i not in mapa]
    assert faltan == [], f"módulos de DOC-01 §2 que el mapa no menciona: {faltan}"
