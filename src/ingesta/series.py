"""IN-1 · Series diarias por persona a partir de registros DC-01: solo `calidad = ok` (la ausencia y lo sospechoso no se rellenan ni cuentan)."""
from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from datetime import date

from src.contratos.dc01_sensores import CalidadDato, DC01Sensor


def series_de(registros: Iterable[DC01Sensor], indicador) -> dict[str, list[tuple[date, float]]]:
    """{persona_id: [(día, valor), …]} del `indicador` dado, en el orden de entrada; solo registros con calidad OK."""
    por: dict[str, list[tuple[date, float]]] = defaultdict(list)
    for r in registros:
        if r.indicador is indicador and r.calidad is CalidadDato.OK:
            por[r.persona_id].append((r.ts_utc.date(), r.valor))
    return dict(por)
