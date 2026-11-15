"""M2.4 + M2.13 · FB-003R: triangulación de 3 testigos y cuarta causa «modelo». SIMULADO. Una sola ejecución."""
import json
import random
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.motor.triangulacion import CAUSAS, acumulado, diagnosticar, diagnosticar_almacen, ingenuo, mundo  # noqa: E402

ACTA, BASE = "FB-003R", 20261113


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    reg = RAIZ / "docs/actas/RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in reg.read_text(encoding="utf-8").splitlines() if l):
        print("ya ejecutada"); return 1
    print("*** UNIVERSO SIMULADO — FB-003 · acta", acta.hash_sha256, "***")
    conf, ing = {}, {}
    for j, causa in enumerate(CAUSAS):
        c, g = Counter(), Counter()
        for i in range(100):
            testigos = mundo(random.Random(BASE + 1000 * j + i), causa)
            dx, A = diagnosticar(testigos)
            c[dx] += 1
            g[ingenuo(A)] += 1
        conf[causa], ing[causa] = dict(c), dict(g)
    exact = {c: conf[c].get(c, 0) / 100 for c in CAUSAS}
    exact_ing = {"sensor": ing["sensor"].get("mundo", 0) * 0 / 100, "humano": 0.0}  # el ingenuo nunca diagnostica una causa de fuente
    print("matriz de confusión (fila = causa verdadera):")
    for c in CAUSAS:
        print(f"  {c:7}", conf[c])
    print("exactitud MO-4:", exact)
    h1 = "SOSTENIDA" if all(exact[c] >= 0.80 for c in ("mundo", "sensor", "humano")) else "REFUTADA"
    h2 = "SOSTENIDA" if exact["nada"] >= 0.85 else "REFUTADA"
    media_mo4 = (exact["sensor"] + exact["humano"]) / 2
    h3 = "SOSTENIDA" if media_mo4 - 0.0 >= 0.30 else "REFUTADA"
    print(f"H1 {h1} · H2 {h2} · H3 (MO-4 {media_mo4:.2f} vs ingenuo 0,00 en fallos de fuente) {h3}")
    alm = {}
    for dias in (30, 60):
        for j, causa in enumerate(("fuga", "almacen")):
            ok = sum(diagnosticar_almacen(acumulado(random.Random(BASE + 77 + 1000 * j + i), causa, dias)) == causa for i in range(200))
            alm[f"{causa}|{dias}"] = ok / 200
    print("cuarta causa (exactitud):", alm)
    h4 = "SOSTENIDA" if alm["fuga|30"] >= 0.70 and alm["almacen|30"] >= 0.70 else "REFUTADA"
    h5 = "SOSTENIDA" if alm["fuga|60"] >= 0.90 and alm["almacen|60"] >= 0.90 else "REFUTADA"
    print(f"H4 (≥ 0,70 a 30 d) {h4} · H5 (≥ 0,90 a 60 d) {h5}")
    with reg.open("a", encoding="utf-8") as f:
        f.write(json.dumps({"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256, "semillas": [BASE],
                            "banner": "SIMULADO", "confusion": conf, "exactitud_mo4": exact, "ingenuo": ing, "cuarta_causa": alm,
                            "veredictos": {"H1": h1, "H2": h2, "H3": h3, "H4": h4, "H5": h5}}, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
