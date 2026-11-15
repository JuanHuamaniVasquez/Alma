"""IN-3 · Compuerta de admisión: ningún registro entra sin banner, sin fuente identificable
ni (si es simulado) sin semilla pública. Mandamiento 3 + regla 4 de dependencia (DOC-01)."""
from __future__ import annotations

import json
from collections.abc import Mapping
from pathlib import Path

from pydantic import ValidationError

from src.contratos.comunes import SEMILLAS_PUBLICAS, Banner
from src.contratos.dc03_eventos import DC03Evento

from .archivo import sha256_hex

CITA_OS892 = "they continue to lose about 1 – 2% of their bone mass a month"


class RegistroRechazado(ValueError):
    """El registro no cumple la ley de ingesta; el mensaje dice por qué."""


def admitir(registro: Mapping | DC03Evento, *, semilla: int | None = None) -> DC03Evento:
    try:
        ev = registro if isinstance(registro, DC03Evento) else DC03Evento.model_validate(registro)
    except ValidationError as e:
        raise RegistroRechazado(f"registro inválido: {e.error_count()} error(es): " +
                                "; ".join(f"{'.'.join(map(str, x['loc']))}: {x['msg']}" for x in e.errors())) from e
    if ev.banner is Banner.SIMULADO and semilla not in SEMILLAS_PUBLICAS:
        raise RegistroRechazado("registro SIMULADO sin semilla pública: sin semilla no hay fila nueva")
    return ev


def cargar_ficha_os892(raiz: Path) -> dict:
    """Lee la ficha de verdad de OS-892 y la rechaza si no cuadra con su lectura cruda archivada."""
    ficha = json.loads((raiz / "data" / "OS-892-extracto.json").read_text(encoding="utf-8"))
    if ficha.get("banner") != "REAL" or ficha.get("fuente") != "osdr" or ficha.get("id") != "OS-892":
        raise RegistroRechazado("ficha OS-892: exige banner REAL, fuente osdr e id OS-892")
    if CITA_OS892 not in ficha.get("extracto_verbatim", "").replace(" - ", " – "):
        raise RegistroRechazado("ficha OS-892 sin la cita textual del extracto")
    cruda = raiz / ficha["respuesta_cruda"]
    if not cruda.is_file() or sha256_hex(cruda.read_bytes()) != ficha["hash_lectura_cruda"]:
        raise RegistroRechazado("ficha OS-892: la lectura cruda archivada no existe o su hash no coincide")
    if ficha.get("archivos_publicos") != 0:
        raise RegistroRechazado("OS-892 se cita como fenómeno documentado, no como archivo de datos")
    return ficha
