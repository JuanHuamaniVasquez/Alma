# TASKS.md — cola de construcción ALMA (la única lista viva del repo)

> **Reglas de esta cola (heredadas del protocolo §5 de MAP-S1):**
> 1. Se trabaja SIEMPRE el ítem abierto de menor número que no esté bloqueado.
> 2. **Jamás borrar ni reordenar ítems.** Solo marcar `[x]` con evidencia: tests que pasan + hash del commit.
> 3. Cada ítem define su "hecho" con un test. Sin test verde no hay ítem hecho.
> 4. Si aparece trabajo nuevo, entra como fila nueva al final de su bloque — nunca se implementa fuera de la cola.
> 5. Prioridad de fondo (DOC-03 §5): **P0 no negociable** = M0, M1, M2 y M3.1-M3.4. P2 si alcanza. P3 con datos fijos.

## M0 · Base (bloquea todo lo demás)

- [x] **M0.1 Cerrar el stack** y escribirlo en CLAUDE.md §2 (borrar la alternativa que no se use). *Hecho: CLAUDE.md §2 sin "SIN CERRAR".* — humano + Claude, 15 min · evidencia: Django+DRF / PostgreSQL / Next.js, conexión a Postgres verificada; sin test (es una decisión) — commit en el log
- [x] **M0.2 Init del repo**: git, pytest corriendo, estructura según CLAUDE.md §7 (`scripts/`, `src/ingesta|libro|motor|fabrica|superficies/`, `docs/`, `docs/actas/`, `data/`). *Hecho: pytest verde vacío + commit inicial.* — Dev A · evidencia: 3 tests pytest verdes (tests/test_estructura.py), commit 1d1875b
- [x] **M0.3 Materializar contratos DC-01…DC-12** como schemas validados (pydantic o dataclasses con validación) — campo a campo desde DOC-01 §3, incluyendo `estado_linea` de DC-04 (v0.2) y los 11 campos de DC-12. *Hecho: un test de validación por contrato (12 tests), y un test que RECHAZA una tarjeta DC-12 sin `fuentes[]` con identificador y una DC-05 sin `regla_exacta`.* — Dev A · evidencia: 48 tests en tests/test_contratos.py (12 válidos, 12 rechazo de campo ajeno, DC-12 sin fuentes/fuente inválida/sin mecanismo, DC-05 sin regla_exacta, +reglas por contrato); contratos en `src/contratos/`, commit 637a843
- [x] **M0.4 Datos y fixtures reales al repo**: NOAA SWPC (IN-3, sin API key), dataset OS-892 o extracto con identificador en `data/`, fichas de verdad, bestiario K-1/K-2 (`docs/inventario-maestro-bestiario.md`). *Hecho: loader lee los datos reales, imprime banner REAL/SIMULADO y rechaza registros sin banner, sin fuente con id o sin semilla.* — Dev B **[Decisiones 2026-11-15: incluye MP-3 (archivo de lecturas crudas `data/lecturas/` + manifiesto JSONL); feeds SWPC verificados: Kp, rtsw_wind_1m, rtsw_mag_1m, xrays-1-day, integral-protons-1-day, products/alerts.json; depende de M0.11]** · evidencia: loader IN-3 en `src/ingesta/` (swpc, archivo, compuerta, cliente) + `scripts/ingestar_swpc.py`; corrida real 2026-11-15: Kp 57 lecturas, rayos X 2.876, alertas 72, todas banner REAL con hash y crudo archivado; 93 tests pytest verdes (17 nuevos: lecturas reales, DC-13 de fallo/vacío, solo-anexar, compuerta con los 3 casos negativos, ficha OS-892 verificada contra su crudo); commit f6d692a. **Parcial, abierto:** donki y OSDR-en-vivo no se implementan (sin fuente verificada aún); `rtsw`/protones para LA TORMENTA van en M3.3
- [ ] **M0.5 Regenerar/verificar los 8 preregistros FB-001…FB-008** en `docs/actas/` con sus hashes SHA-256 (GO-2; hashes de referencia en DOC-02 Apéndice B — p. ej. FB-005 `6c923ac5…`). *Hecho: script recalcula los 8 hashes y cuadran; test lo verifica.* — Dev B **[PARCIAL 2026-11-15 — NO cerrada: el criterio "los 8 hashes cuadran" no se cumple]** Hecho: GO-2 automatizado en `src/gobernanza/preregistro.py` (hash de bytes exactos, índice solo-anexar `docs/actas/INDEX.jsonl`, compuerta `exigir_preregistro`, anti-HARKing); FB-005…FB-008 re-registradas antes de ejecutar, 101 tests pytest verdes, commit fc94096. **Bloqueado:** (1) los hashes publicados de DOC-02 Ap. B no se pueden reproducir (texto original no está en el repo; 0 de 4 con búsqueda amplia); (2) FB-001/FB-002 no tienen acta ni script en el repo; (3) FB-003/FB-004 no tienen acta redactada. Decisión del humano pendiente: ver `docs/actas/README.md`
- [x] **M0.13 Persistencia de DC-03 y DC-13 en PostgreSQL** (fila añadida antes de implementar): modelos en `apps.ingesta` + migraciones + comando `manage.py ingestar_swpc` que usa `src/ingesta` y guarda eventos e intentos; el dominio sigue sin importar Django. *Hecho: test de integración con la BD real (ida y vuelta de un DC-03 y un DC-13; el hash del crudo se conserva).* — Dev A · evidencia: modelos `EventoClimaEspacial` (DC-03) e `IntentoIngesta` (DC-13) con restricciones CHECK en PostgreSQL, repositorio con re-validación al leer, `manage.py ingestar_swpc`, migración aplicada en la BD real; ingesta idempotente y archivo sin duplicados (misma lectura = mismo crudo); 112 tests pytest verdes (11 nuevos de persistencia); corrida real 2026-11-15: 57 lecturas Kp en BD; commit d36604a
- [ ] **M0.14 Clasificar las alertas oficiales de SWPC → DC-03 `tormenta_solar`** (fila añadida antes de implementar): hoy `products/alerts.json` solo se archiva. Decidir con evidencia qué códigos de producto (ALTK*/WARK*/ALTEF*/ALTTP*…) declaran un evento y qué parámetros numéricos llevan, citando la documentación oficial de SWPC. **Bloqueado: requiere leer y citar la guía de mensajes de SWPC; no se inventa la taxonomía.** — Dev B
- [x] **M0.6 Andamio Django + política de datos** (fila añadida por petición del humano 2026-11-15): proyecto `backend/` (config + 6 apps: ingesta, libro, motor, fabrica, superficies, gobernanza), PostgreSQL real, dominio puro en `src/`, `docs/politica-de-datos.md`. *Hecho: tests de conexión a Postgres, una-app-por-módulo, dominio sin imports de Django y flujo unidireccional.* — Dev A · evidencia: 12 tests pytest verdes, commit 4b10956
- [x] **M0.7 Alinear contratos con las decisiones del humano de 2026-11-15** (fila añadida antes de implementar): bump DOC-01 → v0.2.1 (DC-03 `lectura_clima_espacial` + `banner`; ausencia con `valor` vacío en DC-01/DC-02; DC-12 `preregistro_hash` desde `en_prueba`; fila IN-3 en §6) y `CLAUDE.md` §3/§13. *Hecho: tests de aceptación y rechazo de cada regla nueva.* — Dev A · evidencia: 65 tests pytest verdes, commit eb8bafe
- [x] **M0.8 Herencia de banner** (`banner_heredado`): un derivado hereda SIMULADO si alguna fuente lo es; sin fuentes se rechaza. *Hecho: test en tests/test_contratos.py.* — Dev A · evidencia: 65 tests pytest verdes, commit eb8bafe
- [x] **M0.9 Auditoría de fuentes** (fila añadida antes de implementar, petición del humano 2026-11-15): verificación reproducible de todas las citas con identificador contra NCBI/Crossref/arXiv/NTRS + informe `docs/auditoria-de-fuentes.md`. *Hecho: 2 tests offline de extracción; la consulta en red no se testea (depende de servicios externos) y se justifica así; el informe lista 19 citas verificadas y 8 hallazgos.* — Dev B · evidencia: 67 tests pytest verdes, commit 67b9648
- [x] **M0.10 Correcciones por auditoría (doble anclaje de la cifra ósea, OS-892 verificado, MP-3 parcial)** (fila añadida antes de implementar): bestiario con ancla primaria NASA HRP (1–1,5 % densidad/mes) + cita secundaria OS-892 (1–2 % masa/mes); `OS-892-extracto.*` verificados vía API de OSDR con control negativo; respuesta cruda archivada en `data/lecturas/` con manifiesto JSONL; `verificar_fuentes.py` prueba OS-892 en vivo; H-1 de la auditoría retractado. *Hecho: 3 tests con el fixture real (registro OS-892 verificable, rechaza otra accesión/título, hash del manifiesto = hash del archivo).* — Dev B · evidencia: 70 tests pytest verdes, commit dccddbb
- [x] **M0.11 DC-13 · Registro de intento de ingesta (MP-4, aceptada por el humano 2026-11-15)**: `intento_id`, `ts_utc`, `fuente`, `url`, `resultado` (ok/fallo/vacio), `http_status`, `hash_lectura_cruda` (solo si ok), `error` (solo si fallo), `banner`. Cambio de contrato → DOC-01 v0.2.2 + fila en §6 + fila en CLAUDE.md. *Hecho: schema con tests (ok exige hash y prohíbe error; fallo exige error y prohíbe hash).* — Dev A · **bloquea M0.4** (el loader escribe DC-13) · evidencia: 76 tests pytest verdes (6 nuevos de DC-13), DOC-01 → v0.2.2, commit 42e1519
- [ ] **M0.12 Citas por nombre → identificador (DOI/PMID/URL)** (aceptada 2026-11-15): resolver con Crossref/NCBI vía script (no de memoria) Frost 2003, Mehta 2014/2017, Hassler 2014, etc., y registrarlas en `docs/politica-de-datos.md` §2; NASA-STD-3001 por revisión + URL oficial. Ejecutar después de M0.4/M0.5 y antes de M4.2. *Hecho: cada cita resuelta pasa `verificar_fuentes.py --red`.* — Dev B

