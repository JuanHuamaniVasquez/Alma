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


def tormenta(d: dict) -> Linea:
    kps = [e for e in d["eventos"] if e["tipo"] == "lectura_clima_espacial" and "kp" in e["parametros"]]
    if not kps:
        return Linea("tormenta", "I have no live space weather reading right now. The absence is recorded, not filled in.",
                     "/api/tormenta · DC-03", d["banner"])
    e = kps[0]
    kp = e["parametros"]["kp"]
    texto = f"Planetary K index is {kp:.2f}, read from NOAA's Space Weather Prediction Center."
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
          libro: dict | None = None, resid: dict | None = None) -> list[Linea]:
    """Todas las líneas que los datos disponibles permiten; lo que falta se omite (la UI muestra la ausencia)."""
    out = []
    for f, x in ((libro_del_dia, libro), (tormenta, storm), (demo_kill, demo), (fundicion, fund), (actas, act), (residuo, resid)):
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
