"""MO-3 · Estado de un indicador oficial para UNA persona: línea base de 14 días → ventana de 14 días → verde con recibo (DC-14) o alarma con recibo (DC-05).

Reutiliza MO-1 (línea base), MO-3 (CUSUM bilateral con h fijado en FB-009) y el recibo de verde con potencia (M2.10). Solo se evalúan
indicadores con σ de sensor VERIFICADA (`sigma_de`): fc y sueño; los demás no se emiten (política de datos: sin dato, el ítem se bloquea).
Sin línea base (menos de 14 días válidos) no hay evaluación: la persona está en modo aprendizaje y no aparece (la ausencia es dato).
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from src.contratos.comunes import Banner, Indicador, IndicadorSensor
from src.contratos.dc05_alarma import DC05Alarma, Detector, EstadoAlarma, Sentido
from src.contratos.dc14_recibo_verde import DC14ReciboVerde
from src.ingesta.incertidumbre import sigma_de

from .cusum import K_REF, ejecutar_regla, regla_exacta
from .evaluacion import H_FB009
from .linea_base import estimar_linea_base
from .verde import recibo_verde

SEMILLA = 20261113
VENTANA = 14


@dataclass(frozen=True)
class Evaluacion:
    recibo: DC14ReciboVerde | None   # verde / sin_datos_suficientes (None si la regla alarma)
    alarma: DC05Alarma | None        # alarma con recibo (None si hay verde)


def evaluar_persona(persona_id: str, indicador: Indicador, sensor: IndicadorSensor, observaciones: Sequence[tuple[date, float]],
                    hash_preregistro: str, *, banner: Banner = Banner.REAL) -> Evaluacion | None:
    s = sigma_de(sensor)                                   # lanza SinIncertidumbreVerificada si no hay σ verificada
    obs = sorted(observaciones)
    lb = estimar_linea_base(persona_id, indicador.value, obs, s.sigma)
    if lb is None or not obs:
        return None                                        # modo aprendizaje: no se afirma nada
    ultimo = obs[-1][0]
    por_dia = dict(obs)
    dias = [ultimo - timedelta(days=VENTANA - 1 - i) for i in range(VENTANA)]
    valores = [por_dia.get(d) if d > lb.hasta else None for d in dias]      # los días de la línea base no cuentan como monitoreo
    ts = datetime(ultimo.year, ultimo.month, ultimo.day, tzinfo=UTC) + timedelta(days=1)   # fin de la ventana
    rid = f"rv-{persona_id}-{indicador.value}-{ultimo.isoformat()}"
    recibo = recibo_verde(recibo_id=rid, linea=lb, valores=valores, ts=ts, sujeto=persona_id, indicador=indicador, unidad=s.unidad,
                          semilla=SEMILLA, hash_preregistro=hash_preregistro, banner=banner, h=H_FB009)
    if recibo is not None:
        return Evaluacion(recibo, None)
    regla = regla_exacta(K_REF, H_FB009, lb.media, lb.sigma_efectiva)
    r = ejecutar_regla(regla, [v for v in valores if v is not None])
    alarma = DC05Alarma(alarma_id=f"al-{persona_id}-{indicador.value}-{ultimo.isoformat()}", ts_utc=ts, indicador=indicador, detector=Detector.CUSUM,
                        sentido=Sentido.ALZA if r.sentido == "alza" else Sentido.CAIDA, umbral=H_FB009, valor_cruzado=r.s_cruzado,
                        regla_exacta=regla, semilla=SEMILLA, hash_preregistro=hash_preregistro, estado=EstadoAlarma.ACTIVA)
    return Evaluacion(None, alarma)
