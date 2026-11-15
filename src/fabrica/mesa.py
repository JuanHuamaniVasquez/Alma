"""FA-1 · LA MESA: registro solo-anexar de tarjetas DC-12 y su tablero (nacidas → refutadas → sostenidas → detectores).

La puerta es el propio contrato `DC12Tarjeta`: sin mecanismo, sin fuente con identificador o sin precio, la tarjeta no existe.
El estado de una tarjeta cambia anexando una línea nueva con el mismo `tarjeta_id` (la última manda; el historial se conserva).
"""
from __future__ import annotations

import json
import uuid
from collections import Counter
from pathlib import Path

from src.contratos.dc12_fundicion import DC12Tarjeta, EstadoTarjeta

NAMESPACE = uuid.UUID("5d2c9c2e-7c3e-4a52-9a0e-a1f0a1f0a1f0")


def id_de(clave: str) -> uuid.UUID:
    """UUID determinista a partir de un nombre corto de tarjeta (reproducible entre corridas)."""
    return uuid.uuid5(NAMESPACE, clave)


def acunar(datos: dict) -> DC12Tarjeta:
    """Valida y construye una tarjeta; lanza `pydantic.ValidationError` si no pasa la puerta."""
    return DC12Tarjeta.model_validate(datos)


def registrar(ruta: Path, tarjeta: DC12Tarjeta, nota: str = "") -> None:
    with ruta.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"tarjeta": json.loads(tarjeta.model_dump_json()), "nota": nota}, ensure_ascii=False) + "\n")


def leer(ruta: Path) -> list[DC12Tarjeta]:
    """Última versión de cada tarjeta (orden de primera aparición)."""
    ultimas: dict[str, DC12Tarjeta] = {}
    if ruta.exists():
        for linea in ruta.read_text(encoding="utf-8").splitlines():
            if linea.strip():
                t = DC12Tarjeta.model_validate(json.loads(linea)["tarjeta"])
                ultimas[str(t.tarjeta_id)] = t
    return list(ultimas.values())


def tablero(tarjetas: list[DC12Tarjeta], detectores: list[dict] | None = None) -> dict:
    """Métrica que se muestra al jurado: solo conteos por estado. «listas_para_detector» NO son detectores: M4.5 exige registrarlos."""
    c = Counter(t.estado for t in tarjetas)
    return {"nacidas": len(tarjetas), **{e.value: c.get(e, 0) for e in EstadoTarjeta},
            "listas_para_detector": sum(1 for t in tarjetas if t.estado is EstadoTarjeta.SOSTENIDA),
            "detectores_nuevos": len(detectores or [])}


def registrar_detector(ruta: Path, tarjeta: DC12Tarjeta, detector: str, regla_exacta: str) -> None:
    """La circulación (M4.5): solo una tarjeta SOSTENIDA con preregistro puede registrar un detector. Solo-anexar."""
    if tarjeta.estado is not EstadoTarjeta.SOSTENIDA:
        raise ValueError("solo una tarjeta sostenida puede circular como detector")
    with ruta.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"tarjeta_id": str(tarjeta.tarjeta_id), "detector": detector, "regla_exacta": regla_exacta,
                            "hash_preregistro": tarjeta.preregistro_hash}, ensure_ascii=False) + "\n")


def leer_detectores(ruta: Path) -> list[dict]:
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()] if ruta.exists() else []
