# Checklist del backend — mapa vivo de todas las funcionalidades

> Generado el 2026-11-15 a partir de DOC-01 §2 (registro oficial de módulos), `CLAUDE.md` y `TASKS.md`. Es un **mapa**, no una fuente: ante conflicto manda DOC-01. Cada línea dice qué existe **de verdad** en el repo (código + test) y qué falta. `[x]` = hecho con test verde; `[~]` = parcial; `[ ]` = pendiente; `[!]` = bloqueado (con la razón).
> Reglas de este archivo: no se marca nada sin evidencia; lo simulado se etiqueta (ver `docs/politica-de-datos.md` §3); lo que no se leyó de un DOC se dice.

## 0 · Lo que entiendo del proyecto (para que lo verifiques)

1. **ALMA / TONO-LAB** es software de monitoreo de salud *cuerpo + máquina* para astronautas (reto NASA Space Apps 2026 #4). El **paciente es la persona**; el hábitat es una **variable de entrada del cuerpo** (CO₂→cabeza, ruido→sueño, radiación→ADN), nunca el paciente en pantalla.
2. Tiene **dos corazones**: el **Guardián** (monitorea y avisa: Capas 0–4) y **LA FUNDICIÓN** (laboratorio que acuña hipótesis; cada una que sobrevive **compila en un detector nuevo** del Guardián — es el único output que el lab puede publicar).
3. **La columna vertebral** es el **Libro contable LB-1** con los **9 presupuestos** (aire, agua, energía, dosis, ritmo, carga, inmunidad, conducta, tiempo), donde se cruzan cuerpo y máquina. El flujo es **unidireccional**: Ingesta → Libro → Motor → Fábrica → Superficies. Nada lee directo de los sensores.
4. **El motor detecta sin causa**: modelo nulo personal (línea base de 14 días) → residuo (2σ, agudo) → CUSUM bilateral (deriva lenta). El **piso de detección lo fija la incertidumbre del manifiesto**, no el sensor (hallazgo v4). Los cierres de conservación (**El Contrapeso**) comprueban agua/aire/energía contra la ley física.
5. **Los 3 mandamientos**: (1) nada lee de sensores directo; (2) **nada se prueba sin preregistro con hash SHA-256 ANTES de correr**; (3) **colores solo con regla contestable** — toda alarma lleva recibo (regla exacta, semilla, hash), si la regla no se cumple se retira sola, y todo registro/pantalla lleva banner **REAL/SIMULADO**.
6. **Política de datos del humano**: nada simulado sin etiqueta, nada inventado; todo dato real con fuente enlazada; sin dato real el ítem se **bloquea**, no se simula.
7. **Stack cerrado**: Django (+DRF) · PostgreSQL · Next.js; dominio puro en `src/` (sin Django), una app Django por módulo. El frontend (`web/`, Next, en inglés) ya existe.
8. **Lo que el jurado compra**: LA SALA + detectores con recibo + preregistros públicos con hash; el lab como **métrica** (tarjetas nacidas → refutadas → sostenidas → detectores nuevos).

**Lectura completada el 2026-11-15: DOC-01, DOC-02, DOC-03 y DOC-04 leídos enteros, más el bestiario, el radar y el LEEME.** La coherencia documento ⇄ código la comprueba una máquina (`tests/test_doc_vs_codigo.py`: campos y enums de los 13 contratos + que los 36 módulos de DOC-01 §2 estén en este mapa). Las afirmaciones heredadas con su estado real están en `docs/afirmaciones-por-verificar.md`. Lo que cambió al leerlos: (1) FB-001, FB-002 y FB-005 dependen de «el banco Monte Carlo de FB-002», que **no está en este repo**, y tampoco sus actas ni scripts: M2.3 y M2.6 siguen bloqueados hasta que el humano los aporte; (2) la tesis del producto es medir **sin wearables**, leyendo la telemetría del hábitat: **LifeSnaps (wearables) solo valida D1**; P8/P9/P11 no tienen datos reales; (3) DOC-04 §10 prohíbe construir M-L1…M-L5 ahora; (4) DC-12 y su puerta de «fuente con identificador» ya coinciden con lo implementado.

## 1 · Resumen de estado (actualizado 2026-11-15, tras la vitrina)

| Bloque | Hecho (con evidencia en TASKS.md) | Falta |
|---|---|---|
| M0 Base | Stack, repo, contratos DC-01…DC-14 (DOC-01 **v0.2.8**), ingesta SWPC (Kp, rayos X, alertas → `tormenta_solar`), banner heredado, GO-2 automatizado, DOIs verificados (S-16) | DONKI y OSDR en vivo; ingesta periódica programada |
| M1 Libro + Contrapeso | LB-1 con persistencia y API, Contrapeso (ρ sensible, M2.17b), FB-005-D1, libro real de `tiempo` (LifeSnaps) | Los otros 7 presupuestos: **bloqueados por falta de dato real** (se muestran vacíos) |
| M2 Motor | MO-1/2/3, banco IN-4 (3 anomalías, Monte Carlo, adversario), MO-4 (FB-003R), MO-5 (FB-004R), verde con potencia DC-14, canal de varianza (MP-15, FB-020), réplica de FB-002 (**no replicó, 8/10**, D-35) | M2.22 (validar el canal robusto: necesita ≥300 ventanas independientes) |
| M3 Vitrina | `web/` (Next 15, inglés): 8 salas, voz de ALMA determinista, escenarios de tormenta simulados | Ensayo humano; pulido visual con feedback |
| M4 Fundición | 5 tarjetas DC-12, 1 detector circulado, Faro F-001, Adversario, cápsulas DC-07 | MP-15/M2.22 para el detector de varianza |
| M5 Entrega | Checklist de honestidad ejecutable, borradores de formulario/video/ruta/preprint, revisión de literatura (PubMed+NTRS) | URLs, video, ensayo, IEEE/Scholar, revisión humana |

Tests: **385 pytest verdes** (HEAD en `git log`). `sysmap check`: nada peor que la línea base.

## 2 · Contratos de datos (DC-01…DC-14) — `src/contratos/`

Todos con schema y tests (`tests/test_contratos.py`, coherencia con DOC-01 en `tests/test_doc_vs_codigo.py`). Persistencia en Postgres: **DC-03, DC-04, DC-05, DC-06, DC-08, DC-13, DC-14**. DC-01/02 viven como adaptadores de dominio (no se persisten sensores crudos); DC-07 se construye bajo demanda desde las actas (`/api/capsulas/`); DC-12 en `data/fundicion/*.jsonl` (solo-anexar); DC-09/10/11 solo schema (sin experimento que los alimente todavía).

## 3 · Capa 0 · Ingesta — `src/ingesta/`

- [x] **IN-1** adaptadores reales: LifeSnaps (S-07), Zenodo 8018238 (S-13), Utah agua (S-12); series por persona en `series.py`.
- [x] **IN-2** autorreporte de ánimo en 3 toques → DC-02: HECHO (`POST /api/animo/`, UI en el modo Body; sin detector aún).
- [~] **IN-3** SWPC operativo (Kp, rayos X, alertas oficiales Kp ≥ 5; compuerta de admisión; archivo crudo con hash; persistido). Pendiente: DONKI, OSDR en vivo, plasma/campo magnético, programar la ingesta (hoy `manage.py ingestar_swpc`).
- [x] **IN-4** banco de falsaciones (`src/motor/banco.py`, `scripts/banco.py`), adversario (`adversario.py`) y escenarios de tormenta (`escenarios.py`, X-14). Todo SIMULADO y etiquetado.

## 4 · Capa 1 · Libro — `src/libro/` · app `apps.libro`

- [x] **LB-1** DC-04 con `estado_linea`, persistencia solo-anexar, cierre por presupuesto; `sembrar_demo` (X-13: aire y agua con ancla pública). [x] libro real de `tiempo` (M1.1).
- [ ] Los demás presupuestos (energía, dosis, ritmo, carga, inmunidad, conducta): sin ancla real → bloqueados, no simulados.

## 5 · Capa 2 · Motor — `src/motor/` · app `apps.motor`

- [x] MO-1 modelo nulo · MO-2 residuo 2σ · MO-3 CUSUM bilateral con h calibrado y retiro automático · MO-6 Contrapeso (FB-005-D1; ρ sensible) · MO-4 triangulación (FB-003R) · MO-5 integrador del agua (FB-004R, caudal real de Utah).
- [~] FB-002: **documentado, no replicado** (FB-015-v2: 8/10; D-35). Regresión permanente en `tests/test_banco_ocio_v2.py`.
- [~] Canal de varianza (MP-15): contrato y módulo hechos; **refutado en datos reales (FPR 9,0 %, FB-020)**; candidato robusto C4 sin validar (FB-020-v2, M2.22). No emite verde ni alarma reales.
- [~] MO-8: solo el prior de MTBF de Jones 2019 (M2.11). [ ] MO-7 forma diaria: sin iniciar.

## 6 · Capa 3 · Fábrica / LA FUNDICIÓN — `src/fabrica/`

- [x] FA-1 mesa de tarjetas (`mesa.py`) · FA-3 cápsulas DC-07 (`capsula.py`) · FA-4 El Faro (`faro.py`, F-001 fechada).
- [x] 5 tarjetas DC-12 (2 refutadas, 1 sostenida, 1 sin datos, 1 en prueba), 1 detector circulado (`umbral_personal`, DC-05 v0.2.7).
- [ ] FA-2 N-of-1 A-B-A-B: especificado, sin implementar.

## 7 · Capa 4 · Superficies — `src/superficies/` · `backend/apps/superficies` · `web/`

- [x] **API de solo lectura** (13 rutas GET): libro, días, alarmas, residuo, cierres, verdes, fundición, actas, demo-kill, tormenta, escenario, cápsulas. Privacidad por mutación; banner en toda respuesta.
- [x] **Narrador de ALMA** determinista (`narrador.py`): plantilla + dato + fuente; jamás texto libre. Audio con Kokoro-82M local (`scripts/voz_alma.py`).
- [x] **SU-5 frontend** `web/`: Medical Module, Machine Room, The Leak, The Vault, The Foundry, The Storm, The Budget, The Capsule. Checklist de honestidad: `tests/test_checklist_honestidad.py`.
- [~] **SU-1** alertas con recibo y **SU-2** tablero (agregados): cubiertos por el recibo de papel y las salas de `web/`; no son módulos aparte.
- [ ] SU-3 sello semanal · SU-4 minería de premortems (diseñados, sin implementar).

## 8 · Gobernanza — `src/gobernanza/` · `docs/actas/`

- [x] **GO-2**: hash de bytes exactos, índice solo-anexar, `exigir_preregistro` en cada runner; 21 actas, 16 ejecutadas una vez. [ ] GO-6 epidemiología del error (DC-10, FB-007). [ ] GO-1 árbitro externo: humano. GO-3, GO-4, GO-5 y GO-7 son proceso, no código (GO-7, el MODO FRONTERA, declarado en DOC-01).

## 8b · Contenido curado (K-1…K-6) — se mina, no se programa

| ID | Qué es (DOC-01 §2) | Estado real en el repo (2026-11-15) |
|---|---|---|
| K-1 | Bestiario: familias de hipótesis minadas de ficción + clase real | [~] `docs/inventario-maestro-bestiario.md` presente; es **andamio** (BRONCE) y quedó **anterior a DOC-01 v0.2** (8 balances vs 9 presupuestos); lleva nota de verificación de unicidad |
| K-2 | Familias de casos FM-1…FM-10 con ancla citada | [~] listadas en el bestiario y en DOC-01 §6; las anclas con identificador están verificadas en `auditoria-de-fuentes.md`; **faltan** las que solo se citan por nombre (M0.12) |
| K-3 | Semillas públicas y reglas de reproducibilidad | [x] `SEMILLAS_PUBLICAS` en `src/contratos/comunes.py`, compuerta en `preregistro.py` y `compuerta.py` |
| K-4 | Ficha de Verdad (8 CIENCIA REAL + 3 EXTRAPOLACIÓN) | [~] **reconstruida** en `docs/ficha-de-verdad.md` (21 filas, 5 clases incl. SIN VERIFICAR) con lo verificado; la original sigue sin estar en el repo |
| K-5 | Banco de anclas citadas (~45 fuentes verificadas) | [~] 23 anclas en DOC-02 Ap. C + banco del bestiario §7 + 19 identificadores verificados (`auditoria-de-fuentes.md`) + fuentes S-01…S-10; **no consolidado** en un solo registro de ~45 |
| K-6 | Ideas dormidas (10 de 17) con razón de muerte escrita | [ ] **no está en el repo**; solo se las menciona. Hay que pedirlas al humano o reconstruirlas |

## 9 · Transversal — reglas que ya hacen cumplir los tests

- [x] Flujo unidireccional y dominio sin Django (`test_arquitectura.py`) · Postgres real (`test_base_de_datos.py`) · contratos estrictos (`test_contratos.py`).
- [x] Banner heredado, nunca ascendido en silencio · privacidad en la API (con prueba de mutación) · banner en toda respuesta.
- [x] Checklist de honestidad ejecutable (14 comprobaciones) · actas intactas · la UI no afirma «10/10».
- [x] Auditoría de fuentes repetible (`scripts/verificar_fuentes.py --red`).

## 10 · Propuestas y decisiones abiertas

- Aceptadas e implementadas: MP-3, MP-4, MP-5, MP-14, MP-15 (con su refutación parcial). MP-1 (conformal) y MP-2 (BOCPD): PROPUESTA sin aceptar.
- Pendiente del humano: URLs del repo y PDF, video, ensayo, elegir voz, tramitar acceso a GLOBEM (M2.22), revisar los borradores antes de enviar.
