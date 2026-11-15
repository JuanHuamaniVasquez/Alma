"""M1.4 · FB-005-D1: demo «kill» del Contrapeso. UNIVERSO SIMULADO — DÍA 7.

Se niega a correr sin el acta registrada e intacta (GO-2) y registra UNA sola ejecución por acta
(`docs/actas/RESULTADOS.jsonl`, solo-anexar): no se puede repetir hasta que salga lo que se quiere.
Uso:  uv run python scripts/fb005_demo_kill.py
"""
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.motor.fb005_demo import BANNER_DEMO, ejecutar  # noqa: E402

ACTA = "FB-005-D1"


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    registro = RAIZ / "docs" / "actas" / "RESULTADOS.jsonl"
    if registro.exists() and any(json.loads(l)["acta"] == ACTA for l in registro.read_text(encoding="utf-8").splitlines() if l):
        print(f"{ACTA} ya se ejecutó: una acta se ejecuta una sola vez (ver {registro.name}).")
        return 1
    r = ejecutar(acta.semillas[0])
    print(f"*** {BANNER_DEMO} · semilla pública {r['semilla']} · acta {ACTA} sha256={acta.hash_sha256} ***\n")
    for nombre in ("control", "fuga"):
        e = r[nombre]
        print(f"[{nombre:7}] fuga={e['fuga_kg']:.2f} kg | A (manifiesto): z={e['A_manifiesto']['z']:+.3f} → "
              f"{'ALARMA' if e['A_manifiesto']['alarma'] else 'ciego/ok'} | B (ley): residuo={e['B_ley']['residuo_kg']:+.4f} kg "
              f"(2σ={2 * e['B_ley']['sigma_propagada_kg']:.4f}) → {e['B_ley']['veredicto']} [{e['B_ley']['sentido']}]")
    print("\nPREDICCIÓN PREVIA:", "CONFIRMADA" if r["prediccion_confirmada"] else "REFUTADA " + "; ".join(r["reglas_de_muerte_cumplidas"]))
    print("Límite: 1 corrida por escenario; la ceguera de A es por construcción. La prueba estadística es FB-005 (400 corridas, M2.6).")
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "hash_acta": acta.hash_sha256,
             "acta_registrada_utc": acta.registrada_utc, **r}
    with registro.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
