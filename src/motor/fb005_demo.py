"""FB-005-D1 · demo «kill» del Contrapeso (M1.4). UNIVERSO SIMULADO — DÍA 7.

Implementa EXACTAMENTE el diseño de docs/actas/FB-005-D1.md (registrada antes de escribir este código).
No cambiar ningún parámetro aquí sin una acta nueva: sería HARKing.
"""
from __future__ import annotations

import math
import random

from src.contratos.comunes import Banner
from src.contratos.dc08_conservacion import Bucle
from src.motor.contrapeso import Corriente, abre_investigacion, cierre_de_conservacion, sentido

TRIPULACION = 4
O2_PERSONA = 0.89        # P-02 (Ewert & Stromgren 2019); el manifiesto declara lo mismo
SIGMA_CONSUMO = 0.025    # supuesto declarado: semirrango entre los protocolos 0.84 y 0.89
SIGMA_SUMINISTRO = 0.02
SIGMA_ALMACEN = 0.01
FUGA = 0.30              # kg de O₂ perdidos y NO declarados en el escenario «fuga»
UMBRAL_A = 2.0
DIA = 7
BANNER_DEMO = "UNIVERSO SIMULADO — DÍA 7"


def _escenario(rng: random.Random, fuga: float) -> dict:
    consumo_medido = [O2_PERSONA + rng.gauss(0.0, SIGMA_CONSUMO) for _ in range(TRIPULACION)]
    suministro_medido = TRIPULACION * O2_PERSONA + fuga + rng.gauss(0.0, SIGMA_SUMINISTRO)
    delta_medido = 0.0 + rng.gauss(0.0, SIGMA_ALMACEN)
    z_a = (sum(consumo_medido) - TRIPULACION * O2_PERSONA) / math.sqrt(TRIPULACION * SIGMA_CONSUMO ** 2)
    cierre = cierre_de_conservacion(
        dia_habitat=DIA, bucle=Bucle.AIRE,
        entradas=[Corriente("suministro_OGA", suministro_medido, SIGMA_SUMINISTRO, Banner.SIMULADO)],
        salidas=[Corriente(f"consumo_{i}", c, SIGMA_CONSUMO, Banner.SIMULADO) for i, c in enumerate(consumo_medido)],
        delta_almacen=Corriente("delta_atmosfera", delta_medido, SIGMA_ALMACEN, Banner.SIMULADO),
        perdida_declarada=Corriente("venteo_declarado", 0.0, 0.0, Banner.SIMULADO))
    return {
        "fuga_kg": fuga,
        "A_manifiesto": {"z": z_a, "alarma": abs(z_a) > UMBRAL_A},
        "B_ley": {"residuo_kg": cierre.residuo_conservacion, "sigma_propagada_kg": cierre.incertidumbre_propagada,
                  "veredicto": cierre.veredicto.value, "sentido": sentido(cierre).value,
                  "abre_investigacion_D6": abre_investigacion(cierre)},
    }


def ejecutar(semilla: int) -> dict:
    """Corre control y luego fuga con un único generador sembrado (orden fijado por el acta)."""
    rng = random.Random(semilla)
    control = _escenario(rng, 0.0)
    fuga = _escenario(rng, FUGA)
    exito_fuga = (not fuga["A_manifiesto"]["alarma"]) and fuga["B_ley"]["veredicto"] == "NO CIERRA"
    exito_control = (not control["A_manifiesto"]["alarma"]) and control["B_ley"]["veredicto"] == "CIERRA"
    refutaciones = []
    if fuga["A_manifiesto"]["alarma"]:
        refutaciones.append("(i) A alarma en «fuga»: deja de ser ciego")
    if fuga["B_ley"]["veredicto"] != "NO CIERRA":
        refutaciones.append("(ii) B dice CIERRA en «fuga»")
    if control["A_manifiesto"]["alarma"] or control["B_ley"]["veredicto"] != "CIERRA":
        refutaciones.append("(iii) falsa alarma en «control»")
    return {"acta": "FB-005-D1", "semilla": semilla, "banner": BANNER_DEMO, "control": control, "fuga": fuga,
            "prediccion_confirmada": exito_fuga and exito_control, "reglas_de_muerte_cumplidas": refutaciones}
