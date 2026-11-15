"""SU · Genera los clips de voz del buscador de La Bóveda (Kokoro-82M local) → web/public/voice/search/*.mp3 + manifest.json.
ALMA compone sus respuestas encadenando estos clips (vocabulario cerrado: `src/superficies/busqueda.py`).
Uso:  uv run --with kokoro-onnx --with soundfile python scripts/voz_busqueda.py     Env: ALMA_VOICE (af_heart), ALMA_FX=0 (sin eco)."""
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.superficies.busqueda import clips  # noqa: E402

SALIDA = RAIZ / "web" / "public" / "voice" / "search"
FX = "highpass=f=110,aecho=0.85:0.5:35|70:0.22|0.12,chorus=0.7:0.9:45:0.3:0.2:2,equalizer=f=3200:t=q:w=1.2:g=2.5,alimiter=limit=0.9"


def main() -> int:
    from kokoro_onnx import Kokoro
    import soundfile as sf
    ids = [json.loads(l)["acta"] for l in (RAIZ / "docs/actas/INDEX.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    voz = os.environ.get("ALMA_VOICE", "af_heart")
    k = Kokoro(str(RAIZ / "data/voz_modelo/kokoro-v1.0.int8.onnx"), str(RAIZ / "data/voz_modelo/voices-v1.0.bin"))
    SALIDA.mkdir(parents=True, exist_ok=True)
    manifiesto = {}
    for clave, texto in clips(ids).items():
        destino = SALIDA / f"{clave}.mp3"
        if not destino.exists() or destino.with_suffix(".txt").read_text(encoding="utf-8") != texto:
            audio, sr = k.create(texto, voice=voz, speed=0.95, lang="en-us")
            with tempfile.TemporaryDirectory() as t:
                wav = Path(t) / "a.wav"
                sf.write(wav, audio, sr)
                filtro = ["-af", FX] if os.environ.get("ALMA_FX", "1") != "0" else []
                subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(wav), *filtro, "-b:a", "96k", str(destino)], check=True)
            destino.with_suffix(".txt").write_text(texto, encoding="utf-8")       # para saber si hay que regenerar
        manifiesto[clave] = {"texto": texto, "audio": f"/voice/search/{clave}.mp3"}
    (SALIDA / "manifest.json").write_text(json.dumps(manifiesto, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    print(len(manifiesto), "clips")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
