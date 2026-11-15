"""IN-3 · Ingesta de un feed externo: leer, archivar el crudo, interpretar y registrar el intento.

Cada intento deja un DC-13 (también el fallido). La lectura cruda se archiva antes de entregar
eventos (MP-3). El `fetch` es inyectable: los tests usan lecturas reales archivadas, sin red.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from src.contratos.comunes import Banner
from src.contratos.dc03_eventos import DC03Evento, FuenteEvento
from src.contratos.dc13_intento_ingesta import DC13Intento, ResultadoIntento

from .archivo import archivar, sha256_hex
from .swpc import alertas_a_registros, kp_a_eventos, normalizar_tabla, xrays_a_eventos

BASE = "https://services.swpc.noaa.gov/"


@dataclass(frozen=True)
class Respuesta:
    status: int | None  # None = ni siquiera hubo respuesta HTTP
    cuerpo: bytes = b""
    error: str | None = None


def fetch_http(url: str, timeout: float = 30.0) -> Respuesta:
    req = urllib.request.Request(url, headers={"User-Agent": "alma-ingesta/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:  # noqa: S310 — https fijo (feeds públicos)
            return Respuesta(r.status, r.read())
    except urllib.error.HTTPError as e:
        return Respuesta(e.code, b"", f"HTTP {e.code}")
    except (urllib.error.URLError, TimeoutError, OSError) as e:
        return Respuesta(None, b"", f"{type(e).__name__}: {e}")


Interprete = Callable[[list[dict], str], tuple[list[DC03Evento], int]]


@dataclass(frozen=True)
class Feed:
    nombre: str
    url: str
    a_eventos: Interprete | None  # None = solo se archiva (alertas: ver TASKS M0.14)


FEEDS = {
    "kp": Feed("kp", BASE + "products/noaa-planetary-k-index.json", kp_a_eventos),
    "xrays": Feed("xrays", BASE + "json/goes/primary/xrays-1-day.json", xrays_a_eventos),
    "alertas": Feed("alertas", BASE + "products/alerts.json", None),
}


@dataclass(frozen=True)
class ResultadoIngesta:
    intento: DC13Intento
    eventos: tuple[DC03Evento, ...]
    omitidas: int
    filas: int
    archivo: Path | None


def ingestar(feed: Feed, *, fetch: Callable[[str], Respuesta], ahora: datetime, raiz: Path) -> ResultadoIngesta:
    marca = ahora.strftime("%Y%m%dT%H%M%SZ")

    def intento(resultado, status, hash_=None, error=None) -> DC13Intento:
        return DC13Intento(intento_id=f"swpc-{feed.nombre}-{marca}", ts_utc=ahora, fuente=FuenteEvento.SWPC,
                           url=feed.url, resultado=resultado, http_status=status,
                           hash_lectura_cruda=hash_, error=error, banner=Banner.REAL)

    def fallo(status, error) -> ResultadoIngesta:
        return ResultadoIngesta(intento(ResultadoIntento.FALLO, status, error=error), (), 0, 0, None)

    r = fetch(feed.url)
    if r.status is None:
        return fallo(None, r.error or "sin respuesta")
    if not 200 <= r.status < 300:
        return fallo(r.status, r.error or f"HTTP {r.status}")
    try:
        filas = normalizar_tabla(json.loads(r.cuerpo))
    except (ValueError, TypeError) as e:
        return fallo(r.status, f"respuesta no interpretable: {e}")
    if not filas:
        return ResultadoIngesta(intento(ResultadoIntento.VACIO, r.status), (), 0, 0, None)

    hash_ = sha256_hex(r.cuerpo)
    eventos, omitidas = ([], 0)
    if feed.a_eventos is not None:
        eventos, omitidas = feed.a_eventos(filas, hash_)
        if not eventos:
            return fallo(r.status, "ninguna fila interpretable en la respuesta")
    else:
        _, omitidas = alertas_a_registros(filas)
        if omitidas == len(filas):
            return fallo(r.status, "ninguna alerta interpretable en la respuesta")
    ruta, hash_archivo = archivar(r.cuerpo, fuente="swpc", nombre=feed.nombre, url=feed.url, ts=ahora, raiz=raiz)
    assert hash_archivo == hash_
    return ResultadoIngesta(intento(ResultadoIntento.OK, r.status, hash_=hash_), tuple(eventos), omitidas, len(filas), ruta)
