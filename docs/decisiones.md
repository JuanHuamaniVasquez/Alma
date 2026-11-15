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

## Decisiones pendientes del humano
- ¿Se adoptan los **re-registros** de FB-005…008 como referencia pública o se conserva el hash publicado el 11-nov? (`docs/actas/README.md`)
- ¿Se aceptan **MP-5 y MP-6** (`docs/propuestas.md`)?
- Mecanismo citable para la tarjeta sueño × Kp (sin mecanismo no pasa la puerta DC-12).
