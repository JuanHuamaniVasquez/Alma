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


_ULT_ARCHIVO: dict[str, float] = {}
ARCHIVO_CADA_S = 600.0      # una lectura cruda archivada por fuente cada 10 min (la fuente cambia cada minuto; sin tope llenaría el disco)
ULTIMOS_HASHES: dict[str, str] = {}
ARCHIVADOS_NUEVOS: set[str] = set()      # fuentes cuya lectura se archivó desde la última vez que se registraron como evento (DC-03) e intento (DC-13)


def _get(url: str, t: float = 8.0):
    """Lee la fuente; el cuerpo CRUDO se hashea siempre y se archiva (MP-3, `src/ingesta/archivo.py`) con tope temporal: mandamiento 1 — ninguna lectura sin hash ni archivo."""
    import time
    from pathlib import Path

    from . import archivo
    req = urllib.request.Request(url, headers={"User-Agent": "ALMA-TONO-LAB/0.1 (student project; contact: repo issues)"})
    with urllib.request.urlopen(req, timeout=t) as r:                      # noqa: S310 (URL fija, https)
        cuerpo = r.read()
    ULTIMOS_HASHES[url] = archivo.sha256_hex(cuerpo)
    if time.time() - _ULT_ARCHIVO.get(url, 0.0) >= ARCHIVO_CADA_S:
        nombre = url.rsplit("/", 1)[-1].replace(".json", "") or "iss"
        archivo.archivar(cuerpo, fuente="entorno", nombre=nombre, url=url, ts=archivo.ahora_utc(), raiz=Path(__file__).resolve().parents[2] / "data" / "entorno_vivo")      # carpeta propia (ignorada por git): el manifiesto de SWPC no se ensucia
        _ULT_ARCHIVO[url] = time.time()
        ARCHIVADOS_NUEVOS.add(url)
    return json.loads(cuerpo)


def clase_xrays(flujo: float) -> str:
    for letra, techo in (("A", 1e-7), ("B", 1e-6), ("C", 1e-5), ("M", 1e-4)):
        if flujo < techo:
            return f"{letra}{flujo / (techo / 10):.1f}"
    return f"X{flujo / 1e-4:.1f}"


def iss(datos: dict | None = None) -> dict:
    d = datos if datos is not None else _get(URL_ISS)
    return {"disponible": True, "lat": round(d["latitude"], 2), "lon": round(d["longitude"], 2), "alt_km": round(d["altitude"], 1), "vel_kms": round(d["velocity"] / 3600, 2),
            "visibilidad": d["visibility"], "sol_lat": round(d["solar_lat"], 2), "sol_lon": round(d["solar_lon"], 2),
            "ts_utc": datetime.fromtimestamp(d["timestamp"], UTC).strftime("%Y-%m-%dT%H:%M:%SZ"), "fuente": URL_ISS, "hash_lectura_cruda": ULTIMOS_HASHES.get(URL_ISS),
            "a_la_luz": d["visibility"] == "daylight"}


def protones(serie: list | None = None) -> dict:
    s = serie if serie is not None else [x for x in _get(URL_PROT) if x.get("energy") == ">=10 MeV"]
    u = s[-1]
    return {"disponible": True, "pfu": u["flux"], "ts_utc": u["time_tag"], "max_ventana_pfu": max(x["flux"] for x in s), "n_lecturas": len(s),
            "tormenta_s1_o_mas": u["flux"] >= UMBRAL_S1_PFU, "umbral_s1_pfu": UMBRAL_S1_PFU, "satelite": u.get("satellite"), "fuente": URL_PROT, "hash_lectura_cruda": ULTIMOS_HASHES.get(URL_PROT),
            "serie": [round(x["flux"], 3) for x in s]}


