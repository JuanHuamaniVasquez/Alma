"""M8 · Descarga una colección corta y CURADA de imágenes REALES de la Biblioteca de Imágenes de NASA (images-api.nasa.gov) a web/public/nasa/ + credits.json.
Las imágenes de NASA son, en general, de dominio público (nasa.gov/nasa-brand-center/images-and-media); se acredita cada una con su nasa_id y enlace y no se sugiere patrocinio de NASA.
Uso:  uv run --with pillow python scripts/descargar_imagenes_nasa.py"""
import io
import json
import urllib.request
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
SALIDA = RAIZ / "web" / "public" / "nasa"
# sala → nasa_id (elegidos a mano mirando cada imagen; ver docs/politica-de-datos.md S-28)
IMAGENES = {"frontier": "iss073e0702307", "machine": "iss072e143163", "leak": "iss033e017337", "foundry": "iss072e861307", "budget": "iss058e005282", "capsule": "iss071e264174"}


def get(url: str) -> bytes:
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": "ALMA-TONO-LAB/0.1"}), timeout=40).read()


def main() -> int:
    SALIDA.mkdir(parents=True, exist_ok=True)
    creditos = {}
    for sala, nid in IMAGENES.items():
        meta = json.loads(get(f"https://images-api.nasa.gov/asset/{nid}"))["collection"]["items"]
        url = next((i["href"] for i in meta if i["href"].endswith("~large.jpg")), None) or next(i["href"] for i in meta if i["href"].endswith("~medium.jpg"))
        busc = json.loads(get(f"https://images-api.nasa.gov/search?nasa_id={nid}"))["collection"]["items"][0]["data"][0]
        im = Image.open(io.BytesIO(get(url))).convert("RGB")
        im.thumbnail((1600, 1600))
        im.save(SALIDA / f"{sala}.jpg", quality=80, optimize=True, progressive=True)
        creditos[sala] = {"nasa_id": nid, "titulo": busc.get("title"), "centro": busc.get("center"), "fecha": (busc.get("date_created") or "")[:10], "descripcion": (busc.get("description") or "")[:300],
                          "url": f"https://images.nasa.gov/details/{nid}", "tam": list(im.size)}
        print(sala, nid, im.size, (SALIDA / f"{sala}.jpg").stat().st_size // 1024, "KB")
    (SALIDA / "credits.json").write_text(json.dumps(creditos, ensure_ascii=False, indent=1), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
