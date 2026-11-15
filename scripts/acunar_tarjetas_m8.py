"""M8 · Acuña con el GENERADOR las tarjetas que el vivero marca «ya_probada» (FB-022: sus hipótesis estaban preregistradas y sostenidas). Idempotente. Uso: uv run python scripts/acunar_tarjetas_m8.py"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.fabrica import generador as G, mesa  # noqa: E402
from src.gobernanza.preregistro import leer_indice  # noqa: E402

H = {e.acta: e.hash_sha256 for e in leer_indice(RAIZ)}
LS = {"id": "10.1038/s41597-022-01764-x", "tipo": "DOI"}
P = lambda d, c, n: {"datos": d, "computo": c, "dias": n}
CUERPO = lambda a, b: {"senal_cuerpo": a, "otra_senal": b, "tipo_otra_senal": "cuerpo"}
M = {m.clave: m for m in G.BIBLIOTECA}

TARJETAS = [
    ("temp-fc", dict(par_variables=CUERPO("temperatura nocturna de la muñeca de cada persona", "su pulso en reposo (mismos días)"), mecanismo=M["temp-fc"].mecanismo + "; ancla por verificar en M5.5",
        prediccion="En la mitad de PRUEBA de cada serie, la mediana de ρ de Spearman intrapersonal entre temperatura nocturna y pulso en reposo es ≥ 0,20 y ≥ 65 % de las personas tienen ρ > 0.",
        senal_refutadora="Mediana < 0,20 o < 65 % de personas con ρ > 0 (acta FB-022, H1).", fuentes=[LS], precio=P("LifeSnaps (S-07), ya cargado", "Spearman intrapersona, mitad/mitad", 1), valor_si_cierta=["DC-05"],
        estado="sostenida", preregistro_hash=H["FB-022"]), "FB-022 H1: ρ mediana +0,24; 72 % de 47 personas positivas"),
    ("resp-fc", dict(par_variables=CUERPO("frecuencia respiratoria nocturna de cada persona", "su pulso en reposo (mismos días)"), mecanismo=M["resp-fc"].mecanismo + "; ancla por verificar en M5.5",
        prediccion="En la mitad de PRUEBA, la mediana de ρ de Spearman intrapersonal entre respiración nocturna y pulso en reposo es ≥ 0,20 y ≥ 65 % de las personas tienen ρ > 0.",
        senal_refutadora="Mediana < 0,20 o < 65 % de personas con ρ > 0 (acta FB-022, H3).", fuentes=[LS], precio=P("LifeSnaps (S-07), ya cargado", "Spearman intrapersona, mitad/mitad", 1), valor_si_cierta=["DC-05"],
        estado="sostenida", preregistro_hash=H["FB-022"]), "FB-022 H3: ρ mediana +0,27; 79 % de 33 personas positivas"),
]
EN = {"temp-fc": {"title": "Warmer nights, faster resting pulse", "prediction": "Within each person, on held-out days, nightly skin temperature and resting pulse rise together (median rank correlation ≥ 0.20, ≥ 65% of people positive).",
                  "refuter": "Median below 0.20 or fewer than 65% positive (act FB-022, H1).", "mechanism": "Thermoregulation: a warmer night raises resting heart rate.", "result": "Sustained on real wearable data: median ρ = +0.24, 72% of 47 people positive (FB-022). Real coupling, modest size."},
      "resp-fc": {"title": "Faster breathing, faster pulse", "prediction": "Within each person, on held-out days, nightly breathing rate and resting pulse rise together (median rank correlation ≥ 0.20, ≥ 65% positive).",
                  "refuter": "Median below 0.20 or fewer than 65% positive (act FB-022, H3).", "mechanism": "Cardiorespiratory coupling.", "result": "Sustained on real wearable data: median ρ = +0.27, 79% of 33 people positive (FB-022)."}}

# FB-026: hipótesis del vivero, redactadas por el generador y ejecutadas una vez
_F26 = {"sueno-fc": ("pulso en reposo", "FB-026 H1: +0,250 lpm (p = 0,0034) < 0,5 lpm mínimo preregistrado, 50 personas", "refutada"),
        "sueno-rmssd": ("rmssd nocturna", "FB-026 H2: −0,206 sd (p = 0,0001), 36 personas; placebo válido", "sostenida"),
        "carga-rmssd": ("rmssd nocturna", "FB-026 H3: +0,026 sd (p = 0,72), 36 personas", "refutada")}
for _c, (_y, _nota, _est) in _F26.items():
    _sp = G.TEST_SPEC[_c]
    _lado = "por debajo" if _sp["x_lado"] == "bajo" else "por encima"
    TARJETAS.append((_c, dict(par_variables=CUERPO("%s de cada persona (cortado en su mediana personal)" % ("minutos dormidos" if _sp["x_col"] == "minutesAsleep" else "minutos de actividad intensa"), "su %s" % _y),
        mecanismo=M[_c].mecanismo, prediccion="Intrapersonal: los días con %s %s de su mediana personal difieren en %s en S %s %g %s (p unilateral ≤ 0,0167)." % (
            "sueño" if _sp["x_col"] == "minutesAsleep" else "actividad intensa", _lado, _y, "≥" if _sp["signo"] > 0 else "≤", _sp["signo"] * _sp["efecto_min"], _sp["unidad"]),
        senal_refutadora="S no alcanza el mínimo preregistrado o p > 0,0167 (acta FB-026); el placebo con etiquetas desplazadas debe ser nulo.", fuentes=[LS], precio=P("LifeSnaps (S-07), ya cargado", "barajado intrapersona (10 000)", 1),
        valor_si_cierta=["DC-02", "DC-05"], estado=_est, preregistro_hash=H["FB-026"]), _nota))
EN.update({"sueno-fc": {"title": "Short sleep, faster resting pulse", "prediction": "Within each person, days with sleep below their own median have a resting pulse at least 0.5 bpm higher.", "refuter": "Effect under 0.5 bpm or p > 0.0167; the placebo (labels shifted 40 days) must be null (act FB-026).",
                        "mechanism": "Sleep restriction raises sympathetic activation.", "result": "Refuted by the sealed rule: the effect is real (+0.25 bpm, p = 0.003) but half the minimum we fixed before looking. Written by the lab's generator (FB-026)."},
           "sueno-rmssd": {"title": "Short sleep, lower overnight HRV", "prediction": "Within each person, days with sleep below their own median have overnight heart-rate variability at least 0.05 sd lower.", "refuter": "Effect smaller than 0.05 sd or p > 0.0167; the placebo must be null (act FB-026).",
                          "mechanism": "Sleep restriction lowers vagal tone.", "result": "Sustained on real wearable data: −0.21 sd (p = 0.0001, 36 people); the placebo sees nothing. The lab's first clean result, written by its own generator (FB-026)."},
           "carga-rmssd": {"title": "A hard day, a quieter night", "prediction": "Within each person, days with intense activity above their own median have overnight heart-rate variability at least 0.05 sd lower.", "refuter": "Effect smaller than 0.05 sd or p > 0.0167 (act FB-026).",
                         "mechanism": "Heavy training load lowers vagal activity that night.", "result": "Refuted: no effect (+0.03 sd, p = 0.72). The effect may act on the next night, which a same-row pairing cannot see. Written by the generator (FB-026)."}})


def main() -> int:
    ruta = RAIZ / "data/fundicion/tarjetas.jsonl"
    existentes = {str(t.tarjeta_id) for t in mesa.leer(ruta)}
    en_p = RAIZ / "data/fundicion/en.json"; en = json.loads(en_p.read_text(encoding="utf-8"))
    for clave, datos, nota in TARJETAS:
        t = mesa.acunar({"tarjeta_id": mesa.id_de(clave), **datos})
        if str(t.tarjeta_id) not in existentes:
            mesa.registrar(ruta, t, nota)
        en["tarjetas"][str(mesa.id_de(clave))] = EN[clave]
    en_p.write_text(json.dumps(en, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(mesa.tablero(mesa.leer(ruta)), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