## M1 · El libro + El Contrapeso (P0 — Dev A)

- [ ] **M1.1 LB-1**: los 9 presupuestos (aire, agua, energia, dosis, ritmo, carga, inmunidad, conducta, tiempo) sobre DC-04; el libro debe cerrar. *Hecho: fixture de 14 días sin anomalías → libro cierra, `residuo_contable` dentro de `incertidumbre_del_manifiesto`.*
- [ ] **M1.2 MO-6 · El Contrapeso**: cierre de conservación agua/aire/energía → DC-08 (residuo = entradas − salidas − Δalmacén − pérdida declarada, con incertidumbre propagada). *Hecho: fixture con fuga no contabilizada produce veredicto `NO CIERRA` el mismo día; fixture limpio produce `CIERRA`.*
- [ ] **M1.3 Endpoints REST** que exponen DC-04 / DC-05 / DC-06 (lo que consumirá la vitrina). *Hecho: test de integración HTTP verde; el endpoint nunca expone contenido individual.*
- [ ] **M1.4 FB-005 · demo kill**: dos columnas — detector contra el manifiesto (debe quedar CIEGO ante flujo no contabilizado) vs detector de ley (debe alarmar). *Hecho: acta ejecutada con hash publicado ANTES de correr; 1/1 corrida con semilla pública; la columna A verde y la B alarmada en el mismo fixture.*

