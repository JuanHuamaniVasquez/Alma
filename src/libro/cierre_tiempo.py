"""M2.9 · Cierre del tiempo (1440 min/día) como compuerta de calidad de la línea `tiempo` de LB-1 → DC-04 `estado_linea`.

Regla (de la identidad contable del export de Fitbit, NO una ley fisiológica; docs/ideas-extremas.md I-02):
    sedentario + ligero + moderado + muy activo + dormido + despierto = 1440 min  (tolerancia ±1 min: redondeo del export)
- cierra (|residuo| ≤ 1)                → `limpio`
- no cierra (|residuo| > 1)             → `sospechoso`  (un componente mal medido o fuera de la ventana de 24 h)
- falta algún componente (p. ej. no hubo registro de sueño) → `sospechoso` con motivo «incompleto»: la ausencia es dato
Medido en LifeSnaps (S-07): ver el resultado en docs/ideas-extremas.md I-02. Nunca se rellena ni se corrige un valor.
"""
from __future__ import annotations

from dataclasses import dataclass

from src.contratos.dc04_libro import EstadoLinea

MINUTOS_DIA = 1440.0
TOLERANCIA_MIN = 1.0
COMPONENTES = ("sedentary_minutes", "lightly_active_minutes", "moderately_active_minutes", "very_active_minutes",
               "minutesAsleep", "minutesAwake")


@dataclass(frozen=True)
class CierreTiempo:
    estado: EstadoLinea
    residuo_min: float | None
    motivo: str


def _num(v) -> float | None:
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return f if f == f else None  # descarta NaN


def evaluar_dia(fila: dict) -> CierreTiempo:
    valores = {c: _num(fila.get(c)) for c in COMPONENTES}
    faltan = [c for c, v in valores.items() if v is None]
    if faltan:
        return CierreTiempo(EstadoLinea.SOSPECHOSO, None, "incompleto: falta " + ", ".join(faltan))
    r = sum(valores.values()) - MINUTOS_DIA  # type: ignore[arg-type]
    if abs(r) <= TOLERANCIA_MIN:
        return CierreTiempo(EstadoLinea.LIMPIO, r, "cierra a 1440 min")
    return CierreTiempo(EstadoLinea.SOSPECHOSO, r, f"no cierra: residuo {r:+.0f} min")
