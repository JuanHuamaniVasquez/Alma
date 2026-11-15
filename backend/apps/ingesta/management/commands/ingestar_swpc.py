"""`manage.py ingestar_swpc [kp] [xrays] [alertas]` — lee SWPC en vivo, archiva el crudo y persiste.

Datos REALES de NOAA SWPC. Cada feed deja su DC-13 (también si falla) y sus eventos DC-03.
"""
from django.conf import settings
from django.core.management.base import BaseCommand

from apps.ingesta.repositorio import guardar_resultado
from src.ingesta.archivo import ahora_utc
from src.ingesta.cliente import FEEDS, fetch_http, ingestar


class Command(BaseCommand):
    help = "Ingesta en vivo de NOAA SWPC (banner REAL): archiva la lectura cruda y guarda DC-03 + DC-13."

    def add_arguments(self, parser):
        parser.add_argument("feeds", nargs="*", default=list(FEEDS))

    def handle(self, *args, feeds, **opts):
        for nombre in feeds:
            if nombre not in FEEDS:
                self.stderr.write(f"feed desconocido: {nombre} (válidos: {', '.join(FEEDS)})")
                continue
            r = ingestar(FEEDS[nombre], fetch=fetch_http, ahora=ahora_utc(), raiz=settings.RAIZ)
            nuevos, intento = guardar_resultado(r)
            self.stdout.write(f"[{intento.banner}] {nombre:8} {intento.resultado:5} http={intento.http_status} "
                              f"filas={r.filas} eventos_nuevos={nuevos}"
                              + (f" hash={intento.hash_lectura_cruda}" if intento.hash_lectura_cruda else "")
                              + (f" error={intento.error}" if intento.error else ""))
