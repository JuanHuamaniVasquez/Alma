"""M4.2/M4.3/M4.7 · Acuña las 5 tarjetas DC-12 de LA FUNDICIÓN y registra la primera predicción del Faro. Idempotente por id.
Cada tarjeta lleva fuentes reales con identificador y el hash del acta preregistrada ANTES de probar. Uso: uv run python scripts/acunar_tarjetas.py"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.fabrica import faro, mesa  # noqa: E402
from src.gobernanza.preregistro import leer_indice  # noqa: E402

H = {e.acta: e.hash_sha256 for e in leer_indice(RAIZ)}
LIFESNAPS = {"id": "10.1038/s41597-022-01764-x", "tipo": "DOI"}
KP = {"id": "10.1029/2020SW002641", "tipo": "DOI"}
ZEN = {"id": "10.5281/zenodo.8018238", "tipo": "DOI"}
JONES = {"id": "20190027319", "tipo": "NTRS"}
P = lambda d, c, n: {"datos": d, "computo": c, "dias": n}
CUERPO = lambda a, b, t="cuerpo": {"senal_cuerpo": a, "otra_senal": b, "tipo_otra_senal": t}

TARJETAS = [
    ("kp-sueno-hrv", dict(par_variables=CUERPO("sueño (min dormidos) y HRV nocturna (rmssd) personales", "índice Kp planetario (clima espacial)", "habitat"),
        mecanismo="Acoplamiento geomagnético–autonómico (heliobiología; evidencia controvertida; ancla por verificar en M5.5)",
        prediccion="Con ≥ 30 días por persona, la media de ρ de Spearman exposición-Kp vs desenlace sale fuera del nulo por desplazamiento circular (p ≤ 0,0125).",
        senal_refutadora="Estadístico dentro del nulo circular (acta FB-014).", fuentes=[LIFESNAPS, KP],
        precio=P("LifeSnaps (S-07) + Kp GFZ (S-09), ya cargados", "10 000 permutaciones", 1), valor_si_cierta=["DC-03", "DC-05"],
        estado="refutada", preregistro_hash=H["FB-014"]), "FB-014: refutada (H1 y H2, 2 desenlaces); potencia limitada (16 días Kp ≥ 5)"),
    ("sueno-corto-cansancio", dict(par_variables=CUERPO("minutos dormidos de la noche", "cansancio autorreportado (TIRED) del mismo día"),
        mecanismo="Restricción de sueño → fatiga subjetiva (relación sueño-vigilia; ancla por verificar en M5.5). Control positivo del pipeline",
        prediccion="Días con sueño < su mediana personal aumentan P(TIRED) ≥ 3 puntos porcentuales respecto a los demás días de la misma persona.",
        senal_refutadora="Diferencia intrapersonal < 0,03 o p > 0,025 (acta FB-016, tarjeta A).", fuentes=[LIFESNAPS],
        precio=P("LifeSnaps (S-07), ya cargado", "10 000 barajados intrapersona", 1), valor_si_cierta=["DC-02", "DC-05"],
        estado="sostenida", preregistro_hash=H["FB-016"]), "FB-016 A: +7,9 puntos (27 personas), p = 0,001. Control positivo superado"),
    ("tension-hrv", dict(par_variables=CUERPO("tensión/ansiedad autorreportada (TENSE/ANXIOUS)", "HRV nocturna (rmssd) del mismo día"),
        mecanismo="Activación simpática ↔ menor variabilidad vagal (ancla por verificar en M5.5)",
        prediccion="Los días tensos tienen rmssd ≤ −0,05 desviaciones típicas respecto a los no tensos de la misma persona.",
        senal_refutadora="Diferencia ≥ −0,05 sd o p > 0,025 (acta FB-016, tarjeta B).", fuentes=[LIFESNAPS],
        precio=P("LifeSnaps (S-07), ya cargado", "10 000 barajados intrapersona", 1), valor_si_cierta=["DC-02", "DC-05"],
        estado="refutada", preregistro_hash=H["FB-016"]), "FB-016 B: +0,03 sd (signo contrario), 13 personas, p = 0,62"),
    ("hueso-upa", dict(par_variables=CUERPO("pérdida ósea del tripulante (calcio urinario)", "obstrucción del ensamble de destilación del UPA por sulfato de calcio", "habitat"),
        mecanismo="Hipercalciuria por pérdida ósea → precipitación de CaSO4 en el DA del UPA (Jones 2019 citando a Do 2016; texto verificado)",
        prediccion="Entre ≥ 8 misiones, el tiempo hasta obstrucción decrece con el calcio urinario agregado: rho ≤ −0,5.",
        senal_refutadora="rho > −0,2 con n ≥ 8 o sin dosis-respuesta (acta FB-017).", fuentes=[JONES],
        precio=P("telemetría UPA + calcio urinario de ≥ 8 misiones (sin acceso público)", "correlación por rangos", 0), valor_si_cierta=["DC-08", "DC-05"],
        estado="sin_datos", preregistro_hash=H["FB-017"]), "bloqueada: no hay datos abiertos; se declara, no se simula"),
    ("pulso-blanqueado", dict(par_variables=CUERPO("pulso diario personal (autocorrelación ≈ 0,18)", "falsas alarmas del detector CUSUM", "habitat"),
        mecanismo="Autocorrelación positiva del pulso diario infla las falsas alarmas del CUSUM; blanquear AR(1) la corregiría (nace del residuo DC-06 de FB-009)",
        prediccion="El detector blanqueado (φ congelado 0,182) baja las falsas alarmas del pulso por debajo de x_crítico en una cohorte independiente.",
        senal_refutadora="x_pw ≥ x_crítico o x_pw > x_base (acta FB-013, H2).", fuentes=[LIFESNAPS, ZEN],
        precio=P("LifeSnaps + Zenodo 8018238 (cargados); falta una cohorte con más unidades", "evaluación del detector", 1), valor_si_cierta=["DC-05", "DC-06"],
        estado="en_prueba", preregistro_hash=H["FB-013"]), "FB-013: H2 NO CONCLUYENTE (el problema no replicó, 2/66); sigue en prueba"),
]


def main() -> int:
    ruta = RAIZ / "data/fundicion/tarjetas.jsonl"
    existentes = {str(t.tarjeta_id) for t in mesa.leer(ruta)}
    for clave, datos, nota in TARJETAS:
        t = mesa.acunar({"tarjeta_id": mesa.id_de(clave), **datos})
        if str(t.tarjeta_id) not in existentes:
            mesa.registrar(ruta, t, nota)
    print(json.dumps(mesa.tablero(mesa.leer(ruta)), ensure_ascii=False))
    f = RAIZ / "data/faro/predicciones.jsonl"
    p = faro.Prediccion("F-001", "OSDR publicará al menos 1 archivo de datos del experimento OS-892 antes del 2027-12-31.",
                        "Se califica VERDADERA si la API oficial https://osdr.nasa.gov/geode-py/ws/repo/experiments/OS-892 lista ≥ 1 elemento en `fields[0].files` en cualquier fecha ≤ 2027-12-31; FALSA si al 2028-01-01 sigue en 0.",
                        0.25, "2026-11-15T07:40:00Z", "2027-12-31", "https://osdr.nasa.gov/geode-py/ws/repo/experiments/OS-892")
    try:
        print("Faro F-001 sha256", faro.registrar(f, p))
    except ValueError as e:
        print("Faro:", e)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
