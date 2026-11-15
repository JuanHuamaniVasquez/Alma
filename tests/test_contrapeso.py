"""M1.2 · MO-6 El Contrapeso.

TODAS las corrientes son SIMULADAS (registro X-05 de docs/politica-de-datos.md): el lazo de O₂ de una
tripulación se construye con el consumo publicado de NASA (docs/parametros-publicos.md P-02: 0.89 kg
O₂/persona/día; 0.84 en el otro protocolo). Supuestos DECLARADOS de la simulación, no medidos: tripulación
de 4, σ por persona = mitad de la diferencia entre los dos protocolos publicados (0.025 kg), σ del
suministro 0.02 kg y del almacén 0.01 kg. Resultados «en silicio».
"""
import math

import pytest

from src.contratos import Banner
from src.contratos.dc08_conservacion import Bucle, DC08Cierre, Veredicto
from src.motor.contrapeso import Corriente, Sentido, abre_investigacion, cierre_de_conservacion, sentido

SIM = Banner.SIMULADO
TRIPULACION = 4
O2_PERSONA = 0.89            # P-02, Ewert & Stromgren 2019 (perfil de 90 min de ejercicio)
SIGMA_PERSONA = (0.89 - 0.84) / 2  # supuesto declarado: semirrango entre dos protocolos publicados


def consumo():
    return [Corriente(f"consumo_astronauta_{i}", O2_PERSONA, SIGMA_PERSONA, SIM) for i in range(TRIPULACION)]


def dia(*, suministro=TRIPULACION * O2_PERSONA, extra_salida=0.0, almacen=0.0, venteo_declarado=0.0, bucle=Bucle.AIRE):
    salidas = consumo() + ([Corriente("fuente_no_declarada", extra_salida, 0.0, SIM)] if extra_salida else [])
    return cierre_de_conservacion(
        dia_habitat=7, bucle=bucle,
        entradas=[Corriente("suministro_OGA", suministro, 0.02, SIM)],
        salidas=salidas,
        delta_almacen=Corriente("delta_atmosfera", almacen, 0.01, SIM),
        perdida_declarada=Corriente("venteo_declarado", venteo_declarado, 0.0, SIM))


def test_dia_limpio_cierra():
    c = dia()
    assert c.veredicto is Veredicto.CIERRA and abs(c.residuo_conservacion) < 1e-9
    assert sentido(c).value == "ninguno" and not abre_investigacion(c)


def test_fuga_no_contabilizada_no_cierra_el_mismo_dia():
    c = dia(suministro=TRIPULACION * O2_PERSONA + 0.30)  # 0.30 kg de O₂ salen y nadie lo declaró
    assert c.veredicto is Veredicto.NO_CIERRA
    assert c.residuo_conservacion == pytest.approx(0.30)
    assert sentido(c) is Sentido.PERDIDA_NO_DECLARADA and abre_investigacion(c)


def test_si_la_perdida_esta_declarada_no_hay_alarma():
    c = dia(suministro=TRIPULACION * O2_PERSONA + 0.30, venteo_declarado=0.30)
    assert c.veredicto is Veredicto.CIERRA and c.perdida_declarada == 0.30


def test_es_bilateral_una_fuente_no_declarada_tambien_no_cierra():
    c = dia(extra_salida=0.30)  # sale 0.30 kg más de lo que entró: el «octavo pasajero»
    assert c.veredicto is Veredicto.NO_CIERRA and c.residuo_conservacion == pytest.approx(-0.30)
    assert sentido(c) is Sentido.FUENTE_NO_DECLARADA


def test_la_incertidumbre_se_propaga_en_cuadratura():
    c = dia()
    esperada = math.sqrt(TRIPULACION * SIGMA_PERSONA ** 2 + 0.02 ** 2 + 0.01 ** 2 + 0.0 ** 2)
    assert c.incertidumbre_propagada == pytest.approx(esperada)


def test_el_umbral_es_2_sigma_y_es_simetrico():
    sigma = dia().incertidumbre_propagada
    dentro = dia(suministro=TRIPULACION * O2_PERSONA + 1.9 * sigma)
    fuera = dia(suministro=TRIPULACION * O2_PERSONA + 2.1 * sigma)
    assert dentro.veredicto is Veredicto.CIERRA and fuera.veredicto is Veredicto.NO_CIERRA
    assert dia(suministro=TRIPULACION * O2_PERSONA - 2.1 * sigma).veredicto is Veredicto.NO_CIERRA


def test_un_cambio_en_el_almacen_explica_el_residuo():
    c = dia(suministro=TRIPULACION * O2_PERSONA + 0.20, almacen=0.20)  # el tanque subió 0.20 kg
    assert c.veredicto is Veredicto.CIERRA


def test_el_banner_se_hereda_y_nunca_asciende_a_real():
    assert dia().banner is Banner.SIMULADO
    real = Corriente("x", 1.0, 0.1, Banner.REAL)
    todo_real = cierre_de_conservacion(dia_habitat=1, bucle=Bucle.ENERGIA, entradas=[real], salidas=[real],
                                       delta_almacen=Corriente("d", 0.0, 0.0, Banner.REAL),
                                       perdida_declarada=Corriente("p", 0.0, 0.0, Banner.REAL))
    assert todo_real.banner is Banner.REAL
    mezcla = cierre_de_conservacion(dia_habitat=1, bucle=Bucle.ENERGIA, entradas=[real], salidas=[real],
                                    delta_almacen=Corriente("d", 0.0, 0.0, Banner.SIMULADO),
                                    perdida_declarada=Corriente("p", 0.0, 0.0, Banner.REAL))
    assert mezcla.banner is Banner.SIMULADO


def test_sin_corrientes_no_se_afirma_un_cierre_y_no_acepta_flujos_negativos():
    cero = Corriente("0", 0.0, 0.0, SIM)
    with pytest.raises(ValueError, match="sin corrientes"):
        cierre_de_conservacion(dia_habitat=1, bucle=Bucle.AGUA, entradas=[], salidas=[], delta_almacen=cero, perdida_declarada=cero)
    with pytest.raises(ValueError, match="negativa"):
        cierre_de_conservacion(dia_habitat=1, bucle=Bucle.AGUA, entradas=[Corriente("x", -1.0, 0.0, SIM)],
                               salidas=[cero], delta_almacen=cero, perdida_declarada=cero)
    with pytest.raises(ValueError):
        Corriente("x", 1.0, -0.1, SIM)  # σ negativa
    with pytest.raises(ValueError):
        Corriente("x", float("nan"), 0.1, SIM)


def test_la_salida_es_un_dc08_valido_y_reproducible():
    c = dia(suministro=TRIPULACION * O2_PERSONA + 0.30)
    assert DC08Cierre.model_validate(c.model_dump()) == c
    assert dia(suministro=TRIPULACION * O2_PERSONA + 0.30) == c  # determinista