def rayosx(serie: list | None = None) -> dict:
    s = serie if serie is not None else [x for x in _get(URL_XR) if x.get("energy") == "0.1-0.8nm"]
    u = s[-1]
    return {"disponible": True, "flujo_wm2": u["flux"], "clase": clase_xrays(u["flux"]), "ts_utc": u["time_tag"], "max_ventana": clase_xrays(max(x["flux"] for x in s)), "fuente": URL_XR, "hash_lectura_cruda": ULTIMOS_HASHES.get(URL_XR)}


def seguro(f: Callable[[], dict], fuente: str) -> dict:
    try:
        return f()
    except Exception as e:                                                # noqa: BLE001  la ausencia es dato: se dice, no se rellena
        return {"disponible": False, "fuente": fuente, "error": type(e).__name__}


def a_eventos(env: dict) -> list:
    """DC-03 (v0.2.9): cada lectura archivada entra como EVENTO con su `hash_lectura_cruda` (mandamiento 1: el consumidor lee del libro de eventos, no de la fuente)."""
    from src.contratos.comunes import Banner
    from src.contratos.dc03_eventos import DC03Evento, FuenteEvento, TipoEvento
    out = []
    iss_, p, x = env["iss"], env["protones"], env["rayosx"]
    plan = [(iss_, URL_ISS, TipoEvento.POSICION_ESTACION, FuenteEvento.WHERETHEISS,
             lambda r: {"latitud_deg": r["lat"], "longitud_deg": r["lon"], "altitud_km": r["alt_km"], "velocidad_kms": r["vel_kms"], "luz_solar": 1.0 if r["a_la_luz"] else 0.0}),
            (p, URL_PROT, TipoEvento.LECTURA_PROTONES, FuenteEvento.SWPC, lambda r: {"flujo_protones_pfu": r["pfu"]}),
            (x, URL_XR, TipoEvento.LECTURA_RAYOSX, FuenteEvento.SWPC, lambda r: {"flujo_rayosx_wm2": r["flujo_wm2"]})]
    for r, url, tipo, fuente, params in plan:
        if not r.get("disponible") or url not in ARCHIVADOS_NUEVOS or not r.get("hash_lectura_cruda"):
            continue
        ts = datetime.strptime(r["ts_utc"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC)
        out.append(DC03Evento(evento_id=f"entorno-{tipo.value}-{r['ts_utc']}-{r['hash_lectura_cruda'][:12]}", ts_utc_inicio=ts, ts_utc_fin=ts, tipo=tipo, fuente=fuente,
                              parametros=params(r), hash_lectura_cruda=r["hash_lectura_cruda"], banner=Banner.REAL))
    return out


def a_intentos(env: dict) -> list:
    """DC-13: los fallos SIEMPRE se registran (la ausencia es dato); los éxitos, cuando la lectura se archiva."""
    from src.contratos.comunes import Banner
    from src.contratos.dc03_eventos import FuenteEvento
    from src.contratos.dc13_intento_ingesta import DC13Intento, ResultadoIntento
    ahora = datetime.now(UTC)
    out = []
    for clave, url, fuente in (("iss", URL_ISS, FuenteEvento.WHERETHEISS), ("protones", URL_PROT, FuenteEvento.SWPC), ("rayosx", URL_XR, FuenteEvento.SWPC)):
        r = env[clave]
        if r.get("disponible"):
            if url in ARCHIVADOS_NUEVOS and r.get("hash_lectura_cruda"):
                out.append(DC13Intento(intento_id=f"entorno-{clave}-{ahora:%Y%m%dT%H%M%S}-{r['hash_lectura_cruda'][:8]}", ts_utc=ahora, fuente=fuente, url=url,
                                       resultado=ResultadoIntento.OK, http_status=200, hash_lectura_cruda=r["hash_lectura_cruda"], banner=Banner.REAL))
        else:
            out.append(DC13Intento(intento_id=f"entorno-{clave}-{ahora:%Y%m%dT%H%M%S}-fallo", ts_utc=ahora, fuente=fuente, url=url, resultado=ResultadoIntento.FALLO,
                                   http_status=None, error=str(r.get("error", "desconocido")), banner=Banner.REAL))
    return out
