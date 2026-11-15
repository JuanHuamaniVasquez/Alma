"""Siembra el universo SIMULADO de la vitrina (X-13): 14 días de hábitat con los presupuestos que SÍ tienen ancla pública.

  · aire  : 4 tripulantes × 0,89 kg O₂/día (P-02, Ewert & Stromgren 2019); σ del manifiesto 0,2 kg; el día 11 hay una fuga de 0,62 kg (≈ 3σ, no declarada).
  · agua  : 4 × 1,40 kg/día de agua en orina (P-09, Ewert & Stromgren); σ del manifiesto 0,3 kg.
Los otros 7 presupuestos NO se siembran: sin ancla real no hay línea (la ausencia es dato y la vitrina la muestra como tal).
Todo con banner SIMULADO y semilla pública 20261113. Solo-anexar: si el día ya existe, se omite.
"""
import random

from django.core.management.base import BaseCommand

from apps.libro.models import LineaLibro
from apps.libro.repositorio import guardar_linea
from src.contratos import CONTRATOS, Banner

SEMILLA = 20261113
DIAS, DIA_FUGA, FUGA_KG = 14, 11, 0.62
PRESUPUESTOS = {"aire": (4 * 0.89, 0.2, 0.10), "agua": (4 * 1.40, 0.3, 0.15)}  # (esperada kg, σ manifiesto kg, σ del ruido observado kg)


class Command(BaseCommand):
    help = "Siembra 14 días de hábitat SIMULADO (aire, agua) con semilla pública"

    def handle(self, *args, **opts):
        rng, nuevas = random.Random(SEMILLA), 0
        for dia in range(1, DIAS + 1):
            for pres, (esperada, sigma, ruido) in PRESUPUESTOS.items():
                obs = esperada + rng.gauss(0.0, ruido) + (FUGA_KG if (pres == "aire" and dia == DIA_FUGA) else 0.0)
                if LineaLibro.objects.filter(dia_habitat=dia, presupuesto_id=pres, sujeto="habitat").exists():
                    continue
                linea = CONTRATOS["DC-04"].model_validate(dict(
                    dia_habitat=dia, presupuesto_id=pres, sujeto="habitat", emision_esperada=esperada, incertidumbre_del_manifiesto=sigma,
                    emision_observada=obs, residuo_contable=obs - esperada, fuente_linea="DC-03:simulador-X13", estado_linea="limpio"))
                guardar_linea(linea, Banner.SIMULADO)
                nuevas += 1
        self.stdout.write(f"sembradas {nuevas} líneas SIMULADAS (semilla {SEMILLA})")
