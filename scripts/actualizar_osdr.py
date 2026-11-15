"""M7.3 · Instantánea del catálogo REAL de NASA OSDR: estudios con humanos y vuelo espacial → data/referencias/osdr_humanos.json.
Consulta: https://osdr.nasa.gov/osdr/data/search?term=spaceflight&type=cgene&ffield=organism&fvalue=Homo sapiens (+ términos «astronaut», «Inspiration4», «crew»).
Clasificación (heurística DECLARADA, sobre el título): «crew» si contiene astronaut|crew|Inspiration4|mission simulation|confinement; el resto = células/tejidos humanos enviados al espacio.
Uso:  uv run python scripts/actualizar_osdr.py"""
import json
import re
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
BASE = "https://osdr.nasa.gov/osdr/data/search"
CONSULTAS = ("spaceflight", "astronaut", "Inspiration4", "crew")
CREW = re.compile(r"astronaut|crew|inspiration4|mission simulation|confinement|cosmonaut", re.I)


def _texto(v) -> str | None:
    if isinstance(v, dict):
        v = v.get("Name") or v.get("name") or v.get("Identifier") or ""
    v = (v or "").strip() if isinstance(v, str) else ""
    return v or None


def buscar(term: str) -> list[dict]:
    url = f"{BASE}?term={urllib.parse.quote(term)}&from=0&size=100&type=cgene&ffield=organism&fvalue={urllib.parse.quote('Homo sapiens')}"
    with urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ALMA-TONO-LAB/0.1"}), timeout=30) as r:       # noqa: S310
        return [h["_source"] for h in json.load(r)["hits"]["hits"]]


def main() -> int:
    por_id = {}
    for q in CONSULTAS:
        for s in buscar(q):
            por_id.setdefault(s["Accession"], s)
    estudios = []
    for acc, s in sorted(por_id.items(), key=lambda kv: int(kv[0].split("-")[1])):
        titulo = (s.get("Study Title") or "").strip()
        lib = s.get("Study Public Release Date")
        estudios.append({"accession": acc, "titulo": titulo, "liberado": datetime.fromtimestamp(float(lib), UTC).strftime("%Y-%m-%d") if lib and float(lib) > 0 else None,
                         "ensayos": [x.strip() for x in re.split(r"\s{2,}", (s.get("Study Assay Measurement Type") or "")) if x.strip()],
                         "mision": _texto(s.get("Mission") or s.get("Flight Program")), "tipo": "crew" if CREW.search(titulo) else "cells",
                         "url": f"https://osdr.nasa.gov/bio/repo/data/studies/{acc}"})
    out = {"capturado_utc": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "fuente": BASE, "consultas": list(CONSULTAS), "filtro": "organism = Homo sapiens",
           "nota": "Catálogo de metadatos de OSDR. Acceso a archivos y contenido NO verificados estudio por estudio (solo OSD-569 CBC se descargó y analizó: FB-024).",
           "n": len(estudios), "n_crew": sum(e["tipo"] == "crew" for e in estudios), "estudios": estudios}
    (RAIZ / "data" / "referencias" / "osdr_humanos.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(out["n"], "estudios,", out["n_crew"], "con tripulación")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
