"""IN-1 · Adaptador de LifeSnaps (datos REALES de personas en vida cotidiana, NO astronautas) → DC-01.

Fuente: Yfantidou et al. 2022, doi:10.1038/s41597-022-01764-x · Zenodo 7229547 · CC BY 4.0.
Se mapean solo los indicadores con σ de sensor verificada (src/ingesta/incertidumbre.py):
    bpm          → `fc`    (lpm)  frecuencia cardiaca media diaria (agregado del CSV; definición exacta no verificada)
    minutesAsleep → `sueño` (min)  minutos dormidos
NO se emiten: temperatura (sin σ verificada), presión/glucosa (el dataset no las trae) y ánimo (DC-02
exige `duracion_respuesta_s` y LifeSnaps no registra el tiempo de respuesta de las EMA).

Reglas: banner REAL; fecha = día calendario LOCAL del participante (los autores convirtieron todo a su zona
horaria, que no divulgan) y se marca a las 00:00Z por convención; un valor ausente se registra como
`calidad=ausente` (la ausencia es dato), nunca se rellena; un valor físicamente imposible → `sospechoso`.
"""
from __future__ import annotations

import csv
import math
from collections import Counter
from dataclasses import dataclass
from datetime import UTC, date, datetime
from pathlib import Path

from src.contratos.comunes import Banner, IndicadorSensor
from src.contratos.dc01_sensores import CalidadDato, DC01Sensor

from .incertidumbre import sigma_de

DISPOSITIVO = "fitbit_sense"
# columna del CSV → (indicador, máximo físicamente posible; None = sin tope)
MAPEO = {
    "bpm": (IndicadorSensor.FC, 300.0),
    "minutesAsleep": (IndicadorSensor.SUENO, 1440.0),
}


@dataclass(frozen=True)
class ResultadoCarga:
    filas: int
    registros: tuple[DC01Sensor, ...]
    por_calidad: dict[str, int]


def _numero(texto: str | None) -> float | None:
    try:
        v = float(texto)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _ts(dia: str) -> datetime:
    return datetime.combine(date.fromisoformat(dia), datetime.min.time(), tzinfo=UTC)


def fila_a_registros(fila: dict) -> list[DC01Sensor]:
    persona, ts = fila["id"], _ts(fila["date"])
    out: list[DC01Sensor] = []
    for columna, (indicador, tope) in MAPEO.items():
        s = sigma_de(indicador)  # sin σ verificada no se emite
        v = _numero(fila.get(columna))
        if v is None:
            out.append(DC01Sensor(persona_id=persona, ts_utc=ts, indicador=indicador, valor=None, unidad=s.unidad,
                                  incertidumbre_sensor=None, calidad=CalidadDato.AUSENTE, fuente=DISPOSITIVO, banner=Banner.REAL))
            continue
        imposible = v <= 0 and indicador is IndicadorSensor.FC or v < 0 or v > tope
        out.append(DC01Sensor(persona_id=persona, ts_utc=ts, indicador=indicador, valor=v, unidad=s.unidad,
                              incertidumbre_sensor=s.sigma, calidad=CalidadDato.SOSPECHOSO if imposible else CalidadDato.OK,
                              fuente=DISPOSITIVO, banner=Banner.REAL))
    return out


def leer_diario(ruta: Path) -> list[dict]:
    with ruta.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def cargar(ruta: Path) -> ResultadoCarga:
    filas = leer_diario(ruta)
    regs = [r for fila in filas for r in fila_a_registros(fila)]
    return ResultadoCarga(len(filas), tuple(regs), dict(Counter(r.calidad.value for r in regs)))
