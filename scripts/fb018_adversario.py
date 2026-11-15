"""M4.4 · FB-018: El Adversario. SIMULADO. Una sola ejecución."""
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.motor.adversario import PERFILES, calibrar_hv, tasas  # noqa: E402

ACTA, BASE, N = "FB-018", 20261113, 400


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    reg = RAIZ / "docs/actas/RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in reg.read_text(encoding="utf-8").splitlines() if l):
        print("ya ejecutada"); return 1
    print("*** UNIVERSO SIMULADO — El Adversario · semilla", BASE, "· acta", acta.hash_sha256, "***")
    hv = calibrar_hv()
    print(f"h_v (CUSUM de varianza, 1 % en 14 d) = {hv:.4f}")
    nulo = tasas("nulo", 0.0, BASE, N, hv)
    print("sin cambio:", {k: f'{100 * v:.1f} %' for k, v in nulo.items()})
    res = {}
    for nombre in PERFILES:
        for H in (0.5, 1.0, 1.5, 2.0):
            r = tasas(nombre, H, BASE, N, hv)
            res[f"{nombre}|{H}"] = r
            print(f"{nombre:8} H={H}: CUSUM media {100 * r['media']:5.1f} % · varianza {100 * r['varianza']:5.1f} % · unión {100 * r['union']:5.1f} %")
    escapes = [(k, v) for k, v in res.items() if float(k.split("|")[1]) >= 1.0 and v["media"] <= 0.10]
    h1 = "SOSTENIDA" if escapes else "REFUTADA"
    mejor = max(escapes, key=lambda kv: float(kv[0].split("|")[1])) if escapes else None
    h2 = "SOSTENIDA" if mejor and mejor[1]["varianza"] >= 0.80 and nulo["varianza"] <= 0.05 else "REFUTADA"
    h3 = "SOSTENIDA" if nulo["union"] <= 0.06 else "REFUTADA"
    print(f"escapes (H ≥ 1, detección ≤ 10 %): {[k for k, _ in escapes]} · mejor: {mejor[0] if mejor else None}")
    print(f"H1 {h1} · H2 {h2} · H3 {h3}")
    with reg.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256, "semillas": [BASE],
                            "banner": "SIMULADO", "h_v": hv, "nulo": nulo, "resultados": res, "escapes": [k for k, _ in escapes],
                            "veredictos": {"H1": h1, "H2": h2, "H3": h3}}, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
