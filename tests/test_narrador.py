"""SU · el narrador de ALMA solo dice lo que dicen los datos: plantillas deterministas, cada número trazable, ausencia ≠ invención."""
import re

from src.superficies import narrador as n

DEMO = {"acta": "FB-005-D1", "hash_acta": "e0d28c09bf51789725997692f90371c29d8e11edcf77fda7c4ee147838296a36",
        "control": {"fuga_kg": 0.0, "A_manifiesto": {"z": 1.33, "alarma": False}, "B_ley": {"veredicto": "CIERRA"}},
        "fuga": {"fuga_kg": 0.3, "A_manifiesto": {"z": 0.528, "alarma": False}, "B_ley": {"veredicto": "NO CIERRA"}}}
FUND = {"tablero": {"nacidas": 5, "refutada": 2, "sostenida": 1, "detectores_nuevos": 1}}
STORM = {"banner": "REAL", "eventos": [{"tipo": "lectura_clima_espacial", "parametros": {"kp": 3.33}, "fuente": "swpc",
                                         "ts_utc_inicio": "2026-11-15T12:00:00Z", "hash_lectura_cruda": "ab" * 32, "banner": "REAL"}]}
ACTAS = {"actas": [{"ejecutada": True}, {"ejecutada": True}, {"ejecutada": False}]}
LIBRO = {"dia_habitat": 7, "banner": "SIMULADO", "presupuestos": {"aire": {"cierra": True}, "agua": {"cierra": False}}}


def numeros(t):
    return {float(x) for x in re.findall(r"\d+(?:\.\d+)?", t)}


def test_cada_numero_dicho_viene_de_los_datos():
    assert numeros(n.demo_kill(DEMO).texto) == {0.53, 0.3}
    assert numeros(n.fundicion(FUND).texto) == {5, 2, 1}
    assert numeros(n.tormenta(STORM).texto) == {3.33}
    assert numeros(n.actas(ACTAS).texto) == {3, 2, 256}                          # 256 = «SHA-256», nombre del algoritmo
    assert numeros(n.libro_del_dia(LIBRO).texto) == {7, 1, 2}


def test_el_texto_es_determinista_y_el_id_del_audio_depende_del_texto():
    assert n.demo_kill(DEMO) == n.demo_kill(DEMO)
    otra = {**DEMO, "fuga": {**DEMO["fuga"], "fuga_kg": 0.5}}
    assert n.demo_kill(otra).id != n.demo_kill(DEMO).id


def test_cada_linea_lleva_fuente_y_banner_heredado():
    for l in n.todas(demo=DEMO, fund=FUND, storm=STORM, act=ACTAS, libro=LIBRO):
        assert l.fuente and l.banner in ("REAL", "SIMULADO")
    assert n.libro_del_dia(LIBRO).banner == "SIMULADO" and n.demo_kill(DEMO).banner == "SIMULADO"
    assert "e0d28c09" in n.demo_kill(DEMO).fuente


def test_la_ausencia_se_dice_no_se_inventa():
    vacio = n.tormenta({"banner": "REAL", "eventos": []})
    assert "absence" in vacio.texto and not numeros(vacio.texto)
    assert n.todas() == []


def test_si_la_demo_no_se_comporta_como_se_preregistro_alma_lo_dice():
    roto = {**DEMO, "fuga": {**DEMO["fuga"], "B_ley": {"veredicto": "CIERRA"}}}
    assert "did not behave as preregistered" in n.demo_kill(roto).texto


def test_escenario_se_dice_como_simulado_y_sin_numeros_ajenos():
    d = {"escala": "G3", "pico_kp": 7.0, "paso_horas": 3, "semilla": 20261113,
         "eventos": [{"hash_lectura_cruda": "cd" * 32}] * 12}
    l = n.escenario(d)
    assert l.banner == "SIMULADO" and l.clave == "escenario-G3" and "Nothing here is real" in l.texto
    assert numeros(l.texto) == {3, 7, 33}                                  # G3, Kp 7.00, 11 pasos × 3 h


