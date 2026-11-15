# Registro de decisiones (fechado, con su evidencia)

> Cada decisión del humano o de diseño que cambió el rumbo, con fecha y commit. Si una decisión cambia, se **añade** una fila nueva; no se borra la anterior.

| ID | Fecha | Decisión | Quién | Evidencia |
|---|---|---|---|---|
| D-01 | 2026-11-14 | **Stack cerrado:** Django (+DRF) · PostgreSQL · Next.js; dominio puro en `src/`, una app Django por módulo | humano | `ee8d38b`, `CLAUDE.md` §2 |
| D-02 | 2026-11-15 | **Política de datos:** todo real con fuente enlazada; lo simulado/inventado se etiqueta SIMULADO y se registra; sin dato real el ítem se bloquea | humano | `4b10956`, `docs/politica-de-datos.md` |
| D-03 | 2026-11-15 | Contratos DC-01…DC-12 como schemas pydantic con rechazo de campos ajenos | Claude (confirmado por humano) | `637a843` |
| D-04 | 2026-11-15 | **DOC-01 v0.2.1:** `lectura_clima_espacial`, banner en DC-03, ausencia con `valor` vacío, herencia de banner | humano (vía segunda IA) | `eb8bafe` |
| D-05 | 2026-11-15 | **MP-3** (archivo de lecturas crudas) y **MP-4** (DC-13, intentos de ingesta) aceptadas; DOC-01 → v0.2.2 | humano | `42e1519`, `f6d692a` |
| D-06 | 2026-11-15 | Cifra ósea con **doble anclaje**: NASA HRP (1–1,5 % densidad/mes) primaria, OS-892 secundaria. OS-892 verificado por API con control negativo | humano + Claude | `dccddbb` |
| D-07 | 2026-11-15 | **GO-2:** el hash es el SHA-256 de los bytes exactos del acta; FB-005…FB-008 re-registradas (los hashes publicados no eran reproducibles) | Claude | `fc94096` |
| D-08 | 2026-11-15 | **Residuo contable = observada − esperada; la línea cierra si \|r\| ≤ 2σ.** DOC-01 → v0.2.3 (sin validar con datos reales) | humano (propuesta de Claude) | `8213a44` |
| D-09 | 2026-11-15 | **Posicionamiento:** el Contrapeso es *conciliación de datos aplicada a un hábitat tripulado* (no una invención). Eje de originalidad: protocolo preregistrado + libro único cuerpo/máquina + piso fijado por el manifiesto | humano (acepta recomendaciones) | `9b5c0f3`, `docs/evaluacion-paper.md` §7 |
| D-10 | 2026-11-15 | **Alcance congelado** hasta cerrar M2.8: prioridad LB-1, Contrapeso, MO-1…MO-3, preregistro; LA FUNDICIÓN en segundo plano salvo tarjetas con fuente real | humano (acepta recomendaciones) | `CLAUDE.md` §14 |
| D-11 | 2026-11-15 | La simulación de FB-005 se **parametriza con números públicos de NASA** (sigue SIMULADA) | humano (acepta recomendaciones) | `docs/parametros-publicos.md` |
| D-12 | 2026-11-15 | **LifeSnaps** (Zenodo 7229547, CC-BY 4.0) elegido como dataset real para validar línea base + CUSUM; md5 verificado contra Zenodo | Claude (humano delegó la búsqueda) | `docs/politica-de-datos.md` S-07 |
| D-13 | 2026-11-15 | **Se adoptan los re-registros** de FB-005…FB-008 (hash de bytes exactos, `docs/actas/INDEX.jsonl`) como referencia pública; el hash publicado el 11-nov se conserva como histórico no reproducible | humano | `docs/actas/README.md` |
| D-14 | 2026-11-15 | **MP-5 (verde con potencia) y MP-6 (tarjeta sueño/HRV × Kp) aceptadas**; entran a la cola como M2.10 y M4.6 | humano | `docs/propuestas.md`, `TASKS.md` |
| D-15 | 2026-11-15 | **Claude lidera la ejecución técnica**; norte: un proyecto de nivel de avance científico (preregistrado, reproducible, datos reales, nulos publicados). Se sigue el orden de la cola | humano | `CLAUDE.md` §15 |
| D-16 | 2026-11-15 | **El Contrapeso propaga la incertidumbre en cuadratura** (errores independientes, supuesto declarado) y cierra con \|residuo\| ≤ 2·σ_propagada; sus fixtures son SIMULADOS y parametrizados con números públicos de NASA | Claude (bajo D-15) | `src/motor/contrapeso.py` |
| D-17 | 2026-11-15 | **Primer experimento del proyecto:** FB-005-D1 (demo kill del Contrapeso) preregistrada con hash antes de escribir el runner y ejecutada una sola vez; predicción confirmada. No sustituye a FB-005 (400 corridas) | Claude (bajo D-15) | `7d53d7a`, `docs/actas/RESULTADOS.jsonl` |
| D-18 | 2026-11-15 | **La σ de un sensor solo existe con fuente verificada**; si es de otro dispositivo se declara PROXY. Sin σ verificada el indicador no se emite | Claude (bajo D-15) | `src/ingesta/incertidumbre.py` |
| D-19 | 2026-11-15 | **DC-02 no se emite desde LifeSnaps** (el dataset no trae `duracion_respuesta_s`). Si se quiere usar ánimo de datasets sin ese metadato, requiere un cambio de contrato (a decidir por el humano) | Claude (bajo D-15) | `src/ingesta/lifesnaps.py` |
| D-20 | 2026-11-15 | **DC-12 admite NTRS y PMID** como fuentes con identificador (DOC-01 → v0.2.4): DOC-04 §2 listaba NTRS y DOC-01 no lo admitía. Hallado al leer DOC-04 completo | Claude (bajo D-15) | `src/contratos/dc12_fundicion.py` |
| D-21 | 2026-11-15 | **Coherencia documento ⇄ código comprobada por máquina** y registro de afirmaciones heredadas (`afirmaciones-por-verificar.md`): lo ✗/⚠ no se dice al jurado como hecho | Claude (bajo D-15), a petición del humano | `tests/test_doc_vs_codigo.py` |
| D-22 | 2026-11-15 | **MP-7 y MP-8 aceptadas** por el humano («acepto lo que propones»; Claude como ejecutor) | humano | `docs/propuestas.md` |

## Decisiones pendientes del humano
- Mecanismo citable para la tarjeta sueño × Kp (sin mecanismo no pasa la puerta DC-12).
- Aportar el **banco Monte Carlo, actas y scripts de FB-001/FB-002** (bloquean M2.3 y M2.6), la **Ficha de Verdad (K-4)** y las **ideas dormidas (K-6)**.
