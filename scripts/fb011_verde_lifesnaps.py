"""M2.10 · FB-011: contraste del recibo de verde (DC-14) en datos REALES de LifeSnaps (no astronautas) + caída SIMULADA.
Se niega a correr sin el acta registrada e intacta; exige el CSV preregistrado; UNA sola ejecución.
Uso:  uv run python scripts/fb011_verde_lifesnaps.py
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
from src.motor.evaluacion import H_FB009, evaluar_verde, veredictos_verde  # noqa: E402

ACTA = "FB-011"
CSV = RAIZ / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"
TABLA = RAIZ / "data/calibracion/tabla_potencia.json"


def imprimir(titulo, r):
    print(f"\n== {titulo} · {r['n_unidades']} unidades ==")
    for m, v in r["por_m"].items():
        print(f"m={m:>2} días válidos · MDE declarado {v['mde_sigma']}σ (≈{v['mediana_mde_fisico']:.1f} en unidades físicas) · "
              f"potencia observada {v['detecciones']}/{v['n']} = {100 * v['tasa']:.1f} % Wilson95=[{100 * v['wilson95'][0]:.1f},{100 * v['wilson95'][1]:.1f}] "
              f"(refuta si ≤ {v['k_critico_H1']}) · control (MDE/2): {v['control_detecciones']}/{v['n']} = {100 * v['control_tasa']:.1f} %")


def main() -> int:
    ahora = datetime.now(UTC)
    acta = exigir_preregistro(RAIZ, ACTA, ahora=ahora)
    texto = (RAIZ / "docs" / "actas" / f"{ACTA}.md").read_text(encoding="utf-8")
    sha_csv, sha_tabla = hashlib.sha256(CSV.read_bytes()).hexdigest(), hashlib.sha256(TABLA.read_bytes()).hexdigest()
    if sha_csv not in texto or sha_tabla not in texto:
        print("El CSV o la tabla de potencia no son los preregistrados en FB-011: no se ejecuta.")
        return 2
    registro = RAIZ / "docs" / "actas" / "RESULTADOS.jsonl"
    if registro.exists() and any(json.loads(l)["acta"] == ACTA for l in registro.read_text(encoding="utf-8").splitlines() if l):
        print(f"{ACTA} ya se ejecutó: una acta se ejecuta una sola vez.")
        return 1
    regs = cargar(CSV).registros
    sueno = evaluar_verde(series_de(regs, IndicadorSensor.SUENO), Indicador.SUENO, sigma_de(IndicadorSensor.SUENO).sigma)
    pulso = evaluar_verde(series_de(regs, IndicadorSensor.FC), Indicador.FC, sigma_de(IndicadorSensor.FC).sigma)
    v = veredictos_verde(sueno, pulso)
    print(f"*** FB-011 · LifeSnaps REAL (no astronautas) + caída SIMULADA · acta sha256={acta.hash_sha256} · h={H_FB009} ***")
    imprimir("PRIMARIO: sueño", sueno)
    imprimir("SECUNDARIO: pulso (iid optimista por autocorrelación)", pulso)
    print(f"\nVEREDICTOS → H1 (potencia declarada, sueño): {v['H1']} · H2 (control negativo): {v['H2']} · "
          f"H3 (predicción de fallo en pulso, m=14): {v['H3']} (significativamente menor: {v['H3_significativamente_menor']})")
    print("Límites: no son astronautas; σ de sensor proxy; días quitados MCAR; bloques correlacionados; n limitado.")
    linea = {"ts_ejecucion_utc": ahora.strftime("%Y-%m-%dT%H:%M:%SZ"), "acta": ACTA, "hash_acta": acta.hash_sha256,
             "acta_registrada_utc": acta.registrada_utc, "semillas": list(acta.semillas), "csv_sha256": sha_csv,
             "tabla_sha256": sha_tabla, "banner": "REAL (LifeSnaps, no astronautas) + caída SIMULADA", "h": H_FB009,
             "sueno": sueno, "pulso": pulso, "veredictos": v}
    with registro.open("a", encoding="utf-8") as f:
        f.write(json.dumps(linea, ensure_ascii=False) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
