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


# --- OS-892: fixture REAL archivado (data/lecturas/, MP-3) -----------------------------------
import hashlib
import json

RAIZ = Path(__file__).resolve().parent.parent
TITULO = "Role of Mesenchymal Stem Cells in Microgravity Induced Bone Loss"


def _manifiesto():
    return [json.loads(l) for l in (RAIZ / "data" / "lecturas" / "manifiesto.jsonl").read_text(encoding="utf-8").splitlines() if l]


def test_os892_registro_real_archivado_se_verifica():
    entrada = next(e for e in _manifiesto() if e["fuente"] == "osdr")
    registro = json.loads((RAIZ / "data" / "lecturas" / entrada["archivo"]).read_text(encoding="utf-8"))
    assert vf.comprobar_experimento(registro, "OS-892", TITULO) == []
    campos = registro["fields"][0]
    assert campos["files"] == [] and campos["studies"] == []  # sin archivos de datos publicados
    assert "they continue to lose about 1 – 2% of their bone mass a month" in campos["objectives"]


def test_os892_rechaza_otra_accesion_o_titulo():
    entrada = next(e for e in _manifiesto() if e["fuente"] == "osdr")
    registro = json.loads((RAIZ / "data" / "lecturas" / entrada["archivo"]).read_text(encoding="utf-8"))
    assert vf.comprobar_experimento(registro, "OS-999999", TITULO)
    assert vf.comprobar_experimento(registro, "OS-892", "otro título")
    assert vf.comprobar_experimento({}, "OS-892", TITULO)


def test_manifiesto_hash_coincide_con_el_archivo_crudo():
    for e in _manifiesto():
        crudo = (RAIZ / "data" / "lecturas" / e["archivo"]).read_bytes()
        assert hashlib.sha256(crudo).hexdigest() == e["hash_sha256"]
        assert len(crudo) == e["bytes"]
