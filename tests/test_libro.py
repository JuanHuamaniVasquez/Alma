"""M1.1 (núcleo) · LB-1: fórmula del residuo, regla de cierre 2σ y cierre diario del libro.

Las líneas son ESTRUCTURALES (X-01), construidas para ejercitar la regla; NO son datos de salud.
El criterio de hecho de M1.1 pide un fixture REAL de 14 días: sigue pendiente (política de datos).
"""
import pytest
from pydantic import ValidationError

from src.contratos import CONTRATOS
from src.contratos.dc04_libro import K_CIERRE, DC04Linea
from src.libro.libro import Libro, LineaDuplicada

DC04 = CONTRATOS["DC-04"]


def linea(dia=1, pres="aire", sujeto="habitat", esperada=10.0, observada=10.1, sigma=0.2, estado="limpio"):
    return DC04.model_validate(dict(
        dia_habitat=dia, presupuesto_id=pres, sujeto=sujeto, emision_esperada=esperada,
        incertidumbre_del_manifiesto=sigma, emision_observada=observada,
        residuo_contable=observada - esperada, fuente_linea="DC-03:ev-1", estado_linea=estado))


def test_residuo_contable_es_observada_menos_esperada():
    with pytest.raises(ValidationError, match="observada"):
        DC04.model_validate({**linea().model_dump(), "residuo_contable": 7.0})


def test_la_regla_de_cierre_es_2_sigma():
    assert K_CIERRE == 2.0
    assert linea(observada=10.39, sigma=0.2).cierra       # 0.39 ≤ 0.40
    assert not linea(observada=10.41, sigma=0.2).cierra   # 0.41 > 0.40
    assert linea(observada=9.62, sigma=0.2).cierra        # simétrica: también las caídas
    assert not linea(observada=9.50, sigma=0.2).cierra


def test_el_libro_cierra_si_todas_las_lineas_cierran():
    libro = Libro()
    for pres in ("aire", "agua", "energia"):
        libro.anotar(linea(pres=pres))
    c = libro.cierre_del_dia(1)
    assert c.cierra and c.lineas == 3 and not c.abiertas
    assert all(c.por_presupuesto.values())


def test_una_linea_abierta_hace_que_el_libro_no_cierre_y_dice_cual():
    libro = Libro()
    libro.anotar(linea(pres="aire"))
    libro.anotar(linea(pres="agua", observada=11.5))  # residuo 1.5 ≫ 0.4
    c = libro.cierre_del_dia(1)
    assert not c.cierra
    assert [l.presupuesto_id.value for l in c.abiertas] == ["agua"]
    assert c.por_presupuesto == {libro.lineas_del_dia(1)[0].presupuesto_id: True, libro.lineas_del_dia(1)[1].presupuesto_id: False}


def test_un_dia_sin_libro_no_cierra():
    assert not Libro().cierre_del_dia(5).cierra  # la ausencia es dato: no se afirma un cierre sin líneas


def test_cuarentena_no_se_cuenta_como_cerrada_ni_se_esconde():
    libro = Libro()
    libro.anotar(linea(pres="aire"))
    libro.anotar(linea(pres="agua", observada=99.0, estado="cuarentena"))
    c = libro.cierre_del_dia(1)
    assert c.cierra and len(c.en_cuarentena) == 1 and c.lineas == 2
    solo = Libro()
    solo.anotar(linea(estado="cuarentena"))
    assert not solo.cierre_del_dia(1).cierra  # solo cuarentena: nada contabilizable, no cierra


def test_el_libro_es_solo_anexar():
    libro = Libro()
    libro.anotar(linea())
    with pytest.raises(LineaDuplicada):
        libro.anotar(linea(observada=10.2))


def test_cada_dia_se_cierra_por_separado():
    libro = Libro()
    libro.anotar(linea(dia=1))
    libro.anotar(linea(dia=2, observada=12.0))
    assert libro.dias() == [1, 2]
    assert libro.cierre_del_dia(1).cierra and not libro.cierre_del_dia(2).cierra
