"""Siembra el estado REAL de fc y sueño por persona a partir de LifeSnaps (personas cotidianas, NO astronautas).

Por persona e indicador: línea base de 14 días → ventana de 14 días → verde con recibo (DC-14) o alarma con recibo (DC-05), con el h del acta FB-009
y su hash. Persiste con banner REAL; la API solo expone AGREGADOS por indicador (nunca ids ni valores). Solo-anexar: lo ya sembrado se omite.
Sin el CSV (data/externos/, no versionado) el comando se niega: sin dato real no se simula.
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError

from apps.motor.models import Alarma, ReciboVerde
from apps.motor.repositorio import guardar_alarma, guardar_recibo_verde
from src.contratos.comunes import Banner, Indicador, IndicadorSensor
from src.gobernanza.preregistro import leer_indice
from src.ingesta import lifesnaps
from src.ingesta.series import series_de
from src.motor.estado_indicadores import evaluar_persona

CSV = "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"
INDICADORES = ((IndicadorSensor.FC, Indicador.FC), (IndicadorSensor.SUENO, Indicador.SUENO))


class Command(BaseCommand):
    help = "Siembra verdes y alarmas con recibo de fc y sueño desde LifeSnaps (REAL, no astronautas)"

    def add_arguments(self, parser):
        parser.add_argument("--csv", default=str(Path(settings.RAIZ) / CSV))

    def handle(self, *args, **opts):
        ruta = Path(opts["csv"])
        if not ruta.is_file():
            raise CommandError(f"no existe {ruta}: sin dato real no se simula (descarga LifeSnaps, Zenodo 7229547)")
        hash_pre = next(e.hash_sha256 for e in leer_indice(Path(settings.RAIZ)) if e.acta == "FB-009")
        regs = lifesnaps.cargar(ruta).registros
        verdes = alarmas = 0
        for sensor, ind in INDICADORES:
            for persona, obs in sorted(series_de(regs, sensor).items()):
                e = evaluar_persona(persona, ind, sensor, obs, hash_pre, banner=Banner.REAL)
                if e is None:
                    continue
                if e.recibo is not None and not ReciboVerde.objects.filter(recibo_id=e.recibo.recibo_id).exists():
                    guardar_recibo_verde(e.recibo)
                    verdes += 1
                if e.alarma is not None and not Alarma.objects.filter(alarma_id=e.alarma.alarma_id).exists():
                    guardar_alarma(e.alarma, Banner.REAL)
                    alarmas += 1
        self.stdout.write(f"sembrados {verdes} recibos de verde y {alarmas} alarmas con recibo (REAL, LifeSnaps, no astronautas)")
