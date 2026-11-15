"""M9 · Sol animado REAL: últimas ~24 h de NOAA SWPC (GOES-19 SUVI 195 Å y 304 Å; SOHO LASCO C2) → JPEG ligeros en web/public/sun/anim/ + manifest.json.
Fuente S-31 (dominio público NOAA): https://services.swpc.noaa.gov/products/animations/{suvi-primary-195,suvi-primary-304,lasco-c2}.json
Uso:  uv run --with pillow python scripts/descargar_sol_animado.py      (pide ~50 MB y genera ~4 MB; reintentable)"""
import io
import json
import re
import urllib.request
from pathlib import Path

from PIL import Image

RAIZ = Path(__file__).resolve().parent.parent
BASE = "https://services.swpc.noaa.gov"
SAL = RAIZ / "web/public/sun/anim"
CANALES = {"suvi195": ("suvi-primary-195", 8, 720), "suvi304": ("suvi-primary-304", 8, 720), "lasco": ("lasco-c2", 3, 512)}   # (lista, cada cuántos cuadros, px)


def get(u: str) -> bytes:
    with urllib.request.urlopen(u, timeout=30) as r:
        return r.read()


def ts(url: str) -> str:
    m = re.search(r"s(\d{8}T\d{6})Z", url) or re.search(r"/(\d{8})_(\d{4})_c2", url)
    t = m.group(1) if m and len(m.groups()) == 1 else m.group(1) + "T" + m.group(2) + "00"
    return f"{t[:4]}-{t[4:6]}-{t[6:8]}T{t[9:11]}:{t[11:13]}:{t[13:15]}Z"


def main() -> None:
    SAL.mkdir(parents=True, exist_ok=True)
    manifiesto = {}
    for clave, (lista, paso, px) in CANALES.items():
        urls = [x["url"] for x in json.loads(get(f"{BASE}/products/animations/{lista}.json"))][::-1][::paso][::-1]
        cuadros = []
        for i, u in enumerate(urls):
            im = Image.open(io.BytesIO(get(BASE + u))).convert("RGB")
            im.thumbnail((px, px))
            f = f"{clave}_{i:02d}.jpg"
            im.save(SAL / f, quality=80, optimize=True)
            cuadros.append({"archivo": f, "ts_utc": ts(u)})
        manifiesto[clave] = cuadros
        print(clave, len(cuadros), "cuadros", cuadros[0]["ts_utc"], "→", cuadros[-1]["ts_utc"])
    (SAL / "manifest.json").write_text(json.dumps({"fuente": "NOAA SWPC · GOES-19 SUVI y SOHO LASCO C2 (dominio público)", "canales": manifiesto}, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
