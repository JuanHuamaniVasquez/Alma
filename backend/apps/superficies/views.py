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


class LibroDias(SoloLectura):
    """Qué días tiene el libro (la vitrina abre en el último). Sin libro: lista vacía, no un día inventado."""

    def get(self, request):
        dias = sorted(set(LineaLibro.objects.values_list("dia_habitat", flat=True)))
        return Response({"banner": banner_de(list(LineaLibro.objects.all()[:LIMITE_MAX])), "dias": dias, "ultimo": dias[-1] if dias else None})


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
        en = json.loads((raiz / "data/fundicion/en.json").read_text(encoding="utf-8"))  # texto en inglés de la vitrina (derivado)
        return Response({
            "tablero": mesa.tablero(tarjetas, detectores),
            "tarjetas": [{**t.model_dump(mode="json"), "en": en["tarjetas"].get(str(t.tarjeta_id))} for t in tarjetas],
            "detectores": [{**d, "en": en["detectores"].get(d["detector"])} for d in detectores],
            "faro": [{**f, "en": en["faro"].get(f["id"])} for f in _jsonl(raiz / "data/faro/predicciones.jsonl")],
        })


class Actas(SoloLectura):
    """Preregistros con hash (GO-2) y su veredicto: el resultado nulo o refutado se publica igual que el sostenido."""

    def get(self, request):
        raiz = Path(settings.RAIZ) / "docs/actas"
        resultados = {r.get("acta"): r for r in _jsonl(raiz / "RESULTADOS.jsonl")}
        en = json.loads((Path(settings.RAIZ) / "data/actas_en.json").read_text(encoding="utf-8"))["actas"]   # resúmenes en inglés (derivados)
        actas = [{
            "acta": a["acta"], "hash_sha256": a["hash_sha256"], "registrada_utc": a["registrada_utc"], "semillas": a["semillas"],
            "estado": a["estado"], "ejecutada": a["acta"] in resultados,
            "veredictos": (resultados.get(a["acta"]) or {}).get("veredictos"),
            "banner": (resultados.get(a["acta"]) or {}).get("banner"), "en": en.get(a["acta"]),
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


class TormentaEscenario(SoloLectura):
    """Escenario SIMULADO de tormenta geomagnética (IN-4, X-14): determinista, con receta y semilla públicas. No escribe en la base."""

    def get(self, request, escala: str):
        from src.motor.escenarios import PASO_H, RECETA, RECETA_EN, UMBRAL_KP, tormenta
        if escala not in UMBRAL_KP:
            raise Http404("escala desconocida (G1…G5)")
        semilla = 20261113
        dias = sorted(set(LineaLibro.objects.values_list("dia_habitat", flat=True)))
        dia = dias[-1] if dias else 1
        ev = tormenta(escala, semilla)
        return Response({
            "banner": Banner.SIMULADO.value, "aviso": f"UNIVERSO SIMULADO — DÍA {dia}", "dia_habitat": dia, "escala": escala,
            "semilla": semilla, "receta": RECETA, "receta_en": RECETA_EN, "paso_horas": PASO_H, "pico_kp": UMBRAL_KP[escala],
            "eventos": [{
                "evento_id": e.evento_id, "ts_utc_inicio": e.ts_utc_inicio.isoformat().replace("+00:00", "Z"), "tipo": e.tipo.value,
                "fuente": e.fuente.value, "parametros": e.parametros, "hash_lectura_cruda": e.hash_lectura_cruda, "banner": e.banner.value,
            } for e in ev]})


class Capsulas(SoloLectura):
    """FA-3 / DC-07: cápsulas exportables de las tarjetas resueltas. Sin límites declarados no hay cápsula (el contrato lo impide)."""

    def get(self, request):
        from src.fabrica.capsula import capsulas
        return Response({"capsulas": [c.model_dump(mode="json") for c in capsulas(Path(settings.RAIZ))]})


class Indicadores(SoloLectura):
    """Los 6 indicadores oficiales del reto, como ESTADOS agregados (nunca ids ni valores). Un indicador sin σ de sensor verificada o sin canal
    de captura NO se simula: se declara bloqueado con su motivo. Datos: personas cotidianas (LifeSnaps), NO astronautas."""

    def get(self, request):
        from apps.motor.models import Alarma
        from src.contratos.comunes import Indicador, IndicadorSensor
        from src.ingesta.incertidumbre import SinIncertidumbreVerificada, sigma_de
        out = []
        for ind in Indicador:
            base = {"indicador": ind.value}
            if ind is Indicador.ANIMO:      # canal de autorreporte (IN-2): solo agregado, sin ids; sin detector todavía (no hay color de estado)
                from apps.ingesta.models import Autorreporte
                rep = list(Autorreporte.objects.filter(tipo="ánimo", registro_ausencia=False))
                dur = sorted(r.duracion_respuesta_s for r in rep)
                out.append({**base, "bloqueado": None, "canal": "autorreporte", "reportes": len(rep), "personas": len({r.persona_id for r in rep}),
                            "distribucion": {str(v): sum(1 for r in rep if r.valor == v) for v in range(1, 6)},
                            "duracion_mediana_s": dur[len(dur) // 2] if dur else None, "escala": "Likert 1-5 (1 = very low, 5 = very good)",
                            "banner": Banner.REAL.value, "fuente": "self-reported by people using this demo: not astronauts"})
                continue
            try:
                sigma_de(IndicadorSensor(ind.value))
            except SinIncertidumbreVerificada:
                out.append({**base, "bloqueado": "No verified sensor uncertainty for this indicator (docs/politica-de-datos.md); nothing is simulated."})
                continue
            rv = [r for r in ReciboVerde.objects.filter(indicador=ind.value, canal="media") if r.sujeto != HABITAT]
            al = Alarma.objects.filter(indicador=ind.value, estado="activa").count()
            estados = Counter(r.estado for r in rv)
            mdes = sorted(r.mde_sigma for r in rv if r.mde_sigma is not None)
            out.append({**base, "bloqueado": None, "personas_con_linea_base": len(rv) + al, "verde": estados.get("verde", 0),
                        "sin_datos_suficientes": estados.get("sin_datos_suficientes", 0), "alarma": al,
                        "cobertura_media": (sum(r.dias_validos / r.ventana_dias for r in rv) / len(rv)) if rv else None,
                        "mde_sigma_mediana": mdes[len(mdes) // 2] if mdes else None, "unidad": rv[0].unidad if rv else None,
                        "potencia_declarada": next((r.potencia_declarada for r in rv if r.potencia_declarada is not None), None), "banner": Banner.REAL.value, "fuente": "LifeSnaps (Zenodo 7229547): everyday people, not astronauts"})
        return Response({"banner": Banner.REAL.value, "indicadores": out})


class ActaArchivo(SoloLectura):
    """Los BYTES EXACTOS del acta preregistrada, para que cualquiera recalcule su SHA-256 (en el navegador) y lo compare con el hash sellado."""

    def get(self, request, acta: str):
        import re

        from django.http import HttpResponse
        if not re.fullmatch(r"FB-[0-9A-Za-z]+(?:-[0-9A-Za-z]+)*", acta):
            raise Http404("id de acta inválido")
        ruta = Path(settings.RAIZ) / "docs/actas" / f"{acta}.md"
        if not ruta.is_file():
            raise Http404("no existe esa acta")
        return HttpResponse(ruta.read_bytes(), content_type="text/markdown; charset=utf-8")


class Tripulacion(SoloLectura):
    """La tripulación SIMULADA de 5 (personajes ficticios) con el estado corporal de un SUSTITUTO real y anónimo (LifeSnaps, no astronautas) por tripulante.
    Solo ESTADOS por indicador (verde / alarma / sin datos suficientes): nunca ids ni valores. El sustituto se elige con una semilla pública."""

    def get(self, request):
        import random
        import re

        from apps.motor.models import Alarma
        from src.libro.tripulacion import ROSTER, SEMILLA_SUSTITUTOS
        estado: dict[str, dict[str, str]] = {}
        for r in ReciboVerde.objects.filter(canal="media", indicador__in=["fc", "sueño"]).exclude(sujeto=HABITAT):
            estado.setdefault(r.sujeto, {})[r.indicador] = r.estado                      # verde | sin_datos_suficientes
        for a in Alarma.objects.filter(indicador__in=["fc", "sueño"], estado="activa"):
            m = re.fullmatch(r"al-(.+)-(fc|sueño)-\d{4}-\d{2}-\d{2}", a.alarma_id)       # ids que genera estado_indicadores.evaluar_persona
            if m:
                estado.setdefault(m.group(1), {})[m.group(2)] = "alarma"
        candidatos = sorted(p for p, e in estado.items() if {"fc", "sueño"} <= set(e))
        elegidos = random.Random(SEMILLA_SUSTITUTOS).sample(candidatos, len(ROSTER)) if len(candidatos) >= len(ROSTER) else []
        return Response({
            "banner": Banner.REAL.value if elegidos else Banner.SIMULADO.value,
            "aviso": "Crew members are FICTIONAL characters of a simulated universe. The body states shown are a stand-in: an anonymous everyday person (LifeSnaps), not an astronaut.",
            "tripulacion": [{"indicativo": t.indicativo, "rol": t.rol, "color": t.color, "piel": t.piel, "pelo": t.pelo, "peinado": t.peinado, "complexion": t.complexion,
                             "estado": ({"fc": estado[elegidos[i]]["fc"], "sueño": estado[elegidos[i]]["sueño"]} if elegidos else None)} for i, t in enumerate(ROSTER)]})


class Privacidad(SoloLectura):
    """M6.4 · El décimo libro: presupuesto de privacidad ε. Publica SOLO conteos ruidosos de la tripulación de 5 (Laplace) y el libro de ε gastado; el conteo exacto
    no sale nunca (con 5 personas, un agregado exacto más su resta identifica a alguien). Banner del conteo = el de la tripulación (stand-in real, no astronautas)."""

    def get(self, request):
        from src.superficies.privacidad import Libro
        datos = Tripulacion().get(request).data
        libro = Libro()
        if datos["tripulacion"] and datos["tripulacion"][0]["estado"]:
            est = [t["estado"] for t in datos["tripulacion"]]
            for ind, etiqueta in (("fc", "crew members with a heart-rate alarm"), ("sueño", "crew members with a sleep alarm")):
                libro.liberar_conteo(etiqueta, sum(e[ind] == "alarma" for e in est), len(est), 0.5)
        return Response({"banner": datos["banner"], "n_tripulacion": len(datos["tripulacion"]), **libro.estado(),
                         "nota": "Each published count spends ε. Exact counts never leave the server: with 5 people, an exact aggregate and one subtraction reveal an individual."})


class Nilm(SoloLectura):
    """M6.2 · Resultado de FB-023 (SIMULADO, X-17): exactitud de atribuir un exceso de CO₂ a un tripulante según el desfase de turnos. Lee el registro sellado, no recalcula."""

    def get(self, request):
        import json
        ruta = Path(settings.BASE_DIR).parent / "docs" / "actas" / "RESULTADOS.jsonl"
        lineas = [json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l]
        r = next((x for x in lineas if x.get("acta") == "FB-023"), None)
        if r is None:
            return Response({"banner": Banner.SIMULADO.value, "ejecutada": False})
        curvas: dict[str, list] = {}
        for k, c in r["celdas"].items():
            curvas.setdefault(str(c["delta"]), []).append({"paso_h": c["paso_h"], "exactitud": c["exactitud"]})
        return Response({"banner": Banner.SIMULADO.value, "ejecutada": True, "hash_acta": r["hash_acta"], "azar": 0.2, "sigma_rel": r["sigma_rel"], "n_por_celda": r["n_por_celda"],
                         "curvas": {d: sorted(v, key=lambda x: x["paso_h"]) for d, v in curvas.items()}, "veredictos": r["veredictos"]})


class EProceso(SoloLectura):
    """M6.1 · FB-021: la garantía anytime-valid y lo que pasó con datos reales. Lee el registro sellado + una curva DEMOSTRATIVA SIMULADA (semilla pública)."""

    def get(self, request):
        import json
        import random

        from src.motor.eproceso import ALFA, mezcla
        ruta = Path(settings.BASE_DIR).parent / "docs" / "actas" / "RESULTADOS.jsonl"
        r = next((x for x in (json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l) if x.get("acta") == "FB-021"), None)
        rng = random.Random(20261113)
        z = [rng.gauss(0, 1) for _ in range(4)] + [rng.gauss(3.2, 1) for _ in range(10)]       # SIMULADO: 4 días sin cambio y un escalón de 3,2σ
        s = (r or {}).get("s_congelado", 1.5)
        return Response({"banner": Banner.SIMULADO.value, "alfa": ALFA, "umbral": 1 / ALFA, "s": s, "curva": [round(m, 4) for m in mezcla(z, s)], "escalon_dia": 5,
                         "ejecutada": r is not None, "hash_acta": (r or {}).get("hash_acta"),
                         "entrenamiento": (r or {}).get("entrenamiento", {}).get("tabla"), "veredictos": (r or {}).get("veredictos"),
                         "banner_resultados": "REAL (LifeSnaps, no astronautas) + escalón SIMULADO"})


_ECG_CACHE: dict = {}


def _ecg():
    """Parsea y procesa UNA vez el registro REAL (lector y detector puros de `src/`); el resultado vive en memoria del proceso."""
    if _ECG_CACHE:
        return _ECG_CACHE
    import statistics

    from src.ingesta import ecg_mitbih as E
    from src.motor.ecg_vitales import FS, comparar, detectar_r, pulso_lpm, rmssd_ms
    reg = E.cargar(Path(settings.BASE_DIR).parent / "data" / "externos" / "mitdb")
    x = list(reg.mlii)
    picos = detectar_r(x)
    lpm = pulso_lpm(picos)
    tend = []
    for t0 in range(0, len(x) // FS - 9, 10):
        v = [p for s, p in lpm if t0 <= s < t0 + 10]
        pk = [p for p in picos if (t0 - 20) * FS <= p < (t0 + 10) * FS]
        if v:
            tend.append({"t": t0, "lpm": round(statistics.median(v), 1), "rmssd": round(rmssd_ms(pk) or 0.0, 1)})
    base = [d["lpm"] for d in tend if d["t"] < 300]                                  # línea base personal = los primeros 5 minutos
    mu, sd = statistics.fmean(base), max(statistics.pstdev(base), 2.0)             # σ mínima de 2 lpm: resolución de una mediana de 10 s
    for d in tend:
        z = (d["lpm"] - mu) / sd
        d["z"] = round(z, 2); d["bandera"] = "sorpresa" if abs(z) > 2 and d["t"] >= 300 else "normal"
    _ECG_CACHE.update(x=x, picos=picos, tend=tend, base={"media": round(mu, 1), "sd": round(sd, 2), "ventana_s": 300}, calidad=comparar(picos, list(reg.latidos_ref)), fs=FS)
    return _ECG_CACHE


class Ecg(SoloLectura):
    """M6.9 · Monitor de constantes con ECG REAL (MIT-BIH registro 100, PhysioNet; paciente ambulatorio anonimizado, NO un astronauta). Con `?t=&dur=` devuelve una ventana de señal."""

    def get(self, request):
        c = _ecg()
        fs = c["fs"]
        if "t" in request.query_params:
            t = max(0.0, float(request.query_params["t"])); dur = min(30.0, max(1.0, float(request.query_params.get("dur", 20))))
            a, b = int(t * fs), min(len(c["x"]), int((t + dur) * fs))
            return Response({"t0": t, "fs_envio": fs // 2, "y": [round(v, 3) for v in c["x"][a:b:2]]})
        from src.ingesta import ecg_mitbih as E
        return Response({"banner": E.BANNER, "fuente": E.FUENTE, "doi": "10.13026/C2F305", "licencia": "Open Data Commons Attribution v1.0",
                         "aviso": "Real ECG of an anonymised hospital outpatient from a public database — not an astronaut. The detector is ours; its accuracy was measured against human beat annotations.",
                         "fs_envio": fs // 2, "duracion_s": len(c["x"]) // fs, "latidos_s": [round(p / fs, 3) for p in c["picos"]], "base": c["base"], "tendencia": c["tend"],
                         "calidad": {k: c["calidad"][k] for k in ("referencia", "detectados", "sensibilidad", "ppv")},
                         "regla": "Surprise flag (not an alarm) when the 10-second pulse is more than 2σ (σ floor 2 bpm) from the first 5 minutes of this same recording."})


class EsperadoEnVuelo(SoloLectura):
    """M6.10 · Lo que la literatura publicada dice que cambia en vuelo, con cifra y cita. Lee `data/referencias/esperado_en_vuelo.json` (copiado de las fuentes, no calculado)."""

    def get(self, request):
        import json
        return Response(json.loads((Path(settings.BASE_DIR).parent / "data" / "referencias" / "esperado_en_vuelo.json").read_text(encoding="utf-8")))


class EnlaceTierra(SoloLectura):
    """M6.11 · Modo sin contacto con la Tierra: retardo publicado por NASA + el paquete de bajada que el Guardián dejaría en cola (SOLO agregados: cuántas alarmas con recibo y cuántos verdes)."""

    def get(self, request):
        import json
        ref = json.loads((Path(settings.BASE_DIR).parent / "data" / "referencias" / "enlace_tierra.json").read_text(encoding="utf-8"))
        return Response({**ref, "banner": Banner.REAL.value,
                         "paquete": {"alarmas_activas_con_recibo": Alarma.objects.filter(estado="activa").count(), "recibos_de_verde": ReciboVerde.objects.count(),
                                     "contenido": "aggregates only: counts and states, never an individual's values"}})


_ENTORNO: dict = {"t": 0.0, "d": None}


class Entorno(SoloLectura):
    """M7.1 · Entorno REAL en vivo de la tripulación: ISS (posición y luz), protones GOES y rayos X solares (el Kp vive en La Tormenta). Si una fuente no responde, `disponible: false` (no se rellena)."""

    def get(self, request):
        import time

        from src.ingesta import entorno as E
        if _ENTORNO["d"] is None or time.time() - _ENTORNO["t"] > 30:                     # caché de 30 s: respeta ≈1 petición/s de la fuente de la ISS
            from concurrent.futures import ThreadPoolExecutor
            with ThreadPoolExecutor(3) as ex:                                              # las tres fuentes en paralelo (≈ 1 s en vez de ≈ 4 s)
                fi, fp, fx = ex.submit(E.seguro, E.iss, E.URL_ISS), ex.submit(E.seguro, E.protones, E.URL_PROT), ex.submit(E.seguro, E.rayosx, E.URL_XR)
            _ENTORNO["d"] = {"banner": Banner.REAL.value, "iss": fi.result(), "protones": fp.result(), "rayosx": fx.result(),
                             "aviso": "Live, real, NASA/NOAA-derived feeds. The ISS position is computed from orbital elements, not station telemetry."}
            _ENTORNO["t"] = time.time()
        return Response(_ENTORNO["d"])


class AstronautasHematologia(SoloLectura):
    """M7.2 · Resultado sellado de FB-024 (hemograma REAL de 4 astronautas de Inspiration4): solo agregados, nunca la serie de una persona."""

    def get(self, request):
        import json
        ruta = Path(settings.BASE_DIR).parent / "docs" / "actas" / "RESULTADOS.jsonl"
        r = next((x for x in (json.loads(l) for l in ruta.read_text(encoding="utf-8").splitlines() if l) if x.get("acta") == "FB-024"), None)
        if r is None:
            return Response({"banner": Banner.REAL.value, "ejecutada": False})
        return Response({"banner": Banner.REAL.value, "ejecutada": True, "hash_acta": r["hash_acta"], "fuente": "NASA OSDR OSD-569 (SpaceX Inspiration4), LSDS-7 CBC", "n_personas": 4,
                         "tiempos": ["R+1", "R+45", "R+82", "R+194"], "conciliacion": {"valores": r["conciliacion"]["valores"], "filas": len(r["conciliacion"]["filas"]), "de_filas": 28}, "tabla": r["tabla"], "veredictos": r["veredictos"],
                         "aviso": "Four real astronauts (civilian crew), three pre-flight draws each, none in flight. Aggregates only."})


class OsdrHumanos(SoloLectura):
    """M7.3 · Instantánea del catálogo REAL de OSDR (estudios con humanos y vuelo espacial)."""

    def get(self, request):
        import json
        return Response(json.loads((Path(settings.BASE_DIR).parent / "data" / "referencias" / "osdr_humanos.json").read_text(encoding="utf-8")))