## M2 · El motor (P0 — Dev B)

- [ ] **M2.1 MO-1 modelo nulo personal**: línea base de 14 días, priors OSDR, modo aprendizaje honesto. *Hecho: predicción + σ_efectiva sobre fixture real.*
- [ ] **M2.2 MO-2 residuo (2σ) + MO-3 CUSUM bilateral** → DC-06 / DC-05. *Hecho: alarmas con recibo completo (regla exacta + semilla + hash); el CUSUM es bilateral (alza y caída) — la falsación v4 lo obligó.*
- [ ] **M2.3 FB-002 reproducible: 10/10 detecciones, preaviso mediano 21 días** (semillas 20261113/14/15). *Hecho: test de regresión permanente que reproduce el 10/10 y el mediano; si falla, no se sube nada.*
- [ ] **M2.4 FB-003 · triangulación de 3 testigos** (MO-4: planta × chip × humano — ¿quién miente?). *Hecho: acta ejecutada con hash ANTES; diagnóstico correcto del testigo corrupto en el fixture.*
- [ ] **M2.5 FB-004 · integrador lento del agua** (MO-5: TOC como censo colectivo, con la normalización MP-3 integrada en el diseño). *Hecho: acta con hash ANTES; resultado publicado aunque sea feo.*
- [ ] **M2.6 IN-4 Banco de Falsaciones materializado**: replay histórico, Monte Carlo, inyección de los 3 tipos de anomalía (deriva coherente / flujo no contabilizado / fuga física) y **modo adversario**. *Hecho: cada corrida imprime banner UNIVERSO SIMULADO — DÍA N + semilla; las 3 clases de anomalía se inyectan y se detectan/no-detectan según diseño.*

