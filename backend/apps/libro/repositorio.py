from src.contratos.comunes import Banner
from src.contratos.dc04_libro import DC04Linea

from .models import LineaLibro


def guardar_linea(l: DC04Linea, banner: Banner) -> LineaLibro:
    """Anexa una línea del libro con su banner heredado. Duplicada ⇒ IntegrityError (solo-anexar)."""
    return LineaLibro.objects.create(
        dia_habitat=l.dia_habitat, presupuesto_id=l.presupuesto_id.value, sujeto=l.sujeto,
        emision_esperada=l.emision_esperada, incertidumbre_del_manifiesto=l.incertidumbre_del_manifiesto,
        emision_observada=l.emision_observada, residuo_contable=l.residuo_contable, fuente_linea=l.fuente_linea,
        estado_linea=l.estado_linea.value, banner=banner.value)


def a_dominio(f: LineaLibro) -> DC04Linea:
    return DC04Linea.model_validate(dict(
        dia_habitat=f.dia_habitat, presupuesto_id=f.presupuesto_id, sujeto=f.sujeto, emision_esperada=f.emision_esperada,
        incertidumbre_del_manifiesto=f.incertidumbre_del_manifiesto, emision_observada=f.emision_observada,
        residuo_contable=f.residuo_contable, fuente_linea=f.fuente_linea, estado_linea=f.estado_linea))
