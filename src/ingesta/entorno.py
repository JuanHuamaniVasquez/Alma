"""IN-3b · Entorno en vivo REAL de la tripulación: posición/luz de la ISS, protones energéticos GOES y rayos X solares (NOAA SWPC). M7.1.

Fuentes (verificadas 2026-11-15; sin clave):
  · ISS: https://api.wheretheiss.at/v1/satellites/25544 (posición derivada de elementos orbitales; `visibility` = daylight/eclipsed/visible; límite ≈ 1 petición/s).
  · Protones GOES ≥10 MeV: https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json — la escala de tormentas de radiación S de NOAA
    arranca en **10 pfu** (≥10 MeV) (NOAA SWPC, spaceweather.gov/node/415); por encima se declara «S1 o más» sin afirmar el nivel exacto.
  · Rayos X 0,1–0,8 nm (GOES): https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json — clase de fulguración por flujo (A<1e-7, B<1e-6, C<1e-5, M<1e-4, X≥1e-4 W/m²).
  · Electrones GOES ≥2 MeV (cinturones atrapados): https://services.swpc.noaa.gov/json/goes/primary/integral-electrons-1-day.json — NOAA SWPC emite la alerta ALTEF3 cuando el flujo
    ≥2 MeV en órbita geoestacionaria supera **1 000 pfu** (documentación de alertas de SWPC, leída 2026-11-15). v0.2.10.
  · Monitor de neutrones de Oulu (Finlandia) vía NMDB: https://www.nmdb.eu/nest/draw_graph.php (salida ascii, 1 h, corregido por eficiencia). Es el **proxy en tierra** de los rayos cósmicos
    galácticos que superan el corte geomagnético; NO es una dosis. Licencia: gratis no comercial con reconocimiento a NMDB y a Oulu (texto en `ACK_NMDB`). v0.2.10.
Todo es REAL y de ahora mismo; si una fuente no responde, el campo viene `disponible: false` (la ausencia es dato, no se rellena).
"""
from __future__ import annotations

import json
import re
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime

URL_ISS = "https://api.wheretheiss.at/v1/satellites/25544"
URL_PROT = "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json"
URL_XR = "https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json"
URL_EL = "https://services.swpc.noaa.gov/json/goes/primary/integral-electrons-1-day.json"
URL_AL = "https://services.swpc.noaa.gov/products/alerts.json"
URL_NM = "https://www.nmdb.eu/nest/draw_graph.php"          # clave estable de la fuente (la consulta lleva fechas y cambia)
UMBRAL_S1_PFU = 10.0
UMBRAL_ELECTRONES_PFU = 1000.0
ESTACION_NM = "OULU"
ACK_NMDB = "We acknowledge the NMDB database (www.nmdb.eu), founded under the European Union's FP7 programme (contract no. 213007), and the PIs of individual neutron monitors: Oulu (Sodankyla Geophysical Observatory of the University of Oulu, Finland)."


_ULT_ARCHIVO: dict[str, float] = {}
ARCHIVO_CADA_S = 600.0      # una lectura cruda archivada por fuente cada 10 min (la fuente cambia cada minuto; sin tope llenaría el disco)
ULTIMOS_HASHES: dict[str, str] = {}
ARCHIVADOS_NUEVOS: set[str] = set()      # fuentes cuya lectura se archivó desde la última vez que se registraron como evento (DC-03) e intento (DC-13)


def _leer(url: str, clave: str, nombre: str, t: float = 8.0) -> bytes:
    """Lee la fuente; el cuerpo CRUDO se hashea siempre y se archiva (MP-3, `src/ingesta/archivo.py`) con tope temporal: mandamiento 1 — ninguna lectura sin hash ni archivo."""
    import time
    from pathlib import Path

    from . import archivo
    req = urllib.request.Request(url, headers={"User-Agent": "ALMA-TONO-LAB/0.1 (student project; contact: repo issues)"})
    with urllib.request.urlopen(req, timeout=t) as r:                      # noqa: S310 (URL fija, https)
        cuerpo = r.read()
    ULTIMOS_HASHES[clave] = archivo.sha256_hex(cuerpo)
    if time.time() - _ULT_ARCHIVO.get(clave, 0.0) >= ARCHIVO_CADA_S:
        archivo.archivar(cuerpo, fuente="entorno", nombre=nombre, url=url, ts=archivo.ahora_utc(), raiz=Path(__file__).resolve().parents[2] / "data" / "entorno_vivo")      # carpeta propia (ignorada por git)
        _ULT_ARCHIVO[clave] = time.time()
        ARCHIVADOS_NUEVOS.add(clave)
    return cuerpo


def _get(url: str, t: float = 8.0):
    return json.loads(_leer(url, url, url.rsplit("/", 1)[-1].replace(".json", "") or "iss", t))


