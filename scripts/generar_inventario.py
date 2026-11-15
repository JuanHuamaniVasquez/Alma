"""Genera la tabla de experimentos de `docs/informe/INVENTARIO-IEEE.md` a partir de los registros sellados (INDEX.jsonl, RESULTADOS.jsonl, actas_en.json).
No inventa nada: cada fila sale de un registro. Uso:  uv run python scripts/generar_inventario.py"""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
A = RAIZ / "docs" / "actas"
INI, FIN = "<!-- TABLA-EXPERIMENTOS:INICIO -->", "<!-- TABLA-EXPERIMENTOS:FIN -->"


def jl(p):
    return [json.loads(l) for l in p.read_text(encoding="utf-8").splitlines() if l.strip()]


def main() -> int:
    idx = {e["acta"]: e for e in jl(A / "INDEX.jsonl")}
    res = {}
    for r in jl(A / "RESULTADOS.jsonl"):
        res.setdefault(r["acta"], r)
    en = json.loads((RAIZ / "data" / "actas_en.json").read_text(encoding="utf-8"))["actas"]
    filas = ["| Acta | Hash (8) | Registrada (UTC) | Ejecutada | Datos | Resultado (EN) | Nota interna |", "|---|---|---|---|---|---|---|"]
    for acta, e in idx.items():
        r, t = res.get(acta), en.get(acta, {})
        ejec = (r.get("ts_ejecucion_utc") or r.get("ts_utc") or r.get("fecha") or "ejecutada") if r else "no ejecutada"
        filas.append(f"| {acta} | `{e['hash_sha256'][:8]}` | {e['registrada_utc']} | {ejec} | {t.get('data', '—')} | {t.get('outcome', '—')} | {(e.get('nota') or '')[:110]} |")
    tabla = "\n".join(filas)
    f = RAIZ / "docs" / "informe" / "INVENTARIO-IEEE.md"
    s = f.read_text(encoding="utf-8")
    a, b = s.index(INI) + len(INI), s.index(FIN)
    f.write_text(s[:a] + "\n" + tabla + "\n" + s[b:], encoding="utf-8")
    print(f"{len(idx)} actas, {len(res)} ejecutadas → {f.relative_to(RAIZ)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
