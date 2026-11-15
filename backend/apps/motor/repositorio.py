from src.contratos.comunes import Banner
from src.contratos.dc05_alarma import DC05Alarma
from src.contratos.dc06_residuo import DC06Residuo
from src.contratos.dc08_conservacion import DC08Cierre

from .models import Alarma, CierreConservacion, ResiduoStream


def guardar_alarma(a: DC05Alarma, banner: Banner) -> Alarma:
    return Alarma.objects.create(
        alarma_id=a.alarma_id, ts_utc=a.ts_utc, presupuesto_id=a.presupuesto_id.value if a.presupuesto_id else None,
        indicador=a.indicador.value if a.indicador else None, detector=a.detector.value,
        sentido=a.sentido.value, umbral=a.umbral, valor_cruzado=a.valor_cruzado, regla_exacta=a.regla_exacta,
        semilla=a.semilla, hash_preregistro=a.hash_preregistro, estado=a.estado.value, banner=banner.value)


def guardar_residuo(r: DC06Residuo, banner: Banner) -> ResiduoStream:
    return ResiduoStream.objects.create(
        sujeto=r.sujeto, ts_utc=r.ts_utc, indicador=r.indicador.value if r.indicador else None,
        presupuesto_id=r.presupuesto_id.value if r.presupuesto_id else None, observado=r.observado, predicho=r.predicho,
        residuo=r.residuo, sigma_efectiva=r.sigma_efectiva, cusum_acumulado=r.cusum_acumulado, bandera=r.bandera.value,
        banner=banner.value)


def guardar_cierre(c: DC08Cierre) -> CierreConservacion:
    return CierreConservacion.objects.create(
        dia_habitat=c.dia_habitat, bucle=c.bucle.value, entradas=c.entradas, salidas=c.salidas, delta_almacen=c.delta_almacen,
        perdida_declarada=c.perdida_declarada, residuo_conservacion=c.residuo_conservacion,
        incertidumbre_propagada=c.incertidumbre_propagada, veredicto=c.veredicto.value, banner=c.banner.value)


def guardar_recibo_verde(r, banner=None):
    """Guarda un DC-14 (el banner ya viaja en el contrato)."""
    from .models import ReciboVerde
    return ReciboVerde.objects.create(
        recibo_id=r.recibo_id, ts_utc=r.ts_utc, sujeto=r.sujeto, presupuesto_id=r.presupuesto_id.value if r.presupuesto_id else None,
        indicador=r.indicador.value if r.indicador else None, estado=r.estado.value, ventana_dias=r.ventana_dias, dias_validos=r.dias_validos,
        canal=r.canal.value, detector=r.detector.value, k=r.k, h=r.h, potencia_declarada=r.potencia_declarada, mde_sigma=r.mde_sigma, mde_fisico=r.mde_fisico,
        unidad=r.unidad, supuesto=r.supuesto, regla_exacta=r.regla_exacta, semilla=r.semilla, hash_preregistro=r.hash_preregistro,
        banner=r.banner.value)
