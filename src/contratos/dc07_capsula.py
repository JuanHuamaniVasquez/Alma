"""DC-07 · Cápsula exportable (DOC-01 §3). Sin `limites` no hay cápsula."""
from __future__ import annotations

from pydantic import model_validator

from .comunes import Banner, Contrato, Real, Sha256, Texto


class Preregistro(Contrato):
    hash: Sha256
    semilla: int


class MapaFrontera(Contrato):
    gamma: Real
    tau: Real


class DC07Capsula(Contrato):
    version: Texto
    banner: Banner
    hipotesis: Texto
    prueba_protocolo: Texto  # con el diseño A-B-A-B declarado
    preregistro: Preregistro  # antes de mirar datos
    numeros: dict[str, Real | str]  # resultado completo, sin redacción publicitaria
    senal_refutadora: Texto  # escrita antes; viaja con el veredicto
    veredicto: Texto
    limites: Texto  # obligatorio: sin frontera, no hay cápsula
    mapa_frontera: MapaFrontera | None = None  # cuando aplique (p. ej. D4)
    empaquetado: Texto | None = None  # ref MP-4 (propuesta, no aceptada aún)
    gobernanza: Texto | None = None  # ref GO-5 (consentimiento/anonimización)

    @model_validator(mode="after")
    def _numeros(self):
        if not self.numeros:
            raise ValueError("numeros no puede estar vacío")
        return self
