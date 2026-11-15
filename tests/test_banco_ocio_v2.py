"""Regresión permanente de FB-015-v2 (SIMULADO, semillas públicas): fija los números publicados en NOTA-FB-015-v2.md.
Si cambian, el acta o el código se alteraron y no se sube nada (M2.3 reencuadrado)."""
import random

from src.motor.banco_ocio_v2 import calibrar_h, correr, mediana, preaviso

H = calibrar_h(20261113)


def test_h_calibrado_es_201_y_cumple_el_fpr():
    assert H[0] == 201 and H[1] <= 0.018


def test_diez_corridas_publicas_son_exactamente_las_del_acta():
    diez = [preaviso(*correr(random.Random(20261113 + i), 0.06, 7, 9, 201, 0.2)) for i in range(10)]
    assert diez == [-1, 15, 28, 18, 20, 16, 29, -1, 10, 18]
    assert sum(1 for p in diez if p >= 2) == 8   # el «10/10» del documento NO se replica: 8/10


def test_estructura_de_la_tabla_9_decrece_con_gamma_y_crece_con_tau():
    m = lambda g, t: mediana(20261115, g, t, 9, 201, 0.2, 100)[0]
    assert m(0.06, 7) > m(0.12, 7) > m(0.20, 7)
    assert m(0.06, 7) > m(0.06, 1)
