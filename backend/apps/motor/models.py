"""Persistencia de la Capa 2: DC-05 (alarmas con recibo), DC-06 (stream de residuo), DC-08 (cierres).

Las CHECK de la base repiten las reglas de los contratos: sin `regla_exacta` no hay alarma; el hash
de preregistro es un SHA-256; un residuo identifica indicador XOR presupuesto.
"""
from django.db import models
from django.db.models import Q

BANNER = [("REAL", "REAL"), ("SIMULADO", "SIMULADO")]


class Alarma(models.Model):
    """DC-05."""
    alarma_id = models.CharField(max_length=100, unique=True)
    ts_utc = models.DateTimeField(db_index=True)
    presupuesto_id = models.CharField(max_length=20)
    detector = models.CharField(max_length=12)
    sentido = models.CharField(max_length=8)
    umbral = models.FloatField()
    valor_cruzado = models.FloatField()
    regla_exacta = models.TextField()
    semilla = models.BigIntegerField()
    hash_preregistro = models.CharField(max_length=64)
    estado = models.CharField(max_length=10, choices=[("activa", "activa"), ("retirada", "retirada"), ("apelada", "apelada")])
    banner = models.CharField(max_length=10, choices=BANNER)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=~Q(regla_exacta=""), name="dc05_regla_exacta_no_vacia"),
            models.CheckConstraint(condition=Q(hash_preregistro__regex=r"^[0-9a-f]{64}$"), name="dc05_hash_preregistro_sha256"),
        ]


class ResiduoStream(models.Model):
    """DC-06."""
    sujeto = models.CharField(max_length=64, db_index=True)
    ts_utc = models.DateTimeField(db_index=True)
    indicador = models.CharField(max_length=20, null=True)
    presupuesto_id = models.CharField(max_length=20, null=True)
    observado = models.FloatField()
    predicho = models.FloatField()
    residuo = models.FloatField()
    sigma_efectiva = models.FloatField()
    cusum_acumulado = models.FloatField()
    bandera = models.CharField(max_length=10, choices=[("normal", "normal"), ("sorpresa", "sorpresa"), ("deriva", "deriva")])
    banner = models.CharField(max_length=10, choices=BANNER)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=(Q(indicador__isnull=False, presupuesto_id__isnull=True)
                                              | Q(indicador__isnull=True, presupuesto_id__isnull=False)),
                                   name="dc06_indicador_xor_presupuesto"),
            models.CheckConstraint(condition=Q(sigma_efectiva__gt=0), name="dc06_sigma_positiva"),
        ]


class CierreConservacion(models.Model):
    """DC-08 — un cierre por bucle y día."""
    dia_habitat = models.PositiveIntegerField(db_index=True)
    bucle = models.CharField(max_length=10)
    entradas = models.FloatField()
    salidas = models.FloatField()
    delta_almacen = models.FloatField()
    perdida_declarada = models.FloatField()
    residuo_conservacion = models.FloatField()
    incertidumbre_propagada = models.FloatField()
    veredicto = models.CharField(max_length=10, choices=[("CIERRA", "CIERRA"), ("NO CIERRA", "NO CIERRA")])
    banner = models.CharField(max_length=10, choices=BANNER)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["dia_habitat", "bucle"], name="dc08_un_cierre_por_bucle_y_dia"),
            models.CheckConstraint(condition=Q(perdida_declarada__gte=0), name="dc08_perdida_no_negativa"),
        ]
