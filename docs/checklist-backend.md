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
7. **Stack cerrado**: Django (+DRF) · PostgreSQL · Next.js; dominio puro en `src/` (sin Django), una app Django por módulo. Frontend (Next) viene después del backend.
8. **Lo que el jurado compra**: LA SALA + detectores con recibo + preregistros públicos con hash; el lab como **métrica** (tarjetas nacidas → refutadas → sostenidas → detectores nuevos).

**Cosas que NO sé o no he leído (honestidad):** DOC-02 (apéndices B/C: actas FB-001…008 y anclas C-1…C-23), DOC-03 (pantallas y banco del jurado) y DOC-04 (contrato E/S del lab) **no los he leído enteros**; hoy los conozco por `CLAUDE.md` y DOC-01. Antes de implementar FUNDICIÓN o las falsaciones los abriré. Los scripts de FB-001/FB-002 que `CLAUDE.md` dice que "ya existen" **no están en este repo**.

## 1 · Resumen de estado

| Bloque | Hecho | Falta |
|---|---|---|
| M0 Base | M0.1 stack · M0.2 repo · M0.3 contratos · M0.4 IN-3 (parcial) · M0.5 (parcial: GO-2 automatizado) · M0.6 andamio · M0.7 v0.2.1 · M0.8 banner heredado · M0.9 auditoría · M0.10 correcciones · M0.11 DC-13 · M0.13 persistencia | M0.5 (cierre de FB-001…004) · M0.12 citas→id · M0.14 alertas |
| M1 Libro + Contrapeso | M1.1 (núcleo, parcial) · M1.2 Contrapeso | M1.1 con datos reales, endpoints REST (M1.3), FB-005 (M1.4) |
| M2 Motor | — | MO-1…MO-3, FB-002, MO-4, MO-5, IN-4 |
| M3 Vitrina | — (frontend Next, después del backend) | 6 pantallas |
| M4 FUNDICIÓN | — | minería, ≥5 tarjetas, Faro, Adversario |

Tests: **130 pytest verdes**. `sysmap check`: nada peor que la línea base.

## 2 · Contratos de datos (DC-01…DC-13) — `src/contratos/`

| Contrato | Es | Schema+tests | Persistencia (Postgres) | Notas |
|---|---|---|---|---|
| DC-01 | Canal A, sensores | [x] | [ ] | ausencia = `valor` vacío solo si `calidad=ausente` (v0.2.1) |
| DC-02 | Canal B, autorreporte | [x] | [ ] | idem con `registro_ausencia` |
| DC-03 | Canal C, eventos físicos | [x] | [x] | + `lectura_clima_espacial` y `banner` (v0.2.1); banner coherente con la fuente |
| DC-04 | Libro GPV (9 presupuestos) | [x] | [ ] | `incertidumbre_del_manifiesto` > 0; `estado_linea` (v0.2) |
| DC-05 | Alarma con recibo | [x] | [ ] | sin `regla_exacta` no hay alarma |
| DC-06 | Stream de residuo | [x] | [ ] | residuo = observado − predicho (verificado) |
| DC-07 | Cápsula exportable | [x] | [ ] | sin `limites` no exporta |
| DC-08 | Cierre de conservación | [x] | [ ] | residuo = entradas − salidas − Δalmacén − pérdida; el umbral CIERRA/NO CIERRA es lógica de MO-6 |
| DC-09 | Forma diaria del hábitat | [x] | [ ] | amplitud ≥ 1 |
| DC-10 | Errores y contagio | [x] | [ ] | brote ⇔ más de `k_brote` descendientes |
| DC-11 | Ficha de vida de sensor | [x] | [ ] | |
| DC-12 | Tarjeta de la Fundición | [x] | [ ] | fuente con id válido obligatoria; hash desde `en_prueba` |
| DC-13 | Intento de ingesta (v0.2.2) | [x] | [x] | el fallo del feed es dato |

Ideas de contrato **pendientes de decisión humana**: hash de DC-12 inmutable una vez fijado (anti-HARKing; requiere persistencia); `banner` en DC-04/05/06/10/11/12 (hoy se hereda, regla de DOC-01 v0.2.1).

## 3 · Capa 0 · Ingesta — `src/ingesta/` · app `apps.ingesta`