def _url_nm(ahora: datetime | None = None, dias: int = 3) -> str:
    """Consulta ascii de 1 h de la estación de Oulu para los últimos `dias` días (parámetros de la interfaz NEST de NMDB)."""
    from datetime import timedelta
    fin = ahora or datetime.now(UTC)
    ini = fin - timedelta(days=dias)
    return (f"{URL_NM}?formchk=1&stations%5B%5D={ESTACION_NM}&tabchoice=1h&dtype=corr_for_efficiency&tresolution=60&force=1&yunits=0&date_choice=bydate"
            f"&start_day={ini.day}&start_month={ini.month}&start_year={ini.year}&start_hour={ini.hour}&start_min=0"
            f"&end_day={fin.day}&end_month={fin.month}&end_year={fin.year}&end_hour={fin.hour}&end_min=59&output=ascii")


def _get_nm() -> str:
    return _leer(_url_nm(), URL_NM, "neutrones_oulu", 15.0).decode("utf-8", "replace")


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


def electrones(serie: list | None = None) -> dict:
    s = serie if serie is not None else [x for x in _get(URL_EL) if x.get("energy") == ">=2 MeV"]
    u = s[-1]
    return {"disponible": True, "pfu": u["flux"], "ts_utc": u["time_tag"], "max_ventana_pfu": max(x["flux"] for x in s), "n_lecturas": len(s), "alerta_swpc": u["flux"] >= UMBRAL_ELECTRONES_PFU,
            "umbral_swpc_pfu": UMBRAL_ELECTRONES_PFU, "satelite": u.get("satellite"), "fuente": URL_EL, "hash_lectura_cruda": ULTIMOS_HASHES.get(URL_EL), "serie": [round(x["flux"], 1) for x in s]}


def parsear_nmdb(texto: str) -> list[tuple[str, float]]:
    """Filas `YYYY-MM-DD HH:MM:SS;valor` dentro del bloque de la respuesta ascii de NMDB; ignora comentarios (`#`) y valores ausentes."""
    import re
    m = re.search(r"<pre><code>(.*?)</code></pre>", texto, re.S)
    out = []
    for linea in (m.group(1) if m else texto).splitlines():
        p = linea.strip().split(";")
        if len(p) == 2 and re.fullmatch(r"\d{4}-\d\d-\d\d \d\d:\d\d:\d\d", p[0]):
            try:
                out.append((p[0].replace(" ", "T") + "Z", float(p[1])))
            except ValueError:
                continue
    return out


