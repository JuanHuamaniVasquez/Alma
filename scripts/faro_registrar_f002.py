"""M9 · registra el Faro F-002: el aviso (WATCH) de NOAA del 15-nov-2026 contra lo que pase en el cielo. Solo-anexar; una vez.  Uso: uv run python scripts/faro_registrar_f002.py"""
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.fabrica import faro  # noqa: E402

p = faro.Prediccion(
    "F-002",
    "El aviso WATCH de NOAA SWPC (mensaje A20F, emitido 2026-11-15 13:34 UTC: tormenta geomagnética G1 prevista para el 17 y 18 de noviembre) se cumplirá: el índice Kp planetario llegará a 5 o más en alguna lectura de 3 h entre el 2026-11-17 00:00 y el 2026-11-19 00:00 UTC.",
    "VERDADERA si https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json trae alguna lectura con 2026-11-17T00:00:00 ≤ time_tag < 2026-11-19T00:00:00 y Kp ≥ 5 (G1 = Kp 5, escalas de NOAA); FALSA si ninguna la alcanza. Probabilidad: estimación propia, sin modelo.",
    0.55, datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "2026-11-19", "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json")
print("Faro F-002 sha256", faro.registrar(RAIZ / "data/faro/predicciones.jsonl", p), "· emitida", p.emitida_utc)