def test_indicadores_dice_estados_y_lo_bloqueado_queda_vacio():
    d = {"banner": "REAL", "indicadores": [
        {"indicador": "fc", "bloqueado": None, "personas_con_linea_base": 70, "verde": 50, "alarma": 8, "sin_datos_suficientes": 12},
        {"indicador": "sueño", "bloqueado": None, "personas_con_linea_base": 60, "verde": 40, "alarma": 5, "sin_datos_suficientes": 15},
        {"indicador": "presión", "bloqueado": "x"}, {"indicador": "glucosa", "bloqueado": "x"},
        {"indicador": "temperatura", "bloqueado": "x"}, {"indicador": "ánimo", "bloqueado": "x"}]}
    l = n.indicadores(d)
    assert numeros(l.texto) == {70, 50, 8, 12, 60, 40, 5, 15} and "nothing is simulated" in l.texto and "not astronauts" in l.texto
    assert "two have a verified" in l.texto and "other four stay empty" in l.texto and l.banner == "REAL"
    assert "absence" in n.indicadores({"banner": "REAL", "indicadores": [{"indicador": "fc", "bloqueado": None, "personas_con_linea_base": 0}]}).texto


def test_indicadores_con_canal_de_animo_lo_cuenta_aparte_y_no_lo_da_por_vacio():
    base = [{"indicador": "fc", "bloqueado": None, "personas_con_linea_base": 10, "verde": 9, "alarma": 1, "sin_datos_suficientes": 0},
            {"indicador": "sueño", "bloqueado": None, "personas_con_linea_base": 10, "verde": 9, "alarma": 0, "sin_datos_suficientes": 1},
            {"indicador": "presión", "bloqueado": "x"}, {"indicador": "glucosa", "bloqueado": "x"}, {"indicador": "temperatura", "bloqueado": "x"}]
    con = n.indicadores({"banner": "REAL", "indicadores": base + [{"indicador": "ánimo", "bloqueado": None, "canal": "autorreporte", "reportes": 3}]})
    assert "Mood is a self-report channel with 3 reports" in con.texto and "other three stay empty" in con.texto
    sin = n.indicadores({"banner": "REAL", "indicadores": base + [{"indicador": "ánimo", "bloqueado": None, "canal": "autorreporte", "reportes": 0}]})
    assert "no reports yet; I will not invent any" in sin.texto


def test_frases_de_anillos_indicadores_y_astronauta_solo_dicen_lo_que_hay():
    ln = {"emision_esperada": 3.56, "emision_observada": 4.011, "residuo_contable": 0.451, "incertidumbre_del_manifiesto": 0.2, "cierra": False}
    a = n.presupuesto(11, "aire", ln, "SIMULADO")
    assert a.clave == "ring-aire-11" and "does not close" in a.texto and "question, not a verdict" in a.texto and numeros(a.texto) == {11, 3.56, 4.01, 0.451, 0.4}
    vacio = n.presupuesto(14, "energia", None, "SIMULADO")
    assert vacio.clave == "ring-energia" and "nothing is simulated" in vacio.texto and not numeros(vacio.texto)
    fc = n.indicador({"indicador": "fc", "bloqueado": None, "personas_con_linea_base": 68, "verde": 58, "alarma": 8, "mde_sigma_mediana": 1.75, "potencia_declarada": 0.9})
    assert numeros(fc.texto) == {58, 68, 8, 1.75, 90} and "Known limit" in fc.texto
    assert "no data" in n.indicador({"indicador": "glucosa", "bloqueado": "x"}).texto and not numeros(n.indicador({"indicador": "glucosa", "bloqueado": "x"}).texto)
    assert "Mood" in n.indicador({"indicador": "ánimo", "bloqueado": None, "canal": "autorreporte", "reportes": 5}).texto
    assert "not a real person" in n.astronauta().texto
