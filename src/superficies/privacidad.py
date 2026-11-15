"""M6.4 · Presupuesto de privacidad ε — el décimo libro (MP-19).

Problema real (CLAUDE.md: «el contenido individual jamás cruza a las superficies»): con una tripulación de 4–6 personas, hasta un AGREGADO identifica
a alguien por DIFERENCIAS (conteo de la tripulación de 5 menos el de los otros 4 = el estado de una persona). Defensa: mecanismo de Laplace
(privacidad diferencial ε) y un LIBRO que suma el ε gastado por cada publicación (composición secuencial); al agotarse, no se publica nada más.
Es el mismo gesto de todos los libros del sistema: lo que entra, menos lo que sale, debe cuadrar con lo declarado.
Límites: ε concreto (2,0 de ejemplo) NO es una política de la NASA; la composición secuencial es conservadora; el ruido es de conteos (sensibilidad 1).
"""
from __future__ import annotations

import hashlib
import math
import random
from dataclasses import dataclass, field

SEMILLA = 20261113
EPSILON_TOTAL = 2.0


class PresupuestoAgotado(RuntimeError):
    """La publicación gastaría más ε del que queda: no se publica."""


def laplace(escala: float, rng: random.Random) -> float:
    u = rng.random() - 0.5
    return -escala * math.copysign(1.0, u) * math.log(1.0 - 2.0 * abs(u))


@dataclass
class Libro:
    total: float = EPSILON_TOTAL
    asientos: list[dict] = field(default_factory=list)

    @property
    def gastado(self) -> float:
        return round(sum(a["epsilon"] for a in self.asientos), 10)

    @property
    def restante(self) -> float:
        return round(self.total - self.gastado, 10)

    def liberar_conteo(self, etiqueta: str, verdadero: int, n: int, epsilon: float, semilla: int = SEMILLA) -> int:
        """Publica un conteo (0..n) con ruido de Laplace de escala 1/ε; deja asiento. El ruido es reproducible por (semilla, etiqueta)."""
        if epsilon <= 0:
            raise ValueError("ε debe ser positivo")
        if epsilon > self.restante + 1e-12:
            raise PresupuestoAgotado(f"«{etiqueta}» gastaría ε={epsilon} y quedan {self.restante}")
        rng = random.Random(int(hashlib.sha256(f"{semilla}-{etiqueta}".encode()).hexdigest(), 16) % 2**63)
        valor = min(n, max(0, round(verdadero + laplace(1.0 / epsilon, rng))))        # recorte = postprocesado: no gasta ε
        self.asientos.append({"etiqueta": etiqueta, "epsilon": epsilon, "mecanismo": "Laplace", "sensibilidad": 1, "n": n, "valor_publicado": valor})
        return valor

    def estado(self) -> dict:
        return {"epsilon_total": self.total, "epsilon_gastado": self.gastado, "epsilon_restante": self.restante, "cierra": self.restante >= 0,
                "asientos": self.asientos}
