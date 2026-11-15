"""Persistencia de LB-1 (DC-04). Solo se anexa: una línea (día, presupuesto, sujeto) no se sobrescribe.

DC-04 no declara `banner`; se guarda el banner **heredado** de las fuentes de la línea (regla de
herencia de DOC-01 v0.2.1), calculado por quien escribe con `banner_heredado`.
"""
from django.db import models
from django.db.models import Q


class LineaLibro(models.Model):
    dia_habitat = models.PositiveIntegerField(db_index=True)
    presupuesto_id = models.CharField(max_length=20)
    sujeto = models.CharField(max_length=64)  # persona_id pseudónimo o "habitat"
    emision_esperada = models.FloatField()
    incertidumbre_del_manifiesto = models.FloatField()
    emision_observada = models.FloatField()
    residuo_contable = models.FloatField()
    fuente_linea = models.CharField(max_length=200)
    estado_linea = models.CharField(max_length=12, choices=[("limpio", "limpio"), ("sospechoso", "sospechoso"), ("cuarentena", "cuarentena")])
    banner = models.CharField(max_length=10, choices=[("REAL", "REAL"), ("SIMULADO", "SIMULADO")])

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["dia_habitat", "presupuesto_id", "sujeto"], name="dc04_una_linea_por_dia_presupuesto_sujeto"),
            models.CheckConstraint(condition=Q(incertidumbre_del_manifiesto__gt=0), name="dc04_sigma_manifiesto_positiva"),
        ]
