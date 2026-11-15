"""IN-3 en vivo: lee SWPC, archiva la lectura cruda y muestra el banner REAL con su hash.

Uso:  uv run python scripts/ingestar_swpc.py [kp] [xrays] [alertas]
Datos REALES de NOAA SWPC (sin llave). Semilla: n/a — las semillas públicas aplican a corridas
simuladas (IN-4); una lectura en vivo no tiene semilla. Cada intento se imprime como DC-13.
"""
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.ingesta.archivo import ahora_utc  # noqa: E402
from src.ingesta.cliente import FEEDS, fetch_http, ingestar  # noqa: E402


def main(argv: list[str]) -> int:
    nombres = argv or list(FEEDS)
    for nombre in nombres:
        r = ingestar(FEEDS[nombre], fetch=fetch_http, ahora=ahora_utc(), raiz=RAIZ)
        i = r.intento
        print(f"[{i.banner.value}] {nombre:8} {i.resultado.value:5} http={i.http_status} filas={r.filas} "
              f"eventos_DC03={len(r.eventos)} omitidas={r.omitidas}")
        if i.hash_lectura_cruda:
            print(f"         hash_lectura_cruda={i.hash_lectura_cruda}")
            print(f"         archivo={r.archivo.relative_to(RAIZ)}")
        if i.error:
            print(f"         error={i.error}")
        if r.eventos:
            u = r.eventos[-1]
            print(f"         última lectura: {u.ts_utc_inicio.isoformat()} {u.parametros}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
