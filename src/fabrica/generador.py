"""FA-1b · El GENERADOR de hipótesis de LA FUNDICIÓN: cruza una BIBLIOTECA de mecanismos con el CATÁLOGO de datos que de verdad existen y emite candidatos (vivero).

No mira resultados: parte de mecanismos (con su ancla) y comprueba si la cuestión es respondible con los datos cargados (cuántos pares persona-día reales hay). Un candidato con datos
es «listo para sellar» (falta preregistrarlo con hash ANTES de correr: nada se prueba aquí); sin datos es «bloqueado» y dice exactamente qué dato falta. Jamás simula el dato que falta.
Regla DC-12: sin fuente con identificador no hay tarjeta; el generador solo emite candidatos con fuente verificada.
"""
from __future__ import annotations

import csv
import uuid
from dataclasses import dataclass
from pathlib import Path

LIFESNAPS = {"id": "10.1038/s41597-022-01764-x", "tipo": "DOI", "nombre": "LifeSnaps (everyday wearers, not astronauts)"}
BARGER = {"id": "25127232", "tipo": "PMID", "nombre": "Barger 2014 — astronaut sleep"}
HUGHSON = {"id": "22134699", "tipo": "PMID", "nombre": "Hughson 2012 — cardiovascular control on the ISS"}
MCBRAYER = {"id": "20220013418", "tipo": "NTRS", "nombre": "McBrayer 2022 — Mars communication delays"}
KP = {"id": "10.1029/2020SW002641", "tipo": "DOI", "nombre": "GFZ Kp index"}
NS = uuid.UUID("5b0e8a1e-7d1c-4f43-9d3a-0a1f5e7a2c11")


@dataclass(frozen=True)
class Mecanismo:
    clave: str
    titulo: str
    mecanismo: str
    causa: str          # variable (clave del catálogo)
    efecto: str
    fuentes: tuple      # fuentes con identificador (la primera, la de los datos)
    mata: str           # señal refutadora PLANTILLA (el umbral final lo fija el acta)
    valor: tuple        # contratos/detectores que aparecerían si sobrevive
    precio_computo: str
    ya_probada_en: str | None = None   # acta que ya lo probó (el generador no lo repite)


# Variable del catálogo → columna del CSV de LifeSnaps (o None si NO existe dato abierto)
CATALOGO = {
    "sueno_min": "minutesAsleep", "fc_reposo": "resting_hr", "rmssd": "rmssd", "temp_noche": "nightly_temperature", "resp_noche": "full_sleep_breathing_rate",
    "estres": "stress_score", "eficiencia_sueno": "sleep_efficiency", "actividad_intensa": "very_active_minutes", "cansancio": "TIRED", "tension": "TENSE/ANXIOUS",
    "kp": "__kp__",                                              # índice Kp de GFZ (archivo propio, no es columna de LifeSnaps)
    "vlf_hf_en_vuelo": None, "sueno_en_vuelo": None, "estres_con_retardo": None,   # no existe dato abierto por persona en vuelo
}

