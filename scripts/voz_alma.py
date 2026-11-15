"""SU · Pre-render de la voz de ALMA (Kokoro-82M, Apache-2.0, local y sin red): narrador determinista → audio + manifiesto para la vitrina.
Cada frase sale de `src/superficies/narrador.py` con datos de los endpoints de lectura; el audio se nombra por el hash del texto.
Uso:  uv run --with kokoro-onnx --with soundfile python scripts/voz_alma.py
Env:  ALMA_VOICE (af_heart por defecto) · ALMA_FX=0 desactiva el eco/coro «holográfico» sutil.
El modelo (data/voz_modelo/, ~120 MB) no se versiona: https://github.com/thewh1teagle/kokoro-onnx/releases/tag/model-files-v1.0
"""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path[:0] = [str(RAIZ), str(RAIZ / "backend")]
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django  # noqa: E402

django.setup()
from rest_framework.test import APIClient  # noqa: E402

from src.superficies import narrador  # noqa: E402

SALIDA = RAIZ / "web" / "public" / "voice"
FX = "highpass=f=110,aecho=0.85:0.5:35|70:0.22|0.12,chorus=0.7:0.9:45:0.3:0.2:2,equalizer=f=3200:t=q:w=1.2:g=2.5,alimiter=limit=0.9"


def lineas() -> list:
    c = APIClient(HTTP_HOST="localhost")
    g = lambda u: (lambda r: r.json() if r.status_code == 200 else None)(c.get(u))  # noqa: E731
    base = narrador.todas(demo=g("/api/demo-kill/"), fund=g("/api/fundicion/"), storm=g("/api/tormenta/"), act=g("/api/actas/"), resid=g("/api/residuo/"), ind=g("/api/indicadores/"))
    dias = (g("/api/libro/dias/") or {}).get("dias", [])
    esc = [narrador.escenario(x) for x in (g(f"/api/tormenta/escenario/{e}/") for e in ("G1", "G2", "G3", "G4", "G5")) if x]
    libros = [d for d in (g(f"/api/libro/dia/{n}/") for n in dias) if d]
    anillos = []
    for d in libros:                                   # un anillo con libro habla por día; los que no tienen libro, una sola vez
        for pres in ("aire", "agua", "energia", "dosis", "ritmo", "carga", "inmunidad", "conducta", "tiempo"):
            ln = next((h for h in d["habitat"] if h["presupuesto_id"] == pres), None)
            if ln is not None or not any(a.clave == f"ring-{pres}" for a in anillos):
                anillos.append(narrador.presupuesto(d["dia_habitat"], pres, ln, d["banner"]))
    inds = (g("/api/indicadores/") or {}).get("indicadores", [])
    return base + esc + [narrador.libro_del_dia(d) for d in libros] + anillos + [narrador.indicador(i) for i in inds] + [narrador.astronauta()]


def main() -> int:
    from kokoro_onnx import Kokoro
    import soundfile as sf
    voz = os.environ.get("ALMA_VOICE", "af_heart")
    k = Kokoro(str(RAIZ / "data/voz_modelo/kokoro-v1.0.int8.onnx"), str(RAIZ / "data/voz_modelo/voices-v1.0.bin"))
    SALIDA.mkdir(parents=True, exist_ok=True)
    manifiesto = {}
    for l in lineas():
        destino = SALIDA / f"{l.id}.mp3"
        if not destino.exists():
            audio, sr = k.create(l.texto, voice=voz, speed=0.95, lang="en-us")
            with tempfile.TemporaryDirectory() as t:
                wav = Path(t) / "a.wav"
                sf.write(wav, audio, sr)
                filtro = ["-af", FX] if os.environ.get("ALMA_FX", "1") != "0" else []
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), *filtro, "-b:a", "96k", str(destino)], check=True)
        manifiesto[l.clave] = {"id": l.id, "texto": l.texto, "fuente": l.fuente, "banner": l.banner, "audio": f"/voice/{l.id}.mp3"}
        print(f"{l.clave:10s} {l.id} {l.texto[:70]}…")
    (SALIDA / "manifest.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
