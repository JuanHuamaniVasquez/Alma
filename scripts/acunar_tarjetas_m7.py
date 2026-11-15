"""M7.6/M7.7 · Acuña dos tarjetas DC-12 con datos REALES de astronautas (OSDR OSD-569, Inspiration4). Idempotente. Cada una lleva su acta sellada ANTES de probar.
Uso: uv run python scripts/acunar_tarjetas_m7.py"""
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.fabrica import mesa  # noqa: E402
from src.gobernanza.preregistro import leer_indice  # noqa: E402

H = {e.acta: e.hash_sha256 for e in leer_indice(RAIZ)}
OSD569 = {"id": "OSD-569", "tipo": "accesión OSDR"}
P = lambda d, c, n: {"datos": d, "computo": c, "dias": n}
CUERPO = lambda a, b: {"senal_cuerpo": a, "otra_senal": b, "tipo_otra_senal": "cuerpo"}

TARJETAS = [
    ("hemograma-banda-personal", dict(par_variables=CUERPO("linfocitos absolutos de cada astronauta (hemograma)", "su propia línea base de 3 extracciones previas al vuelo"),
        mecanismo="Respuesta de estrés inmune al regreso del vuelo (redistribución de linfocitos; ancla por verificar en M5.5): una banda personal debería ver la caída el día del aterrizaje",
        prediccion="En R+1, los linfocitos absolutos salen por debajo de la banda de predicción personal (n = 3, t = 4,30) en ≥ 2 de 4 astronautas.",
        senal_refutadora="Menos de 2 de 4 fuera de la banda (acta FB-024, H2).", fuentes=[OSD569],
        precio=P("OSD-569 CBC (9 KB), ya descargado", "intervalo de predicción t", 1), valor_si_cierta=["DC-05", "DC-14"],
        estado="refutada", preregistro_hash=H["FB-024"]), "FB-024: 0 de 4 pese a una caída mediana de −23,8 %; la banda con 3 puntos es demasiado ancha"),
    ("hemograma-banda-agrupada", dict(par_variables=CUERPO("linfocitos absolutos de cada astronauta (hemograma)", "la variación intra-persona AGRUPADA de las 4 personas"),
        mecanismo="Tomar prestada la variación intra-persona del grupo da más grados de libertad (t = 2,36 en vez de 4,30) y estrecha la banda (análisis exploratorio, mismos datos que FB-024)",
        prediccion="En R+1, los linfocitos absolutos salen por debajo de la banda agrupada en ≥ 2 de 4 astronautas.",
        senal_refutadora="Menos de 2 de 4 fuera de la banda agrupada (acta FB-025, H1).", fuentes=[OSD569],
        precio=P("OSD-569 CBC (9 KB), ya descargado", "varianza agrupada", 1), valor_si_cierta=["DC-05", "DC-14"],
        estado="refutada", preregistro_hash=H["FB-025"]), "FB-025: 0 de 4; las bandas se estrechan ~30 %, pero el piso de detección sigue en ±70 % de la media (la variación diaria es enorme)"),
]


def main() -> int:
    ruta = RAIZ / "data/fundicion/tarjetas.jsonl"
    existentes = {str(t.tarjeta_id) for t in mesa.leer(ruta)}
    en_path = RAIZ / "data/fundicion/en.json"
    en = json.loads(en_path.read_text(encoding="utf-8"))
    EN = {
        "hemograma-banda-personal": {"title": "A personal band sees astronauts' blood change", "prediction": "On landing day, lymphocytes fall below each astronaut's own prediction band (built from three pre-flight draws) in at least 2 of 4 astronauts.",
                                     "refuter": "Fewer than 2 of 4 leave the band (act FB-024, H2).", "mechanism": "Immune stress response on return from flight (lymphocyte redistribution).",
                                     "result": "Refuted on real astronaut data (NASA OSDR, Inspiration4): 0 of 4, despite a median fall of 24% — the band built from 3 samples is too wide to see it (FB-024)."},
        "hemograma-banda-agrupada": {"title": "Borrowing the group's variation narrows the band", "prediction": "On landing day, lymphocytes fall below the pooled band (variation shared across the four astronauts) in at least 2 of 4.",
                                     "refuter": "Fewer than 2 of 4 leave the pooled band (act FB-025, H1).", "mechanism": "Pooling within-person variation gives more degrees of freedom (t = 2.36 instead of 4.30) and a tighter band (exploratory: same data as FB-024).",
                                     "result": "Refuted on real astronaut data: 0 of 4. Bands narrow by about 30%, but the detection floor stays near ±70% of the person's mean — day-to-day variation is huge (FB-025)."},
    }
    for clave, datos, nota in TARJETAS:
        t = mesa.acunar({"tarjeta_id": mesa.id_de(clave), **datos})
        if str(t.tarjeta_id) not in existentes:
            mesa.registrar(ruta, t, nota)
        en["tarjetas"][str(mesa.id_de(clave))] = EN[clave]
    en_path.write_text(json.dumps(en, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(mesa.tablero(mesa.leer(ruta)), ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
