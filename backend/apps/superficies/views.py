"""SU · API REST de solo lectura que consumirá la vitrina (DC-04 / DC-05 / DC-06 / DC-08).

Reglas duras:
  · **Privacidad como arquitectura (DOC-01 regla 5):** el contenido individual NUNCA sale. Del hábitat
    se expone el detalle; del cuerpo (`persona_id`) solo agregados y estados: ni ids ni valores.
  · **Banner REAL/SIMULADO en toda respuesta**, heredado de las filas (basta una SIMULADA para que
    la respuesta lo sea; nunca se asciende a REAL en silencio).
  · Solo GET. La ausencia es dato: un día sin libro responde 404 y no un cierre inventado.
"""
from __future__ import annotations

import json
from collections import Counter, defaultdict
from pathlib import Path

from django.conf import settings
from django.http import Http404
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.ingesta.models import EventoClimaEspacial
from apps.libro.models import LineaLibro
from apps.libro.repositorio import a_dominio
from apps.motor.models import Alarma, CierreConservacion, ReciboVerde, ResiduoStream
from src.contratos.comunes import HABITAT, Banner

LIMITE_MAX = 1000


def banner_de(filas) -> str:
    bs = {f.banner for f in filas}
    if not bs:
        return Banner.REAL.value  # sin filas no se afirma nada; el cuerpo lo dirá
    return Banner.SIMULADO.value if Banner.SIMULADO.value in bs else Banner.REAL.value


class SoloLectura(APIView):
    http_method_names = ["get", "head", "options"]


class LibroDia(SoloLectura):
    def get(self, request, dia: int):
        filas = list(LineaLibro.objects.filter(dia_habitat=dia))
        if not filas:
            raise Http404("no hay libro para ese día (la ausencia es dato)")
        dominio = [(f, a_dominio(f)) for f in filas]
        presupuestos: dict[str, dict] = defaultdict(lambda: {"lineas": 0, "abiertas": 0})
        for f, l in dominio:
            p = presupuestos[f.presupuesto_id]
            p["lineas"] += 1
            if f.estado_linea != "cuarentena" and not l.cierra:
                p["abiertas"] += 1
        for p in presupuestos.values():
            p["cierra"] = p["abiertas"] == 0
        habitat = [{
            "presupuesto_id": f.presupuesto_id, "emision_esperada": f.emision_esperada,
            "incertidumbre_del_manifiesto": f.incertidumbre_del_manifiesto, "emision_observada": f.emision_observada,
            "residuo_contable": f.residuo_contable, "estado_linea": f.estado_linea, "cierra": l.cierra,
        } for f, l in dominio if f.sujeto == HABITAT]
        cuerpo = [(f, l) for f, l in dominio if f.sujeto != HABITAT]
        personas = {f.sujeto for f, _ in cuerpo}
        con_abierta = {f.sujeto for f, l in cuerpo if f.estado_linea != "cuarentena" and not l.cierra}
        return Response({
            "banner": banner_de(filas), "dia_habitat": dia,
            "cierra": all(p["cierra"] for p in presupuestos.values()),
            "presupuestos": dict(presupuestos), "habitat": habitat,
            "cuerpo_agregado": {"personas": len(personas), "con_linea_abierta": len(con_abierta)},  # sin ids ni valores
        })


class Alarmas(SoloLectura):
    def get(self, request):
        qs = Alarma.objects.order_by("-ts_utc")
        if estado := request.query_params.get("estado"):
            qs = qs.filter(estado=estado)
        filas = list(qs[:LIMITE_MAX])
        return Response({"banner": banner_de(filas), "alarmas": [{
            "alarma_id": a.alarma_id, "ts_utc": a.ts_utc.isoformat().replace("+00:00", "Z"),
            "presupuesto_id": a.presupuesto_id, "indicador": a.indicador, "detector": a.detector, "sentido": a.sentido, "umbral": a.umbral,
            "valor_cruzado": a.valor_cruzado, "regla_exacta": a.regla_exacta, "semilla": a.semilla,
            "hash_preregistro": a.hash_preregistro, "estado": a.estado, "banner": a.banner,
        } for a in filas]})


class Residuo(SoloLectura):
    def get(self, request):
        try:
            limite = min(int(request.query_params.get("limite", 200)), LIMITE_MAX)
        except ValueError:
            limite = 200
        filas = list(ResiduoStream.objects.order_by("-ts_utc")[:limite])
        habitat = [{
            "ts_utc": r.ts_utc.isoformat().replace("+00:00", "Z"), "indicador": r.indicador, "presupuesto_id": r.presupuesto_id,
            "observado": r.observado, "predicho": r.predicho, "residuo": r.residuo, "sigma_efectiva": r.sigma_efectiva,
            "cusum_acumulado": r.cusum_acumulado, "bandera": r.bandera, "banner": r.banner,
        } for r in filas if r.sujeto == HABITAT]
        por_bandera = Counter(r.bandera for r in filas if r.sujeto != HABITAT)
        return Response({"banner": banner_de(filas), "habitat": habitat,
                         "cuerpo_agregado": {"registros": sum(por_bandera.values()), "por_bandera": dict(por_bandera)}})


class CierresDia(SoloLectura):
    def get(self, request, dia: int):
        filas = list(CierreConservacion.objects.filter(dia_habitat=dia).order_by("bucle"))
        if not filas:
            raise Http404("no hay cierres de conservación para ese día")
        return Response({"banner": banner_de(filas), "dia_habitat": dia, "cierres": [{
            "bucle": c.bucle, "entradas": c.entradas, "salidas": c.salidas, "delta_almacen": c.delta_almacen,
            "perdida_declarada": c.perdida_declarada, "residuo_conservacion": c.residuo_conservacion,
            "incertidumbre_propagada": c.incertidumbre_propagada, "veredicto": c.veredicto, "banner": c.banner,
        } for c in filas]})


