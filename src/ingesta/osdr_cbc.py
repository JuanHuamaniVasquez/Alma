"""IN-6 · Lector del hemograma REAL de la misión Inspiration4 (NASA OSDR, OSD-569, `LSDS-7_Complete_Blood_Count_CBC_TRANSFORMED.csv`). DATOS REALES DE ASTRONAUTAS (4 civiles).

Fuente: https://osdr.nasa.gov/bio/repo/data/studies/OSD-569 · descargado con la API de OSDR el 2026-11-15 (sha256 abajo) · 28 filas = 4 personas × 7 extracciones.
Extracciones: L-92, L-44, L-3 (antes del vuelo) y R+1, R+45, R+82, R+194 (después); NO hay extracciones en vuelo.
Conciliación (regla de «el libro cierra» aplicada al hemograma, acta FB-024): conteo absoluto = porcentaje × leucocitos totales (±10 %); si no, `sospechoso`.
"""
from __future__ import annotations

import csv
import hashlib
import re
from dataclasses import dataclass
from pathlib import Path

SHA256 = "32e4f9c97d3b636b5d5c2e72dab8c4d3319dee64c437508b092dad04603b2b8f"
FUENTE = "NASA OSDR OSD-569 (SpaceX Inspiration4), LSDS-7 Complete Blood Count"
PRE = ("L-92", "L-44", "L-3")
POST = ("R+1", "R+45", "R+82", "R+194")
DIFERENCIALES = ("neutrophils", "lymphocytes", "monocytes", "eosinophils", "basophils")
TOL_CONCILIACION = 0.10


@dataclass(frozen=True)
class Fila:
    persona: str      # C001…C004 (pseudónimo de la fuente)
    t: str            # L-92 … R+194
    v: dict           # nombre_corto → valor (float | None)
    sospechosos: frozenset   # nombres cuyo valor NO concilia


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def cargar(ruta: Path) -> list[Fila]:
    if hashlib.sha256(ruta.read_bytes()).hexdigest() != SHA256:
        raise ValueError("el CSV no coincide con el sha256 preregistrado")
    out = []
    with ruta.open(encoding="utf-8-sig", newline="") as f:
        for r in csv.DictReader(f):
            m = re.match(r"(C\d+)_whole-blood_(.+?)_cbc", r["Sample Name"])
            persona, t = m.group(1), m.group(2)
            g = lambda col: _num(r.get(col))                                              # noqa: E731
            wbc = g("white_blood_cell_count_value_thousand_per_microliter")
            v = {"wbc": wbc, "hb": g("hemoglobin_value_percent"), "hct": g("hematocrit_value_percent"), "plt": g("platelet_count_value_thousand_per_microliter")}
            sosp, suma = set(), 0.0
            for d in DIFERENCIALES:
                absol, pct = g(f"absolute_{d}_value_cells_per_microliter"), g(f"{d}_value_percent")
                v[f"abs_{d}"], v[f"pct_{d}"] = absol, pct
                suma += pct or 0.0
                if None not in (absol, pct, wbc) and pct > 0 and wbc > 0:
                    esperado = pct / 100.0 * wbc * 1000.0
                    if abs(absol - esperado) > TOL_CONCILIACION * esperado:
                        sosp.add(f"abs_{d}")
            if abs(suma - 100.0) > 3.0:
                sosp |= {f"abs_{d}" for d in DIFERENCIALES}                                # la fila entera no concilia
            nl = (v["abs_neutrophils"] / v["abs_lymphocytes"]) if v["abs_neutrophils"] and v["abs_lymphocytes"] else None
            v["nlr"] = nl
            if sosp & {"abs_neutrophils", "abs_lymphocytes"}:
                sosp.add("nlr")
            out.append(Fila(persona, t, v, frozenset(sosp)))
    return out
