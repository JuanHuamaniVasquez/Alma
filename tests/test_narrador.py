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
