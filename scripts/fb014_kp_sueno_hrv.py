"""M4.6 · FB-014: sueño/HRV × Kp (LifeSnaps REAL × GFZ Kp). Una sola ejecución; exige acta e intactos los datos."""
import csv
import hashlib
import json
import sys
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.motor.exposicion import contraste, exposicion, kp_max_por_dia  # noqa: E402

ACTA, SEMILLA = "FB-014", 20261113
CSV = RAIZ / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"
KP = RAIZ / "data/externos/gfz_kp/Kp_ap_since_1932.txt"
SHA = {CSV: "82c84ee495be4b0ff636a8a44271ffb124e2358d9dd52012b529b897f3d54963",
       KP: "d61e03ada312c1d3af8a3235e5d4a566951aabc8e7c69967aa69fb6627a99684"}
D0, D1, ALFA = date(2021, 4, 8), date(2022, 1, 22), 0.05 / 4


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    for ruta, h in SHA.items():
        if hashlib.sha256(ruta.read_bytes()).hexdigest() != h:
            print("datos distintos del preregistro:", ruta.name); return 2
    registro = RAIZ / "docs/actas/RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in registro.read_text(encoding="utf-8").splitlines() if l):
        print("ya ejecutada"); return 1
    kp = kp_max_por_dia(KP)
    dias = [D0 + timedelta(i) for i in range((D1 - D0).days + 1)]
    expo = exposicion([kp[d] for d in dias])
    filas = list(csv.DictReader(CSV.read_text(encoding="utf-8").splitlines()))
    out = {}
    for col in ("minutesAsleep", "rmssd"):
        por = defaultdict(list)
        for r in filas:
            try:
                v, d = float(r[col]), date.fromisoformat(r["date"])
            except ValueError:
                continue
            if v == v and D0 <= d <= D1:
                por[r["id"]].append(((d - D0).days, v))
        personas = {p: s for p, s in por.items() if len(s) >= 30}
        c = contraste(personas, expo, SEMILLA)
        c["H1"] = "NO REFUTADA" if c["p_S1_bilateral"] <= ALFA else "REFUTADA"
        c["H2"] = "NO REFUTADA" if c["p_S2_unilateral"] <= ALFA else "REFUTADA"
        out[col] = c
        print(f"\n== {col} · {c['n_personas']} personas ==\nS1 (media ρ) = {c['S1_obs']:+.4f}  nulo 95 % [{c['S1_nulo_q025_q975'][0]:+.4f}, {c['S1_nulo_q025_q975'][1]:+.4f}]  p = {c['p_S1_bilateral']:.4f}  → H1 {c['H1']}")
        print(f"S2 (sd ρ)    = {c['S2_obs']:.4f}  nulo medio {c['S2_nulo_media']:.4f}  p = {c['p_S2_unilateral']:.4f}  → H2 {c['H2']}")
    estado = "sostenida" if any(v["H1"] == "NO REFUTADA" and v["H2"] == "NO REFUTADA" for v in out.values()) else (
        "refutada" if all(v["H1"] == "REFUTADA" and v["H2"] == "REFUTADA" for v in out.values()) else "mixto")
    print(f"\nESTADO DE LA TARJETA: {estado}   (α Bonferroni = {ALFA})")
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256,
             "acta_registrada_utc": acta.registrada_utc, "semillas": [SEMILLA], "datos_sha256": {p.name: h for p, h in SHA.items()},
             "banner": "REAL (LifeSnaps, no astronautas × Kp GFZ)", "resultados": out, "estado_tarjeta": estado}
    with registro.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
