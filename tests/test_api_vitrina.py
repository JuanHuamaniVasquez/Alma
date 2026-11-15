"""M2.19 · API de lectura de la vitrina: Fundición, actas, demo kill, tormenta. Lee los archivos reales del repo (sin datos inventados)."""
import json
from datetime import UTC, datetime
from pathlib import Path

import pytest
from rest_framework.test import APIClient

from apps.ingesta.models import EventoClimaEspacial

RAIZ = Path(__file__).resolve().parent.parent
H = "e" * 64


def get(url):
    return APIClient().get(url)


def test_fundicion_expone_tablero_tarjetas_detector_y_faro():
    r = get("/api/fundicion/")
    assert r.status_code == 200
    d = r.json()
    assert d["tablero"]["nacidas"] == len(d["tarjetas"]) == 7
    assert d["tablero"]["detectores_nuevos"] == len(d["detectores"]) == 1
    assert all(t["senal_refutadora"] and t["fuentes"] for t in d["tarjetas"])  # sin fuente o sin señal refutadora no existe
    assert len(d["faro"]) == 1
    assert all(t["en"] and t["en"]["refuter"] for t in d["tarjetas"]) and d["detectores"][0]["en"] and d["faro"][0]["en"]  # nada sin su versión en inglés


def test_actas_publica_refutadas_y_hash_de_cada_una():
    d = get("/api/actas/").json()["actas"]
    assert len(d) == len(open(RAIZ / "docs/actas/INDEX.jsonl").read().splitlines())
    assert all(len(a["hash_sha256"]) == 64 for a in d)
    assert any(a["ejecutada"] for a in d) and any(not a["ejecutada"] for a in d)


def test_demo_kill_dos_columnas_y_hash_antes_de_correr():
    d = get("/api/demo-kill/").json()
    assert d["acta_registrada_utc"] < d["ts_ejecucion_utc"]          # el hash precede a la ejecución
    assert d["fuga"]["A_manifiesto"]["alarma"] is False                # ciego
    assert d["fuga"]["B_ley"]["veredicto"] == "NO CIERRA"             # alarma
    assert d["control"]["B_ley"]["veredicto"] == "CIERRA"             # el control puede fallar y no falla
    assert "SIMULADO" in d["banner"]


@pytest.mark.django_db
def test_tormenta_hereda_banner_simulado():
    t = datetime(2026, 11, 15, 12, tzinfo=UTC)
    base = dict(ts_utc_inicio=t, ts_utc_fin=t, tipo="lectura_clima_espacial", parametros={"kp": 3.33}, hash_lectura_cruda=H)
    EventoClimaEspacial.objects.create(evento_id="e1", fuente="swpc", banner="REAL", **base)
    assert get("/api/tormenta/").json()["banner"] == "REAL"
    EventoClimaEspacial.objects.create(evento_id="e2", fuente="simulador", banner="SIMULADO", **base)
    d = get("/api/tormenta/").json()
    assert d["banner"] == "SIMULADO" and len(d["eventos"]) == 2
    assert len(get("/api/tormenta/?tipo=otro").json()["eventos"]) == 0


def test_solo_lectura():
    for u in ("fundicion", "actas", "demo-kill", "tormenta"):
        assert APIClient().post(f"/api/{u}/", {}).status_code == 405


@pytest.mark.django_db
def test_sembrar_demo_es_simulado_reproducible_y_la_fuga_abre_solo_el_aire_del_dia_11():
    from django.core.management import call_command
    call_command("sembrar_demo")
    call_command("sembrar_demo")                                       # idempotente (solo-anexar)
    d = get("/api/libro/dias/").json()
    assert d["dias"] == list(range(1, 15)) and d["ultimo"] == 14 and d["banner"] == "SIMULADO"
    dia11, dia3 = get("/api/libro/dia/11/").json(), get("/api/libro/dia/3/").json()
    assert dia11["presupuestos"]["aire"]["cierra"] is False and dia11["presupuestos"]["agua"]["cierra"] is True
    assert dia3["cierra"] is True and set(dia3["presupuestos"]) == {"aire", "agua"}   # los otros 7 no existen: ausencia = dato


