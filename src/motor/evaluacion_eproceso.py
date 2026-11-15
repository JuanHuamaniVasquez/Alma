"""M6.1 · Evaluación del e-proceso con los mismos datos y ventanas que el canal de varianza (FB-020-v2). Ver docs/actas/FB-021.md."""
from __future__ import annotations

import statistics
from collections.abc import Sequence
from datetime import date

from .adversario import H_MEDIA, detecta_media
from .eproceso import ALFA, detecta
from .evaluacion_varianza import ventanas, wilson

HS = (1.0, 1.5, 2.0, 3.0)
GRILLA_S = (1.0, 1.25, 1.5, 2.0)


def _z(base: Sequence[float], vig: Sequence[float]) -> list[float] | None:
    mu, sd = statistics.fmean(base), statistics.stdev(base)
    return None if sd == 0 else [(x - mu) / sd for x in vig]


def evaluar(series: dict[str, list[tuple[date, float]]], s: float, hs: Sequence[float] = HS) -> dict:
    todas = [(p, b, v) for p, ser in sorted(series.items()) for b, v in ventanas(ser)]
    zs = [(p, _z(b, v)) for p, b, v in todas]
    zs = [(p, z) for p, z in zs if z is not None]
    n = len(zs)
    alarmas = [detecta(z, s) is not None for _, z in zs]
    k = sum(alarmas)
    cus = sum(detecta_media(z, H_MEDIA) for _, z in zs)
    res = {"s": s, "alfa": ALFA, "n_ventanas": n, "n_personas_con_ventana": len({p for p, _ in zs}),
           "fpr": {"k": k, "n": n, "tasa": k / n if n else None, "wilson95": wilson(k, n), "personas_con_alarma": len({p for (p, _), a in zip(zs, alarmas) if a}),
                   "k_cusum_media": cus, "tasa_cusum_media": cus / n if n else None}, "potencia": {}}
    for h in hs:                                                 # escalón de media de h·sd a lo largo de TODA la vigilancia (SIMULADO sobre datos reales)
        det = [detecta([x + h for x in z], s) for _, z in zs]
        ok = [d for d in det if d is not None]
        cm = sum(detecta_media([x + h for x in z], H_MEDIA) for _, z in zs)
        res["potencia"][str(h)] = {"eproceso": len(ok) / n if n else None, "cusum_media": cm / n if n else None, "k_e": len(ok), "k_cusum": cm,
                                   "retardo_mediano_dias": statistics.median(ok) if ok else None}
    return res


def seleccionar(sueno: dict, pulso: dict, fpr_max: float = ALFA, potencia_min: float = 0.50) -> dict:
    """Entrenamiento (LifeSnaps, sueño + pulso juntos): el MENOR s con FPR ≤ α y potencia(H=2,0, sueño) ≥ 0,50. Ninguno → None."""
    tabla = {}
    elegido = None
    for s in GRILLA_S:
        a, b = evaluar(sueno, s, (2.0,)), evaluar(pulso, s, ())
        k, n = a["fpr"]["k"] + b["fpr"]["k"], a["fpr"]["n"] + b["fpr"]["n"]
        tasa = k / n
        pot = a["potencia"]["2.0"]["eproceso"]
        tabla[str(s)] = {"k": k, "n": n, "fpr_entrenamiento": tasa, "potencia_h2": pot, "apto": tasa <= fpr_max and pot >= potencia_min}
        if elegido is None and tabla[str(s)]["apto"]:
            elegido = s
    return {"elegido": elegido, "tabla": tabla}


def veredictos(sueno: dict, pulso: dict) -> dict:
    f, g, p = sueno["fpr"], pulso["fpr"], sueno["potencia"]
    out = {}
    lim = f["wilson95"][1]
    out["H1_fpr_sueno"] = ("SOSTENIDA" if f["tasa"] <= 0.02 and lim <= 0.04 else "NO CONCLUYENTE" if f["tasa"] <= 0.02 else "REFUTADA")
    out["H2_no_inferioridad_potencia_h2"] = "SOSTENIDA" if p["2.0"]["eproceso"] >= p["2.0"]["cusum_media"] - 0.05 else "REFUTADA"
    d = p["3.0"]["retardo_mediano_dias"]
    out["H3_retardo_h3"] = "SOSTENIDA" if d is not None and d <= 7 else "REFUTADA"
    out["H4_control_positivo"] = "VÁLIDO" if p["3.0"]["eproceso"] >= 0.95 else "INVÁLIDO"
    out["H5_fpr_pulso"] = "SOSTENIDA" if g["tasa"] <= 0.02 and g["wilson95"][1] <= 0.04 else "NO CONCLUYENTE" if g["tasa"] <= 0.02 else "REFUTADA"
    return out
