"""M0.2/M0.1: Django conecta al PostgreSQL real configurado en .env."""
import pytest
from django.db import connection


@pytest.mark.django_db
def test_postgres_responde():
    with connection.cursor() as cur:
        cur.execute("select 1")
        assert cur.fetchone() == (1,)
    assert connection.vendor == "postgresql"
