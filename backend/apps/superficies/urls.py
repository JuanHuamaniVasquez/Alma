from django.urls import path

from . import captura, views

urlpatterns = [
    path("libro/dias/", views.LibroDias.as_view(), name="libro-dias"),
    path("libro/dia/<int:dia>/", views.LibroDia.as_view(), name="libro-dia"),
    path("alarmas/", views.Alarmas.as_view(), name="alarmas"),
    path("residuo/", views.Residuo.as_view(), name="residuo"),
    path("cierres/dia/<int:dia>/", views.CierresDia.as_view(), name="cierres-dia"),
    path("verdes/", views.Verdes.as_view(), name="verdes"),
    path("indicadores/", views.Indicadores.as_view(), name="indicadores"),
    path("animo/", captura.Animo.as_view(), name="animo"),
    path("fundicion/", views.Fundicion.as_view(), name="fundicion"),
    path("actas/", views.Actas.as_view(), name="actas"),
    path("actas/<str:acta>/archivo/", views.ActaArchivo.as_view(), name="acta-archivo"),
    path("capsulas/", views.Capsulas.as_view(), name="capsulas"),
    path("demo-kill/", views.DemoKill.as_view(), name="demo-kill"),
    path("tormenta/", views.Tormenta.as_view(), name="tormenta"),
    path("tormenta/escenario/<str:escala>/", views.TormentaEscenario.as_view(), name="tormenta-escenario"),
]
