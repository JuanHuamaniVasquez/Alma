"""IN-1 · Incertidumbre del sensor DECLARADA y con fuente (DC-01 exige `incertidumbre_sensor`).

Política (docs/politica-de-datos.md): una σ de sensor no se inventa. Aquí solo hay σ derivadas de
límites de acuerdo **publicados** en un estudio de validación. Un indicador sin σ verificada NO se
emite (`sigma_de` lanza `SinIncertidumbreVerificada`): «si el dato no existe, el ítem se bloquea».

σ = (LoA_sup − LoA_inf) / (2 · 1.96)  — la desviación típica de las diferencias de un Bland-Altman,
cuyos límites de acuerdo se definen como sesgo ± 1.96·SD (el propio paper lo define así).
"""
from __future__ import annotations

from dataclasses import dataclass

from src.contratos.comunes import IndicadorSensor

FUENTE = ("Validation of Fitbit Charge 2 Sleep and Heart Rate Estimates Against Polysomnographic Measures in "
          "Shift Workers: Naturalistic Study. JMIR 2021;23(10):e26476. doi:10.2196/26476 · PMC8527385")
ENLACE = "https://pmc.ncbi.nlm.nih.gov/articles/PMC8527385/"

# Tabla «Bland-Altman statistics» del paper: (límite inferior, límite superior)
LOA_TST_MIN = (-204.3, 196.3)   # tiempo total de sueño, minutos; sesgo PSG−Fitbit = −4.0
LOA_FC_LPM = (-6.9, 8.6)        # frecuencia cardiaca global, lpm; sesgo = +0.9


class SinIncertidumbreVerificada(ValueError):
    """No hay una σ de sensor con fuente verificada para ese indicador: no se emite el dato."""


@dataclass(frozen=True)
class SigmaDeclarada:
    indicador: IndicadorSensor
    unidad: str
    sigma: float
    fuente: str
    enlace: str
    es_proxy: bool
    nota: str


def _sd_desde_loa(loa: tuple[float, float]) -> float:
    return (loa[1] - loa[0]) / (2 * 1.96)


_NOTA = ("PROXY: el estudio valida el Fitbit Charge 2 (no el Sense de LifeSnaps) contra polisomnografía portátil en "
         "59 trabajadores por turnos; los límites son por noche/lectura individual, no del agregado diario. "
         "Es una cota conservadora, no la incertidumbre del dispositivo concreto.")

SIGMAS: dict[IndicadorSensor, SigmaDeclarada] = {
    IndicadorSensor.FC: SigmaDeclarada(IndicadorSensor.FC, "lpm", _sd_desde_loa(LOA_FC_LPM), FUENTE, ENLACE, True, _NOTA),
    IndicadorSensor.SUENO: SigmaDeclarada(IndicadorSensor.SUENO, "min", _sd_desde_loa(LOA_TST_MIN), FUENTE, ENLACE, True, _NOTA),
}


def sigma_de(indicador: IndicadorSensor) -> SigmaDeclarada:
    try:
        return SIGMAS[indicador]
    except KeyError:
        raise SinIncertidumbreVerificada(
            f"no hay σ de sensor con fuente verificada para '{indicador.value}': no se emite (política de datos)") from None
