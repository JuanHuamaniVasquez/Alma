"""IN-3b · Entorno en vivo REAL de la tripulación: posición/luz de la ISS, protones energéticos GOES y rayos X solares (NOAA SWPC). M7.1.

Fuentes (verificadas 2026-11-15; sin clave):
  · ISS: https://api.wheretheiss.at/v1/satellites/25544 (posición derivada de elementos orbitales; `visibility` = daylight/eclipsed/visible; límite ≈ 1 petición/s).
  · Protones GOES ≥10 MeV: https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json — la escala de tormentas de radiación S de NOAA
    arranca en **10 pfu** (≥10 MeV) (NOAA SWPC, spaceweather.gov/node/415); por encima se declara «S1 o más» sin afirmar el nivel exacto.
  · Rayos X 0,1–0,8 nm (GOES): https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json — clase de fulguración por flujo (A<1e-7, B<1e-6, C<1e-5, M<1e-4, X≥1e-4 W/m²).
Todo es REAL y de ahora mismo; si una fuente no responde, el campo viene `disponible: false` (la ausencia es dato, no se rellena).
"""
from __future__ import annotations

import json
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime

URL_ISS = "https://api.wheretheiss.at/v1/satellites/25544"
URL_PROT = "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json"
URL_XR = "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json"
UMBRAL_S1_PFU = 10.0


def _get(url: str, t: float = 8.0):
    req = urllib.request.Request(url, headers={"User-Agent": "ALMA-TONO-LAB/0.1 (student project; contact: repo issues)"})
    with urllib.request.urlopen(req, timeout=t) as r:                      # noqa: S310 (URL fija, https)
        return json.load(r)


def clase_xrays(flujo: float) -> str:
    for letra, techo in (("A", 1e-7), ("B", 1e-6), ("C", 1e-5), ("M", 1e-4)):
        if flujo < techo:
            return f"{letra}{flujo / (techo / 10):.1f}"
    return f"X{flujo / 1e-4:.1f}"


def iss(datos: dict | None = None) -> dict:
    d = datos if datos is not None else _get(URL_ISS)
    return {"disponible": True, "lat": round(d["latitude"], 2), "lon": round(d["longitude"], 2), "alt_km": round(d["altitude"], 1), "vel_kms": round(d["velocity"] / 3600, 2),
            "visibilidad": d["visibility"], "sol_lat": round(d["solar_lat"], 2), "sol_lon": round(d["solar_lon"], 2),
            "ts_utc": datetime.fromtimestamp(d["timestamp"], UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "fuente": URL_ISS,
            "a_la_luz": d["visibility"] == "daylight"}


def protones(serie: list | None = None) -> dict:
    s = serie if serie is not None else [x for x in _get(URL_PROT) if x.get("energy") == ">=10 MeV"]
    u = s[-1]
    return {"disponible": True, "pfu": u["flux"], "ts_utc": u["time_tag"], "max_ventana_pfu": max(x["flux"] for x in s), "n_lecturas": len(s),
            "tormenta_s1_o_mas": u["flux"] >= UMBRAL_S1_PFU, "umbral_s1_pfu": UMBRAL_S1_PFU, "satelite": u.get("satellite"), "fuente": URL_PROT,
            "serie": [round(x["flux"], 3) for x in s]}


def rayosx(serie: list | None = None) -> dict:
    s = serie if serie is not None else [x for x in _get(URL_XR) if x.get("energy") == "0.1-0.8nm"]
    u = s[-1]
    return {"disponible": True, "flujo_wm2": u["flux"], "clase": clase_xrays(u["flux"]), "ts_utc": u["time_tag"], "max_ventana": clase_xrays(max(x["flux"] for x in s)), "fuente": URL_XR}


def seguro(f: Callable[[], dict], fuente: str) -> dict:
    try:
        return f()
    except Exception as e:                                                # noqa: BLE001  la ausencia es dato: se dice, no se rellena
        return {"disponible": False, "fuente": fuente, "error": type(e).__name__}
