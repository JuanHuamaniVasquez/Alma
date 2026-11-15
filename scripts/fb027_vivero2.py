"""M9 · FB-027: segunda tanda de hipótesis GENERADAS por el laboratorio (correlaciones intrapersonales con nulo circular + recuperación a un día). Una sola ejecución.
Uso:  uv run python scripts/fb027_vivero2.py"""
import csv
import hashlib
import json
import statistics
import sys
from collections import defaultdict
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.fabrica.generador import TEST_SPEC  # noqa: E402
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.motor.correlacion_intrapersona import mediana_rho_prueba  # noqa: E402
from src.motor.exposicion import kp_max_por_dia  # noqa: E402
from src.motor.intrapersona import contraste  # noqa: E402

ACTA, SEMILLA, ALFA, MIN_DIAS, N_PERM = "FB-027", 20261113, 0.05 / 4, 30, 2000
CLAVES = ["temp-eficiencia", "estres-eficiencia", "kp-respiracion", "carga-rmssd-noche"]
CSV = RAIZ / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"
KPF = RAIZ / "data/externos/gfz_kp/Kp_ap_since_1932.txt"
SHA = {CSV: "82c84ee495be4b0ff636a8a44271ffb124e2358d9dd52012b529b897f3d54963", KPF: "d61e03ada312c1d3af8a3235e5d4a566951aabc8e7c69967aa69fb6627a99684"}


def num(t):
    try:
        v = float(t)
        return v if v == v else None
    except (TypeError, ValueError):
        return None


def pares(filas, sp, kp):
    """{persona: [(x, y), …]} ordenado por fecha; solo días con ambos valores."""
    por = defaultdict(list)
    for r in filas:
        d = date.fromisoformat(r["date"])
        x = kp.get(d) if sp["x_col"] == "__kp__" else num(r[sp["x_col"]])
        y = num(r[sp["y_col"]])
        if x is not None and y is not None:
            por[r["id"]].append((d, x, y))
    return {p: [(x, y) for _, x, y in sorted(v)] for p, v in por.items() if len(v) >= MIN_DIAS}


def pares_lag(filas, sp):
    """x del día D con la y del día D+lag (fechas consecutivas), con etiqueta binaria sobre la mediana personal de x."""
    lag = timedelta(days=sp["lag_dias"])
    mapa = defaultdict(dict)
    for r in filas:
        mapa[r["id"]][date.fromisoformat(r["date"])] = (num(r[sp["x_col"]]), num(r[sp["y_col"]]))
    out = {}
    for p, m in mapa.items():
        v = [(m[d][0], m[d + lag][1]) for d in m if d + lag in m and m[d][0] is not None and m[d + lag][1] is not None]
        if len(v) < MIN_DIAS:
            continue
        med = statistics.median(x for x, _ in v)
        out[p] = [(1 if (x > med if sp["x_lado"] == "alto" else x < med) else 0, y) for x, y in v]
    return out


def regla(r, sp):
    if r["S"] is None:
        return "SIN DATOS"
    if sp["sentido"] == "bilateral":
        ok = abs(r["S"]) >= sp["rho_min"] and r["p_bilateral"] <= ALFA
    elif sp["sentido"] == "neg":
        ok = r["S"] <= -sp["rho_min"] and r["p_neg"] <= ALFA
    else:
        ok = r["S"] >= sp["rho_min"] and r["p_pos"] <= ALFA
    return "SOSTENIDA" if ok else "REFUTADA"


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    for ruta, h in SHA.items():
        if hashlib.sha256(ruta.read_bytes()).hexdigest() != h:
            print("datos distintos del preregistro:", ruta.name); return 2
    reg = RAIZ / "docs/actas/RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in reg.read_text(encoding="utf-8").splitlines() if l):
        print(f"{ACTA} ya se ejecutó: una sola vez."); return 1
    filas = list(csv.DictReader(CSV.read_text(encoding="utf-8").splitlines()))
    kp = kp_max_por_dia(KPF)
    print(f"*** {ACTA} · acta sha256={acta.hash_sha256} · REAL (LifeSnaps × GFZ Kp, no astronautas) ***")
    res, v = {}, {}
    for i, c in enumerate(CLAVES, start=1):
        sp = TEST_SPEC[c]
        if sp.get("tipo") == "correlacion":
            r = mediana_rho_prueba(pares(filas, sp, kp), SEMILLA, N_PERM)
            ver = regla(r, sp)
            print(f"  H{i} {c:18s} {r['n_personas']:3d} personas · S(ρ mediana, prueba) = {r['S']:+.4f} · p− = {r['p_neg']:.4f} · p± = {r['p_bilateral']:.4f} → {ver}")
        else:
            r = contraste(pares_lag(filas, sp), sp["estandarizar"], SEMILLA, sp["signo"])
            ok = (r["S"] <= -sp["efecto_min"] if sp["signo"] < 0 else r["S"] >= sp["efecto_min"]) and r["p_unilateral"] <= ALFA
            ver = "SOSTENIDA" if ok else "REFUTADA"
            print(f"  H{i} {c:18s} {r['n_personas']:3d} personas · S = {r['S']:+.4f} {sp['unidad']} · p = {r['p_unilateral']:.4f} → {ver}")
        res[c] = {**r, "veredicto": ver, "spec": sp}; v[f"H{i}_{c}"] = ver
    # placebo ENTRE PERSONAS para H1: x de una persona con la y de la siguiente (orden de id), longitud común
    sp1 = TEST_SPEC[CLAVES[0]]; base = pares(filas, sp1, kp); ids = sorted(base)
    plac = {}
    for a, b in zip(ids, ids[1:] + ids[:1]):
        n = min(len(base[a]), len(base[b]))
        plac[a] = [(base[a][k][0], base[b][k][1]) for k in range(n)]
    rp = mediana_rho_prueba(plac, SEMILLA, N_PERM)
    ok_pl = regla(rp, sp1) != "SOSTENIDA"
    v[f"H{len(CLAVES) + 1}_control_placebo"] = "VÁLIDO" if ok_pl else "INVÁLIDO"
    print(f"  placebo entre personas (H1): S = {rp['S']:+.4f} · p− = {rp['p_neg']:.4f} → {'VÁLIDO' if ok_pl else 'INVÁLIDO'}")
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256, "acta_registrada_utc": acta.registrada_utc, "semillas": [SEMILLA],
             "datos_sha256": {p.name: h for p, h in SHA.items()}, "banner": "REAL (LifeSnaps × GFZ Kp, no astronautas)", "alfa": ALFA, "n_perm": N_PERM, "hipotesis": res,
             "placebo": rp, "veredictos": v}
    with reg.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")
    print("Límites: no son astronautas; asociaciones, no causalidad; pareo por fila; mitad de prueba.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
