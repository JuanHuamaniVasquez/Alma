"""M6.3 · FB-022: consistencia física cruzada (acoplamiento fuera de muestra + clasificación sensor/cuerpo). Una sola ejecución.
Uso:  uv run python scripts/fb022_consistencia.py"""
import csv
import hashlib
import json
import math
import statistics
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.motor.consistencia import BLOQUE, ajustar, incoherente, spearman  # noqa: E402

ACTA = "FB-022"
LS = RAIZ / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"
SHA = "82c84ee495be4b0ff636a8a44271ffb124e2358d9dd52012b529b897f3d54963"
PARES = {"P1": ("nightly_temperature", "resting_hr"), "P2": ("rmssd", "resting_hr"), "P3": ("full_sleep_breathing_rate", "resting_hr")}
MIN_PARES = 40


def num(t):
    try:
        v = float(t)
        return v if math.isfinite(v) else None
    except (TypeError, ValueError):
        return None


def pares_por_persona(filas, cx, cy):
    por = defaultdict(list)
    for r in filas:
        a, b = num(r[cx]), num(r[cy])
        if a is not None and b is not None:
            por[r["id"]].append((r["date"], a, b))
    return {p: sorted(v) for p, v in por.items() if len(v) >= MIN_PARES}


def acoplamiento(filas, cx, cy):
    rhos, datos = [], {}
    for p, v in pares_por_persona(filas, cx, cy).items():
        m = len(v) // 2
        tr, te = v[:m], v[m:]
        rho = spearman([a for _, a, _ in te], [b for _, _, b in te])
        if rho is not None:
            rhos.append(rho); datos[p] = (tr, te)
    return rhos, datos


def clasificar(datos, h=2.0):
    """Bloques de prueba: fisiológico (x +h·σx, y +b·h·σy) vs fallo de sensor (solo x +h·σx) vs real sin inyección."""
    ok_f = n_f = ok_p = n_p = mal_r = n_r = 0
    for tr, te in datos.values():
        aj = ajustar([a for _, a, _ in tr], [b for _, _, b in tr])
        if aj is None:
            continue
        x, y = [a for _, a, _ in te], [b for _, _, b in te]
        for i in range(0, len(x) - BLOQUE + 1, BLOQUE):
            bx, by = x[i:i + BLOQUE], y[i:i + BLOQUE]
            n_r += 1; mal_r += incoherente(aj, bx, by)
            n_f += 1; ok_f += incoherente(aj, [p + h * aj["sx"] for p in bx], by)                                  # fallo: solo x
            n_p += 1; ok_p += not incoherente(aj, [p + h * aj["sx"] for p in bx], [q + aj["b"] * h * aj["sy"] for q in by])  # cuerpo: coherente
    ex = (ok_f / n_f + ok_p / n_p) / 2 if n_f and n_p else None
    return {"h": h, "bloques": n_f, "tpr_fallo": ok_f / n_f if n_f else None, "tnr_fisiologico": ok_p / n_p if n_p else None,
            "exactitud_balanceada": ex, "reales_incoherentes": mal_r / n_r if n_r else None, "n_reales": n_r}


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    if hashlib.sha256(LS.read_bytes()).hexdigest() != SHA:
        print("dataset distinto del preregistrado"); return 2
    registro = RAIZ / "docs" / "actas" / "RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in registro.read_text(encoding="utf-8").splitlines() if l):
        print(f"{ACTA} ya se ejecutó: una sola vez."); return 1
    with LS.open(encoding="utf-8", newline="") as f:
        filas = list(csv.DictReader(f))
    print(f"*** FB-022 · acta sha256={acta.hash_sha256} ***")
    res, datos_p = {}, {}
    for k, (cx, cy) in PARES.items():
        rhos, datos = acoplamiento(filas, cx, cy)
        datos_p[k] = datos
        med = statistics.median(rhos) if rhos else None
        pos = sum(r > 0 for r in rhos) / len(rhos) if rhos else None
        res[k] = {"par": [cx, cy], "personas": len(rhos), "mediana_spearman": med, "fraccion_positiva": pos}
        print(f"  {k} {cx} ~ {cy}: {len(rhos)} personas · mediana ρ(prueba) = {med if med is None else round(med, 3)} · ρ>0 en {pos if pos is None else round(100 * pos)} %")
    v = {}
    f1 = res["P1"]; v["H1"] = "SOSTENIDA" if f1["mediana_spearman"] is not None and f1["mediana_spearman"] >= 0.20 and f1["fraccion_positiva"] >= 0.65 else "REFUTADA"
    f3 = res["P3"]; v["H3"] = "SOSTENIDA" if f3["mediana_spearman"] is not None and f3["mediana_spearman"] >= 0.20 and f3["fraccion_positiva"] >= 0.65 else "REFUTADA"
    p2 = res["P2"]; v["H2"] = "VÁLIDO" if p2["mediana_spearman"] is not None and p2["mediana_spearman"] <= -0.30 else "INVÁLIDO"
    clas = {}
    if v["H2"] == "VÁLIDO":
        for h in (1.0, 2.0, 3.0):
            clas[str(h)] = clasificar(datos_p["P2"], h)
            c = clas[str(h)]
            print(f"  P2 clasificación h={h}: {c['bloques']} bloques · fallo detectado {100 * c['tpr_fallo']:.1f} % · fisiológico aceptado {100 * c['tnr_fisiologico']:.1f} % · exactitud {100 * c['exactitud_balanceada']:.1f} % · reales marcados incoherentes {100 * c['reales_incoherentes']:.1f} %")
        v["H4"] = "SOSTENIDA" if clas["2.0"]["exactitud_balanceada"] >= 0.80 else "REFUTADA"
    else:
        v["H4"] = "NO EVALUADA (control positivo inválido)"
    print("VEREDICTOS:", v)
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256, "acta_registrada_utc": acta.registrada_utc,
             "semillas": list(acta.semillas), "shas": {LS.name: SHA}, "banner": "REAL (LifeSnaps, no astronautas) + eventos SIMULADOS", "pares": res, "clasificacion": clas, "veredictos": v}
    print("Límites: no son astronautas; sin conjunto externo; inyección simulada; rmssd y pulso salen del mismo sensor óptico.")
    with registro.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(linea, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
