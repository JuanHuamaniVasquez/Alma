"""M9 · FB-029 (P-R2): el CUSUM de caída de MO-3 sobre el monitor de neutrones de Oulu contra las tormentas Kp ≥ 7. Una sola ejecución.
Uso:  uv run python scripts/fb029_forbush.py"""
import hashlib
import json
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.motor import forbush as F  # noqa: E402

ACTA, SEMILLA = "FB-029", 20261113
OULU = RAIZ / "data/externos/nmdb_oulu/oulu_1h_presion_2008_2025.csv"
KPF = RAIZ / "data/externos/gfz_kp/Kp_ap_since_1932.txt"
SHA = {OULU: "6a04c32f3dcc11e1442a79c189c14495108c6d6c09d82a0f4db918300137d94e", KPF: "d61e03ada312c1d3af8a3235e5d4a566951aabc8e7c69967aa69fb6627a99684"}
GRID = (4, 6, 8, 10, 12, 16, 20, 24, 32, 48, 64, 96)
UTC_ = lambda a, m=1, d=1: datetime(a, m, d, tzinfo=UTC)          # noqa: E731
CAL = (UTC_(2008), UTC_(2017)); TEST = (UTC_(2017), UTC_(2026))
MAX_FALSAS_ANIO = 6.0


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    for ruta, h in SHA.items():
        if hashlib.sha256(ruta.read_bytes()).hexdigest() != h:
            print("datos distintos del preregistro:", ruta.name); return 2
    reg = RAIZ / "docs/actas/RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in reg.read_text(encoding="utf-8").splitlines() if l):
        print(f"{ACTA} ya se ejecutó: una sola vez."); return 1
    serie, kp = F.leer_oulu(OULU), F.leer_kp(KPF)
    print(f"*** {ACTA} · acta sha256={acta.hash_sha256} · REAL (NMDB/Oulu × GFZ Kp) ***")
    anios = lambda p: (p[1] - p[0]).days / 365.25               # noqa: E731
    calib, h_elegido = {}, None
    for h in GRID:
        al = F.alarmas(serie, h)
        falsas = F.alarmas_falsas(al, kp, *CAL)
        calib[h] = round(len(falsas) / anios(CAL), 2)
        if h_elegido is None and calib[h] <= MAX_FALSAS_ANIO:
            h_elegido = h
    declarado = h_elegido is None
    h_elegido = h_elegido or GRID[-1]
    print("calibración 2008–2016 · falsas/año por h:", calib, "→ h =", h_elegido, "(NINGÚN h cumplía: se usa el mayor)" if declarado else "")
    al = F.alarmas(serie, h_elegido)
    ev7, ev6 = F.eventos_kp(kp, 7.0, *TEST), F.eventos_kp(kp, 6.0, *TEST)
    r7, r6 = F.evaluar(al, ev7), F.evaluar(al, ev6)
    falsas = F.alarmas_falsas(al, kp, *TEST)
    fpa = len(falsas) / anios(TEST)
    pl = F.placebo(al, ev7, *TEST, SEMILLA)
    alarmas_test = [a for a in al if TEST[0] <= a < TEST[1]]
    h1 = "SOSTENIDA" if (r7["sensibilidad"] or 0) >= 0.5 else "REFUTADA"
    h2 = "SOSTENIDA" if fpa <= MAX_FALSAS_ANIO else "REFUTADA"
    h3 = "SOSTENIDA" if pl["p_unilateral"] <= 0.01 else "REFUTADA"
    h4 = "NO CONCLUYENTE" if r7["detectados"] < 5 else ("SOSTENIDA" if r7["adelanto_mediano_h"] >= 0 else "REFUTADA")
    print(f"prueba 2017–2025 · eventos Kp≥7 = {r7['n_eventos']} · detectados = {r7['detectados']} ({r7['sensibilidad']:.0%}) → H1 {h1}")
    print(f"  falsas/año = {fpa:.2f} (≤ {MAX_FALSAS_ANIO}) → H2 {h2} · alarmas totales {len(alarmas_test)}")
    print(f"  placebo: observada {pl['observada']:.2f}, media por azar {pl['media_placebo']:.2f}, p = {pl['p_unilateral']:.4f} → H3 {h3}")
    print(f"  adelanto mediano = {r7['adelanto_mediano_h']} h (detectados {r7['detectados']}) → H4 {h4}")
    print(f"  descriptivo Kp≥6: {r6['detectados']}/{r6['n_eventos']} = {r6['sensibilidad']:.0%}")
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256, "acta_registrada_utc": acta.registrada_utc, "semillas": [SEMILLA],
             "datos_sha256": {p.name: h for p, h in SHA.items()}, "banner": "REAL (NMDB/Oulu × GFZ Kp)", "h_elegido": h_elegido, "h_sin_cumplir": declarado, "calibracion_falsas_por_anio": calib,
             "prueba": {"kp7": {k: v for k, v in r7.items() if k != "adelantos_h"}, "adelantos_h": [round(x, 1) for x in r7["adelantos_h"]], "falsas_por_anio": round(fpa, 2), "alarmas_totales": len(alarmas_test),
                        "kp6": {k: v for k, v in r6.items() if k != "adelantos_h"}, "placebo": pl},
             "veredictos": {"H1_sensibilidad": h1, "H2_falsas_por_anio": h2, "H3_placebo": h3, "H4_adelanto": h4}}
    with reg.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")
    print("Límites: proxy en tierra, una estación; el Kp se publica con retraso; no se clasifica cada alarma.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