class Verdes(SoloLectura):
    """DC-14: del hábitat, el detalle completo; del cuerpo, SOLO agregados (estado, cobertura, MDE en σ): sin ids ni valores físicos."""

    def get(self, request):
        filas = list(ReciboVerde.objects.order_by("-ts_utc")[:LIMITE_MAX])
        habitat = [{
            "ts_utc": r.ts_utc.isoformat().replace("+00:00", "Z"), "presupuesto_id": r.presupuesto_id, "indicador": r.indicador,
            "canal": r.canal, "estado": r.estado, "dias_validos": r.dias_validos, "ventana_dias": r.ventana_dias, "potencia_declarada": r.potencia_declarada,
            "mde_sigma": r.mde_sigma, "mde_fisico": r.mde_fisico, "unidad": r.unidad, "supuesto": r.supuesto,
            "regla_exacta": r.regla_exacta, "semilla": r.semilla, "hash_preregistro": r.hash_preregistro, "banner": r.banner,
        } for r in filas if r.sujeto == HABITAT]
        cuerpo = [r for r in filas if r.sujeto != HABITAT]
        por_estado = Counter(r.estado for r in cuerpo)
        mdes = sorted(r.mde_sigma for r in cuerpo if r.mde_sigma is not None)
        return Response({"banner": banner_de(filas), "habitat": habitat, "cuerpo_agregado": {
            "recibos": len(cuerpo), "por_estado": dict(por_estado),
            "cobertura_media": (sum(r.dias_validos / r.ventana_dias for r in cuerpo) / len(cuerpo)) if cuerpo else None,
            "mde_sigma_mediana": mdes[len(mdes) // 2] if mdes else None}})


def _jsonl(ruta: Path) -> list[dict]:
    return [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l.strip()] if ruta.exists() else []


class Fundicion(SoloLectura):
    """LA FUNDICIÓN como métrica (DC-12): tarjetas con su señal refutadora, tablero, detectores circulados y Faro. Todo real o etiquetado en origen."""

    def get(self, request):
        from src.fabrica import mesa
        raiz = Path(settings.RAIZ)
        tarjetas = mesa.leer(raiz / "data/fundicion/tarjetas.jsonl")
        detectores = mesa.leer_detectores(raiz / "data/fundicion/detectores.jsonl")
        return Response({
            "tablero": mesa.tablero(tarjetas, detectores),
            "tarjetas": [t.model_dump(mode="json") for t in tarjetas],
            "detectores": detectores,
            "faro": _jsonl(raiz / "data/faro/predicciones.jsonl"),
        })


class Actas(SoloLectura):
    """Preregistros con hash (GO-2) y su veredicto: el resultado nulo o refutado se publica igual que el sostenido."""

    def get(self, request):
        raiz = Path(settings.RAIZ) / "docs/actas"
        resultados = {r.get("acta"): r for r in _jsonl(raiz / "RESULTADOS.jsonl")}
        actas = [{
            "acta": a["acta"], "hash_sha256": a["hash_sha256"], "registrada_utc": a["registrada_utc"], "semillas": a["semillas"],
            "estado": a["estado"], "ejecutada": a["acta"] in resultados,
            "veredictos": (resultados.get(a["acta"]) or {}).get("veredictos"),
            "banner": (resultados.get(a["acta"]) or {}).get("banner"),
        } for a in _jsonl(raiz / "INDEX.jsonl")]
        return Response({"actas": actas})


class DemoKill(SoloLectura):
    """Demo kill (M3.4): dos columnas — detector contra manifiesto (ciego) vs detector contra ley (alarma) — con el hash publicado ANTES de correr."""

    def get(self, request):
        raiz = Path(settings.RAIZ) / "docs/actas"
        filas = [r for r in _jsonl(raiz / "RESULTADOS.jsonl") if r.get("acta") == "FB-005-D1"]
        if not filas:
            raise Http404("FB-005-D1 aún no se ha ejecutado")
        r = filas[-1]
        return Response({
            "acta": r["acta"], "hash_acta": r["hash_acta"], "acta_registrada_utc": r["acta_registrada_utc"],
            "ts_ejecucion_utc": r["ts_ejecucion_utc"], "semilla": r["semilla"], "banner": r["banner"],
            "control": r["control"], "fuga": r["fuga"], "prediccion_confirmada": r["prediccion_confirmada"],
            "reglas_de_muerte_cumplidas": r["reglas_de_muerte_cumplidas"],
        })


class Tormenta(SoloLectura):
    """LA TORMENTA: eventos DC-03 (clima espacial). Banner heredado: un evento del simulador vuelve SIMULADO a toda la respuesta."""

    def get(self, request):
        qs = EventoClimaEspacial.objects.order_by("-ts_utc_inicio")
        if tipo := request.query_params.get("tipo"):
            qs = qs.filter(tipo=tipo)
        filas = list(qs[:LIMITE_MAX])
        return Response({"banner": banner_de(filas), "eventos": [{
            "evento_id": e.evento_id, "ts_utc_inicio": e.ts_utc_inicio.isoformat().replace("+00:00", "Z"),
            "ts_utc_fin": e.ts_utc_fin.isoformat().replace("+00:00", "Z"), "tipo": e.tipo, "fuente": e.fuente,
            "parametros": e.parametros, "hash_lectura_cruda": e.hash_lectura_cruda, "banner": e.banner,
        } for e in filas]})
