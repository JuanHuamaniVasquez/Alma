"""M2.20 · FB-020: canal de varianza (MP-15) en LifeSnaps REAL (no astronautas) + zigzag SIMULADO. Una sola ejecución; exige el acta intacta.
Uso:  uv run python scripts/fb020_canal_varianza_lifesnaps.py"""
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))

from src.ingesta.series import series_de  # noqa: E402
from src.contratos.comunes import IndicadorSensor  # noqa: E402
from src.gobernanza.preregistro import exigir_preregistro  # noqa: E402
from src.ingesta.lifesnaps import cargar  # noqa: E402
from src.motor.evaluacion_varianza import evaluar, veredictos  # noqa: E402

ACTA = "FB-020"
CSV = RAIZ / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    texto = (RAIZ / "docs" / "actas" / f"{ACTA}.md").read_text(encoding="utf-8")
    sha_csv = hashlib.sha256(CSV.read_bytes()).hexdigest()
    if sha_csv not in texto:
        print("El CSV no es el preregistrado en FB-020: no se ejecuta.")
        return 2
    registro = RAIZ / "docs" / "actas" / "RESULTADOS.jsonl"
    if registro.exists() and any(json.loads(l)["acta"] == ACTA for l in registro.read_text(encoding="utf-8").splitlines() if l):
        print(f"{ACTA} ya se ejecutó: una acta se ejecuta una sola vez.")
        return 1
    regs = cargar(CSV).registros
    sueno, pulso = evaluar(series_de(regs, IndicadorSensor.SUENO)), evaluar(series_de(regs, IndicadorSensor.FC), hs=())
    v = veredictos(sueno)
    print(f"*** FB-020 · LifeSnaps REAL (no astronautas) + zigzag SIMULADO · acta sha256={acta.hash_sha256} ***")
    f = sueno["fpr"]
    print(f"SUEÑO: {sueno['n_ventanas']} ventanas de {sueno['n_personas_con_ventana']} personas · FPR {f['k']}/{f['n']} = {100 * f['tasa']:.2f} % "
          f"Wilson95=[{100 * f['wilson95'][0]:.2f}, {100 * f['wilson95'][1]:.2f}] · personas con alarma: {f['personas_con_alarma']}")
    for h, p in sueno["potencia"].items():
        print(f"  zigzag H={h}σ: canal de varianza {100 * p['canal_varianza']:.1f} % · CUSUM de media {100 * p['cusum_media']:.1f} %")
    g = pulso["fpr"]
    print(f"PULSO (secundario): {pulso['n_ventanas']} ventanas · FPR {g['k']}/{g['n']} = {100 * g['tasa']:.2f} % Wilson95=[{100 * g['wilson95'][0]:.2f}, {100 * g['wilson95'][1]:.2f}]")
    print("VEREDICTOS:", v)
    print("Límites: no son astronautas; ventanas de una persona correlacionadas; zigzag simulado; unilateral al alza.")
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256,
             "acta_registrada_utc": acta.registrada_utc, "semillas": list(acta.semillas), "csv_sha256": sha_csv,
             "banner": "REAL (LifeSnaps, no astronautas) + zigzag SIMULADO", "sueno": sueno, "pulso": pulso, "veredictos": v}
    with registro.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(linea, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
