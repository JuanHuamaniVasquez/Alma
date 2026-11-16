"""SU · La voz de ALMA: un narrador DETERMINISTA. Cada frase = plantilla fija + datos de la API + su fuente. Jamás texto libre.

Regla de honestidad (mandamientos 2 y 3): ALMA solo dice lo que un endpoint de lectura le entrega; cada línea lleva su `fuente`
(acta, hash o endpoint) para mostrarla como subtítulo/recibo; un dato ausente produce una línea de AUSENCIA, no una invención.
La UI y la voz están en inglés (decisión del humano, 2026-11-15); el código y los comentarios, en español.
Dominio puro: recibe los diccionarios que devuelve la API (sin Django).
"""
from __future__ import annotations

import hashlib
from dataclasses import dataclass


@dataclass(frozen=True)
class Linea:
    clave: str    # identificador estable de la escena/pregunta
    texto: str    # lo que ALMA dice (y el subtítulo)
    fuente: str   # de dónde sale (acta + hash corto, o endpoint)
    banner: str   # REAL / SIMULADO: se hereda de los datos

    @property
    def id(self) -> str:
        """Id del audio: hash del texto, de modo que cambiar un dato regenera el audio y el audio viejo nunca se reutiliza."""
        return hashlib.sha256(self.texto.encode("utf-8")).hexdigest()[:16]


def _kg(x: float) -> str:
    return f"{abs(x):.2f}".rstrip("0").rstrip(".") if abs(x) >= 0.005 else "0"


def _corto(h: str) -> str:
    return h[:8]


def demo_kill(d: dict) -> Linea:
    f, c = d["fuga"], d["control"]
    texto = (f"The manifest detector looked at the leak day and saw nothing. Its score was {f['A_manifiesto']['z']:.2f} sigma. "
             f"The conservation law found {_kg(f['fuga_kg'])} kilograms missing, and the loop does not close. "
             f"On the control day, with no leak, the loop closes. The preregistration hash was published before the run.")
    if f["B_ley"]["veredicto"] != "NO CIERRA" or f["A_manifiesto"]["alarma"] or c["B_ley"]["veredicto"] != "CIERRA":
        texto = ("The leak demonstration did not behave as preregistered. I am reporting it as it is. "
                 "The preregistration hash was published before the run.")
    return Linea("demo_kill", texto, f"{d['acta']} · sha256 {_corto(d['hash_acta'])}", "SIMULADO")


def fundicion(d: dict) -> Linea:
    t = d["tablero"]
    texto = (f"The foundry has minted {t['nacidas']} hypothesis cards: {t['refutada']} refuted, {t['sostenida']} sustained, "
             f"and {t['detectores_nuevos']} compiled into a new detector. Refuted cards are published exactly like the sustained ones.")
    return Linea("fundicion", texto, "/api/fundicion · DC-12", "REAL")


def frontier(d: dict) -> Linea:
    """THE FRONTIER: solo hechos ESTABLES (resultado sellado de FB-024 y tamaño del catálogo OSDR); lo «en vivo» no se narra porque el audio es estático."""
    a, o = d["astro"], d["osdr"]
    if not a.get("ejecutada"):
        return Linea("frontier", "I have no astronaut blood record to read. The absence is recorded, not filled in.", "/api/astronautas · FB-024", a["banner"])
    cambio = abs(a["tabla"]["abs_lymphocytes|R+1"]["mediana_cambio_pct"])
    c = a["conciliacion"]
    texto = (f"The Frontier. Four real astronauts from the Inspiration4 mission. Their lymphocytes fell a median {cambio:.0f} percent on landing day, and no one left their personal band, "
             f"because three baseline samples make the band too wide to see it. No alarm is not no effect.")
    return Linea("frontier", texto, f"/api/astronautas · FB-024 · sha256 {_corto(a['hash_acta'])}", a["banner"])


def tormenta(d: dict) -> Linea:
    kps = [e for e in d["eventos"] if e["tipo"] == "lectura_clima_espacial" and "kp" in e["parametros"]]
    if not kps:
        return Linea("tormenta", "I have no live space weather reading right now. The absence is recorded, not filled in.",
                     "/api/tormenta · DC-03", d["banner"])
    e = kps[0]
    texto = ("The planetary K index on screen is read live from NOAA's Space Weather Prediction Center. A geomagnetic storm begins when it crosses the dashed line. "
             "I do not say the number aloud: my voice is recorded, and the Sun is not.")
    return Linea("tormenta", texto, f"{e['fuente']} · {e['ts_utc_inicio']} · sha256 {_corto(e['hash_lectura_cruda'])}", e["banner"])


