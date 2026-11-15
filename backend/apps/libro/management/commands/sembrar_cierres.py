"""M8 · Siembra El Contrapeso (DC-08) de los días del hábitat SIMULADO ya sembrados: para cada línea de aire/agua, el cierre de conservación con `src/motor/contrapeso.py`.

Modelo (declarado, SIMULADO X-13): entrada = lo que el manifiesto promete suministrar (σ = incertidumbre del manifiesto); salida = lo medido (σ 0,05 kg); sin almacén ni pérdida
declarada. Así el residuo del cierre es −(residuo contable de la línea): el día 11 (fuga de 0,62 kg) NO CIERRA y los demás CIERRAN. Idempotente.
"""
from django.core.management.base import BaseCommand

from apps.libro.models import LineaLibro
from apps.motor.models import CierreConservacion
from apps.motor.repositorio import guardar_cierre
from src.contratos import Banner
from src.motor.contrapeso import Corriente, cierre_de_conservacion

BUCLE = {"aire": "aire", "agua": "agua"}


class Command(BaseCommand):
    help = "Siembra los cierres de conservación (DC-08) de los días SIMULADOS del hábitat"

    def handle(self, *args, **opts):
        nuevos = 0
        for ln in LineaLibro.objects.filter(sujeto="habitat", presupuesto_id__in=list(BUCLE)).order_by("dia_habitat"):
            if CierreConservacion.objects.filter(dia_habitat=ln.dia_habitat, bucle=BUCLE[ln.presupuesto_id]).exists():
                continue
            sim = Banner.SIMULADO
            c = cierre_de_conservacion(
                dia_habitat=ln.dia_habitat, bucle=BUCLE[ln.presupuesto_id],
                entradas=[Corriente("suministro_manifiesto", ln.emision_esperada, ln.incertidumbre_del_manifiesto, sim)],
                salidas=[Corriente("consumo_medido", ln.emision_observada, 0.05, sim)],
                delta_almacen=Corriente("delta_almacen", 0.0, 0.0, sim), perdida_declarada=Corriente("perdida_declarada", 0.0, 0.0, sim))
            guardar_cierre(c)
            nuevos += 1
        self.stdout.write(f"sembrados {nuevos} cierres DC-08 SIMULADOS (Contrapeso)")