def neutrones(texto: str | None = None) -> dict:
    filas = parsear_nmdb(texto if texto is not None else _get_nm())
    if not filas:
        raise ValueError("NMDB sin filas")
    v = [x for _, x in filas]
    ult = v[-1]
    base = sorted(v)[len(v) // 2]                                         # mediana de la ventana (≈ 72 h)
    return {"disponible": True, "estacion": "Oulu (Finland)", "cps": ult, "ts_utc": filas[-1][0], "mediana_ventana": round(base, 3), "variacion_pct": round(100 * (ult / base - 1), 2),
            "min_ventana": min(v), "max_ventana": max(v), "n_lecturas": len(v), "fuente": URL_NM, "hash_lectura_cruda": ULTIMOS_HASHES.get(URL_NM), "serie": [round(x, 2) for x in v], "reconocimiento": ACK_NMDB}


# Escalas de clima espacial de NOAA (https://www.swpc.noaa.gov/noaa-scales-explanation, leída 2026-11-15): umbrales de nivel 1…5.
ESCALA_S_PFU = (10.0, 100.0, 1e3, 1e4, 1e5)          # protones ≥10 MeV (tormenta de radiación)
ESCALA_R_WM2 = (1e-5, 5e-5, 1e-4, 1e-3, 2e-3)       # rayos X 0,1–0,8 nm: M1, M5, X1, X10, X20 (apagón de radio)
ESCALA_G_KP = (5.0, 6.0, 7.0, 8.0, 9.0)             # Kp (tormenta geomagnética; G5 = Kp 9)
NIVEL_DE_AVISO = {"S": 1, "G": 1, "R": 3}            # a partir de aquí ALMA avisa en todas las salas (R1/R2 son frecuentes y no alteran a una tripulación)


def nivel(valor: float | None, umbrales: tuple[float, ...]) -> int:
    return 0 if valor is None else sum(valor >= u for u in umbrales)


def niveles(env: dict, kp: float | None) -> dict:
    """Nivel S/R/G AHORA, calculado de las lecturas ya contratadas (DC-03) con los umbrales públicos de NOAA. Cada nivel lleva su regla exacta imprimible (mandamiento 3)."""
    p, x = env.get("protones", {}), env.get("rayosx", {})
    out = {"S": {"nivel": nivel(p.get("pfu") if p.get("disponible") else None, ESCALA_S_PFU), "valor": p.get("pfu"), "unidad": "pfu",
                 "regla": "S1 or higher if GOES protons ≥10 MeV reach 10 pfu (S2 100, S3 1,000, S4 10,000, S5 100,000)", "nombre": "Solar radiation storm", "fuente": URL_PROT},
           "R": {"nivel": nivel(x.get("flujo_wm2") if x.get("disponible") else None, ESCALA_R_WM2), "valor": x.get("flujo_wm2"), "unidad": "W/m²",
                 "regla": "R1 = M1 flare (1e-5 W/m²), R2 = M5, R3 = X1 (1e-4), R4 = X10, R5 = X20", "nombre": "Radio blackout", "fuente": URL_XR},
           "G": {"nivel": nivel(kp, ESCALA_G_KP), "valor": kp, "unidad": "Kp",
                 "regla": "G1 = Kp 5, G2 = Kp 6, G3 = Kp 7, G4 = Kp 8, G5 = Kp 9", "nombre": "Geomagnetic storm", "fuente": "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"}}
    for k, v in out.items():
        v["aviso"] = v["nivel"] >= NIVEL_DE_AVISO[k]
        v["etiqueta"] = f"{k}{v['nivel']}" if v["nivel"] else f"{k}0"
    return out


_TITULAR_AVISO = re.compile(r"^(CONTINUED |EXTENDED )?(WATCH|WARNING|ALERT|SUMMARY|CANCEL WATCH)[^\n]*", re.MULTILINE)


def avisos(lista: list | None = None, ahora: datetime | None = None, horas: float = 72.0, maximo: int = 6) -> dict:
    """Mensajes OFICIALES de NOAA SWPC de las últimas `horas` (alerts.json): se muestran tal cual, con su código y hora. NO son detecciones de ALMA (la decisión de no convertirlos en
    eventos DC-03 vive en `src/ingesta/swpc.py`): son lo que NOAA dijo, citado."""
    from datetime import timedelta
    L = lista if lista is not None else _get(URL_AL)
    t0 = (ahora or datetime.now(UTC)) - timedelta(hours=horas)
    out, vistos = [], set()
    for m in L:
        ts = datetime.strptime(m["issue_datetime"][:19], "%Y-%m-%d %H:%M:%S").replace(tzinfo=UTC)
        h = _TITULAR_AVISO.search(m["message"].replace("\r", ""))
        if ts < t0 or not h:
            continue
        titular = re.sub(r"\s+", " ", h.group(0)).strip()
        if titular in vistos:
            continue
        vistos.add(titular)
        out.append({"codigo": m["product_id"], "ts_utc": ts.strftime("%Y-%m-%dT%H:%M:%SZ"), "titular": titular})
        if len(out) >= maximo:
            break
    return {"disponible": True, "mensajes": out, "fuente": URL_AL, "hash_lectura_cruda": ULTIMOS_HASHES.get(URL_AL)}


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
    el, nm = env.get("electrones", {"disponible": False}), env.get("neutrones", {"disponible": False})
    plan = [(iss_, URL_ISS, TipoEvento.POSICION_ESTACION, FuenteEvento.WHERETHEISS,
             lambda r: {"latitud_deg": r["lat"], "longitud_deg": r["lon"], "altitud_km": r["alt_km"], "velocidad_kms": r["vel_kms"], "luz_solar": 1.0 if r["a_la_luz"] else 0.0}),
            (p, URL_PROT, TipoEvento.LECTURA_PROTONES, FuenteEvento.SWPC, lambda r: {"flujo_protones_pfu": r["pfu"]}),
            (x, URL_XR, TipoEvento.LECTURA_RAYOSX, FuenteEvento.SWPC, lambda r: {"flujo_rayosx_wm2": r["flujo_wm2"]}),
            (el, URL_EL, TipoEvento.LECTURA_ELECTRONES, FuenteEvento.SWPC, lambda r: {"flujo_electrones_pfu": r["pfu"]}),
            (nm, URL_NM, TipoEvento.LECTURA_NEUTRONES, FuenteEvento.NMDB, lambda r: {"tasa_neutrones_cps": r["cps"]})]
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
    for clave, url, fuente in (("iss", URL_ISS, FuenteEvento.WHERETHEISS), ("protones", URL_PROT, FuenteEvento.SWPC), ("rayosx", URL_XR, FuenteEvento.SWPC),
                                 ("electrones", URL_EL, FuenteEvento.SWPC), ("neutrones", URL_NM, FuenteEvento.NMDB)):
        if clave not in env:
            continue
        r = env[clave]
        if r.get("disponible"):
            if url in ARCHIVADOS_NUEVOS and r.get("hash_lectura_cruda"):
                out.append(DC13Intento(intento_id=f"entorno-{clave}-{ahora:%Y%m%dT%H%M%S}-{r['hash_lectura_cruda'][:8]}", ts_utc=ahora, fuente=fuente, url=url,
                                       resultado=ResultadoIntento.OK, http_status=200, hash_lectura_cruda=r["hash_lectura_cruda"], banner=Banner.REAL))
        else:
            out.append(DC13Intento(intento_id=f"entorno-{clave}-{ahora:%Y%m%dT%H%M%S}-fallo", ts_utc=ahora, fuente=fuente, url=url, resultado=ResultadoIntento.FALLO,
                                   http_status=None, error=str(r.get("error", "desconocido")), banner=Banner.REAL))
    return out
