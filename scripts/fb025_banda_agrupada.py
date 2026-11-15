"""M7.7 · FB-025: banda personal con varianza agrupada sobre el hemograma REAL de Inspiration4 (exploratoria). Una sola ejecución.
Uso:  uv run python scripts/fb025_banda_agrupada.py"""
import json
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.ingesta import osdr_cbc as O  # noqa: E402
from src.motor.hematologia import ANALITOS, banda, evaluar_agrupada  # noqa: E402

ACTA = "FB-025"
RUTA = RAIZ / "data/externos/osdr569/cbc_transformed.csv"


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    registro = RAIZ / "docs" / "actas" / "RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in registro.read_text(encoding="utf-8").splitlines() if l):
        print(f"{ACTA} ya se ejecutó: una sola vez."); return 1
    filas = O.cargar(RUTA)
    out = evaluar_agrupada(filas, O.PRE, O.POST)
    res, info = out["res"], out["info"]
    personas = sorted({f.persona for f in filas})
    # semiancho personal (FB-024) para la razón de H3
    razones, piso = [], {}
    for a in ANALITOS:
        if a not in info:
            continue
        rs = []
        for p in personas:
            base = [f.v[a] for f in filas if f.persona == p and f.t in O.PRE and f.v.get(a) is not None and a not in f.sospechosos]
            b = banda(base)
            g = next((v for k, v in res.items() if k[0] == p and k[1] == a), None)
            if b and g and g["semiancho_pct"]:
                rs.append((100 * (b[2] - b[0]) / b[0]) / g["semiancho_pct"] if b[0] else None)
                rs = [r for r in rs if r]
        if rs:
            razones.append(statistics.median(rs))
        hs = [v["semiancho_pct"] for k, v in res.items() if k[1] == a and k[2] == "R+1" and v["semiancho_pct"]]
        piso[a] = round(statistics.median(hs), 1) if hs else None
    print(f"*** FB-025 · acta sha256={acta.hash_sha256} · REAL (astronautas de Inspiration4), EXPLORATORIA ***")
    print("grados de libertad / t por analito:", {a: (i['gl'], i['t']) for a, i in info.items()})
    def cuenta(a, t, k):
        return sum(1 for p in personas if res.get((p, a, t), {}).get("estado") == k)
    tabla = {f"{a}|{t}": {k: cuenta(a, t, k) for k in ("dentro", "arriba", "abajo")} for a in info for t in O.POST}
    for a in ("abs_lymphocytes", "nlr", "hb"):
        print(f"  {a:16s} R+1: {tabla[f'{a}|R+1']}  · piso de detección ≈ ±{piso[a]} % de la media personal")
    v = {"H1_linfocitos_abajo_R+1": "SOSTENIDA" if tabla["abs_lymphocytes|R+1"]["abajo"] >= 2 else "REFUTADA",
         "H2_NLR_arriba_R+1": "SOSTENIDA" if tabla["nlr|R+1"]["arriba"] >= 2 else "REFUTADA",
         "H3_reduccion_del_piso": "SOSTENIDA" if razones and statistics.median(razones) >= 1 / 0.80 else "REFUTADA",
         "H3_mediana_razon_personal_sobre_agrupado": round(statistics.median(razones), 2) if razones else None,
         "H4_control_hemoglobina": "SOSTENIDA" if tabla["hb|R+1"]["arriba"] + tabla["hb|R+1"]["abajo"] <= 1 else "INVÁLIDO",
         "piso_deteccion_pct": {"linfocitos": piso["abs_lymphocytes"], "nlr": piso["nlr"]}}
    print("VEREDICTOS:", v)
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256, "acta_registrada_utc": acta.registrada_utc, "semillas": list(acta.semillas),
             "shas": {"cbc_transformed.csv": O.SHA256}, "banner": "REAL (astronautas de Inspiration4; exploratoria, mismos datos que FB-024)", "info": info, "tabla": tabla, "piso_pct": piso, "veredictos": v}
    print("Límites: mismos datos que FB-024; 4 civiles; sin muestras en vuelo; varianza agrupada supone variación intra-persona común.")
    with registro.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(linea, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