- [ ] **IN-1** normaliza telemetría de sensores → DC-01. **Desbloqueado para validar el método:** LifeSnaps (S-07, verificado; **no son astronautas**) trae sueño, pulso, HRV, temperatura y ánimo diarios (M2.7). Para hábitat sigue sin haber telemetría real abierta.
- [ ] **IN-2** autorreporte 3 toques → DC-02 (la ausencia también es dato). Necesita el endpoint de captura (Django/DRF) y no datos externos; los datos serán reales cuando haya usuarios.
- [~] **IN-3** clima espacial en vivo → DC-03/DC-13.
  - [x] SWPC Kp (feed 1), rayos X (feed 4) → DC-03 `lectura_clima_espacial`, banner REAL, hash, crudo archivado (M0.4, MP-3).
  - [x] Alertas oficiales (`products/alerts.json`): se archivan; [ ] **clasificarlas a `tormenta_solar` (M0.14, bloqueado: falta citar la guía de mensajes de SWPC)**.
  - [x] Compuerta de admisión: rechaza sin banner / sin fuente con id / simulado sin semilla pública.
  - [x] Archivo de lecturas crudas solo-anexar + manifiesto (`data/lecturas/`).
  - [x] Ficha de verdad OS-892 verificada contra su lectura cruda.
  - [ ] Plasma y campo magnético (`rtsw_wind_1m`, `rtsw_mag_1m`) y protones → LA TORMENTA (M3.3).
  - [ ] **DONKI** (declarado en DOC-01, sin endpoint verificado) · [ ] **OSDR en vivo** (solo hay un registro estático de OS-892; OS-892 no tiene archivos de datos).
  - [x] Persistido en Postgres (`EventoClimaEspacial`, `IntentoIngesta`, CHECK en BD) + `manage.py ingestar_swpc` (M0.13); archivo sin duplicados.
  - [ ] Programar la ingesta periódica (cron/tarea); hoy se corre a mano con `scripts/ingestar_swpc.py`.
- [ ] **IN-4** Banco de Falsaciones: replay, Monte Carlo, premortem, **modo adversario**, inyección de 3 anomalías (deriva coherente / flujo no contabilizado / fuga física). Todo **SIMULADO** con banner y semilla pública (registro X-02). El script existente no está en el repo (M2.6).

## 4 · Capa 1 · Libro — `src/libro/` · app `apps.libro`

- [ ] **LB-1** los 9 presupuestos sobre DC-04; **el libro debe cerrar** (M1.1). Entradas DC-01/02/03; salida: residuos contables. **P0 antes que detectores nuevos.**
- [ ] `estado_linea` (limpio/sospechoso/cuarentena) que viaja con la línea y marca descendientes (GO-6).
- [ ] Cálculo/recálculo de `incertidumbre_del_manifiesto` (la fija MO-8).
- [ ] Persistencia de DC-04 y trazabilidad `fuente_linea` → DC-01/02/03.

## 5 · Capa 2 · Motor — `src/motor/` · app `apps.motor`

- [ ] **MO-1** modelo nulo personal: línea base de 14 días, **priors OSDR** (**[!] necesita datos reales con archivos en OSDR; OS-892 no los tiene — buscar un estudio OSD con datos publicados**), modo aprendizaje honesto (M2.1).
- [ ] **MO-2** residuo, sorpresa a 2σ → DC-06 · [ ] **MO-3** CUSUM **bilateral**, FPR 1 % en 14 d → DC-05 con recibo (M2.2).
- [ ] **FB-002 reproducible: 10/10 detecciones, preaviso mediano 21 días** (semillas 20261113/14/15) — test de regresión permanente (M2.3). **El script no está en el repo; hay que traerlo o reconstruirlo desde el acta preregistrada, sin inventar el resultado.**
- [ ] **MO-4** matriz co-deriva (planta × chip × humano) · FB-003 (M2.4).
- [ ] **MO-5** integrador lento del agua (TOC/WRS) · FB-004 (M2.5).
- [x] **MO-6 El Contrapeso** (**núcleo hecho, M1.2**: cierre con σ propagada, bilateral, pérdida no declarada no existe; fixtures SIMULADOS X-05; falta DC-08 en la base de datos y FB-005) (= *conciliación de datos aplicada a un hábitat tripulado*, D-09): cierre de conservación agua/aire/energía → DC-08, `CIERRA / NO CIERRA` el mismo día (M1.2). **P0.** La simulación se parametriza con `docs/parametros-publicos.md` (siempre SIMULADA).
- [ ] **MO-7** forma diaria del hábitat → DC-09 (FB-006, P2) · [ ] **MO-8** demografía de testigos → DC-11 (FB-008, P2).

