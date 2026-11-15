"""M2.16/M2.3 · FB-015-v2: reconstrucción calibrada de FB-002 (SIMULADO). Una sola ejecución."""
import json
import random
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.motor.banco_ocio_v2 import ajustar, calibrar_h, correr, mediana, preaviso  # noqa: E402

ACTA = "FB-015-v2"
T9 = {(0.06, 7): 22.0, (0.06, 3): 19.5, (0.06, 1): 17.0, (0.12, 7): 9.5, (0.12, 3): 6.0, (0.12, 1): 5.5, (0.20, 7): 3.0, (0.20, 3): 0.5, (0.20, 1): 0.0}
G, T = (0.06, 0.12, 0.20), (7, 3, 1)
AJUSTE = {(0.06, 7), (0.20, 7)}


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    reg = RAIZ / "docs/actas/RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in reg.read_text(encoding="utf-8").splitlines() if l):
        print("ya ejecutada"); return 1
    print("*** UNIVERSO SIMULADO — reconstrucción calibrada (NO ciega), modelo propio ***", acta.hash_sha256)
    h, fpr = calibrar_h(20261113)
    r, so, perd = ajustar(20261114, h)
    print(f"h = {h} min (FPR {100 * fpr:.2f} %) · ajuste: r = {r} min/día, σ_obs = {so} (pérdida {perd:.2f})")
    celdas = {}
    for g in G:
        for t in T:
            m, con = mediana(20261115, g, t, r, h, so, 400)
            celdas[f"{g}|{t}"] = {"mediana": m, "con_alarma_ocio": con, "tabla9": T9[(g, t)], "usada_en_ajuste": (g, t) in AJUSTE}
    print("\nγ \\ τ     " + "".join(f"{'τ=' + str(t):>16}" for t in T))
    for g in G:
        print(f"γ={g:<7}" + "".join(f"{celdas[f'{g}|{t}']['mediana']:>8.1f} (doc {T9[(g, t)]:>4}){'*' if (g, t) in AJUSTE else ' '}" for t in T))
    print("(* = celda usada en el ajuste)")
    pred = {k: v for k, v in celdas.items() if not v["usada_en_ajuste"]}
    ok = lambda v: v["mediana"] <= 4.5 if v["tabla9"] <= 0.5 else abs(v["mediana"] - v["tabla9"]) <= 4.0
    fuera = [k for k, v in pred.items() if not ok(v)]
    h1 = "REFUTADA" if len(fuera) >= 3 else ("SOSTENIDA" if len(pred) - len(fuera) >= 5 else "REFUTADA")
    m = lambda g, t: celdas[f"{g}|{t}"]["mediana"]
    h2 = "SOSTENIDA" if all(m(G[i], t) >= m(G[i + 1], t) for t in T for i in range(2)) and all(m(g, T[i]) >= m(g, T[i + 1]) for g in G for i in range(2)) else "REFUTADA"
    h3 = "SOSTENIDA" if 170 <= h <= 230 else "REFUTADA"
    diez = [preaviso(*correr(random.Random(20261113 + i), 0.06, 7, r, h, so)) for i in range(10)]
    ok10 = sum(1 for p in diez if p is not None and p >= 2)
    h4 = "SOSTENIDA" if celdas["0.06|7"]["con_alarma_ocio"] / 400 >= 0.95 and ok10 >= 9 else "REFUTADA"
    estado = "CONSISTENTE con el documento (reconstrucción calibrada)" if (h1, h2, h3) == ("SOSTENIDA",) * 3 and h4 == "SOSTENIDA" else (
        "NO REPLICADA" if h1 == "REFUTADA" else "PARCIAL")
    print(f"\nceldas predichas fuera de tolerancia: {fuera or 'ninguna'} ({len(pred) - len(fuera)}/7 dentro)")
    print(f"10 corridas (semillas 20261113..22): {diez} → {ok10}/10 con ≥ 2 d")
    print(f"VEREDICTOS → H1 {h1} · H2 {h2} · H3 {h3} · H4 {h4} · ESTADO: {estado}")
    with reg.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256,
                            "semillas": [20261113, 20261114, 20261115], "banner": "SIMULADO (modelo propio, no ciego)", "h_min": h, "fpr_h": fpr,
                            "r_min_dia": r, "sigma_obs": so, "celdas": celdas, "diez_corridas": diez,
                            "veredictos": {"H1": h1, "H2": h2, "H3": h3, "H4": h4, "estado": estado}}, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