## M3 · La vitrina (P1 — Dev C)

- [ ] **M3.1 LA SALA**: silueta del hábitat como paciente + anillo de los 9 presupuestos; consume DC-04 agregado + DC-05 activas + DC-08 (CIERRA/NO CIERRA). *Regla dura: jamás contenido individual.*
- [ ] **M3.2 EL RESIDUO**: corriente observado vs predicho, bandas σ, nacimiento de alertas; consume DC-06. *Regla dura: banner REAL/SIMULADO siempre visible.*
- [ ] **M3.3 LA TORMENTA**: motor de escenarios + actividad solar real en vivo (SWPC). *Regla dura: banner "UNIVERSO SIMULADO — DÍA N" cuando aplique.*
- [ ] **M3.4 Demo kill en dos columnas en pantalla** (transversal, momento final del pitch). *Hecho: el hash del preregistro FB-005 visible en pantalla, publicado antes de correr.*
- [ ] **M3.5 (P2 si alcanza) LA MESA**: kanban de H-cards nacidas → en prueba → refutadas → confirmadas; cada tarjeta muestra su señal refutadora.
- [ ] **M3.6 (P3 con datos fijos del banco) LA CÁPSULA + EL PRESUPUESTO**: cápsula no exporta sin límites declarados; el presupuesto muestra los libros y el piso de detección (σ del manifiesto computada por MO-8).

## M4 · LA FUNDICIÓN — el segundo corazón (P2 — Dev B con apoyo de Dev A)

- [ ] **M4.1 Minería de residuo**: la FUNDICIÓN consume el residuo del Guardián (DC-05 sin causa, DC-06 sorpresa/deriva) + cuerpos públicos con identificador (OS-892) y acuña tarjetas **DC-12** completas. *Hecho: la puerta rechaza toda tarjeta sin mecanismo, sin fuente con id o sin precio (tests de rechazo).*
- [ ] **M4.2 Acuñar ≥5 tarjetas** (techo 10) desde K-2 + OS-892, cada una con preregistro hasheado ANTES de probar. *Hecho: 5 tarjetas en LA MESA con hash, precio {datos, cómputo, días} y valor_si_cierta (detectores DC-xx nuevos).*
- [ ] **M4.3 FA-4 · El Faro**: **1 predicción fechada** registrada ANTES del dato, con fecha límite de calificación (candidata natural: FM-3 sueño×hueso sobre OS-892, anclas C-18/C-19 de DOC-02). *Hecho: la predicción está hasheada y fechada; la calificación es automática cuando el dato llega.*
- [ ] **M4.4 El Adversario**: generar una tripulación sintética enferma que **evade los detectores** actuales y documentar **1 escape** que entra como pregunta/fila nueva. *Hecho: el escape está escrito en acta y abrió una fila en TASKS.md (regla 4).*
- [ ] **M4.5 (si alcanza) La circulación**: tarjeta sostenida → detector DC-xx nuevo registrado en el Guardián. *Hecho: el detector nuevo aparece con su fila y su alarma con recibo.*

## M5 · Submit (14-nov — DOC-03 §9)

- [ ] **M5.1 Formulario Space Apps** completo (descripción 150-200 palabras, how it works, datos con links, link al repo, link al PDF v0.4).
- [ ] **M5.2 Video 30-60 s** (guion de 4 líneas: problema 10 s → método 15 s → demo 20 s → reproducibilidad 15 s).
- [ ] **M5.3 Dry run del pitch** con la demo abierta (ensayo 2, sin notas).
- [ ] **M5.4 Checklist de honestidad**: todos los datos en pantalla con banner; todas las alarmas con recibo; FB-002 10/10 corriendo en vivo o su test visible.

## Bloqueado / decisiones pendientes del humano (no son ítems de código)

- Stack definitivo (M0.1) — propuesta por defecto en CLAUDE.md §2.
- Nombre oficial del lab (DOC-04 §11: LA FUNDICIÓN preferente) — no bloquea código; solo cambia strings de UI.
- Árbitro externo humano (GO-1) — hasta entonces el árbitro es matemático (hash + semilla); no bloquea.
