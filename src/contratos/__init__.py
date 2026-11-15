"""Los 14 contratos de datos DC-01…DC-14 (DOC-01 §3, v0.2.6). Dominio puro: sin Django."""
from .comunes import SEMILLAS_PUBLICAS, Banner, banner_heredado
from .dc01_sensores import DC01Sensor
from .dc02_autorreporte import DC02Autorreporte
from .dc03_eventos import DC03Evento
from .dc04_libro import DC04Linea
from .dc05_alarma import DC05Alarma
from .dc06_residuo import DC06Residuo
from .dc07_capsula import DC07Capsula
from .dc08_conservacion import DC08Cierre
from .dc09_forma_diaria import DC09Forma
from .dc10_error_contagio import DC10Caso
from .dc11_vida_sensor import DC11Sensor
from .dc12_fundicion import DC12Tarjeta
from .dc13_intento_ingesta import DC13Intento
from .dc14_recibo_verde import DC14ReciboVerde

CONTRATOS = {
    "DC-01": DC01Sensor, "DC-02": DC02Autorreporte, "DC-03": DC03Evento, "DC-04": DC04Linea,
    "DC-05": DC05Alarma, "DC-06": DC06Residuo, "DC-07": DC07Capsula, "DC-08": DC08Cierre,
    "DC-09": DC09Forma, "DC-10": DC10Caso, "DC-11": DC11Sensor, "DC-12": DC12Tarjeta, "DC-13": DC13Intento, "DC-14": DC14ReciboVerde,
}

__all__ = ["SEMILLAS_PUBLICAS", "Banner", "banner_heredado", "CONTRATOS", *(c.__name__ for c in CONTRATOS.values())]
