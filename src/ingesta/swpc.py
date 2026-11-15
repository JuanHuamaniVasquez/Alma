"""IN-3 · Parsers puros de los feeds de NOAA SWPC (sin red, sin disco).

Los feeds de `/products/` pueden venir como lista de listas con el encabezado en la fila 0 y los
de `/json/` como lista de objetos (data/SWPC-fuentes.md): `normalizar_tabla` acepta ambos.
SWPC publica en UTC; algunos `time_tag` vienen sin zona y aquí se interpretan como UTC.
Nunca se rellena ni se interpola: una fila sin valor numérico se omite y se cuenta.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any

from src.contratos.comunes import Banner
from src.contratos.dc03_eventos import DC03Evento, FuenteEvento, TipoEvento


def normalizar_tabla(payload: Any) -> list[dict]:
    """Lista de listas (fila 0 = encabezados) o lista de objetos → lista de objetos."""
    if not isinstance(payload, list):
        raise ValueError("el feed no es una lista")
    if not payload:
        return []
    if isinstance(payload[0], list):
        cabecera = payload[0]
        return [dict(zip(cabecera, fila, strict=False)) for fila in payload[1:]]
    if all(isinstance(f, dict) for f in payload):
        return payload
    raise ValueError("el feed mezcla formatos no reconocidos")


def a_utc(texto: str) -> datetime:
    """ISO 8601 con o sin zona; sin zona se toma como UTC (convención de SWPC)."""
    dt = datetime.fromisoformat(texto.replace("Z", "+00:00"))
    return dt.replace(tzinfo=UTC) if dt.tzinfo is None else dt.astimezone(UTC)


def _numero(v: Any) -> float | None:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if math.isfinite(f) else None


def kp_a_eventos(filas: list[dict], hash_lectura_cruda: str) -> tuple[list[DC03Evento], int]:
    """Índice Kp planetario → un DC-03 `lectura_clima_espacial` por fila (parámetro `kp`, adimensional)."""
    eventos, omitidas = [], 0
    for f in filas:
        kp, tag = _numero(f.get("Kp", f.get("kp"))), f.get("time_tag")
        if kp is None or not tag:
            omitidas += 1
            continue
        t = a_utc(tag)
        eventos.append(DC03Evento(
            evento_id=f"swpc-kp-{tag}", ts_utc_inicio=t, ts_utc_fin=t,
            tipo=TipoEvento.LECTURA_CLIMA_ESPACIAL, fuente=FuenteEvento.SWPC,
            parametros={"kp": kp}, hash_lectura_cruda=hash_lectura_cruda, banner=Banner.REAL))
    return eventos, omitidas


def xrays_a_eventos(filas: list[dict], hash_lectura_cruda: str) -> tuple[list[DC03Evento], int]:
    """Rayos X GOES (flujo en W/m² por banda) → un DC-03 por fila y banda (`flujo_x_w_m2`)."""
    eventos, omitidas = [], 0
    for f in filas:
        flujo, tag, banda = _numero(f.get("flux")), f.get("time_tag"), f.get("energy")
        if flujo is None or not tag or not banda:
            omitidas += 1
            continue
        t = a_utc(tag)
        eventos.append(DC03Evento(
            evento_id=f"swpc-xray-g{f.get('satellite')}-{banda}-{tag}", ts_utc_inicio=t, ts_utc_fin=t,
            tipo=TipoEvento.LECTURA_CLIMA_ESPACIAL, fuente=FuenteEvento.SWPC,
            parametros={"flujo_x_w_m2": flujo}, hash_lectura_cruda=hash_lectura_cruda, banner=Banner.REAL))
    return eventos, omitidas


@dataclass(frozen=True)
class AlertaSwpc:
    """Mensaje oficial de SWPC tal cual (products/alerts.json). Sin clasificar: ver TASKS M0.14."""
    product_id: str
    emitida_utc: datetime
    mensaje: str


def alertas_a_registros(filas: list[dict]) -> tuple[list[AlertaSwpc], int]:
    out, omitidas = [], 0
    for f in filas:
        if not (f.get("product_id") and f.get("issue_datetime") and f.get("message")):
            omitidas += 1
            continue
        out.append(AlertaSwpc(f["product_id"], a_utc(f["issue_datetime"].replace(" ", "T")), f["message"]))
    return out, omitidas


_TITULAR = re.compile(r"^ALERT:\s*Geomagnetic K-index of (\d)\b", re.MULTILINE)
_UMBRAL = re.compile(r"^Threshold Reached:\s*(\d{4} \w{3} \d{2} \d{4}) UTC", re.MULTILINE)
_ESCALA_G = re.compile(r"^Noaa Scale:\s*(G\d)\b", re.MULTILINE | re.IGNORECASE)
KP_MINIMO_TORMENTA = 5  # NOAA Space Weather Scales: G1 = Kp 5 (https://www.swpc.noaa.gov/noaa-scales-explanation, leída 2026-11-15)


def alerta_a_evento(alerta: AlertaSwpc, hash_lectura_cruda: str) -> DC03Evento | None:
    """M0.14 · Solo un `ALERT: Geomagnetic K-index of N` (observado, no pronóstico) con N ≥ 5 declara un evento
    `tormenta_solar`. Los avisos (WARNING/WATCH), las continuaciones, el flujo de electrones, las emisiones de radio
    y los resúmenes NO lo son: devuelven None y siguen archivados tal cual. La escala G que el propio mensaje declara
    debe coincidir con N (G = N − 4); si no, se rechaza (no se adivina)."""
    m = _TITULAR.search(alerta.mensaje)
    if not m:
        return None
    kp = int(m.group(1))
    if kp < KP_MINIMO_TORMENTA:
        return None
    g = _ESCALA_G.search(alerta.mensaje)
    if not g or int(g.group(1)[1:]) != kp - 4:
        raise ValueError(f"alerta {alerta.product_id}: la escala G declarada no corresponde a Kp={kp}")
    t = _UMBRAL.search(alerta.mensaje)
    inicio = datetime.strptime(t.group(1), "%Y %b %d %H%M").replace(tzinfo=UTC) if t else alerta.emitida_utc
    return DC03Evento(evento_id=f"swpc-alerta-{alerta.product_id}-{inicio:%Y%m%dT%H%MZ}", ts_utc_inicio=inicio, ts_utc_fin=inicio,
                      tipo=TipoEvento.TORMENTA_SOLAR, fuente=FuenteEvento.SWPC, parametros={"kp": float(kp)},
                      hash_lectura_cruda=hash_lectura_cruda, banner=Banner.REAL)
