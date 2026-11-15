"""GO-2 en la historia de git (auditoría 2026-11-15): el commit que AÑADE el acta debe ser anterior o igual al que añade su línea en RESULTADOS.jsonl, y para las actas
nuevas ESTRICTAMENTE anterior (el hash se publica antes de correr). Las 12 actas listadas en HEREDADAS se commitearon junto con su resultado: el orden solo lo prueban los
timestamps de INDEX.jsonl (registrada_utc < ejecución); se declara, no se oculta (docs/decisiones.md D-37)."""
import json
import subprocess
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parent.parent
pytestmark = pytest.mark.skipif(not (RAIZ / ".git").exists(), reason="sin historial de git")
HEREDADAS = {"FB-012", "FB-013", "FB-014", "FB-015", "FB-015-v2", "FB-016", "FB-003R", "FB-004R", "FB-018", "FB-019", "FB-020", "FB-020-v2"}


def _t(*args) -> int | None:
    out = subprocess.run(["git", "-C", str(RAIZ), *args], capture_output=True, text=True).stdout.strip().split("\n")[-1]
    return int(out.split()[0]) if out else None


def _jl(p):
    return [json.loads(l) for l in (RAIZ / p).read_text(encoding="utf-8").splitlines() if l.strip()]


def test_el_acta_se_commitea_antes_que_su_resultado():
    ejecutadas = {r["acta"] for r in _jl("docs/actas/RESULTADOS.jsonl")}
    archivos = {e["acta"]: e["archivo"] for e in _jl("docs/actas/INDEX.jsonl")}
    mal = []
    for a in sorted(ejecutadas):
        if a in HEREDADAS or a not in archivos:
            continue
        c_acta = _t("log", "--diff-filter=A", "--format=%ct %h", "--", f"docs/actas/{archivos[a]}")
        c_res = _t("log", f'-S"acta": "{a}"', "--format=%ct %h", "--", "docs/actas/RESULTADOS.jsonl")
        if c_acta is None or c_res is None:
            continue                                                       # aún sin commitear: lo vigila el siguiente commit
        if c_acta > c_res:
            mal.append(a)
    assert not mal, f"actas cuyo resultado se commiteó ANTES que el acta: {mal}"


def test_las_actas_nuevas_no_comparten_commit_con_su_resultado():
    """Desde FB-021 el acta se commitea ANTES de correr (estricto): un acta nueva que comparta commit con su resultado no pasa."""
    nuevas = [a for a in ("FB-021", "FB-022", "FB-023", "FB-024", "FB-025")]
    archivos = {e["acta"]: e["archivo"] for e in _jl("docs/actas/INDEX.jsonl")}
    for a in nuevas:
        h_acta = subprocess.run(["git", "-C", str(RAIZ), "log", "--diff-filter=A", "--format=%h", "--", f"docs/actas/{archivos[a]}"], capture_output=True, text=True).stdout.split()[-1]
        h_res = subprocess.run(["git", "-C", str(RAIZ), "log", f'-S"acta": "{a}"', "--format=%h", "--", "docs/actas/RESULTADOS.jsonl"], capture_output=True, text=True).stdout.split()[-1]
        assert h_acta != h_res, f"{a}: acta y resultado en el mismo commit {h_acta}"