BIBLIOTECA = (
    Mecanismo("sueno-fc", "Short sleep, faster resting pulse", "Restricción de sueño → mayor activación simpática → pulso en reposo más alto al día siguiente (ancla por verificar en M5.5)", "sueno_min", "fc_reposo",
              (LIFESNAPS, BARGER), "Diferencia intrapersonal de pulso en reposo < 0,5 lpm o p > 0,025 entre días de sueño corto y el resto", ("DC-02", "DC-05"), "barajado intrapersona (10 000)"),
    Mecanismo("sueno-rmssd", "Short sleep, lower overnight HRV", "Restricción de sueño → menor variabilidad vagal nocturna (ancla por verificar en M5.5)", "sueno_min", "rmssd",
              (LIFESNAPS, BARGER), "Diferencia intrapersonal de rmssd ≥ −0,05 sd o p > 0,025", ("DC-02", "DC-05"), "barajado intrapersona (10 000)"),
    Mecanismo("carga-rmssd", "A hard day, a quieter night", "Carga de entrenamiento intensa → menor variabilidad vagal esa noche (ancla por verificar en M5.5)", "actividad_intensa", "rmssd",
              (LIFESNAPS,), "Correlación de rangos intrapersonal mediana > −0,1 en prueba (mitad final de cada serie)", ("DC-05", "DC-14"), "Spearman intrapersona, mitad/mitad"),
    Mecanismo("estres-eficiencia", "Stress score, worse sleep efficiency", "Estrés alto → sueño más fragmentado (ancla por verificar en M5.5)", "estres", "eficiencia_sueno",
              (LIFESNAPS,), "Correlación intrapersonal mediana > −0,1 en prueba", ("DC-05",), "Spearman intrapersona, mitad/mitad"),
    Mecanismo("temp-eficiencia", "Warmer skin at night, lighter sleep", "Temperatura nocturna de la muñeca más alta → peor eficiencia del sueño (termorregulación; ancla por verificar en M5.5)", "temp_noche", "eficiencia_sueno",
              (LIFESNAPS,), "Correlación intrapersonal mediana > −0,1 en prueba", ("DC-05",), "Spearman intrapersona, mitad/mitad"),
    Mecanismo("kp-respiracion", "Geomagnetic activity, breathing rate", "Actividad geomagnética → frecuencia respiratoria nocturna (heliobiología; evidencia controvertida)", "kp", "resp_noche",
              (LIFESNAPS, KP), "Estadístico dentro del nulo por desplazamiento circular (p > 0,0125)", ("DC-03", "DC-05"), "10 000 permutaciones circulares"),
    Mecanismo("hf-en-vuelo", "Weightlessness lowers vagal power", "Vuelo espacial → menor potencia de alta frecuencia del intervalo RR (Hughson 2012, 6 astronautas)", "vlf_hf_en_vuelo", "rmssd",
              (HUGHSON,), "HF no menor en vuelo que antes del vuelo en ≥ 4 de 6", ("DC-01", "DC-14"), "pareada pre/en vuelo (n pequeña)"),
    Mecanismo("sueno-en-vuelo", "Sleep in flight vs on the ground", "Vuelo espacial → menos sueño obtenido (Barger 2014: 6,09 h en la ISS)", "sueno_en_vuelo", "sueno_min",
              (BARGER,), "Diferencia en vuelo − tierra ≥ −0,2 h", ("DC-01", "DC-14"), "pareada por astronauta"),
    Mecanismo("retardo-estres", "Delayed ground contact, more crew stress", "Retardo y apagones de comunicación → más estrés del equipo (McBrayer 2022 describe retardos de 0–22 min)", "estres_con_retardo", "tension",
              (MCBRAYER,), "Sin relación dosis-respuesta entre retardo y estrés autorreportado", ("DC-02", "DC-05"), "regresión ordinal por misión"),
    Mecanismo("temp-fc", "Warmer night, faster rest", "Temperatura nocturna más alta → pulso en reposo más alto (termorregulación)", "temp_noche", "fc_reposo",
              (LIFESNAPS,), "Mediana de Spearman de prueba < 0,20 o < 65 % positivos", ("DC-05",), "Spearman intrapersona, mitad/mitad", "FB-022"),
    Mecanismo("resp-fc", "Faster breathing, faster pulse", "Respiración nocturna más rápida → pulso en reposo más alto (acoplamiento cardiorrespiratorio)", "resp_noche", "fc_reposo",
              (LIFESNAPS,), "Mediana de Spearman de prueba < 0,20 o < 65 % positivos", ("DC-05",), "Spearman intrapersona, mitad/mitad", "FB-022"),
)


# Texto de la vitrina (inglés; derivado de los campos en español, que mandan)
EN = {
    "sueno-fc": ("Cutting sleep raises sympathetic activation, so resting pulse should be higher the next day.", "Within-person resting-pulse difference under 0.5 bpm, or p > 0.025, between short-sleep days and the rest."),
    "sueno-rmssd": ("Cutting sleep lowers vagal tone, so overnight heart-rate variability should fall.", "Within-person HRV difference no lower than −0.05 sd, or p > 0.025."),
    "carga-rmssd": ("A hard training day should leave less vagal activity that night.", "Median within-person rank correlation above −0.1 on held-out days."),
    "estres-eficiencia": ("A high stress score should fragment the night: lower sleep efficiency.", "Median within-person correlation above −0.1 on held-out days."),
    "temp-eficiencia": ("A warmer wrist at night should mean lighter, less efficient sleep (thermoregulation).", "Median within-person correlation above −0.1 on held-out days."),
    "kp-respiracion": ("Geomagnetic activity might shift nightly breathing rate (heliobiology; contested).", "The statistic falls inside the circular-shift null (p > 0.0125)."),
    "hf-en-vuelo": ("Weightlessness should lower the high-frequency power of the beat-to-beat interval (Hughson 2012, six astronauts).", "High-frequency power not lower in flight than before flight in at least 4 of 6."),
    "sueno-en-vuelo": ("Spaceflight should cut the sleep obtained (Barger 2014: 6.09 h on the ISS).", "In-flight minus ground difference no lower than −0.2 h."),
    "retardo-estres": ("Delayed and blacked-out ground contact (0–22 min one-way, McBrayer 2022) should raise crew stress.", "No dose–response between delay and self-reported stress."),
    "temp-fc": ("A warmer night should raise resting pulse (thermoregulation).", "Median rank correlation on held-out days below 0.20, or fewer than 65% of people positive."),
    "resp-fc": ("Faster nightly breathing should come with a faster resting pulse (cardiorespiratory coupling).", "Median rank correlation on held-out days below 0.20, or fewer than 65% of people positive."),
}


