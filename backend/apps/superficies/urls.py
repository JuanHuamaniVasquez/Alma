from django.urls import path

from . import views

urlpatterns = [
    path("libro/dia/<int:dia>/", views.LibroDia.as_view(), name="libro-dia"),
    path("alarmas/", views.Alarmas.as_view(), name="alarmas"),
    path("residuo/", views.Residuo.as_view(), name="residuo"),
    path("cierres/dia/<int:dia>/", views.CierresDia.as_view(), name="cierres-dia"),
    path("verdes/", views.Verdes.as_view(), name="verdes"),
    path("fundicion/", views.Fundicion.as_view(), name="fundicion"),
    path("actas/", views.Actas.as_view(), name="actas"),
    path("demo-kill/", views.DemoKill.as_view(), name="demo-kill"),
    path("tormenta/", views.Tormenta.as_view(), name="tormenta"),
]