@pytest.mark.django_db
def test_libro_vacio_no_inventa_dias():
    d = get("/api/libro/dias/").json()
    assert d["dias"] == [] and d["ultimo"] is None


@pytest.mark.django_db
def test_sembrar_demo_siembra_el_residuo_dc06_y_la_fuga_es_la_unica_sorpresa():
    from django.core.management import call_command
    call_command("sembrar_demo")
    call_command("sembrar_demo")
    d = get("/api/residuo/").json()
    assert d["banner"] == "SIMULADO" and len(d["habitat"]) == 28
    sorpresas = [r for r in d["habitat"] if r["bandera"] != "normal"]
    assert [(r["presupuesto_id"], r["ts_utc"][:10]) for r in sorpresas] == [("aire", "2026-11-12")]   # día 11 = 2 nov + 10 días
    from src.superficies import narrador
    texto = narrador.residuo(d).texto
    assert "air on 2026-11-12" in texto and "not an alarm" in texto


def test_narrador_residuo_sin_datos_dice_la_ausencia():
    from src.superficies import narrador
    assert "absence" in narrador.residuo({"banner": "REAL", "habitat": []}).texto


# --- inyector de escenarios de LA TORMENTA (UNIVERSO SIMULADO, X-14) -------------------------------------
def test_escenarios_pico_exacto_determinismo_y_banner_simulado():
    from src.motor.escenarios import UMBRAL_KP, tormenta
    for g, umbral in UMBRAL_KP.items():
        s = tormenta(g)
        kps = [e.parametros["kp"] for e in s]
        assert len(s) == 12 and max(kps) == umbral and kps.count(umbral) == 1       # el pico es el umbral NOAA, una sola vez
        assert all(e.banner.value == "SIMULADO" and e.fuente.value == "simulador" and e.tipo.value == "inyeccion_escenario" for e in s)
        assert all(0.0 <= k <= 9.0 for k in kps) and kps[0] < 5 and kps[-1] < kps[4]  # empieza en calma y decae
    assert [e.model_dump() for e in tormenta("G3")] == [e.model_dump() for e in tormenta("G3")]
    assert tormenta("G3")[0].hash_lectura_cruda != tormenta("G4")[0].hash_lectura_cruda   # el hash cubre la serie completa
    with pytest.raises(ValueError):
        tormenta("G9")


@pytest.mark.django_db
def test_api_escenario_es_simulada_reproducible_y_no_toca_la_base():
    from apps.ingesta.models import EventoClimaEspacial
    antes = EventoClimaEspacial.objects.count()
    d = get("/api/tormenta/escenario/G3/").json()
    assert d["banner"] == "SIMULADO" and d["escala"] == "G3" and d["pico_kp"] == 7.0 and d["semilla"] == 20261113
    assert len(d["eventos"]) == 12 and "N(0, 0.2)" in d["receta"] and "receta_en" in d and d["aviso"].startswith("UNIVERSO SIMULADO")
    assert d == get("/api/tormenta/escenario/G3/").json()
    assert get("/api/tormenta/escenario/G7/").status_code == 404
    assert EventoClimaEspacial.objects.count() == antes                             # solo lectura: nada se escribe


