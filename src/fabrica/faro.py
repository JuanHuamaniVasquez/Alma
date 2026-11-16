"""FA-4 · EL FARO: predicciones fechadas con probabilidad, registradas ANTES del dato y calificadas por regla automática.

Cada predicción lleva el sha256 de su enunciado+regla y la fecha de emisión; no se edita (solo-anexar). La calificación
(acierto y puntaje de Brier) la hace una función pura sobre el dato observado; `scripts/faro_calificar.py` lo trae de la fuente.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path


@dataclass(frozen=True)
class Prediccion:
    id: str
    enunciado: str
    regla_calificacion: str
    probabilidad: float          # de que el enunciado resulte verdadero
    emitida_utc: str
    fecha_limite: str            # YYYY-MM-DD
    fuente_dato: str

    def hash(self) -> str:
        return hashlib.sha256(json.dumps([self.id, self.enunciado, self.regla_calificacion, self.probabilidad,
                                          self.emitida_utc, self.fecha_limite, self.fuente_dato], ensure_ascii=False).encode()).hexdigest()


def registrar(ruta: Path, p: Prediccion) -> str:
    if not 0.0 < p.probabilidad < 1.0:
        raise ValueError("la probabilidad debe estar estrictamente entre 0 y 1")
    if ruta.exists() and any(json.loads(l)["id"] == p.id for l in ruta.read_text(encoding="utf-8").splitlines() if l):
        raise ValueError(f"{p.id} ya está registrada: no se edita")
    h = p.hash()
    with ruta.open("a", encoding="utf-8") as f:
        f.write(json.dumps({**p.__dict__, "sha256": h}, ensure_ascii=False) + "\n")
    return h


def calificar(p: Prediccion, ocurrio: bool, hoy: date | None = None) -> dict:
    """Brier = (probabilidad − resultado)²; 0 = perfecto, 0,25 = no informativo (p = 0,5). No se califica antes de la fecha límite
    salvo que el evento ya ocurriera (un evento que ocurre antes de la fecha límite se puede calificar como verdadero)."""
    limite = date.fromisoformat(p.fecha_limite)
    hoy = hoy or datetime.now(UTC).date()
    if not ocurrio and hoy <= limite:
        return {"id": p.id, "estado": "pendiente", "dias_restantes": (limite - hoy).days}
    return {"id": p.id, "estado": "calificada", "ocurrio": ocurrio, "brier": (p.probabilidad - (1.0 if ocurrio else 0.0)) ** 2}


def osdr_tiene_archivos(payload: dict) -> bool:
    """Regla de calificación del Faro F-001: el registro OSDR del experimento lista ≥ 1 archivo en `files`."""
    campos = payload.get("fields") or []
    return bool(campos) and len(campos[0].get("files") or []) >= 1


def kp_alcanza(payload: list[dict], desde: str, hasta: str, umbral: float = 5.0) -> bool:
    """Regla de calificación del Faro F-002: alguna lectura del índice Kp planetario (3 h) con `desde ≤ time_tag < hasta` (UTC) llega a `umbral`. Formato NOAA SWPC `noaa-planetary-k-index.json`."""
    for f in payload:
        t = str(f.get("time_tag", ""))[:19].replace(" ", "T")
        if desde <= t < hasta and f.get("Kp") is not None and float(f["Kp"]) >= umbral:
            return True
    return False
