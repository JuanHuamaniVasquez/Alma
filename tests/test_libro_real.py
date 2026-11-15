"""M1.1 · el libro LB-1 con 14 días REALES consecutivos de un participante de LifeSnaps (presupuesto `tiempo`)."""
import csv
from datetime import date
from pathlib import Path

from src.libro.libro import Libro
from src.libro.tiempo_real import linea_tiempo

FILAS = sorted(csv.DictReader((Path(__file__).resolve().parent.parent / "data/fixtures/lifesnaps_diario_extracto.csv").open(encoding="utf-8")),
               key=lambda f: f["date"])


def _libro(filas):
    libro, dia = Libro(), 0
    for f in filas:
        l = linea_tiempo(f, dia)
        if l is not None:
            libro.anotar(l)
        dia += 1
    return libro


def test_linea_incompleta_no_se_inventa():
    assert linea_tiempo(dict(FILAS[0], minutesAsleep=""), 0) is None


def test_los_primeros_14_dias_reales_completos_cierran_o_se_listan_abiertos():
    completos = [f for f in FILAS if linea_tiempo(f, 0) is not None]
    primeros = completos[:14]
    fechas = [date.fromisoformat(f["date"]) for f in primeros]
    assert all((b - a).days == 1 for a, b in zip(fechas, fechas[1:]))          # 14 días consecutivos reales
    libro = _libro(primeros)
    cierres = [libro.cierre_del_dia(d) for d in libro.dias()]
    assert len(cierres) == 14
    # ventana elegida a priori (los PRIMEROS 14 días completos, sin elegir la mejor): cada línea cierra o queda listada como abierta
    assert sum(c.cierra for c in cierres) + sum(not c.cierra for c in cierres) == 14
    assert all(c.abiertas for c in cierres if not c.cierra)


def test_tasa_de_cierre_real_sobre_88_dias_completos():
    libro = _libro([f for f in FILAS if linea_tiempo(f, 0) is not None])
    cierra = sum(libro.cierre_del_dia(d).cierra for d in libro.dias())
    assert len(libro.dias()) == 88 and cierra == 79        # 89,8 %: la identidad contable del export falla en ≈ 10 % de los días reales
