"""La tripulación SIMULADA de 5 (X-15): personajes FICTICIOS del universo simulado, nunca personas reales ni astronautas reales.

Cada uno tiene indicativo, rol, color de franja y apariencia estilizada. Su estado corporal que se muestra en la vitrina NO es de ficción ni de astronautas:
es el estado de una persona cotidiana anónima de LifeSnaps asignada como SUSTITUTO (`SEMILLA_SUSTITUTOS`), siempre rotulado «stand-in».
La tripulación fija además el tamaño del consumo del hábitat simulado (aire y agua: `sembrar_demo`). OJO: FB-005-D1 se preregistró con 4 tripulantes y su hash no cambia.
"""
from __future__ import annotations

from dataclasses import dataclass

SEMILLA_SUSTITUTOS = 20261113


@dataclass(frozen=True)
class Tripulante:
    indicativo: str
    rol: str
    color: str       # franja del uniforme (sin cian: paleta propia)
    piel: str
    pelo: str
    peinado: str     # short · bun · buzz · long
    complexion: float  # 1.0 = media; escala de anchura del torso


ROSTER: tuple[Tripulante, ...] = (
    Tripulante("VEGA", "Commander", "#d9a441", "#e6b98f", "#2a1d14", "short", 1.04),
    Tripulante("LYRA", "Pilot", "#86a982", "#c68a5e", "#1a1410", "bun", 0.94),
    Tripulante("ALTAIR", "Flight Engineer", "#c8553d", "#8d5a3a", "#14100c", "buzz", 1.08),
    Tripulante("CASTOR", "Medical Officer", "#c98aa0", "#efc9a6", "#b9a37a", "short", 0.98),
    Tripulante("RIGEL", "Mission Specialist", "#8d86c9", "#5c3a28", "#2b1e18", "long", 1.0),
)
TRIPULACION = len(ROSTER)
assert TRIPULACION == 5
