"""Análisis POSTERIOR (post-hoc) de FB-009: por qué la calibración transfiere en sueño y no en pulso.
NO decide nada ni altera los veredictos del acta; es diagnóstico declarado como tal. Datos reales + simulación X-06
(semilla pública 20261113). Uso: uv run python scripts/fb009_posthoc.py
"""
import random
import statistics
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(RAIZ))
from src.contratos.comunes import Indicador, IndicadorSensor  # noqa: E402
from src.contratos.dc01_sensores import CalidadDato  # noqa: E402
from src.ingesta.incertidumbre import sigma_de  # noqa: E402
from src.ingesta.lifesnaps import cargar  # noqa: E402
from src.motor.evaluacion import ejecutar_unidad, unidades  # noqa: E402
from src.motor.linea_base import estimar_linea_base  # noqa: E402

CSV = RAIZ / "data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv"


def lag1(x):
    m = statistics.fmean(x)
    den = sum((v - m) ** 2 for v in x)
    return sum((x[i] - m) * (x[i + 1] - m) for i in range(len(x) - 1)) / den if den else 0.0


def main():
    regs = cargar(CSV).registros
    for ind, ie in ((Indicador.SUENO, IndicadorSensor.SUENO), (Indicador.FC, IndicadorSensor.FC)):
        por = defaultdict(list)
        for r in regs:
            if r.indicador is ie and r.calidad is CalidadDato.OK:
                por[r.persona_id].append((r.ts_utc.date(), r.valor))
        s = sigma_de(ie).sigma
        us = [(p, u) for p, serie in por.items() for u in unidades(serie)]
        sig_eff = [estimar_linea_base(p, ind.value, b, s).sigma_efectiva for p, (b, _) in us]
        sd_pers = [estimar_linea_base(p, ind.value, b, s).sd for p, (b, _) in us]
        ac = [lag1([v for _, v in b + m]) for _, (b, m) in us]
        print(f"{ind.value}: σ_efectiva mediana {statistics.median(sig_eff):.2f} (SD intrapersonal mediana {statistics.median(sd_pers):.2f}; σ_sensor {s:.2f}) "
              f"| autocorrelación lag-1 entre días válidos sucesivos: media {statistics.fmean(ac):.2f}, mediana {statistics.median(ac):.2f}")
    print("\nSimulación AR(1) (X-06, semilla 20261113): FPR del MISMO pipeline con ruido autocorrelacionado")
    h = 10.011730842174083
    for rho in (0.0, 0.2, 0.4, 0.6):
        rng = random.Random(20261113)
        n, alarmas = 3000, 0
        for _ in range(n):
            x = rng.gauss(0, 1)
            vals = []
            for _ in range(28):
                x = rho * x + (1 - rho * rho) ** 0.5 * rng.gauss(0, 1)
                vals.append(x)
            f0 = date(2026, 1, 1)
            serie = [(f0 + timedelta(days=i), v) for i, v in enumerate(vals)]
            alarmas += ejecutar_unidad("sim", Indicador.SUENO, 0.0, serie[:14], serie[14:], h).alarma
        print(f"  ρ = {rho}: FPR = {100 * alarmas / n:.2f} %")


if __name__ == "__main__":
    main()
