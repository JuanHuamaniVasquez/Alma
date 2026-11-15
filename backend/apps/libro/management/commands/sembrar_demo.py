"""Siembra el universo SIMULADO de la vitrina (X-13): 14 días de hábitat con los presupuestos que SÍ tienen ancla pública.

  · aire  : 5 tripulantes (X-15) × 0,89 kg O₂/día (P-02, Ewert & Stromgren 2019); σ del manifiesto 0,2 kg; el día 11 hay una fuga de 0,62 kg (≈ 3σ, no declarada).
  · agua  : 5 × 1,40 kg/día de agua en orina (P-09, Ewert & Stromgren); σ del manifiesto 0,3 kg.
Los otros 7 presupuestos NO se siembran: sin ancla real no hay línea (la ausencia es dato y la vitrina la muestra como tal).
Además siembra el flujo DC-06 de esos días (residuo, σ del manifiesto, CUSUM bilateral, bandera). Todo con banner SIMULADO y semilla pública 20261113. Solo-anexar: si ya existe, se omite.
"""
import random
from datetime import UTC, datetime, timedelta

from django.core.management.base import BaseCommand

from apps.libro.models import LineaLibro
from apps.libro.repositorio import guardar_linea
from apps.motor.models import ResiduoStream
from apps.motor.repositorio import guardar_residuo
from src.contratos import CONTRATOS, Banner
from src.libro.tripulacion import TRIPULACION
from src.motor.adversario import H_MEDIA
from src.motor.cusum import K_REF, paso

SEMILLA = 20261113
DIAS, DIA_FUGA, FUGA_KG = 14, 11, 0.62
DIA_1 = datetime(2026, 11, 2, 12, 0, tzinfo=UTC)   # día 1 del hábitat simulado
PRESUPUESTOS = {"aire": (TRIPULACION * 0.89, 0.2, 0.10), "agua": (TRIPULACION * 1.40, 0.3, 0.15)}  # (esperada kg, σ manifiesto kg, σ del ruido observado kg)


class Command(BaseCommand):
    help = "Siembra 14 días de hábitat SIMULADO (aire, agua) con semilla pública"

    def add_arguments(self, parser):
        parser.add_argument("--reiniciar", action="store_true", help="borra antes SOLO lo simulado del hábitat (líneas y residuos con banner SIMULADO) y lo vuelve a sembrar")

    def handle(self, *args, **opts):
        if opts.get("reiniciar"):
            LineaLibro.objects.filter(sujeto="habitat", banner="SIMULADO").delete()
            ResiduoStream.objects.filter(sujeto="habitat", banner="SIMULADO").delete()
        rng, nuevas = random.Random(SEMILLA), 0
        cusum = {p: (0.0, 0.0) for p in PRESUPUESTOS}      # (S alza, S caída) por presupuesto: el CUSUM bilateral de MO-3
        for dia in range(1, DIAS + 1):
            for pres, (esperada, sigma, ruido) in PRESUPUESTOS.items():
                obs = esperada + rng.gauss(0.0, ruido) + (FUGA_KG if (pres == "aire" and dia == DIA_FUGA) else 0.0)
                z = (obs - esperada) / sigma
                sa, sc = paso(*cusum[pres], z, K_REF)
                cusum[pres] = (sa, sc)
                ts = DIA_1 + timedelta(days=dia - 1)
                if not ResiduoStream.objects.filter(sujeto="habitat", presupuesto_id=pres, ts_utc=ts).exists():     # DC-06 con la misma regla de la API
                    bandera = "deriva" if max(sa, sc) >= H_MEDIA else "sorpresa" if abs(z) > 2 else "normal"
                    guardar_residuo(CONTRATOS["DC-06"].model_validate(dict(
                        sujeto="habitat", ts_utc=ts, presupuesto_id=pres, observado=obs, predicho=esperada, residuo=obs - esperada,
                        sigma_efectiva=sigma, cusum_acumulado=sa if sa >= sc else -sc, bandera=bandera)), Banner.SIMULADO)
                if LineaLibro.objects.filter(dia_habitat=dia, presupuesto_id=pres, sujeto="habitat").exists():
                    continue
                linea = CONTRATOS["DC-04"].model_validate(dict(
                    dia_habitat=dia, presupuesto_id=pres, sujeto="habitat", emision_esperada=esperada, incertidumbre_del_manifiesto=sigma,
                    emision_observada=obs, residuo_contable=obs - esperada, fuente_linea="DC-03:simulador-X13", estado_linea="limpio"))
                guardar_linea(linea, Banner.SIMULADO)
                nuevas += 1
        self.stdout.write(f"sembradas {nuevas} líneas SIMULADAS (semilla {SEMILLA}); residuo DC-06 con CUSUM bilateral k={K_REF}, h={H_MEDIA:.2f}")