def actas(d: dict) -> Linea:
    a = d["actas"]
    ejec = [x for x in a if x["ejecutada"]]
    texto = (f"{len(a)} experiments were preregistered with a SHA-256 hash before they ran. {len(ejec)} have been executed, "
             f"each exactly once. Failures are part of the record.")
    return Linea("actas", texto, "/api/actas · GO-2", "REAL")


def libro_del_dia(d: dict) -> Linea:
    pres = d["presupuestos"]
    abiertos = sorted(k for k, v in pres.items() if not v["cierra"])
    if not abiertos:
        texto = f"Day {d['dia_habitat']}. All {len(pres)} books close within their stated uncertainty."
    else:
        texto = (f"Day {d['dia_habitat']}. {len(abiertos)} of {len(pres)} books do not close: {', '.join(abiertos)}. "
                 f"A book that does not close is a question, not a verdict.")
    return Linea(f"libro-{d['dia_habitat']}", texto, f"/api/libro/dia/{d['dia_habitat']} · DC-04", d["banner"])


def todas(*, demo: dict | None = None, fund: dict | None = None, storm: dict | None = None, act: dict | None = None,
          libro: dict | None = None, resid: dict | None = None, ind: dict | None = None, front: dict | None = None) -> list[Linea]:
    """Todas las líneas que los datos disponibles permiten; lo que falta se omite (la UI muestra la ausencia)."""
    out = []
    for f, x in ((libro_del_dia, libro), (tormenta, storm), (demo_kill, demo), (fundicion, fund), (actas, act), (residuo, resid), (indicadores, ind), (frontier, front)):
        if x is not None:
            out.append(f(x))
    return out


def residuo(d: dict) -> Linea:
    """EL RESIDUO: la mayor sorpresa del hábitat (|residuo|/σ). Una bandera de sorpresa NO es una alarma: no tiene recibo de regla."""
    from src.motor.adversario import H_MEDIA
    h = d["habitat"]
    if not h:
        return Linea("residuo", "I have no residual stream to read. The absence is recorded, not filled in.", "/api/residuo · DC-06", d["banner"])
    m = max(h, key=lambda r: abs(r["residuo"]) / r["sigma_efectiva"])
    z = abs(m["residuo"]) / m["sigma_efectiva"]
    fecha = m["ts_utc"][:10]
    nombre = {"aire": "air", "agua": "water"}.get(m["presupuesto_id"], m["presupuesto_id"])
    if m["bandera"] == "normal":
        texto = f"Every residual stays inside two sigma. The largest is {nombre} on {fecha}, at {z:.2f} sigma."
    else:
        texto = (f"The largest surprise is {nombre} on {fecha}: {abs(m['residuo']):.3f} kilograms from the plan, {z:.2f} sigma. "
                 f"The cumulative sum stands at {abs(m['cusum_acumulado']):.2f} of its {H_MEDIA:.2f} threshold. A surprise flag is not an alarm.")
    return Linea("residuo", texto, f"/api/residuo · DC-06 · {fecha}", d["banner"])


def escenario(d: dict) -> Linea:
    """LA TORMENTA simulada: lo dice como simulación, con receta y semilla públicas; jamás se mezcla con el Kp real."""
    horas = (len(d["eventos"]) - 1) * d["paso_horas"]
    texto = (f"Simulated scenario. A {d['escala']} storm builds to a K index of {d['pico_kp']:.2f} and fades over {horas} hours. "
             f"Nothing here is real. The recipe and the public seed are printed, so anyone can regenerate it.")
    return Linea(f"escenario-{d['escala']}", texto, f"simulator · seed {d['semilla']} · sha256 {_corto(d['eventos'][0]['hash_lectura_cruda'])}", "SIMULADO")