# --- los 6 indicadores oficiales como estados agregados (reto NASA) -------------------------------------------------
@pytest.mark.django_db
def test_indicadores_agregados_sin_ids_y_los_bloqueados_no_se_simulan():
    from pathlib import Path

    from django.core.management import call_command
    call_command("sembrar_verdes", csv=str(RAIZ / "data/fixtures/lifesnaps_diario_extracto.csv"))
    call_command("sembrar_verdes", csv=str(RAIZ / "data/fixtures/lifesnaps_diario_extracto.csv"))        # idempotente
    r = get("/api/indicadores/")
    d = r.json()
    por = {i["indicador"]: i for i in d["indicadores"]}
    assert set(por) == {"presión", "fc", "glucosa", "temperatura", "sueño", "ánimo"} and d["banner"] == "REAL"
    for k in ("presión", "glucosa", "temperatura"):
        assert por[k]["bloqueado"] and "nothing is simulated" in por[k]["bloqueado"] and "personas_con_linea_base" not in por[k]
    assert por["ánimo"]["bloqueado"] is None and por["ánimo"]["canal"] == "autorreporte" and por["ánimo"]["reportes"] == 0   # canal abierto, sin reportes: no se inventa ninguno
    for k in ("fc", "sueño"):
        assert por[k]["bloqueado"] is None and por[k]["personas_con_linea_base"] == 1 and por[k]["fuente"].endswith("not astronauts")
        assert por[k]["verde"] + por[k]["sin_datos_suficientes"] + por[k]["alarma"] == 1
    assert "621e2f9167b776a240011ccb" not in r.content.decode()                       # el id pseudónimo jamás sale
    assert APIClient().post("/api/indicadores/", {}).status_code == 405


@pytest.mark.django_db
def test_sembrar_verdes_sin_csv_se_niega_no_simula():
    from django.core.management import call_command
    from django.core.management.base import CommandError
    with pytest.raises(CommandError):
        call_command("sembrar_verdes", csv="/no/existe.csv")


@pytest.mark.django_db
def test_ingestar_swpc_cada_repite_y_se_detiene_sin_red(monkeypatch):
    """`--cada N` repite la ingesta (LA TORMENTA en vivo). Sin red: cada feed deja su DC-13 de fallo; el bucle duerme N s entre rondas."""
    from django.core.management import call_command

    from apps.ingesta.models import IntentoIngesta
    from apps.ingesta.management.commands import ingestar_swpc as cmd
    llamadas = []

    from datetime import UTC, datetime, timedelta

    from src.ingesta.cliente import Respuesta
    reloj = iter(datetime(2026, 11, 15, 12, 0, tzinfo=UTC) + timedelta(seconds=i * 10) for i in range(10))

    def sin_red(*a, **k):
        return Respuesta(None, b"", "OSError: sin red")

    def duerme(s):
        llamadas.append(s)
        if len(llamadas) == 2:
            raise KeyboardInterrupt
    monkeypatch.setattr(cmd, "fetch_http", sin_red)
    monkeypatch.setattr(cmd, "ahora_utc", lambda: next(reloj))
    monkeypatch.setattr(cmd.time, "sleep", duerme)
    with pytest.raises(KeyboardInterrupt):
        call_command("ingestar_swpc", "kp", cada=7)
    assert llamadas == [7, 7] and IntentoIngesta.objects.filter(resultado="fallo").count() == 2   # 2 rondas completas antes de la interrupción; cada fallo es dato


# --- IN-2: captura del ánimo en 3 toques (DC-02) ---------------------------------------------------------------------
@pytest.mark.django_db
def test_animo_valida_con_dc02_guarda_agrega_sin_ids_y_limita_el_ritmo():
    from apps.ingesta.models import Autorreporte
    c = APIClient()
    ok = c.post("/api/animo/", {"persona_id": "crew-ab12cd34", "valor": 4, "duracion_respuesta_s": 2.7}, format="json")
    assert ok.status_code == 201 and Autorreporte.objects.count() == 1
    assert c.post("/api/animo/", {"persona_id": "crew-ab12cd34", "valor": 2, "duracion_respuesta_s": 1.0}, format="json").status_code == 429   # < 10 s
    for malo in ({"persona_id": "crew-zz9yy8xx", "valor": 9, "duracion_respuesta_s": 1.0},           # fuera de la escala
                 {"persona_id": "crew-zz9yy8xx", "valor": 3},                                           # sin duración medida: el contrato lo rechaza
                 {"persona_id": "Juan Pérez!", "valor": 3, "duracion_respuesta_s": 1.0},               # no es un pseudónimo
                 {"persona_id": "crew-zz9yy8xx", "valor": 3, "duracion_respuesta_s": -1.0}):
        assert c.post("/api/animo/", malo, format="json").status_code == 400, malo
    assert Autorreporte.objects.count() == 1
    r = get("/api/indicadores/")
    ani = next(i for i in r.json()["indicadores"] if i["indicador"] == "ánimo")
    assert ani["bloqueado"] is None and ani["reportes"] == 1 and ani["distribucion"]["4"] == 1 and ani["duracion_mediana_s"] == 2.7
    assert "crew-ab12cd34" not in r.content.decode()                                                      # el pseudónimo no sale
    assert c.get("/api/animo/").status_code == 405                                                        # solo se escribe, no se lee


