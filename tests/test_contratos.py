"""M0.3: un test de validación por contrato (DC-01…DC-12) y los rechazos que exige la cola.

Honestidad (docs/politica-de-datos.md, registro X-01): las instancias válidas de abajo son
ESTRUCTURALES, construidas para ejercitar el schema; NO son datos de salud ni se persisten.
Lo único real en ellas es la fuente de DC-12 (accesión OS-892, verificada en OSDR).
"""
import hashlib
import uuid

import pytest
from pydantic import ValidationError

from src.contratos import CONTRATOS, SEMILLAS_PUBLICAS

H = hashlib.sha256(b"x-01 estructural").hexdigest()
T = "2026-11-15T00:00:00Z"

VALIDOS = {
    "DC-01": dict(persona_id="astro-01", ts_utc=T, indicador="fc", valor=62.0, unidad="lpm",
                  incertidumbre_sensor=1.5, calidad="ok", fuente="dev-7", banner="SIMULADO"),
    "DC-02": dict(persona_id="astro-01", ts_utc=T, banner="SIMULADO", tipo="ánimo", escala="Likert 1-5",
                  valor=4, duracion_respuesta_s=2.4, registro_ausencia=False),
    "DC-03": dict(evento_id="ev-1", ts_utc_inicio=T, ts_utc_fin="2026-11-15T03:00:00Z", tipo="tormenta_solar",
                  fuente="swpc", parametros={"kp": 7.0, "flujo_protones_pfu": 120.0},
                  hash_lectura_cruda=H, banner="REAL"),
    "DC-04": dict(dia_habitat=12, presupuesto_id="aire", sujeto="habitat", emision_esperada=3.5,
                  incertidumbre_del_manifiesto=0.2, emision_observada=3.6, residuo_contable=0.1,
                  fuente_linea="DC-03:ev-1", estado_linea="limpio"),
    "DC-05": dict(alarma_id="al-1", ts_utc=T, presupuesto_id="aire", detector="cusum", sentido="caída",
                  umbral=5.0, valor_cruzado=5.4, regla_exacta="cusum_bilateral(h=5.0) cruza en caída",
                  semilla=20261113, hash_preregistro=H, estado="activa"),
    "DC-06": dict(sujeto="astro-01", ts_utc=T, indicador="sueño", observado=6.0, predicho=7.5, residuo=-1.5,
                  sigma_efectiva=0.5, cusum_acumulado=-3.0, bandera="sorpresa"),
    "DC-07": dict(version="0.1", banner="SIMULADO", hipotesis="h", prueba_protocolo="A-B-A-B",
                  preregistro=dict(hash=H, semilla=20261114), numeros={"efecto": 0.3},
                  senal_refutadora="s", veredicto="v", limites="solo en silicio"),
    "DC-08": dict(dia_habitat=3, bucle="agua", entradas=10.0, salidas=8.0, delta_almacen=1.5,
                  perdida_declarada=0.2, residuo_conservacion=0.3, incertidumbre_propagada=0.1,
                  veredicto="NO CIERRA", banner="SIMULADO"),
    "DC-09": dict(dia_habitat=3, banner="SIMULADO", curva="potencia", fase_valle_local="03:30",
                  amplitud_relativa=1.8, residuo_forma=0.4, covariables=["DC-03:ev-1"]),
    "DC-10": dict(caso_id="c-1", ts_utc_deteccion=T, nodo_origen="DC-01:l-9", clase_error="unidad",
                  descendientes=["DC-04:a", "DC-04:b"], estado="abierto", r0_fuente=2.0,
                  brote=True, k_brote=1),
    "DC-11": dict(device_id="dev-7", clase_sensor="termistor", nacimiento="2026-10-01T00:00:00Z",
                  calibraciones=["2026-10-02T00:00:00Z"], edad_dias=45, dias_desde_calibracion=44,
                  hazard_dia=0.01, sigma_manifiesto_recomendada=0.3, estado="vivo"),
    "DC-12": dict(tarjeta_id=str(uuid.UUID(int=1)),
                  par_variables=dict(senal_cuerpo="sueño", otra_senal="hueso", tipo_otra_senal="cuerpo"),
                  mecanismo="FA-mecanismo-ref", prediccion="p", senal_refutadora="s",
                  fuentes=[dict(id="OS-892", tipo="accesión OSDR")],
                  precio=dict(datos="OSDR", computo="local", dias=3), valor_si_cierta=["DC-13"],
                  estado="vivero"),
}
# DC-12: valor_si_cierta apunta a detectores NUEVOS (DC-xx aún por crear), p. ej. DC-13.


def con(contrato, **cambios):
    datos = {**VALIDOS[contrato], **cambios}
    return CONTRATOS[contrato].model_validate(datos)


def sin(contrato, campo):
    datos = {k: v for k, v in VALIDOS[contrato].items() if k != campo}
    return CONTRATOS[contrato].model_validate(datos)


@pytest.mark.parametrize("dc", sorted(VALIDOS))
def test_contrato_valido(dc):
    assert CONTRATOS[dc].model_validate(VALIDOS[dc])


@pytest.mark.parametrize("dc", sorted(VALIDOS))
def test_rechaza_campo_fuera_del_contrato(dc):
    with pytest.raises(ValidationError):
        con(dc, campo_inventado=1)


def test_son_exactamente_12_contratos():
    assert sorted(CONTRATOS) == sorted(VALIDOS) and len(CONTRATOS) == 12


def test_semillas_publicas():
    assert SEMILLAS_PUBLICAS == (20261113, 20261114, 20261115, 20261111, 20261112)