_NUM = {0: "zero", 1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six"}
_NOM = {"fc": "heart rate", "sueño": "sleep", "presión": "blood pressure", "glucosa": "glucose", "temperatura": "temperature", "ánimo": "mood"}


def indicadores(d: dict) -> Linea:
    """Los indicadores oficiales como ESTADOS: solo cuenta (personas, verdes, alarmas); lo bloqueado se dice bloqueado, nunca se rellena."""
    todos = d["indicadores"]
    activos = [i for i in todos if not i["bloqueado"] and i.get("personas_con_linea_base")]
    animo = next((i for i in todos if i.get("canal") == "autorreporte"), None)
    vacios = [i for i in todos if i["bloqueado"]]
    if not activos:
        return Linea("indicadores", "I hold no personal baselines yet. The absence is recorded, not filled in.", "/api/indicadores · DC-14", d["banner"])
    partes = [(f"{_NOM[i['indicador']]}: {i['verde']} of {i['personas_con_linea_base']} people with a personal baseline have a green with a receipt, "
               f"{i['alarma']} an alarm, and {i['sin_datos_suficientes']} too few days to say") for i in activos]
    texto = (f"Of the {_NUM[len(todos)]} official indicators, {_NUM[len(activos)]} have a verified sensor uncertainty. For {'; for '.join(partes)}. ")
    if animo is not None:
        texto += (f"Mood is a self-report channel with {animo['reportes']} reports so far, taken by people using this very demo, and no detector yet. "
                  if animo["reportes"] else "Mood is a self-report channel with no reports yet; I will not invent any. ")
    texto += f"The other {_NUM[len(vacios)]} stay empty on purpose: nothing is simulated. This is everyday people, not astronauts."
    return Linea("indicadores", texto, "/api/indicadores · DC-14 · LifeSnaps", d["banner"])


_PRES = {"aire": "Air", "agua": "Water", "energia": "Energy", "dosis": "Dose", "ritmo": "Rhythm", "carga": "Load", "inmunidad": "Immunity",
         "conducta": "Conduct", "tiempo": "Time"}


def presupuesto(dia: int, pres: str, linea: dict | None, banner: str) -> Linea:
    """Lo que ALMA dice al tocar un anillo: la cuenta del libro de ese día, o la ausencia (no hay ancla real, no se simula)."""
    nombre = _PRES[pres]
    if linea is None:
        return Linea(f"ring-{pres}", f"{nombre}: no ledger. No public anchor exists for this book yet, so nothing is simulated. The absence is data.",
                     "/api/libro · DC-04", "SIMULADO")
    res, piso = linea["residuo_contable"], 2 * linea["incertidumbre_del_manifiesto"]
    if linea["cierra"]:
        cierre = "The book closes, inside its stated uncertainty."
    else:
        cierre = "The book does not close. That is a question, not a verdict."
    texto = (f"{nombre}, day {dia}. The manifest expected {linea['emision_esperada']:.2f} kilograms and {linea['emision_observada']:.2f} were observed. "
             f"The residual is {abs(res):.3f} kilograms {'above' if res >= 0 else 'below'} the plan, against a blind floor of {piso:.2f}. {cierre}")
    return Linea(f"ring-{pres}-{dia}", texto, f"/api/libro/dia/{dia} · DC-04", banner)


def indicador(i: dict) -> Linea:
    """Lo que ALMA dice al tocar un marcador del cuerpo. Bloqueado = lo dice; con datos = cuenta de estados; ánimo = cómo funciona (sin cifras)."""
    nom = _NOM[i["indicador"]]
    clave = f"ind-{i['indicador']}"
    if i.get("canal") == "autorreporte":
        return Linea(clave, "Mood is a self-report channel: three touches, and I also record how long you took to answer. It has no detector yet, so its dot stays neutral.",
                     "/api/indicadores · DC-02", "REAL")
    if i["bloqueado"]:
        return Linea(clave, f"{nom.capitalize()}: no data. There is no verified sensor uncertainty for this indicator, so nothing is simulated. The absence is data.",
                     "/api/indicadores · política de datos", "REAL")
    texto = (f"{nom.capitalize()}: {i['verde']} of {i['personas_con_linea_base']} people with a personal baseline have a green with a receipt, {i['alarma']} an alarm. "
             f"A green means it could have seen a drop of {i['mde_sigma_mediana']} sigma with {round(i['potencia_declarada'] * 100)} percent power, and nothing more.")
    if i["indicador"] == "fc":
        texto += " Known limit: daily pulse is autocorrelated, so treat an alarm as a question."
    return Linea(clave, texto, "/api/indicadores · DC-14 · LifeSnaps", "REAL")


def astronauta() -> Linea:
    return Linea("suit", "This is a NASA Z-2 prototype suit, not a real person. The rings are the ship's nine books; the Body view shows the six official indicators. "
                         "Touch a ring or a dot and I will explain it.", "NASA 3D Resources · Z-2", "REAL")


_EST = {"verde": "a green with a receipt", "alarma": "an alarm with a receipt, which is a question, not a verdict", "sin_datos_suficientes": "too few days to say"}


def tripulante(c: dict) -> Linea:
    """Lo que ALMA dice al elegir un tripulante: es ficticio; su estado corporal es de un SUSTITUTO real y anónimo, y se dice."""
    nombre = c["indicativo"].capitalize()
    base = f"{nombre}, {c['rol'].lower()}. A fictional crew member of a simulated universe, and not a real person. "
    if not c.get("estado"):
        return Linea(f"crew-{c['indicativo']}", base + "I have no body states to show for this seat yet; nothing is invented.", "/api/tripulacion · X-15", "SIMULADO")
    e = c["estado"]
    texto = (base + f"The body states you see belong to a stand-in, an anonymous everyday person and not an astronaut. Heart rate: {_EST[e['fc']]}. "
             f"Sleep: {_EST[e['sueño']]}.")
    return Linea(f"crew-{c['indicativo']}", texto, "/api/tripulacion · X-15 · stand-in LifeSnaps", "REAL")
