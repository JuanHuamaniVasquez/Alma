"""M2.8 · FB-009: evaluación del motor sobre datos REALES de LifeSnaps (híbrida: inyección SIMULADA).

Se niega a correr sin el acta FB-009 registrada e intacta (GO-2), exige que el CSV sea exactamente el preregistrado
(sha256) y registra UNA sola ejecución (`docs/actas/RESULTADOS.jsonl`, solo-anexar).
Uso:  uv run python scripts/fb009_evaluacion_lifesnaps.py
"""
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.ingesta.series import series_de  # noqa: E402
from src.contratos.comunes import Indicador, IndicadorSensor  # noqa: E402
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.ingesta.incertidumbre import sigma_de  # noqa: E402
from src.ingesta.lifesnaps import cargar  # noqa: E402
from src.motor.evaluacion import H_FB009, evaluar, veredictos  # noqa: E402

ACTA = "FB-009"
CSV = RAIZ / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"


def imprimir(titulo, r):
    m1, m2 = r["M1"], r["M2"]
    print(f"\n== {titulo} · {r['n_unidades']} unidades de {r['n_personas']} personas ==")
    print(f"M1 FPR natural: {m1['alarmas']}/{m1['n']} = {100 * m1['tasa']:.2f} %  Wilson95=[{100 * m1['wilson95'][0]:.2f}, {100 * m1['wilson95'][1]:.2f}] %  "
          f"remuestreo-por-persona95=[{100 * m1['remuestreo95'][0]:.2f}, {100 * m1['remuestreo95'][1]:.2f}] %  (x crítico = {m1['x_critico']})")
    print(f"M2 FPR primera unidad por persona: {m2['alarmas']}/{m2['n']}")
    for d, v in r["M3"].items():
        print(f"M3 caída de {d}σ: detectada en {v['detectadas']}/{v['de']} = {100 * v['tasa']:.1f} %  mediana de días = {v['mediana_dias']}")
    print(f"M4 manda el sensor en {100 * r['M4']['fraccion_manda_el_sensor']:.0f} % de las unidades · alarmas naturales por sentido {r['M4']['alarmas_naturales_por_sentido']}")


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    texto = (RAIZ / "docs" / "actas" / f"{ACTA}.md").read_text(encoding="utf-8")
    sha_csv = hashlib.sha256(CSV.read_bytes()).hexdigest()
    if sha_csv not in texto:
        print("El CSV no es el preregistrado en FB-009 (sha256 distinto): no se ejecuta.")
        return 2
    registro = RAIZ / "docs" / "actas" / "RESULTADOS.jsonl"
    if registro.exists() and any(json.loads(l)["acta"] == ACTA for l in registro.read_text(encoding="utf-8").splitlines() if l):
        print(f"{ACTA} ya se ejecutó: una acta se ejecuta una sola vez.")
        return 1
    regs = cargar(CSV).registros
    sueno, fc = series_de(regs, IndicadorSensor.SUENO), series_de(regs, IndicadorSensor.FC)
    s_sueno, s_fc = sigma_de(IndicadorSensor.SUENO).sigma, sigma_de(IndicadorSensor.FC).sigma
    primaria = evaluar(sueno, Indicador.SUENO, s_sueno)
    s1 = evaluar(sueno, Indicador.SUENO, s_sueno, filtro=lambda v: v >= 120)
    s2 = evaluar(fc, Indicador.FC, s_fc)
    v = veredictos(primaria)
    print(f"*** FB-009 · LifeSnaps REAL (NO astronautas) + inyección SIMULADA · acta sha256={acta.hash_sha256} · h={H_FB009} ***")
    imprimir("PRIMARIO: sueño, sin limpieza", primaria)
    imprimir("S1 (sensibilidad): sueño ≥ 120 min", s1)
    imprimir("S2 (sensibilidad): frecuencia cardiaca", s2)
    print(f"\nVEREDICTOS (reglas del acta) → H1 (calibración): {v['H1']} · H2 (potencia, δ=2σ ≥ 80 %): {v['H2']}")
    print("Límites: no son astronautas; σ de sensor es proxy; ausencia no aleatoria; bloques correlacionados; n pequeño (H1 solo detecta descalibración gruesa).")
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256,
             "acta_registrada_utc": acta.registrada_utc, "semillas": list(acta.semillas), "csv_sha256": sha_csv,
             "banner": "REAL (LifeSnaps, no astronautas) + inyección SIMULADA", "h": H_FB009,
             "primario": primaria, "S1": s1, "S2": s2, "veredictos": v}
    with registro.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
