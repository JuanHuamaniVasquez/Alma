"""Puente dominio ⇄ base de datos de la Capa 0. Al leer, cada fila se re-valida con su contrato."""
from __future__ import annotations

from collections.abc import Iterable

from src.contratos.dc03_eventos import DC03Evento
from src.contratos.dc13_intento_ingesta import DC13Intento
from src.ingesta.cliente import ResultadoIngesta

from .models import EventoClimaEspacial, IntentoIngesta


def guardar_eventos(eventos: Iterable[DC03Evento]) -> int:
    """Anexa los eventos nuevos (idempotente por `evento_id`). Devuelve cuántos eran nuevos."""
    filas = [EventoClimaEspacial(
        evento_id=e.evento_id, ts_utc_inicio=e.ts_utc_inicio, ts_utc_fin=e.ts_utc_fin, tipo=e.tipo.value,
        fuente=e.fuente.value, parametros=e.parametros, hash_lectura_cruda=e.hash_lectura_cruda, banner=e.banner.value)
        for e in eventos]
    antes = EventoClimaEspacial.objects.count()
    EventoClimaEspacial.objects.bulk_create(filas, ignore_conflicts=True, batch_size=1000)
    return EventoClimaEspacial.objects.count() - antes


def guardar_intento(i: DC13Intento) -> IntentoIngesta:
    obj, _ = IntentoIngesta.objects.get_or_create(intento_id=i.intento_id, defaults=dict(
        ts_utc=i.ts_utc, fuente=i.fuente.value, url=i.url, resultado=i.resultado.value, http_status=i.http_status,
        hash_lectura_cruda=i.hash_lectura_cruda, error=i.error, banner=i.banner.value))
    return obj


def guardar_resultado(r: ResultadoIngesta) -> tuple[int, IntentoIngesta]:
    """Guarda el intento (siempre, también el fallido) y los eventos que dejó."""
    return guardar_eventos(r.eventos), guardar_intento(r.intento)


def a_dominio_evento(fila: EventoClimaEspacial) -> DC03Evento:
    return DC03Evento.model_validate(dict(
        evento_id=fila.evento_id, ts_utc_inicio=fila.ts_utc_inicio, ts_utc_fin=fila.ts_utc_fin, tipo=fila.tipo,
        fuente=fila.fuente, parametros=fila.parametros, hash_lectura_cruda=fila.hash_lectura_cruda, banner=fila.banner))


def a_dominio_intento(fila: IntentoIngesta) -> DC13Intento:
    return DC13Intento.model_validate(dict(
        intento_id=fila.intento_id, ts_utc=fila.ts_utc, fuente=fila.fuente, url=fila.url, resultado=fila.resultado,
        http_status=fila.http_status, hash_lectura_cruda=fila.hash_lectura_cruda, error=fila.error, banner=fila.banner))


def guardar_autorreporte(r):
    """Guarda un DC-02 ya validado (el contrato rechaza lo incoherente antes de llegar aquí)."""
    from .models import Autorreporte
    return Autorreporte.objects.create(persona_id=r.persona_id, ts_utc=r.ts_utc, banner=r.banner.value, tipo=r.tipo.value, escala=r.escala,
                                       valor=r.valor, duracion_respuesta_s=r.duracion_respuesta_s, registro_ausencia=r.registro_ausencia)
