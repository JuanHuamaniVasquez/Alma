"""M0.12 · Resuelve citas por nombre a DOI con Crossref (búsqueda bibliográfica) y muestra los candidatos para revisión humana/Claude.
No elige solo: imprime título, autores, año y revista de los mejores candidatos. Uso: uv run python scripts/resolver_citas.py"""
import json
import urllib.parse
import urllib.request

CONSULTAS = {
    "Frost 2003": "Frost Bone's mechanostat: a 2003 update",
    "Mehta 2014": "Mehta Multiple latent viruses reactivate in astronauts during Space Shuttle missions",
    "Mehta 2017": "Mehta Latent virus reactivation in astronauts on the International Space Station",
    "Hassler 2014": "Hassler Mars' surface radiation environment measured with the Mars Science Laboratory's Curiosity rover",
    "Parsons & Townsend 2000": "Parsons Townsend Interplanetary crew dose rates for the August 1972 solar particle event",
}


def buscar(q: str) -> list[dict]:
    url = "https://api.crossref.org/works?rows=3&select=DOI,title,author,issued,container-title&query.bibliographic=" + urllib.parse.quote(q)
    d = json.loads(urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "alma-citas/1.0"}), timeout=60).read())
    return d["message"]["items"]


for nombre, q in CONSULTAS.items():
    print("==", nombre)
    for it in buscar(q):
        a = ", ".join(x.get("family", "?") for x in it.get("author", [])[:3])
        print(f"   {it['DOI']} | {it['title'][0][:90]} | {a} | {it['issued']['date-parts'][0][0]} | {(it.get('container-title') or [''])[0][:40]}")
