"""IN-1 · Adaptador del dataset Fitbit de Sjögren/LES/sanos (datos REALES, NO astronautas) → DC-01.

Fuente: Zenodo 8018238, doi:10.5281/zenodo.8018238 (CC BY 4.0), «Wearable data and self reported fatigue scores from a
remote observational study in Sjogren's disease, SLE and healthy participants». Dispositivo: Fitbit (modelo no declarado
en los archivos leídos). Uso: validación INDEPENDIENTE de FB-009/FB-010 (M2.15), solo participantes `diagnosis == none`.

    heart_rate__mean            → `fc`    (lpm)  FC media diaria (misma naturaleza que `bpm` de LifeSnaps; definición exacta no verificada)
    sleep__total_asleep_minutes → `sueño` (min)

Mismas reglas que LifeSnaps: valor ausente = `calidad=ausente` (nunca se rellena); imposible = `sospechoso`; banner REAL;
fecha = día calendario local marcado 00:00Z. σ de sensor = la proxy de `incertidumbre.py` (declarada como proxy).
"""
from __future__ import annotations

import csv
import math
from datetime import UTC, date, datetime
from pathlib import Path

from src.contratos.comunes import Banner, IndicadorSensor
from src.contratos.dc01_sensores import CalidadDato, DC01Sensor

from .incertidumbre import sigma_de

DISPOSITIVO = "fitbit"
MAPEO = {
    "heart_rate__mean": (IndicadorSensor.FC, 300.0),
    "sleep__total_asleep_minutes": (IndicadorSensor.SUENO, 1440.0),
}


def _numero(t: str | None) -> float | None:
    try:
        v = float(t)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def sanos(ruta_screener: Path) -> set[str]:
    with ruta_screener.open(encoding="utf-8", newline="") as f:
        return {r["user_id"] for r in csv.DictReader(f) if r["diagnosis"] == "none"}


def cargar(ruta_dias: Path, permitidos: set[str]) -> list[DC01Sensor]:
    out: list[DC01Sensor] = []
    with ruta_dias.open(encoding="utf-8", newline="") as f:
        for fila in csv.DictReader(f):
            if fila["user_id"] not in permitidos:
                continue
            ts = datetime.combine(date.fromisoformat(fila["date"][:10]), datetime.min.time(), tzinfo=UTC)
            for col, (ind, tope) in MAPEO.items():
                s, v = sigma_de(ind), _numero(fila.get(col))
                if v is None:
                    out.append(DC01Sensor(persona_id=fila["user_id"], ts_utc=ts, indicador=ind, valor=None, unidad=s.unidad,
                                          incertidumbre_sensor=None, calidad=CalidadDato.AUSENTE, fuente=DISPOSITIVO, banner=Banner.REAL))
                    continue
                malo = v < 0 or v > tope or (v <= 0 and ind is IndicadorSensor.FC) or (v == 0 and ind is IndicadorSensor.SUENO)
                out.append(DC01Sensor(persona_id=fila["user_id"], ts_utc=ts, indicador=ind, valor=v, unidad=s.unidad,
                                      incertidumbre_sensor=s.sigma, calidad=CalidadDato.SOSPECHOSO if malo else CalidadDato.OK,
                                      fuente=DISPOSITIVO, banner=Banner.REAL))
    return out
