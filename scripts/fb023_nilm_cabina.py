"""M6.2 · FB-023: identificabilidad del NILM de cabina (SIMULADO, X-17). Una sola ejecución.
Uso:  uv run python scripts/fb023_nilm_cabina.py"""
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.motor.nilm_cabina import exactitud  # noqa: E402

ACTA = "FB-023"
PASOS, DELTAS, N, SIGMA = (0, 1, 2, 4), (0.05, 0.10, 0.20), 400, 0.069
SEMILLA = 20261113


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    registro = RAIZ / "docs" / "actas" / "RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in registro.read_text(encoding="utf-8").splitlines() if l):
        print(f"{ACTA} ya se ejecutó: una sola vez."); return 1
    print(f"*** FB-023 · acta sha256={acta.hash_sha256} · SIMULADO (X-17) ***")
    celdas = {}
    for d in DELTAS:
        for p in PASOS:
            c = exactitud(p, d, SIGMA, N, SEMILLA)
            celdas[f"{p}|{d}"] = c
            print(f"  paso {p} h · δ={d:.2f}: {c['aciertos']}/{N} = {100 * c['exactitud']:.1f} %")
    a = lambda p, d: celdas[f"{p}|{d}"]["exactitud"]
    v = {"H1": "SOSTENIDA" if a(4, 0.20) >= 0.80 else "REFUTADA",
         "H2": "SOSTENIDA" if a(0, 0.20) <= 0.30 else "INVÁLIDO",
         "H3": "SOSTENIDA" if a(4, 0.10) >= a(2, 0.10) - 0.03 >= a(1, 0.10) - 0.06 >= a(0, 0.10) - 0.09 else "REFUTADA",
         "H4": "SOSTENIDA" if a(4, 0.05) >= 0.50 else "REFUTADA"}
    minimo = next((d for d in DELTAS if a(4, d) >= 0.80), None)
    v["delta_minimo_atribuible_paso4"] = minimo
    print("VEREDICTOS:", v)
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256, "acta_registrada_utc": acta.registrada_utc,
             "semillas": list(acta.semillas), "banner": "SIMULADO (X-17): identificabilidad de un método; no hay datos de cabina tripulada", "sigma_rel": SIGMA, "n_por_celda": N,
             "celdas": celdas, "veredictos": v}
    print("Límites: todo simulado; horarios conocidos; exceso multiplicativo; ruido gaussiano independiente; modelo fisiológico simple.")
    with registro.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(linea, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