# --- «verifícalo tú mismo»: los bytes del acta sirven para recomputar el hash sellado ---------------------------------
def test_cada_acta_servida_hashea_a_su_hash_sellado_y_no_hay_path_traversal():
    import hashlib
    indice = [json.loads(l) for l in (RAIZ / "docs/actas/INDEX.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()]
    assert len(indice) >= 20
    for a in indice:
        r = get(f"/api/actas/{a['acta']}/archivo/")
        assert r.status_code == 200 and hashlib.sha256(r.content).hexdigest() == a["hash_sha256"], a["acta"]   # el servidor no altera ni un byte
    for malo in ("..%2F..%2F.env", "FB-005%2F..%2F..%2FREADME", "x", "FB-"):
        assert get(f"/api/actas/{malo}/archivo/").status_code == 404, malo
    assert APIClient().post("/api/actas/FB-005/archivo/", {}).status_code == 405


# --- tripulación de 5 (X-15): ficticia, con sustitutos reales y anónimos mostrados solo como estados --------------------
def test_roster_de_5_ficticios_con_indicativos_unicos_y_sin_cian():
    from src.libro.tripulacion import ROSTER, TRIPULACION
    assert TRIPULACION == 5 and len({t.indicativo for t in ROSTER}) == 5 and len({t.color for t in ROSTER}) == 5
    for t in ROSTER:   # ningún color de franja es cian (r bajo, g y b altos): paleta propia, no la firma de las interfaces generadas
        r, g, b = (int(t.color[i:i + 2], 16) for i in (1, 3, 5))
        assert not (r < 120 and g > 150 and b > 150), t.indicativo


@pytest.mark.django_db
def test_tripulacion_solo_estados_sin_ids_y_con_aviso_de_sustituto():
    from django.core.management import call_command
    from apps.motor.models import ReciboVerde
    from src.contratos import CONTRATOS, Banner
    sin = get("/api/tripulacion/").json()
    assert all(t["estado"] is None for t in sin["tripulacion"]) and sin["banner"] == "SIMULADO"     # sin sustitutos reales no se inventa ningún estado
    from apps.motor.repositorio import guardar_recibo_verde
    from datetime import UTC, datetime
    for i in range(8):                                                                               # 8 personas con fc y sueño (estructurales, X-01)
        for ind in ("fc", "sueño"):
            guardar_recibo_verde(CONTRATOS["DC-14"].model_validate(dict(
                recibo_id=f"rv-p{i:02d}-{ind}", ts_utc=datetime(2026, 11, 15, tzinfo=UTC), sujeto=f"persona-{i:02d}", indicador=ind, estado="verde", ventana_dias=14,
                dias_validos=14, detector="cusum", k=0.5, h=10.01, potencia_declarada=0.9, mde_sigma=1.75, mde_fisico=1.0, unidad="x", supuesto="s",
                regla_exacta="r", semilla=20261113, hash_preregistro="a" * 64, banner=Banner.REAL)))
    r = get("/api/tripulacion/")
    d = r.json()
    assert len(d["tripulacion"]) == 5 and d["banner"] == "REAL" and "FICTIONAL" in d["aviso"] and "not an astronaut" in d["aviso"]
    assert all(t["estado"] == {"fc": "verde", "sueño": "verde"} for t in d["tripulacion"])
    assert "persona-" not in r.content.decode()                                                      # el id del sustituto no sale
    assert d == get("/api/tripulacion/").json()                                                      # semilla pública: siempre los mismos sustitutos


def test_toda_acta_tiene_resumen_en_ingles_buscable_y_coherente_con_su_estado():
    d = get("/api/actas/").json()["actas"]
    resultados = {json.loads(l)["acta"] for l in (RAIZ / "docs/actas/RESULTADOS.jsonl").read_text(encoding="utf-8").splitlines() if l.strip()}
    validos = {"refuted", "sustained", "mixed", "inconclusive", "partial", "not_replicated", "not_run", "no_data"}
    for a in d:
        e = a["en"]
        assert e and e["title"] and len(e["summary"]) > 40 and e["tags"] and e["outcome"] in validos and e["data"] in {"real", "simulated", "real+simulated", "none"}, a["acta"]
        if a["acta"] not in resultados:                       # sellada y no ejecutada ⇒ nunca un resultado inventado
            assert e["outcome"] in {"not_run", "no_data"}, a["acta"]
        else:
            assert e["outcome"] not in {"not_run"}, a["acta"]


def test_m6_eproceso_y_nilm_leen_el_registro_sellado():
    """M6.1/M6.2 · las tarjetas de frontera leen los resultados SELLADOS (no recalculan) y lo simulado lleva su banner."""
    e = get("/api/eproceso/").json()
    assert e["banner"] == "SIMULADO" and e["umbral"] == 100 and len(e["curva"]) == 14 and e["curva"][-1] >= e["umbral"]
    assert e["ejecutada"] and e["entrenamiento"]["1.0"]["fpr_entrenamiento"] > 0.04          # la garantía teórica falló en datos reales (FB-021)
    n = get("/api/nilm/").json()
    assert n["banner"] == "SIMULADO" and n["azar"] == 0.2 and n["veredictos"]["H1"] == "REFUTADA"
    assert all(c["exactitud"] > 0.15 for cs in n["curvas"].values() for c in cs)


@pytest.mark.django_db
def test_m6_privacidad_no_publica_el_conteo_exacto():
    p = get("/api/privacidad/").json()
    assert p["epsilon_total"] == 2.0 and p["epsilon_restante"] >= 0 and p["cierra"] and "verdadero" not in json.dumps(p)   # el conteo exacto nunca sale
    assert all("valor_publicado" in a and a["mecanismo"] == "Laplace" for a in p["asientos"])


@pytest.mark.django_db
def test_m6_esperado_y_enlace_llevan_cita_y_no_calculan_nada_nuevo():
    """M6.10/M6.11 · cifras COPIADAS de la fuente (con DOI/URL) y retardo publicado por NASA; el paquete de bajada son solo conteos."""
    e = get("/api/esperado/").json()
    assert len(e["items"]) == 3 and all(i["fuente"] and i["url"] for i in e["items"])
    assert any("6.09" in i["en_vuelo"] for i in e["items"]) and any(i["doi"] == "10.1152/japplphysiol.01196.2011" for i in e["items"])
    l = get("/api/enlace/").json()
    assert l["retardo_min"] == [0, 22] and "0 to 22 minutes" in l["retardo_cita"] and "aggregates only" in l["paquete"]["contenido"]


@pytest.mark.skipif(not (RAIZ / "data" / "externos" / "mitdb" / "100.dat").exists(), reason="falta el ECG real descargado (S-20)")
def test_m6_ecg_real_con_calidad_medida_y_aviso_de_no_astronauta():
    d = get("/api/ecg/").json()
    assert d["banner"] == "REAL" and "not an astronaut" in d["aviso"] and d["calidad"]["sensibilidad"] >= 0.98 and d["calidad"]["ppv"] >= 0.98
    w = get("/api/ecg/?t=300&dur=10").json()
    assert w["fs_envio"] == 180 and len(w["y"]) == 1800


def test_m7_entorno_con_respuestas_reales_guardadas(monkeypatch):
    """M7.1 · el entorno en vivo se prueba con respuestas REALES capturadas (tests/fixtures/entorno/), sin red; si una fuente cae, se dice y no se rellena."""
    from src.ingesta import entorno as E
    from apps.superficies import views
    F = RAIZ / "tests" / "fixtures" / "entorno"
    monkeypatch.setattr(E, "_get", lambda url, t=8.0: json.loads((F / ("iss.json" if "wheretheiss" in url else "protones.json" if "protons" in url else "rayosx.json")).read_text()))
    views._ENTORNO.update(t=0.0, d=None)
    d = get("/api/entorno/").json()
    assert d["banner"] == "REAL" and d["iss"]["disponible"] and d["iss"]["visibilidad"] in {"daylight", "eclipsed", "visible"} and 350 < d["iss"]["alt_km"] < 450
    assert d["protones"]["disponible"] and d["protones"]["umbral_s1_pfu"] == 10.0 and isinstance(d["protones"]["tormenta_s1_o_mas"], bool)
    assert d["rayosx"]["clase"][0] in "ABCMX"
    monkeypatch.setattr(E, "_get", lambda url, t=8.0: (_ for _ in ()).throw(TimeoutError()))
    views._ENTORNO.update(t=0.0, d=None)
    assert get("/api/entorno/").json()["iss"] == {"disponible": False, "fuente": E.URL_ISS, "error": "TimeoutError"}
    views._ENTORNO.update(t=0.0, d=None)


def test_m7_astronautas_solo_agregados_y_osdr_catalogo():
    a = get("/api/astronautas/").json()
    assert a["banner"] == "REAL" and a["ejecutada"] and a["n_personas"] == 4 and a["conciliacion"]["valores"] == 5
    assert not any(c in json.dumps(a) for c in ("C001", "C002", "C003", "C004"))            # ninguna serie ni id de persona cruza a la superficie
    o = get("/api/osdr/").json()
    assert o["n"] >= 50 and o["n_crew"] >= 10 and any(e["accession"] == "OSD-569" for e in o["estudios"])


@pytest.mark.django_db
@pytest.mark.parametrize("url", ["libro/dias/", "alarmas/", "residuo/", "verdes/", "indicadores/", "tripulacion/", "fundicion/", "actas/", "capsulas/", "demo-kill/", "tormenta/",
                                 "tormenta/escenario/G3/", "privacidad/", "nilm/", "eproceso/", "esperado/", "enlace/", "astronautas/", "osdr/"])
def test_toda_respuesta_de_la_api_lleva_banner_real_o_simulado(url):
    """Mandamiento 3 (auditoría 2026-11-15): banner en la respuesta, o en cada elemento de su lista principal. (`entorno/` y `ecg/` se prueban aparte: red/archivo local.)"""
    d = get("/api/" + url).json()
    if "banner" in d:
        assert str(d["banner"]).split()[0] in {"REAL", "SIMULADO", "UNIVERSO"}
        return
    listas = [v for v in d.values() if isinstance(v, list) and v and isinstance(v[0], dict)]
    assert listas and all("banner" in x for x in listas[0]), f"{url} sin banner"


def test_frontera_deriva_colores_y_cifras_del_registro_sellado():
    from apps.superficies.views import _veredicto_agregado as vg
    assert vg({"H1": "SOSTENIDA", "H2": "VÁLIDO"}) == "held" and vg({"H1": "REFUTADA", "H2": "NO CONCLUYENTE"}) == "failed" and vg({"H1": "SOSTENIDA", "H2": "REFUTADA"}) == "mixed"
    f = {x["id"]: x for x in get("/api/frontera/").json()["fichas"]}
    assert f["FB-021"]["numeros"]["fpr_s1_pct"] == 5.06 and f["FB-024"]["numeros"]["filas"] == 1 and f["FB-023"]["numeros"]["mejor_pct"] == 71
    assert all(x["verdict"] in {"held", "failed", "mixed", "measured", "open"} for x in f.values())
