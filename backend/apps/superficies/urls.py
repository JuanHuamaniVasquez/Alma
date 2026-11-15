from django.urls import path

from . import views

urlpatterns = [
    path("libro/dia/<int:dia>/", views.LibroDia.as_view(), name="libro-dia"),
    path("alarmas/", views.Alarmas.as_view(), name="alarmas"),
    path("residuo/", views.Residuo.as_view(), name="residuo"),
    path("cierres/dia/<int:dia>/", views.CierresDia.as_view(), name="cierres-dia"),
]
