"""Comprueba fallos visibles de infraestructura y preserva el modo local."""
from unittest.mock import patch

from django.db import OperationalError
from django.test import Client
import pytest


@pytest.mark.django_db
def test_health_comprueba_postgresql_real():
    respuesta = Client().get("/healthz/")
    assert respuesta.status_code == 200
    assert respuesta.json() == {"status": "ok"}


def test_health_no_expone_credenciales_si_falla_la_base():
    with patch("config.health.connection.cursor", side_effect=OperationalError("private connection details")):
        respuesta = Client().get("/healthz/")
    assert respuesta.status_code == 503
    assert respuesta.json() == {"status": "unavailable"}
