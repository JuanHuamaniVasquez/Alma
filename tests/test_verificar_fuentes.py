"""M0.9: la extracción de identificadores de citas (offline; la consulta en red no se testea)."""
import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "verificar_fuentes", Path(__file__).resolve().parent.parent / "scripts" / "verificar_fuentes.py")
vf = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(vf)

TEXTO = ("Guyatt 1990, PubMed 2297206; Fahrion (PMC8281973); DOI 10.1038/s41526-026-00628-7. "
         "Glaessgen (NTRS 20120008178); arXiv:2107.07511 y nada más.")


def test_extrae_cada_tipo_de_identificador():
    ids = vf.extraer_identificadores(TEXTO)
    assert ids["pmid"] == {"2297206"}
    assert ids["pmc"] == {"PMC8281973"}
    assert ids["doi"] == {"10.1038/s41526-026-00628-7"}
    assert ids["ntrs"] == {"20120008178"}
    assert ids["arxiv"] == {"2107.07511"}


def test_texto_sin_citas_no_inventa_nada():
    assert all(not v for v in vf.extraer_identificadores("sin ninguna cita aquí").values())
