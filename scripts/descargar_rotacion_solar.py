"""M9 · Rotación REAL del Sol: una imagen de manchas solares (SDO/HMI, luz visible) por día, a las 12:00 UTC, de los últimos 14 días → web/public/sun/rot/ + manifest.json.
Fuente S-35 (NASA SDO, imágenes diarias del navegador público): https://sdo.gsfc.nasa.gov/assets/img/browse/AAAA/MM/DD/AAAAMMDD_120000_1024_HMIIC.jpg
El Sol gira en ≈25 días en el ecuador y ≈35 en los polos: en 14 días las manchas recorren medio disco.
Uso:  uv run --with pillow python scripts/descargar_rotacion_solar.py"""
import io
import json
import urllib.request
from datetime import UTC, datetime, timedelta
from pathlib import Path

from PIL import Image

SAL = Path(__file__).resolve().parent.parent / "web/public/sun/rot"
DIAS = 14


def main() -> None:
    SAL.mkdir(parents=True, exist_ok=True)
    for f in SAL.glob("*.jpg"):
        f.unlink()
    hoy = datetime.now(UTC).date()
    cuadros = []
    for k in range(DIAS, 0, -1):
        d = hoy - timedelta(days=k)
        url = f"https://sdo.gsfc.nasa.gov/assets/img/browse/{d:%Y/%m/%d}/{d:%Y%m%d}_120000_1024_HMIIC.jpg"
        try:
            with urllib.request.urlopen(url, timeout=30) as r:
                im = Image.open(io.BytesIO(r.read())).convert("RGB")
        except Exception as e:                                   # noqa: BLE001  un día sin imagen se omite y se dice, no se rellena
            print("sin imagen", d, e)
            continue
        im.thumbnail((640, 640))
        f = f"hmi_{d:%Y%m%d}.jpg"
        im.save(SAL / f, quality=78, optimize=True)
        cuadros.append({"archivo": f, "ts_utc": f"{d:%Y-%m-%d}T12:00:00Z"})
    (SAL / "manifest.json").write_text(json.dumps({"fuente": "NASA SDO / HMI (browse público)", "cuadros": cuadros}, indent=1), encoding="utf-8")
    print(len(cuadros), "días", cuadros[0]["ts_utc"], "→", cuadros[-1]["ts_utc"])


if __name__ == "__main__":
    main()
