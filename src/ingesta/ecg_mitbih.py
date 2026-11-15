"""IN-5 · Lector del formato PhysioNet (señal 212 + anotaciones .atr) para el registro 100 de la MIT-BIH Arrhythmia Database. DATOS REALES, NO astronautas.

Fuente: Moody & Mark 2001, doi:10.1109/51.932724 · PhysioNet (Goldberger et al. 2000, doi:10.1161/01.CIR.101.23.e215) · v1.0.0, doi:10.13026/C2F305 · licencia
Open Data Commons Attribution v1.0 (verificada en la página del proyecto 2026-11-15). Registro 100: paciente ambulatorio anonimizado, 30 min, 360 Hz, 2 canales.
Formato 212: 3 bytes = 2 muestras de 12 bits (CANAL 0 y CANAL 1 intercaladas). Físico = (adc − base) / ganancia (mV).
Anotaciones: palabras de 16 bits (código en los 6 bits altos, Δtiempo en 10 bits); 59 = SKIP (Δ de 32 bits), 63 = AUX (texto), 60–62 = NUM/SUB/CHN.
"""
from __future__ import annotations

import hashlib
import struct
from dataclasses import dataclass
from pathlib import Path

FS = 360
GANANCIA, BASE = 200.0, 1024
BANNER = "REAL"
FUENTE = "PhysioNet MIT-BIH Arrhythmia Database v1.0.0, record 100 (ODC-By 1.0; not astronauts)"
SHA256 = {"100.dat": "b2ea3c250e56e48f4b7b90697832b8ecd1afa1e0bb31f2dcfea4ed6e1075a639", "100.atr": "8d8a5349fb16638ebbf649f1779d12e96d91b736b2aafe59db43719ae583d471",
          "100.hea": "60ebc904c7bf3e04d142638d3fd5c903e8dc9f10f1ea3264e07926aa089ee75e"}
BEAT_CODES = {1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 34, 35, 38, 41}      # latidos (N, L, R, A, a, J, S, V, F, ...), no ritmo/ruido


@dataclass(frozen=True)
class Registro:
    mlii: tuple[float, ...]          # canal 0 (MLII), mV
    latidos_ref: tuple[int, ...]     # muestras anotadas por humanos (referencia)


def _verificar(carpeta: Path) -> None:
    for n, h in SHA256.items():
        if hashlib.sha256((carpeta / n).read_bytes()).hexdigest() != h:
            raise ValueError(f"{n}: el archivo no coincide con el sha256 registrado")


def leer_senal(dat: bytes, canal: int = 0) -> list[float]:
    """Cada tripleta de 3 bytes trae UNA muestra del canal 0 y UNA del canal 1 (formato 212): se devuelve la del canal pedido, en mV."""
    out = []
    for i in range(0, len(dat) - 2, 3):
        b0, b1, b2 = dat[i], dat[i + 1], dat[i + 2]
        v = (b0 | ((b1 & 0x0F) << 8)) if canal == 0 else (b2 | ((b1 & 0xF0) << 4))
        out.append(((v - 4096 if v >= 2048 else v) - BASE) / GANANCIA)
    return out


def leer_anotaciones(atr: bytes) -> list[int]:
    t, i, out = 0, 0, []
    while i + 2 <= len(atr):
        w = struct.unpack_from("<H", atr, i)[0]; i += 2
        if w == 0:
            break
        code, delta = w >> 10, w & 0x3FF
        if code == 59:                                         # SKIP: intervalo de 32 bits (palabra alta primero)
            hi, lo = struct.unpack_from("<HH", atr, i); i += 4
            t += (hi << 16) | lo
        elif code == 63:                                       # AUX: texto de `delta` bytes, alineado a palabra
            i += delta + (delta & 1)
        elif code in (60, 61, 62):
            pass
        else:
            t += delta
            if code in BEAT_CODES:
                out.append(t)
    return out


def cargar(carpeta: Path) -> Registro:
    _verificar(carpeta)
    return Registro(tuple(leer_senal((carpeta / "100.dat").read_bytes())), tuple(leer_anotaciones((carpeta / "100.atr").read_bytes())))
