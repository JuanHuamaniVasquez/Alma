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
RES = {"temp-fc": ("H1", 0.241, 0.72, 47), "resp-fc": ("H3", 0.271, 0.79, 33)}
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