# --- los rechazos que exige TASKS.md M0.3 ---------------------------------------------------
def test_dc12_rechaza_tarjeta_sin_fuentes():
    with pytest.raises(ValidationError):
        con("DC-12", fuentes=[])
    with pytest.raises(ValidationError):
        sin("DC-12", "fuentes")


@pytest.mark.parametrize("fuente", [
    dict(id="OS-892", tipo="DOI"),                        # id no es un DOI
    dict(id="892", tipo="accesión OSDR"),                 # no tiene forma OS-NNN
    dict(id="lote-1", tipo="lote"),                       # lote sin semilla
    dict(id="", tipo="accesión OSDR"),                    # sin identificador
])
def test_dc12_rechaza_fuente_sin_identificador_valido(fuente):
    with pytest.raises(ValidationError):
        con("DC-12", fuentes=[fuente])


def test_dc12_rechaza_sin_mecanismo_ni_precio():
    with pytest.raises(ValidationError):
        sin("DC-12", "mecanismo")
    with pytest.raises(ValidationError):
        sin("DC-12", "precio")


def test_dc12_en_prueba_exige_preregistro():
    with pytest.raises(ValidationError):
        con("DC-12", estado="en_prueba")
    assert con("DC-12", estado="en_prueba", preregistro_hash=H)


def test_dc12_tiene_los_11_campos():
    assert len(CONTRATOS["DC-12"].model_fields) == 11


def test_dc05_rechaza_alarma_sin_regla_exacta():
    with pytest.raises(ValidationError):
        sin("DC-05", "regla_exacta")
    with pytest.raises(ValidationError):
        con("DC-05", regla_exacta="   ")


# --- reglas que cada contrato hace cumplir ---------------------------------------------------
def test_dc01_la_ausencia_es_dato():
    assert con("DC-01", calidad="ausente", valor=None)
    with pytest.raises(ValidationError):
        con("DC-01", calidad="ausente", valor=60.0)
    with pytest.raises(ValidationError):
        con("DC-01", valor=None)


def test_dc01_rechaza_sin_banner_y_ánimo_como_sensor_y_nan():
    with pytest.raises(ValidationError):
        sin("DC-01", "banner")
    with pytest.raises(ValidationError):
        con("DC-01", indicador="ánimo")
    with pytest.raises(ValidationError):
        con("DC-01", valor=float("nan"))


def test_timestamps_deben_ser_utc():
    with pytest.raises(ValidationError):
        con("DC-01", ts_utc="2026-11-15T00:00:00")  # sin zona
    with pytest.raises(ValidationError):
        con("DC-01", ts_utc="2026-11-15T00:00:00-05:00")


def test_persona_id_es_pseudonimo():
    with pytest.raises(ValidationError):
        con("DC-01", persona_id="ana@correo.com")


def test_dc02_ausencia_y_respuesta():
    assert con("DC-02", registro_ausencia=True, valor=None, duracion_respuesta_s=None)
    with pytest.raises(ValidationError):
        con("DC-02", valor=None)


def test_dc03_unidad_en_el_nombre_hash_y_simulacion():
    with pytest.raises(ValidationError):
        con("DC-03", parametros={"flujo": 1.0})
    with pytest.raises(ValidationError):
        con("DC-03", hash_lectura_cruda="abc")
    with pytest.raises(ValidationError):
        con("DC-03", ts_utc_fin="2026-11-14T00:00:00Z")
    with pytest.raises(ValidationError):
        con("DC-03", tipo="brote_simulado", fuente="swpc")
    with pytest.raises(ValidationError):
        con("DC-03", fuente="simulador", banner="REAL")


def test_dc04_exige_incertidumbre_positiva_y_estado_linea():
    with pytest.raises(ValidationError):
        con("DC-04", incertidumbre_del_manifiesto=0.0)
    with pytest.raises(ValidationError):
        sin("DC-04", "estado_linea")
    with pytest.raises(ValidationError):
        con("DC-04", presupuesto_id="oxigeno")
    with pytest.raises(ValidationError):
        con("DC-04", fuente_linea="DC-05:x")  # la fuente solo puede ser DC-01/02/03


def test_dc06_residuo_es_observado_menos_predicho():
    with pytest.raises(ValidationError):
        con("DC-06", residuo=9.0)
    with pytest.raises(ValidationError):
        con("DC-06", presupuesto_id="aire")  # indicador Y presupuesto a la vez


def test_dc07_sin_limites_no_hay_capsula():
    with pytest.raises(ValidationError):
        sin("DC-07", "limites")
    with pytest.raises(ValidationError):
        con("DC-07", limites="")


def test_dc08_formula_de_conservacion():
    with pytest.raises(ValidationError):
        con("DC-08", residuo_conservacion=5.0)
    with pytest.raises(ValidationError):
        con("DC-08", veredicto="TAL VEZ")


def test_dc09_hora_y_amplitud():
    with pytest.raises(ValidationError):
        con("DC-09", fase_valle_local="25:00")
    with pytest.raises(ValidationError):
        con("DC-09", amplitud_relativa=0.5)


def test_dc10_brote_coherente_con_k():
    with pytest.raises(ValidationError):
        con("DC-10", brote=False)
    assert con("DC-10", brote=False, k_brote=5)


def test_dc11_calibraciones_coherentes():
    with pytest.raises(ValidationError):
        con("DC-11", dias_desde_calibracion=None)
    with pytest.raises(ValidationError):
        con("DC-11", calibraciones=["2026-09-01T00:00:00Z"])
    assert con("DC-11", calibraciones=[], dias_desde_calibracion=None)
