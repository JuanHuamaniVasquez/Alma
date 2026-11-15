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
    path("tripulacion/", views.Tripulacion.as_view(), name="tripulacion"),
    path("entorno/", views.Entorno.as_view(), name="entorno"),
    path("astronautas/", views.AstronautasHematologia.as_view(), name="astronautas"),
    path("osdr/", views.OsdrHumanos.as_view(), name="osdr"),
    path("esperado/", views.EsperadoEnVuelo.as_view(), name="esperado"),
    path("enlace/", views.EnlaceTierra.as_view(), name="enlace"),
    path("ecg/", views.Ecg.as_view(), name="ecg"),
    path("eproceso/", views.EProceso.as_view(), name="eproceso"),
    path("nilm/", views.Nilm.as_view(), name="nilm"),
    path("privacidad/", views.Privacidad.as_view(), name="privacidad"),
    path("animo/", captura.Animo.as_view(), name="animo"),
    path("fundicion/", views.Fundicion.as_view(), name="fundicion"),
    path("actas/", views.Actas.as_view(), name="actas"),
    path("actas/<str:acta>/archivo/", views.ActaArchivo.as_view(), name="acta-archivo"),
    path("capsulas/", views.Capsulas.as_view(), name="capsulas"),
    path("demo-kill/", views.DemoKill.as_view(), name="demo-kill"),
    path("tormenta/", views.Tormenta.as_view(), name="tormenta"),
    path("tormenta/escenario/<str:escala>/", views.TormentaEscenario.as_view(), name="tormenta-escenario"),
]