def id_de(clave: str) -> str:
    return str(uuid.uuid5(NS, "vivero:" + clave))


def _num(x) -> float | None:
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def conteos(csv_ruta: Path) -> dict:
    """Pares REALES disponibles por (causa, efecto): días con ambos valores y personas con ≥ 40 días emparejados."""
    filas = list(csv.DictReader(csv_ruta.open(encoding="utf-8", newline="")))
    out = {}
    for m in BIBLIOTECA:
        a, b = CATALOGO.get(m.causa), CATALOGO.get(m.efecto)
        if a is None or b is None:
            out[m.clave] = {"disponible": False, "pares": 0, "personas": 0, "falta": [k for k in (m.causa, m.efecto) if CATALOGO.get(k) is None]}
            continue
        if a == "__kp__":
            a = None
        por = {}
        for f in filas:
            vb = _num(f.get(b))
            va = 1.0 if a is None else _num(f.get(a))
            if va is not None and vb is not None:
                por[f["id"]] = por.get(f["id"], 0) + 1
        out[m.clave] = {"disponible": True, "pares": sum(por.values()), "personas": sum(1 for v in por.values() if v >= 40), "falta": []}
    return out


def generar(csv_ruta: Path) -> list[dict]:
    cn = conteos(csv_ruta)
    cand = []
    for m in BIBLIOTECA:
        c = cn[m.clave]
        listo = c["disponible"] and c["personas"] >= 20 and m.ya_probada_en is None
        estado = "ya_probada" if m.ya_probada_en else ("listo" if listo else "bloqueado")
        cand.append({"id": id_de(m.clave), "clave": m.clave, "titulo": m.titulo, "mecanismo": m.mecanismo, "causa": m.causa, "efecto": m.efecto,
                     "fuentes": [{"id": f["id"], "tipo": f["tipo"], "nombre": f["nombre"]} for f in m.fuentes], "mata": m.mata, "valor_si_cierta": list(m.valor), "estado": estado,
                     "ya_probada_en": m.ya_probada_en, "datos": {"pares": c["pares"], "personas_con_40_dias": c["personas"], "falta": c["falta"]},
                     "precio": {"datos": ("LifeSnaps cargado: %d pares, %d personas con ≥ 40 días" % (c["pares"], c["personas"])) if c["disponible"] else "no existe dato abierto: " + ", ".join(c["falta"]),
                                "computo": m.precio_computo, "dias": 1 if listo else None},
                     "siguiente": "Preregistrar el acta con hash ANTES de correr" if listo else ("Ya sellada y ejecutada: %s" % m.ya_probada_en if m.ya_probada_en else "Esperar a que el dato exista; no se simula"),
                     "en": {"mechanism": EN[m.clave][0], "kill": EN[m.clave][1],
                            "price": (f"Real wearable data held: {c['pares']:,} person-days, {c['personas']} people with at least 40 days." if c["disponible"] else "No open data exists for: " + ", ".join(c["falta"]).replace("_", " ") + "."),
                            "compute": ("About 1 day of compute." if listo else "Cannot be run today: we do not fill the gap with invented numbers."),
                            "next": ("Seal the preregistration (hash) before running anything." if listo else f"Already sealed and run: {m.ya_probada_en}." if m.ya_probada_en else "Wait for the data to exist.")}})
    orden = {"listo": 0, "ya_probada": 1, "bloqueado": 2}
    return sorted(cand, key=lambda x: (orden[x["estado"]], -x["datos"]["pares"]))
