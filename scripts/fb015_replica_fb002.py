"""M2.16/M2.3 · FB-015: réplica independiente de FB-002 con predicción de la Tabla 9. SIMULADO. Una sola ejecución."""
import json
import random
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.motor.banco_ocio import ajustar_r, calibrar_h, correr, mediana_preaviso  # noqa: E402

ACTA = "FB-015"
TABLA9 = {(0.06, 7): 22.0, (0.06, 3): 19.5, (0.06, 1): 17.0, (0.12, 7): 9.5, (0.12, 3): 6.0, (0.12, 1): 5.5,
          (0.20, 7): 3.0, (0.20, 3): 0.5, (0.20, 1): 0.0}
G, T = (0.06, 0.12, 0.20), (7, 3, 1)


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    registro = RAIZ / "docs/actas/RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in registro.read_text(encoding="utf-8").splitlines() if l):
        print("ya ejecutada"); return 1
    print("*** UNIVERSO SIMULADO — modelo propio, NO el original de FB-002 *** acta", acta.hash_sha256)
    h, fpr = calibrar_h(20261113)
    r = ajustar_r(20261114, h)
    print(f"h calibrado = {h} min (FPR {100 * fpr:.2f} %) · r ajustada en la celda nominal = {r:.3f} min/día")
    celdas = {}
    for g in G:
        for t in T:
            med, n_pre, n_ocio = mediana_preaviso(20261115, g, t, r, h)
            celdas[f"{g}|{t}"] = {"mediana": med, "medibles": n_pre, "con_alarma_ocio": n_ocio, "tabla9": TABLA9[(g, t)]}
    print("\nγ \\ τ     " + "".join(f"{'τ=' + str(t):>16}" for t in T))
    for g in G:
        print(f"γ={g:<7}" + "".join(f"{(celdas[f'{g}|{t}']['mediana'] if celdas[f'{g}|{t}']['mediana'] is not None else float('nan')):>8.1f} (doc {TABLA9[(g, t)]:>4})" for t in T))
    pred = [(k, v) for k, v in celdas.items() if k != "0.06|7"]
    def dentro(v):
        m = v["mediana"]
        return m is not None and ((m <= 4.5) if v["tabla9"] <= 0.5 else abs(m - v["tabla9"]) <= 4.0)
    fuera = [k for k, v in pred if not dentro(v)]
    h1 = "SOSTENIDA" if len(fuera) <= 2 and (8 - len(fuera)) >= 6 else ("REFUTADA" if len(fuera) >= 3 else "SOSTENIDA")
    med = lambda g, t: celdas[f"{g}|{t}"]["mediana"]
    ok_g = all(med(G[i], t) >= med(G[i + 1], t) for t in T for i in range(2) if med(G[i], t) is not None and med(G[i + 1], t) is not None)
    ok_t = all(med(g, T[i]) >= med(g, T[i + 1]) for g in G for i in range(2) if med(g, T[i]) is not None and med(g, T[i + 1]) is not None)
    h2 = "SOSTENIDA" if ok_g and ok_t else "REFUTADA"
    h3 = "SOSTENIDA" if 150 <= h <= 250 else "REFUTADA"
    nominal = celdas["0.06|7"]
    diez = [correr(random.Random(20261113 + i), 0.06, 7, r, h).preaviso for i in range(10)]
    ok10 = sum(1 for p in diez if p is not None and p >= 2)
    h4 = "SOSTENIDA" if nominal["con_alarma_ocio"] / 400 >= 0.95 and ok10 >= 9 else "REFUTADA"
    estado = "CONSISTENTE con el documento" if (h1, h2, h3) == ("SOSTENIDA",) * 3 else ("NO REPLICADA" if h1 == "REFUTADA" else "PARCIAL")
    print(f"\nceldas fuera de ±4 d: {fuera or 'ninguna'} · monotonía γ:{ok_g} τ:{ok_t}")
    print(f"10 corridas (semillas 20261113..22): preavisos {diez} → {ok10}/10 con ≥2 d · mediana {sorted(p for p in diez if p is not None)[len([p for p in diez if p is not None]) // 2]}")
    print(f"VEREDICTOS → H1 {h1} · H2 {h2} · H3 (h∈[150,250]) {h3} (h={h}) · H4 {h4} · ESTADO: {estado}")
    with registro.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256,
                            "semillas": [20261113, 20261114, 20261115], "banner": "SIMULADO (modelo propio)", "h_min": h, "fpr_h": fpr,
                            "r_min_dia": r, "celdas": celdas, "diez_corridas": diez,
                            "veredictos": {"H1": h1, "H2": h2, "H3": h3, "H4": h4, "estado": estado}}, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
