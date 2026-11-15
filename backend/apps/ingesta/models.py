"""Persistencia de la Capa 0 (DC-03 y DC-13). El dominio vive en src/; aquí solo se guarda.

Las restricciones de la base repiten las reglas de los contratos: aunque alguien escriba
directo en la tabla, la BD rechaza un `ok` sin hash o un `fallo` sin error. Solo se anexa:
la ingesta nunca actualiza ni borra lecturas (los ids son únicos e idempotentes).
"""
from django.db import models
from django.db.models import Q


class Banner(models.TextChoices):
    REAL = "REAL"
    SIMULADO = "SIMULADO"


class EventoClimaEspacial(models.Model):
    """DC-03 · Canal C — eventos con firma física."""
    evento_id = models.CharField(max_length=200, unique=True)
    ts_utc_inicio = models.DateTimeField(db_index=True)
    ts_utc_fin = models.DateTimeField()
    tipo = models.CharField(max_length=40)
    fuente = models.CharField(max_length=20)
    parametros = models.JSONField()  # unidades en el nombre del campo
    hash_lectura_cruda = models.CharField(max_length=64)
    banner = models.CharField(max_length=10, choices=Banner.choices)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(ts_utc_fin__gte=models.F("ts_utc_inicio")), name="dc03_fin_no_antes_inicio"),
            models.CheckConstraint(condition=~Q(hash_lectura_cruda=""), name="dc03_hash_no_vacio"),
            models.CheckConstraint(condition=Q(fuente="simulador", banner="SIMULADO") | (~Q(fuente="simulador") & Q(banner="REAL")),
                                   name="dc03_banner_coherente_con_fuente"),
        ]
        indexes = [models.Index(fields=["tipo", "ts_utc_inicio"])]

    def __str__(self) -> str:
        return f"{self.evento_id} [{self.banner}]"


class IntentoIngesta(models.Model):
    """DC-13 · Registro de intento de ingesta: el fallo del feed es dato."""
    intento_id = models.CharField(max_length=200, unique=True)
    ts_utc = models.DateTimeField(db_index=True)
    fuente = models.CharField(max_length=20)
    url = models.URLField(max_length=500)
    resultado = models.CharField(max_length=10, choices=[("ok", "ok"), ("fallo", "fallo"), ("vacio", "vacio")])
    http_status = models.PositiveSmallIntegerField(null=True)
    hash_lectura_cruda = models.CharField(max_length=64, null=True)
    error = models.TextField(null=True)
    banner = models.CharField(max_length=10, choices=Banner.choices)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=(Q(resultado="ok", hash_lectura_cruda__isnull=False, error__isnull=True)
                           | Q(resultado="fallo", hash_lectura_cruda__isnull=True, error__isnull=False)
                           | Q(resultado="vacio", hash_lectura_cruda__isnull=True, error__isnull=True)),
                name="dc13_resultado_coherente"),
            models.CheckConstraint(condition=Q(fuente="simulador", banner="SIMULADO") | (~Q(fuente="simulador") & Q(banner="REAL")),
                                   name="dc13_banner_coherente_con_fuente"),
        ]

    def __str__(self) -> str:
        return f"{self.intento_id} {self.resultado} [{self.banner}]"


class Autorreporte(models.Model):
    """DC-02 · Canal B — autorreporte de ánimo en 3 toques. Solo se anexa. El tiempo de respuesta es dato; el texto libre no existe."""
    persona_id = models.CharField(max_length=64, db_index=True)
    ts_utc = models.DateTimeField(db_index=True)
    banner = models.CharField(max_length=10, choices=Banner.choices)
    tipo = models.CharField(max_length=10)
    escala = models.CharField(max_length=80)
    valor = models.SmallIntegerField(null=True)
    duracion_respuesta_s = models.FloatField(null=True)
    registro_ausencia = models.BooleanField(default=False)

    class Meta:
        constraints = [
            models.CheckConstraint(condition=Q(registro_ausencia=True, valor__isnull=True, duracion_respuesta_s__isnull=True)
                                   | Q(registro_ausencia=False, valor__isnull=False, duracion_respuesta_s__isnull=False),
                                   name="dc02_ausencia_es_dato"),
        ]
