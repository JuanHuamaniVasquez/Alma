"""IN-3 · Archivo inmutable de lecturas crudas (MP-3, aceptada 2026-11-15).

SWPC publica ventanas móviles (Kp ≈ 7 días, rayos X ≈ 24 h): sin guardar la respuesta tal como
llegó, la lectura de hoy no es reproducible mañana y `hash_lectura_cruda` queda sin objeto.
Solo se anexa: nunca se reescribe un archivo ni se borra una línea del manifiesto.
"""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path


def sha256_hex(cuerpo: bytes) -> str:
    return hashlib.sha256(cuerpo).hexdigest()


def buscar_archivada(cuerpo: bytes, raiz: Path) -> Path | None:
    """Si exactamente esta lectura cruda ya está archivada (mismo SHA-256), devuelve su archivo."""
    manifiesto = raiz / "data" / "lecturas" / "manifiesto.jsonl"
    if not manifiesto.exists():
        return None
    h = sha256_hex(cuerpo)
    for linea in manifiesto.read_text(encoding="utf-8").splitlines():
        if linea.strip() and json.loads(linea)["hash_sha256"] == h:
            return raiz / "data" / "lecturas" / json.loads(linea)["archivo"]
    return None


def archivar(cuerpo: bytes, *, fuente: str, nombre: str, url: str, ts: datetime, raiz: Path) -> tuple[Path, str]:
    """Guarda `data/lecturas/{fuente}_{nombre}_{ts}.json` y anexa una línea al manifiesto JSONL."""
    ts = ts.astimezone(UTC)
    carpeta = raiz / "data" / "lecturas"
    carpeta.mkdir(parents=True, exist_ok=True)
    marca = ts.strftime("%Y%m%dT%H%M%SZ")
    ruta = carpeta / f"{fuente}_{nombre}_{marca}.json"
    if ruta.exists():
        raise FileExistsError(f"{ruta.name} ya existe: el archivo de lecturas es solo-anexar")
    hash_ = sha256_hex(cuerpo)
    ruta.write_bytes(cuerpo)
    linea = {"ts_utc": ts.strftime("%Y-%m-%dT%H:%M:%SZ"), "fuente": fuente, "url": url,
             "archivo": ruta.name, "hash_sha256": hash_, "bytes": len(cuerpo), "banner": "REAL"}
    with (carpeta / "manifiesto.jsonl").open("a", encoding="utf-8") as m:
        m.write(json.dumps(linea, ensure_ascii=False) + "\n")
    return ruta, hash_


def ahora_utc() -> datetime:
    return datetime.now(UTC)
