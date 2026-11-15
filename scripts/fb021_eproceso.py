"""M6.1 · FB-021: alarma anytime-valid (e-proceso). Entrena `s` en LifeSnaps, congela y valida UNA vez en Zenodo 8018238 (REAL, no astronautas) + escalón SIMULADO.
Uso:  uv run python scripts/fb021_eproceso.py"""
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
from src.ingesta import fatiga_zenodo, lifesnaps  # noqa: E402
from src.motor import evaluacion_eproceso as ev  # noqa: E402

ACTA = "FB-021"
LS = RAIZ / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"
ZEN = RAIZ / "data/externos/zenodo_8018238"
SHAS = {LS: "82c84ee495be4b0ff636a8a44271ffb124e2358d9dd52012b529b897f3d54963",
        ZEN / "day_activity_features.csv": "004c31d0875782088d7351f500189c06d700dd707f8a20e24c397159036515f3",
        ZEN / "screener_survey.csv": "01b0ea479577db1d4aa8afad8e7b5540632979352acfbb26405e360b8ae01eac"}


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    for ruta, h in SHAS.items():
        if hashlib.sha256(ruta.read_bytes()).hexdigest() != h:
            print("dataset distinto del preregistrado:", ruta.name); return 2
    registro = RAIZ / "docs" / "actas" / "RESULTADOS.jsonl"
    if any(json.loads(l)["acta"] == ACTA for l in registro.read_text(encoding="utf-8").splitlines() if l):
        print(f"{ACTA} ya se ejecutó: una sola vez."); return 1
    ls = lifesnaps.cargar(LS).registros
    ls_s, ls_p = series_de(ls, IndicadorSensor.SUENO), series_de(ls, IndicadorSensor.FC)
    sel = ev.seleccionar(ls_s, ls_p)
    print(f"*** FB-021 · acta sha256={acta.hash_sha256} ***\nENTRENAMIENTO (LifeSnaps):")
    for s, v in sel["tabla"].items():
        print(f"  s={s}: FPR {v['k']}/{v['n']} = {100 * v['fpr_entrenamiento']:.2f} % · potencia H=2,0 {100 * v['potencia_h2']:.1f} % · apto={v['apto']}")
    print("ELEGIDO:", sel["elegido"])
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256,
             "acta_registrada_utc": acta.registrada_utc, "semillas": list(acta.semillas), "shas": {k.name: v for k, v in SHAS.items()},
             "banner": "REAL (LifeSnaps entrenamiento; Zenodo 8018238 validación; no astronautas) + escalón SIMULADO", "entrenamiento": sel}
    if sel["elegido"] is None:
        linea["veredictos"] = {"resultado": "REFUTADA: ningún s apto; Zenodo no se tocó"}
        print("Ningún s apto: FB-021 REFUTADA sin tocar Zenodo.")
    else:
        s = sel["elegido"]
        zr = fatiga_zenodo.cargar(ZEN / "day_activity_features.csv", fatiga_zenodo.sanos(ZEN / "screener_survey.csv"))
        sueno = ev.evaluar(series_de(zr, IndicadorSensor.SUENO), s)
        pulso = ev.evaluar(series_de(zr, IndicadorSensor.FC), s, ())
        v = ev.veredictos(sueno, pulso)
        f, g = sueno["fpr"], pulso["fpr"]
        print(f"VALIDACIÓN (Zenodo, s={s} congelado):\n  SUEÑO {sueno['n_ventanas']} ventanas / {sueno['n_personas_con_ventana']} personas · FPR e-proceso {f['k']}/{f['n']} = "
              f"{100 * f['tasa']:.2f} % Wilson95=[{100 * f['wilson95'][0]:.2f}, {100 * f['wilson95'][1]:.2f}] · CUSUM de media {100 * f['tasa_cusum_media']:.2f} %")
        for h, p in sueno["potencia"].items():
            print(f"    escalón H={h}σ: e-proceso {100 * p['eproceso']:.1f} % (retardo mediano {p['retardo_mediano_dias']}) · CUSUM de media {100 * p['cusum_media']:.1f} %")
        print(f"  PULSO {pulso['n_ventanas']} ventanas · FPR {g['k']}/{g['n']} = {100 * g['tasa']:.2f} % Wilson95=[{100 * g['wilson95'][0]:.2f}, {100 * g['wilson95'][1]:.2f}]")
        print("VEREDICTOS:", v)
        linea.update({"s_congelado": s, "sueno": sueno, "pulso": pulso, "veredictos": v})
    print("Límites: no son astronautas; ventanas por persona correlacionadas; escalón simulado; s es calibración empírica, no garantía teórica.")
    with registro.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(linea, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
