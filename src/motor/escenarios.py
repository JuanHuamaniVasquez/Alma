"""IN-4 · Inyector de escenarios de LA TORMENTA — UNIVERSO SIMULADO (X-14).

Una tormenta geomagnética sintética, determinista y reproducible: 12 lecturas de Kp cada 3 h (calma → subida → pico → decaimiento).
El PICO es exactamente el umbral NOAA de la escala pedida (G1 = Kp 5 … G5 = Kp 9; S-15, https://www.swpc.noaa.gov/noaa-scales-explanation).
Regla de honestidad: todo evento sale con fuente `simulador`, tipo `inyeccion_escenario` y banner SIMULADO (DC-03 lo exige); la receta
y la semilla pública viajan con la respuesta y el hash cubre la serie completa, de modo que cualquiera la regenera y la verifica.
No describe un efecto fisiológico: solo el evento con firma física (mandamiento: el hábitat es variable de entrada del cuerpo, no el paciente).
"""
from __future__ import annotations

import hashlib
import json
import random
from datetime import UTC, datetime, timedelta

from src.contratos.comunes import Banner
from src.contratos.dc03_eventos import DC03Evento, FuenteEvento, TipoEvento

UMBRAL_KP = {"G1": 5.0, "G2": 6.0, "G3": 7.0, "G4": 8.0, "G5": 9.0}
PERFIL = (-4.5, -4.5, -2.0, -1.0, 0.0, -1.0, -2.0, -3.0, -3.5, -4.0, -4.0, -4.0)   # desplazamiento respecto al pico, por lectura
PASO_H = 3
RECETA = ("Kp_i = clip(pico + perfil_i + ruido_i, 0, 9) en tercios; perfil = (-4.5, -4.5, -2, -1, 0, -1, -2, -3, -3.5, -4, -4, -4); "
          "ruido ~ N(0, 0.2) con random.Random(semilla); una lectura cada 3 h; la lectura 4 es el pico y vale exactamente el umbral NOAA de la escala")
RECETA_EN = ("Kp_i = clip(peak + profile_i + noise_i, 0, 9) in thirds; profile = (-4.5, -4.5, -2, -1, 0, -1, -2, -3, -3.5, -4, -4, -4); "
             "noise ~ N(0, 0.2) from random.Random(seed); one reading every 3 h; reading 4 is the peak and equals the NOAA threshold of the scale exactly")


def _tercios(x: float) -> float:
    return round(round(x * 3) / 3, 2)


def tormenta(escala: str, semilla: int = 20261113, inicio: datetime | None = None) -> list[DC03Evento]:
    if escala not in UMBRAL_KP:
        raise ValueError(f"escala desconocida: {escala!r} (válidas: {', '.join(UMBRAL_KP)})")
    pico = UMBRAL_KP[escala]
    t0 = (inicio or datetime(2026, 11, 15, 0, 0, tzinfo=UTC)).astimezone(UTC)
    rng = random.Random(semilla)
    kps = []
    for i, d in enumerate(PERFIL):
        ruido = rng.gauss(0.0, 0.2)                          # se consume siempre, para que la serie sea estable ante cambios de pico
        v = pico if i == 4 else min(_tercios(max(0.0, pico + d + ruido)), pico - 1 / 3)   # nada iguala ni supera al pico
        kps.append(v)
    serie = json.dumps({"escala": escala, "semilla": semilla, "kp": kps, "t0": t0.isoformat()}, sort_keys=True)
    h = hashlib.sha256(serie.encode()).hexdigest()
    out = []
    for i, kp in enumerate(kps):
        t = t0 + timedelta(hours=PASO_H * i)
        out.append(DC03Evento(evento_id=f"sim-{escala}-{semilla}-{i:02d}", ts_utc_inicio=t, ts_utc_fin=t, tipo=TipoEvento.INYECCION_ESCENARIO,
                              fuente=FuenteEvento.SIMULADOR, parametros={"kp": kp}, hash_lectura_cruda=h, banner=Banner.SIMULADO))
    return out
