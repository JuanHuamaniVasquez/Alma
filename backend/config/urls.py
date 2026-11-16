from django.urls import include, path

from .health import health

urlpatterns = [
    path("healthz/", health, name="health"),
    path("api/", include("apps.superficies.urls")),  # M1.3: solo lectura; el cuerpo nunca sale en detalle
]
