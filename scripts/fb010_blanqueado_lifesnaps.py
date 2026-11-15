"""MP-11 · FB-010: CUSUM con residuos blanqueados AR(1), validación cruzada entre personas (LifeSnaps REAL, no astronautas).

Se niega a correr sin el acta FB-010 registrada e intacta; exige el CSV preregistrado; UNA sola ejecución.
Uso:  uv run python scripts/fb010_blanqueado_lifesnaps.py
"""
import hashlib
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.contratos.comunes import Indicador, IndicadorSensor  # noqa: E402
from src.contratos.dc01_sensores import CalidadDato  # noqa: E402
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.ingesta.incertidumbre import sigma_de  # noqa: E402
from src.ingesta.lifesnaps import cargar  # noqa: E402
from src.motor.evaluacion import H_FB009, UMBRAL_H2, estimar_phi, evaluar, particion  # noqa: E402

ACTA = "FB-010"
CSV = RAIZ / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"


def series_de(registros, indicador):
    por = defaultdict(list)
    for r in registros:
        if r.indicador is indicador and r.calidad is CalidadDato.OK:
            por[r.persona_id].append((r.ts_utc.date(), r.valor))
    return dict(por)


def fila(nombre, r):
    m1 = r["M1"]
    pot = " · ".join(f"{d}σ:{100 * v['tasa']:.0f}%" for d, v in r["M3"].items())
    return (f"{nombre:34} n={m1['n']:3} FPR {m1['alarmas']}/{m1['n']} = {100 * m1['tasa']:.2f} % "
            f"Wilson95=[{100 * m1['wilson95'][0]:.1f},{100 * m1['wilson95'][1]:.1f}] · potencia {pot}")


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    texto = (RAIZ / "docs" / "actas" / f"{ACTA}.md").read_text(encoding="utf-8")
    sha_csv = hashlib.sha256(CSV.read_bytes()).hexdigest()
    if sha_csv not in texto:
        print("El CSV no es el preregistrado en FB-010: no se ejecuta.")
        return 2
    registro = RAIZ / "docs" / "actas" / "RESULTADOS.jsonl"
    if registro.exists() and any(json.loads(l)["acta"] == ACTA for l in registro.read_text(encoding="utf-8").splitlines() if l):
        print(f"{ACTA} ya se ejecutó: una acta se ejecuta una sola vez.")
        return 1
    regs = cargar(CSV).registros
    out = {}
    print(f"*** FB-010 · LifeSnaps REAL (no astronautas) + inyección SIMULADA · acta sha256={acta.hash_sha256} · h={H_FB009} ***")
    for ie, ind in ((IndicadorSensor.FC, Indicador.FC), (IndicadorSensor.SUENO, Indicador.SUENO)):
        series, sigma = series_de(regs, ie), sigma_de(ie).sigma
        entrena = {p for p in series if particion(p) == "entrenamiento"}
        prueba = {p for p in series if particion(p) == "prueba"}
        phi = estimar_phi(series, filtro_personas=lambda p: p in entrena)
        r = {"phi_estimado_en_entrenamiento": phi,
             "prueba_base": evaluar(series, ind, sigma, personas=prueba, phi=0.0),
             "prueba_blanqueado": evaluar(series, ind, sigma, personas=prueba, phi=phi),
             "entrenamiento_base": evaluar(series, ind, sigma, personas=entrena, phi=0.0),
             "entrenamiento_blanqueado": evaluar(series, ind, sigma, personas=entrena, phi=phi)}
        out[ind.value] = r
        print(f"\n== {ind.value.upper()} · φ̂ (solo entrenamiento) = {phi:.4f} ==")
        for clave, nombre in (("prueba_base", "PRUEBA sin blanquear (control)"), ("prueba_blanqueado", "PRUEBA blanqueado (φ̂)"),
                              ("entrenamiento_base", "entrenamiento sin blanquear (desc.)"), ("entrenamiento_blanqueado", "entrenamiento blanqueado (desc.)")):
            print(fila(nombre, r[clave]))
    pw, base = out["fc"]["prueba_blanqueado"], out["fc"]["prueba_base"]
    h1 = "SOSTENIDA" if (pw["M1"]["alarmas"] < pw["M1"]["x_critico"] and pw["M1"]["alarmas"] <= base["M1"]["alarmas"]) else "REFUTADA"
    h2 = "SOSTENIDA" if pw["M3"]["2.0"]["tasa"] >= UMBRAL_H2 else "REFUTADA"
    print(f"\nVEREDICTOS (reglas del acta, pulso/prueba) → H1′ (corrección): {h1} (x_pw={pw['M1']['alarmas']}, x_base={base['M1']['alarmas']}, x_crítico={pw['M1']['x_critico']}) · H2′ (potencia δ=2σ ≥ 80 %): {h2}")
    print("Límites: no son astronautas; no es validación independiente (mismos datos que FB-009); AR(1) simple; ausencia no aleatoria.")
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256,
             "acta_registrada_utc": acta.registrada_utc, "semillas": list(acta.semillas), "csv_sha256": sha_csv,
             "banner": "REAL (LifeSnaps, no astronautas) + inyección SIMULADA", "h": H_FB009, "resultados": out,
             "veredictos": {"H1p": h1, "H2p": h2}}
    with registro.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
