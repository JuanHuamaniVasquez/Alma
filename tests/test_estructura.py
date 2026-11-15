"""M0.2: la estructura del repo respeta CLAUDE.md §7."""
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent

DIRECTORIOS = [
    "scripts", "src/ingesta", "src/libro", "src/motor", "src/fabrica",
    "src/superficies", "docs", "docs/actas", "data", ".claude/commands",
]
DOCS = [
    "DOC-01_MAP-S1-mapa-maestro-sistema-v0.2.md",
    "DOC-02_MAP-S2-genesis-nueva-generacion-v0.3.md",
    "DOC-03_TONO-pitch-equipo-v0.2.md",
    "DOC-04_LA-FUNDICION-laboratorio-v0.2.md",
]


def test_directorios_del_paragrafo_7():
    for d in DIRECTORIOS:
        assert (RAIZ / d).is_dir(), f"falta {d}"


def test_docs_oficiales_en_docs():
    for f in DOCS:
        assert (RAIZ / "docs" / f).is_file(), f"falta docs/{f}"


def test_comandos_y_cola_en_su_sitio():
    for f in ("CLAUDE.md", "TASKS.md", ".claude/commands/implementar.md", ".claude/commands/auditoria.md"):
        assert (RAIZ / f).is_file(), f"falta {f}"
