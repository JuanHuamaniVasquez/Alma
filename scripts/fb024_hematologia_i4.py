"""M7.2 · FB-024: hematología REAL de astronautas (Inspiration4, OSD-569). Una sola ejecución.
Uso:  uv run python scripts/fb024_hematologia_i4.py"""
import json
import statistics
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.ingesta import osdr_cbc as O  # noqa: E402
from src.motor.hematologia import ANALITOS, evaluar  # noqa: E402

ACTA = "FB-024"
RUTA = RAIZ / "data/externos/osdr569/cbc_transformed.csv"


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    registro = RAIZ / "docs" / "actas" / "RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in registro.read_text(encoding="utf-8").splitlines() if l):
        print(f"{ACTA} ya se ejecutó: una sola vez."); return 1
    filas = O.cargar(RUTA)                                   # verifica el sha256 del CSV
    res = evaluar(filas, O.PRE, O.POST)
    print(f"*** FB-024 · acta sha256={acta.hash_sha256} · REAL (astronautas de Inspiration4, n=4) ***")
    sosp_vals = sum(len(f.sospechosos - {"nlr"}) for f in filas)
    sosp_filas = [f"{f.persona}/{f.t}" for f in filas if f.sospechosos]
    print(f"CONCILIACIÓN: {sosp_vals} valores absolutos que no cierran con su propio porcentaje, en {len(sosp_filas)} filas de 28: {sosp_filas}")
    tabla = {}
    for a in ANALITOS:
        for t in O.POST:
            est = [res[(p, a, t)] for p in sorted({f.persona for f in filas}) if (p, a, t) in res]
            cnt = {k: sum(e["estado"] == k for e in est) for k in ("dentro", "arriba", "abajo", "sin_datos", "sospechoso")}
            ch = [e["cambio_pct"] for e in est if e["cambio_pct"] is not None]
            tabla[f"{a}|{t}"] = {**cnt, "mediana_cambio_pct": round(statistics.median(ch), 1) if ch else None, "n": len(est)}
            print(f"  {a:16s} {t:5s}: dentro {cnt['dentro']} arriba {cnt['arriba']} abajo {cnt['abajo']} s/datos {cnt['sin_datos']} sosp {cnt['sospechoso']} · mediana Δ% {tabla[f'{a}|{t}']['mediana_cambio_pct']}")
    v = {"H1_NLR_arriba_R+1": "SOSTENIDA" if tabla["nlr|R+1"]["arriba"] >= 2 else "REFUTADA" if tabla["nlr|R+1"]["n"] else "SIN DATOS",
         "H2_linfocitos_abajo_R+1": "SOSTENIDA" if tabla["abs_lymphocytes|R+1"]["abajo"] >= 2 else "REFUTADA",
         "H4_control_hemoglobina": "SOSTENIDA" if tabla["hb|R+1"]["arriba"] + tabla["hb|R+1"]["abajo"] <= 1 else "INVÁLIDO"}
    obs = [res[k] for k in res if k[2] in ("R+82", "R+194") and res[k]["estado"] in ("dentro", "arriba", "abajo")]
    dentro = sum(o["estado"] == "dentro" for o in obs)
    v["H3_retorno_R+82_R+194"] = "SOSTENIDA" if obs and dentro / len(obs) >= 0.90 else "REFUTADA"
    v["H3_detalle"] = f"{dentro}/{len(obs)} dentro de banda"
    v["H5_sospechosos"] = {"valores": sosp_vals, "filas": len(sosp_filas)}
    print("VEREDICTOS:", v)
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256, "acta_registrada_utc": acta.registrada_utc,
             "semillas": list(acta.semillas), "shas": {"cbc_transformed.csv": O.SHA256}, "banner": "REAL (astronautas de Inspiration4, n = 4; NASA OSDR OSD-569)",
             "conciliacion": {"valores": sosp_vals, "filas": sosp_filas}, "tabla": tabla, "veredictos": v}
    print("Límites: 4 civiles; sin extracciones en vuelo; banda con 3 puntos = ancha; sin causalidad; solo agregados se publican.")
    with registro.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(linea, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
