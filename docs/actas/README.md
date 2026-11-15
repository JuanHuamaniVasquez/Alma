# Actas de preregistro (GO-2)

**Regla (mandamiento 2):** nada se prueba sin preregistro con hash ANTES de correr. Aquí el hash es el **SHA-256 de los bytes exactos del archivo del acta** (`sha256sum docs/actas/FB-005.md`), de modo que cualquiera lo recalcula. `INDEX.jsonl` es solo-anexar; `src/gobernanza/preregistro.py` hace cumplir: un acta registrada no se edita (un cambio es un acta nueva `-v2`), y todo runner llama a `exigir_preregistro` antes de ejecutar.

**Estado honesto de los 8 preregistros (M0.5):**

| Acta | Estado | Nota |
|---|---|---|
| FB-005 · El Contrapeso | registrada (re-registro) | hash original de DOC-02 Ap. B no reproducible; ver aviso en el acta |
| FB-006 · El Hábitat Sueña | registrada (re-registro) | idem |
| FB-007 · El Sistema Inmune | registrada (re-registro) | idem |
| FB-008 · La Demografía de los Testigos | registrada (re-registro) | idem |
| FB-001, FB-002 | **no hay acta en el repo** | ejecutadas según DOC-01/02; el acta y el script (`falsacion_d4_creo_ocio.py`) no están aquí. No se inventan |
| FB-003, FB-004 | **sin acta redactada** | figuran como «programadas»; hay que escribirlas y registrarlas antes de correr |

**Decidido por el humano el 2026-11-15 (D-13):** se adoptan los re-registros de este repo como referencia pública; el hash publicado el 11-nov se conserva solo como histórico no reproducible. Los runners pueden ejecutar FB-005…FB-008 con `exigir_preregistro`.
