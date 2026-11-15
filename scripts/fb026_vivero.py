"""M9 · FB-026: ejecuta las hipótesis GENERADAS por el laboratorio (vivero) con la MISMA especificación que redactó el acta (`generador.TEST_SPEC`). Una sola ejecución.
Uso:  uv run python scripts/fb026_vivero.py"""
import csv
import hashlib
import json
import statistics
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.fabrica.generador import TEST_SPEC  # noqa: E402
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.motor.intrapersona import contraste  # noqa: E402

ACTA, SEMILLA, ALFA, MIN_DIAS, DESPLAZ = "FB-026", 20261113, 0.05 / 3, 30, 40
CLAVES = ["sueno-fc", "sueno-rmssd", "carga-rmssd"]
CSV = RAIZ / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"
SHA = "82c84ee495be4b0ff636a8a44271ffb124e2358d9dd52012b529b897f3d54963"


def num(t):
    try:
        v = float(t)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def personas(filas, sp, desplazar=0):
    por = defaultdict(list)
    for r in filas:
        x, y = num(r[sp["x_col"]]), num(r[sp["y_col"]])
        if x is not None and y is not None:
            por[r["id"]].append((x, y))
    out = {}
    for p, v in por.items():
        if len(v) < MIN_DIAS:
            continue
        med = statistics.median(x for x, _ in v)
        et = [1 if (x < med if sp["x_lado"] == "bajo" else x > med) else 0 for x, _ in v]
        if desplazar:
            et = et[desplazar % len(et):] + et[:desplazar % len(et)]            # el placebo rompe la coincidencia temporal y conserva la distribución
        out[p] = [(e, y) for e, (_, y) in zip(et, v)]
    return out


def veredicto(r, sp):
    ok_efecto = r["S"] >= sp["efecto_min"] if sp["signo"] > 0 else r["S"] <= -sp["efecto_min"]
    return "SOSTENIDA" if ok_efecto and r["p_unilateral"] <= ALFA else "REFUTADA"


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    if hashlib.sha256(CSV.read_bytes()).hexdigest() != SHA:
        print("CSV distinto del preregistrado"); return 2
    reg = RAIZ / "docs/actas/RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in reg.read_text(encoding="utf-8").splitlines() if l):
        print(f"{ACTA} ya se ejecutó: una sola vez."); return 1
    filas = list(csv.DictReader(CSV.read_text(encoding="utf-8").splitlines()))
    print(f"*** {ACTA} · acta sha256={acta.hash_sha256} · REAL (LifeSnaps, no astronautas) ***")
    res, v = {}, {}
    for i, c in enumerate(CLAVES, start=1):
        sp = TEST_SPEC[c]
        r = contraste(personas(filas, sp), sp["estandarizar"], SEMILLA, sp["signo"])
        res[c] = {**r, "veredicto": veredicto(r, sp), "spec": sp}
        v[f"H{i}_{c}"] = res[c]["veredicto"]
        print(f"  H{i} {c:12s} {r['n_personas']:3d} personas · S = {r['S']:+.4f} {sp['unidad']} · p = {r['p_unilateral']:.4f} → {res[c]['veredicto']}")
    sp0 = TEST_SPEC[CLAVES[0]]
    rp = contraste(personas(filas, sp0, DESPLAZ), sp0["estandarizar"], SEMILLA, sp0["signo"])
    placebo_ok = veredicto(rp, sp0) != "SOSTENIDA"
    v[f"H{len(CLAVES) + 1}_control_placebo"] = "VÁLIDO" if placebo_ok else "INVÁLIDO"
    print(f"  control placebo ({DESPLAZ} días): S = {rp['S']:+.4f} · p = {rp['p_unilateral']:.4f} → {'VÁLIDO' if placebo_ok else 'INVÁLIDO'}")
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256, "acta_registrada_utc": acta.registrada_utc, "semillas": [SEMILLA],
             "csv_sha256": SHA, "banner": "REAL (LifeSnaps, no astronautas)", "alfa": ALFA, "hipotesis": res, "placebo": {**rp, "desplazamiento": DESPLAZ}, "veredictos": v}
    with reg.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")
    print("Límites: no son astronautas; asociaciones intrapersonales, no causalidad; pareo por fila.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
