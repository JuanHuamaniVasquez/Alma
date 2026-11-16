"""FA-4 · califica las predicciones abiertas del Faro contra su fuente. Uso: uv run python scripts/faro_calificar.py"""
import json
import sys
import urllib.request
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.fabrica.faro import Prediccion, calificar, kp_alcanza, osdr_tiene_archivos  # noqa: E402

for linea in (RAIZ / "data/faro/predicciones.jsonl").read_text(encoding="utf-8").splitlines():
    d = json.loads(linea)
    p = Prediccion(**{k: d[k] for k in Prediccion.__dataclass_fields__})
    if p.id == "F-001":
        payload = json.loads(urllib.request.urlopen(urllib.request.Request(p.fuente_dato, headers={"User-Agent": "alma/1.0"}), timeout=60).read())
        print(calificar(p, osdr_tiene_archivos(payload)))
    if p.id == "F-002":
        payload = json.loads(urllib.request.urlopen(urllib.request.Request(p.fuente_dato, headers={"User-Agent": "alma/1.0"}), timeout=60).read())
        print(calificar(p, kp_alcanza(payload, "2026-11-17T00:00:00", "2026-11-19T00:00:00")))
