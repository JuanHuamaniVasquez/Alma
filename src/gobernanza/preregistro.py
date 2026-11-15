"""GO-2 · Preregistro con hash SHA-256 ANTES de correr (mandamiento 2).

Cada acta es un archivo de `docs/actas/`; su hash es el SHA-256 de **los bytes exactos del
archivo**, así cualquiera puede recalcularlo. El índice `docs/actas/INDEX.jsonl` es solo-anexar:
una vez registrada, un acta no se edita (editarla sería HARKing); un cambio exige un acta nueva
(FB-005-v2) con su propio hash y fecha. Todo runner debe llamar a `exigir_preregistro` primero.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

from src.contratos.comunes import SEMILLAS_PUBLICAS


class PreregistroInvalido(ValueError):
    """No hay preregistro válido: la prueba no puede correr (mandamiento 2)."""


@dataclass(frozen=True)
class Entrada:
    acta: str
    archivo: str
    hash_sha256: str
    registrada_utc: str
    semillas: tuple[int, ...]
    estado: str
    hash_publicado_origen: str | None
    nota: str | None


def hash_acta(ruta: Path) -> str:
    return hashlib.sha256(ruta.read_bytes()).hexdigest()


def _indice(raiz: Path) -> Path:
    return raiz / "docs" / "actas" / "INDEX.jsonl"


def leer_indice(raiz: Path) -> list[Entrada]:
    ruta = _indice(raiz)
    if not ruta.exists():
        return []
    out = []
    for linea in ruta.read_text(encoding="utf-8").splitlines():
        if linea.strip():
            d = json.loads(linea)
            out.append(Entrada(d["acta"], d["archivo"], d["hash_sha256"], d["registrada_utc"], tuple(d["semillas"]),
                               d["estado"], d.get("hash_publicado_origen"), d.get("nota")))
    return out


def registrar(raiz: Path, acta: str, *, semillas: tuple[int, ...], ahora: datetime | None = None,
              hash_publicado_origen: str | None = None, nota: str | None = None) -> Entrada:
    """Registra `docs/actas/<acta>.md` con el hash de sus bytes exactos. Solo-anexar."""
    archivo = raiz / "docs" / "actas" / f"{acta}.md"
    if not archivo.is_file():
        raise PreregistroInvalido(f"no existe {archivo.name}")
    if any(e.acta == acta for e in leer_indice(raiz)):
        raise PreregistroInvalido(f"{acta} ya está registrada: un acta registrada no se edita ni se re-registra (usa {acta}-v2)")
    if not semillas or any(s not in SEMILLAS_PUBLICAS for s in semillas):
        raise PreregistroInvalido("el acta debe declarar semillas públicas del proyecto")
    ts = (ahora or datetime.now(UTC)).astimezone(UTC)
    e = Entrada(acta, archivo.name, hash_acta(archivo), ts.strftime("%Y-%m-%dT%H:%M:%SZ"), tuple(semillas),
                "preregistrada", hash_publicado_origen, nota)
    with _indice(raiz).open("a", encoding="utf-8") as f:
        f.write(json.dumps({**e.__dict__, "semillas": list(e.semillas)}, ensure_ascii=False) + "\n")
    return e


def verificar(raiz: Path) -> list[str]:
    """Problemas del índice (lista vacía = todas las actas intactas)."""
    problemas = []
    for e in leer_indice(raiz):
        ruta = raiz / "docs" / "actas" / e.archivo
        if not ruta.is_file():
            problemas.append(f"{e.acta}: falta el archivo {e.archivo}")
        elif hash_acta(ruta) != e.hash_sha256:
            problemas.append(f"{e.acta}: el archivo cambió después del preregistro (hash distinto)")
    return problemas


def exigir_preregistro(raiz: Path, acta: str, *, ahora: datetime | None = None) -> Entrada:
    """Compuerta de todo runner: sin acta registrada e intacta, y registrada ANTES de ahora, no se corre."""
    por_acta = {e.acta: e for e in leer_indice(raiz)}
    if acta not in por_acta:
        raise PreregistroInvalido(f"{acta} no está preregistrada: no hay ciencia sin preregistro previo")
    e = por_acta[acta]
    ruta = raiz / "docs" / "actas" / e.archivo
    if not ruta.is_file() or hash_acta(ruta) != e.hash_sha256:
        raise PreregistroInvalido(f"{acta}: el acta no coincide con su hash registrado")
    momento = (ahora or datetime.now(UTC)).astimezone(UTC)
    if datetime.strptime(e.registrada_utc, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=UTC) > momento:
        raise PreregistroInvalido(f"{acta}: registrada después de la ejecución")
    return e