## 6 · Capa 3 · Fábrica / LA FUNDICIÓN — `src/fabrica/` · app `apps.fabrica`

- [ ] **FA-1** kanban de H-cards (señal refutadora ANTES de probar) · [ ] **FA-2** N-of-1 A-B-A-B · [ ] **FA-3** cápsula DC-07 (sin límites no exporta).
- [ ] **FA-4 El Faro**: predicciones fechadas registradas antes del dato, calificadas en público (M4.3). **Meta del submit: 1.**
- [ ] **LA FUNDICIÓN**: minería de residuo → tarjetas DC-12 (puerta que rechaza sin mecanismo/fuente/precio) (M4.1); **≥5 tarjetas** con fuente con identificador y hash ANTES de probar (M4.2); **El Adversario** (tripulación sintética que evade detectores — SIMULADO, documentar 1 escape) (M4.4); circulación: tarjeta sostenida → detector nuevo (M4.5).
- Ancla real disponible para tarjetas: NASA HRP (riesgo óseo 1–1,5 %/mes), OS-892 (cita 1–2 %), bibliografía con identificador en `docs/auditoria-de-fuentes.md`.

## 7 · Capa 4 · Superficies — `src/superficies/` · app `apps.superficies`

- [ ] **Endpoints REST** DC-04/05/06 (M1.3). **Regla dura: jamás exponen contenido individual, solo agregados y estados** (privacidad como arquitectura; el contenido individual no cruza de Capa 3 a Capa 4).
- [ ] SU-1 alertas con recibo · SU-2 tablero del comandante (agregados) · SU-3 sello semanal (regla `arbitro.proveedor ≠ operador`) · SU-4 miner de premortems.
- [ ] SU-5 frontend Next.js (LA SALA, EL RESIDUO, LA MESA, LA TORMENTA, LA CÁPSULA, EL PRESUPUESTO): **después del backend**.

## 8 · Gobernanza — `src/…` / `docs/actas/` · app `apps.gobernanza`

- [~] **GO-2 preregistro con hash SHA-256 ANTES de correr**: **automatizado** (`src/gobernanza/preregistro.py`: hash de bytes exactos, índice solo-anexar, compuerta `exigir_preregistro`, detección de edición posterior). FB-005…FB-008 re-registradas (101 tests). **[!] M0.5 sigue abierta:** los hashes de DOC-02 Ap. B no son reproducibles; FB-001/002 sin acta ni script; FB-003/004 sin acta redactada. [ ] Enlazar el hash del acta a la alarma DC-05 (`hash_preregistro`).
- [ ] **GO-6** epidemiología del error: caso con linaje, cuarentena, R0 por fuente, acta de brote (DC-10; FB-007).
- [ ] GO-1 árbitro externo (humano, pendiente; mientras tanto el árbitro es matemático: hash + semilla) · GO-3, GO-4, GO-5, GO-7 son proceso, no código.

## 9 · Transversal — reglas y tests que ya las hacen cumplir

- [x] Flujo unidireccional del dominio y dominio sin Django (`tests/test_arquitectura.py`).
- [x] Una app Django por módulo; Postgres real conectado (`tests/test_base_de_datos.py`).
- [x] Contratos que rechazan campos ajenos, timestamps no-UTC, NaN/inf, personas con identidad real (`tests/test_contratos.py`).
- [x] Herencia de banner: un derivado nunca asciende a REAL en silencio (`banner_heredado`).
- [x] Auditoría de fuentes repetible (`scripts/verificar_fuentes.py --red`).
- [ ] Test de privacidad en la API (cuando existan endpoints): ningún campo individual en las respuestas.
- [ ] Banner REAL/SIMULADO visible en toda respuesta de la API.

## 10 · Propuestas y decisiones abiertas

- MP-3 archivo de lecturas crudas — **aceptada, implementada** (M0.4) · MP-4 registro de intentos — **aceptada, implementada** (DC-13, M0.11).
- MP-1 predicción conformal (bandas en DC-06) y MP-2 BOCPD — PROPUESTA en DOC-01 §7, sin aceptar.
- Pendiente tuyo: confirmar interpretación de DC-12 (`precio` = {datos, cómputo, días}; `valor_si_cierta` lista de DC-xx) y decidir si `banner` se declara en los derivados o se hereda.
