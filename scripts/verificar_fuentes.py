"""Verifica contra bases públicas todas las citas con identificador de los docs del repo.

Uso:  uv run python scripts/verificar_fuentes.py [--red]
Sin --red solo lista los identificadores encontrados (offline). Con --red consulta PubMed,
Crossref, arXiv y NTRS y muestra el título real para compararlo a mano con lo que dice el doc.
Un HTTP 200 NO prueba existencia en sitios que son aplicaciones JS (p. ej. OSDR): por eso
aquí se consultan APIs de metadatos, no páginas. Política: docs/politica-de-datos.md.
"""
from __future__ import annotations

import glob
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

PATRONES = {
    "pmid": r"(?:PubMed|PMID)[\s:]*([0-9]{6,9})",
    "pmc": r"\b(PMC[0-9]{6,8})\b",
    "doi": r"\b(10\.[0-9]{4,9}/[^\s)\]>,;`*]+)",
    "ntrs": r"NTRS[\s:#]*([0-9]{8,11})",
    "arxiv": r"arXiv[\s:]*([0-9]{4}\.[0-9]{4,5})",
}


def extraer_identificadores(texto: str) -> dict[str, set[str]]:
    """Función pura: identificadores de citas encontrados en un texto."""
    return {k: {m.rstrip(".") for m in re.findall(p, texto)} for k, p in PATRONES.items()}


def _get(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "alma-verificar-fuentes/1.0"})
    return urllib.request.urlopen(req, timeout=30).read().decode("utf-8", "replace")


def consultar(tipo: str, ident: str) -> str:
    """Devuelve 'título | fecha | primer autor' desde la API pública del identificador."""
    try:
        if tipo == "pmid":
            d = json.loads(_get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pubmed&id={ident}&retmode=json"))["result"][ident]
            return f"{d['title'][:90]} | {d['pubdate']} | {d['authors'][0]['name']}"
        if tipo == "pmc":
            n = ident[3:]
            d = json.loads(_get(f"https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi?db=pmc&id={n}&retmode=json"))["result"][n]
            return f"{d['title'][:90]} | {d['pubdate']} | {d['authors'][0]['name']}"
        if tipo == "doi":
            m = json.loads(_get("https://api.crossref.org/works/" + urllib.parse.quote(ident)))["message"]
            return f"{m['title'][0][:90]} | {m['issued']['date-parts'][0]} | {m['author'][0]['family']}"
        if tipo == "ntrs":
            d = json.loads(_get(f"https://ntrs.nasa.gov/api/citations/{ident}"))
            return f"{d['title'][:90]} | {d.get('distributionDate', '')[:10]}"
        if tipo == "arxiv":
            t = _get(f"https://arxiv.org/abs/{ident}")
            return re.search(r"<title>(.*?)</title>", t, re.S).group(1).strip()[:100]
    except Exception as e:  # noqa: BLE001 — se informa, no se oculta
        return f"NO VERIFICADO ({type(e).__name__}: {str(e)[:60]})"
    return "tipo desconocido"


OSDR_API = "https://osdr.nasa.gov/geode-py/ws/repo/experiments/"


def comprobar_experimento(registro: dict, accesion: str, titulo: str) -> list[str]:
    """Función pura: problemas de un registro de experimento OSDR (lista vacía = verificado).

    OS-NNN es una accesión de *experimento* (API `repo/experiments`), no un *study* OSD-NNN;
    la página web de OSDR es una app JS que responde 200 a cualquier ruta y no sirve de prueba.
    """
    problemas: list[str] = []
    campos = (registro.get("fields") or [{}])[0]
    if campos.get("osID") != accesion:
        problemas.append(f"osID {campos.get('osID')!r} != {accesion!r}")
    if campos.get("title") != titulo:
        problemas.append(f"título {campos.get('title')!r} != {titulo!r}")
    if campos.get("status") != "Public":
        problemas.append(f"estado {campos.get('status')!r} != 'Public'")
    return problemas


def verificar_osdr(accesion: str, titulo: str, control: str = "OS-999999") -> str:
    """Consulta la API real y hace el control negativo con una accesión inexistente."""
    try:
        registro = json.loads(_get(OSDR_API + accesion))
        problemas = comprobar_experimento(registro, accesion, titulo)
    except Exception as e:  # noqa: BLE001
        return f"NO VERIFICADO ({type(e).__name__}: {str(e)[:60]})"
    try:
        _get(OSDR_API + control)
        return f"{accesion}: control {control} respondió algo: la API no distingue, NO VERIFICADO"
    except urllib.error.HTTPError as e:
        control_ok = e.code in (403, 404)
    except Exception:  # noqa: BLE001
        control_ok = False
    if problemas or not control_ok:
        return f"{accesion}: FALLA {problemas or 'control negativo inesperado'}"
    return f"{accesion}: VERIFICADO (registro real; control {control} rechazado)"


def main(argv: list[str]) -> int:
    raiz = Path(__file__).resolve().parent.parent
    archivos = sorted(glob.glob(str(raiz / "docs" / "*.md")) + glob.glob(str(raiz / "data" / "*.md")))
    todo: dict[str, set[str]] = {k: set() for k in PATRONES}
    for f in archivos:
        for k, v in extraer_identificadores(Path(f).read_text(encoding="utf-8")).items():
            todo[k] |= v
    for tipo, ids in todo.items():
        for ident in sorted(ids):
            print(f"{tipo:6} {ident:28}", consultar(tipo, ident) if "--red" in argv else "")
            if "--red" in argv:
                time.sleep(1.5)  # arXiv/NCBI limitan peticiones
    if "--red" in argv:
        print("osdr  ", verificar_osdr("OS-892", "Role of Mesenchymal Stem Cells in Microgravity Induced Bone Loss"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
