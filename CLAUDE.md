# CLAUDE.md — ALMA (TONO-LAB) · ley operativa del repositorio

> Este archivo se carga automáticamente en cada sesión de Claude Code. Es el resumen operativo.
> **Regla de oro (DOC-00 §4): antes de citar cualquier número, contrato o experimento, abrir el DOC correspondiente y leerlo ahí — no de memoria.** Ante conflicto entre este archivo y DOC-01, manda DOC-01 y se corrige este archivo.

## 1 · Qué es este proyecto (para no improvisar nunca)

- **ALMA** (nombre de trabajo **TONO-LAB**): software de monitoreo de salud cuerpo+máquina para astronautas. NASA Space Apps 2026, reto *"Create Health Monitoring Software for Astronauts on Space Missions"*. Jurado: 14-nov-2026. Equipo: 3 devs.
- **Dos corazones:** el **Guardián** (monitorea y avisa — Capas 0-4 del sistema) y **LA FUNDICIÓN** (laboratorio que acuña hipótesis; cada hipótesis que sobrevive **compila en un detector nuevo** del Guardián — es el único output que la FUNDICIÓN puede publicar).
- **La cerradura de enfoque:** el paciente es la **persona**. El hábitat es **variable de entrada del cuerpo** (CO₂→cabeza, ruido→sueño, radiación→ADN), jamás el paciente en pantalla.
- Lo que el jurado compra: LA SALA + detectores con recibo + preregistros públicos con hash. El lab se muestra como **métrica** (tarjetas nacidas → refutadas → sostenidas → detectores nuevos), nunca como poesía.
- Indicadores oficiales del brief (exactos, no adaptar): presión, fc, glucosa, temperatura, sueño (DC-01) + ánimo (DC-02, autorreporte en 3 toques).

## 2 · Stack y decisiones cerradas (no reabrir entre sesiones)

- **ESTADO: CERRADO (M0.1, 2026-11-14, decide el humano).** Cambiar el stack requiere decisión explícita del humano; no se reabre por gusto.
- **Backend:** Python 3.12 (gestionado con `uv`) + **Django** (+ Django REST Framework para los endpoints de Dev A). El motor y los scripts de falsación siguen siendo Python puro en `src/motor/` y `scripts/`, sin depender de Django; Django solo los expone. Tests con **pytest** (+ pytest-django).
- **Base de datos:** **PostgreSQL** local (usuario y contraseña en `.env`, **nunca** en el repo; `.env.example` documenta las variables). Los contratos DC-xx se materializan como schemas puros validados (M0.3); persistirlos en Postgres es una capa aparte.
- **Frontend (vitrina, Dev C):** **Next.js** (React, TypeScript) en `web/`, consumiendo la API REST. Sustituye a la propuesta anterior de FastAPI.
- **Reglas de arquitectura:** el dominio (`src/`) no importa Django ni Next; las dependencias van hacia dentro (superficies → fábrica → motor → libro → ingesta no se invierte, ver mandamiento 1). `sysmap check` y `pytest` en verde antes de cada commit.
- **Semillas públicas del proyecto: 20261113 · 20261114 · 20261115 · 20261111 · 20261112.** Toda corrida es reproducible: usa estas semillas y las imprime en su salida. Sin semilla pública, no hay fila nueva (regla de dependencia 4 de DOC-01).

## 3 · Los 3 mandamientos (reglas que el código jamás rompe)

1. **Nada lee directo de los sensores.** Todo consumidor lee del libro contable LB-1 (DC-04) o de los contratos de eventos. Flujo unidireccional: Ingesta → Libro → Motor → Fábrica → Superficies. Ningún módulo escribe hacia atrás (salvo recalibración de MO-1 vía GO-1).
2. **Nada se prueba sin preregistro hasheado ANTES de correr (GO-2).** El acta (pregunta, regla de éxito, regla de muerte, semillas) se hashea SHA-256 antes de ejecutar; el hash queda en `docs/actas/` y en la alarma (DC-05). Si el diseño se escribió después del resultado, no es ciencia y no va al pitch.
3. **Colores solo con regla contestable.** Toda alarma lleva recibo completo (DC-05): regla exacta imprimible, semilla, hash de preregistro; si la regla no se cumple, la alarma se retira sola. Banner **REAL/SIMULADO** obligatorio en todo registro y en toda pantalla. El verde sin recibo no aparece.

Esquema (convención general): `persona_id` siempre pseudónimo; timestamps ISO 8601 UTC; unidades en el nombre del campo de `parametros`; **el contenido individual jamás cruza a las superficies de decisión** (solo agregados y estados).

**Herencia de banner (DOC-01 v0.2.1):** el banner de un registro derivado se computa trazando a sus fuentes de ingesta; si alguna entrada es SIMULADO, el derivado muestra SIMULADO; jamás se asciende a REAL en silencio. Ingesta: registra todo (sin umbrales); el detector califica con su recibo.

## 4 · Contratos de datos DC-01…DC-13 — NO se improvisan

Detalle campo a campo: **DOC-01 §3** (única fuente). Resumen operativo:

| Contrato | Es | Campos que no pueden faltar |
|---|---|---|
| DC-01 | Canal A — sensores automáticos | persona_id, ts_utc, indicador, valor, unidad, `incertidumbre_sensor`, calidad (ok/sospechoso/**ausente** — la ausencia es dato), fuente, banner |
| DC-02 | Canal B — autorreporte 3 toques | tipo (ánimo/síntoma), escala declarada, `duracion_respuesta_s`, `registro_ausencia` |
| DC-03 | Canal C — eventos con firma física | tipo (tormenta_solar/**lectura_clima_espacial**/eva/eclss/inyeccion_escenario/brote_simulado), fuente (swpc/donki/osdr/simulador), parametros con unidades, `hash_lectura_cruda`, `banner` (v0.2.1) |
| DC-04 | Libro GPV — los 9 presupuestos (contrato central) | dia_habitat, presupuesto_id (aire/agua/energia/dosis/ritmo/carga/inmunidad/conducta/tiempo), sujeto, `emision_esperada`, **`incertidumbre_del_manifiesto` (el piso de detección)**, emision_observada, `residuo_contable`, fuente_linea, `estado_linea` (limpio/sospechoso/cuarentena — desde v0.2) |
| DC-05 | Alarma con recibo | presupuesto_id, detector (dos_sigma/cusum + sentido), umbral, valor_cruzado, `regla_exacta` (texto ejecutable), `semilla`, `hash_preregistro`, estado (activa/retirada/apelada) |
| DC-06 | Stream de residuo | observado, predicho, residuo, sigma_efectiva, cusum_acumulado, bandera (normal/sorpresa/deriva) |
| DC-07 | Cápsula exportable | hipotesis, prueba_protocolo, preregistro (hash+semilla), numeros, senal_refutadora, veredicto, **limites (obligatorio: sin límites no exporta)**, mapa_frontera |
| DC-08 | Cierre de conservación — El Contrapeso (MO-6) | bucle (agua/aire/energia), entradas, salidas, delta_almacen, `perdida_declarada`, residuo_conservacion, incertidumbre_propagada, veredicto (**CIERRA / NO CIERRA**) |
| DC-09 | Forma diaria del hábitat (MO-7) | curva (potencia/agua/aire), fase_valle_local, amplitud_relativa, residuo_forma, covariables |
| DC-10 | Casos de error y contagio — sistema inmune (GO-6) | nodo_origen, clase_error, descendientes, estado (abierto/en_cuarentena/cerrado/corregido_estructural), r0_fuente, brote |
| DC-11 | Ficha de vida de sensor (MO-8) | clase_sensor, calibraciones[], edad_dias, **`hazard_dia` (Weibull por clase)**, sigma_manifiesto_recomendada, estado (vivo/convaleciente/muerto) |
| DC-12 | Contrato de Fundición — la tarjeta del lab | tarjeta_id, par_variables, **mecanismo (ref biblioteca FA — obligatorio)**, prediccion falsable, senal_refutadora, `fuentes[]` (accesión OSDR/DOI/lote con semilla — **sin fuente cargada la tarjeta no existe**), precio {datos, cómputo, días}, valor_si_cierta (detectores DC-xx nuevos), estado (vivero/en_prueba/refutada/sostenida/sin_datos), preregistro_hash, vencimiento |
| DC-13 | Registro de intento de ingesta (v0.2.2) | intento_id, ts_utc, fuente, url, `resultado` (ok/fallo/vacio), http_status, `hash_lectura_cruda` (solo ok), `error` (solo fallo), `banner` |

## 5 · Estado real de los módulos (qué ya existe como script y qué no)

Fuente: DOC-01 §2. Al materializar al repo, respeta estos estados — no reconstruyas lo que existe ni asumas código que no existe.

| Módulo | Qué es | Estado |
|---|---|---|
| IN-3 | SWPC/DONKI/OSDR en vivo | OPERATIVO (SWPC, sin API key; verificado Kp=3,33 el 9-nov) / ESPECIFICADO (OSDR) |
| IN-4 | Banco de Falsaciones: replay, Monte Carlo, premortem, **modo adversario** | OPERATIVO (script) |
| MO-1 / MO-2 / MO-3 | Modelo nulo personal / residuo 2σ / CUSUM bilateral | OPERATIVO (script; FB-001, FB-002 ya ejecutadas) |
| LB-1 | Libro GPV de los 9 presupuestos | ESPECIFICADO — **P0, antes que detectores nuevos** |
| MO-6 | El Contrapeso (cierre de conservación → DC-08) | DISEÑADO — FB-005 preregistrada |
| MO-4 / MO-5 | Triangulación 3 testigos / integrador lento del agua | DISEÑADO — FB-003 / FB-004 programadas |
| MO-7 / MO-8 | Forma diaria del hábitat / demografía de testigos | DISEÑADO — FB-006 / FB-008 preregistradas |
| FA-1 / FA-2 / FA-3 | Kanban H-cards / N-of-1 A-B-A-B / cápsula | ESPECIFICADO |
| FA-4 | El Faro (predicciones fechadas, calificadas en público) | DISEÑADO |
| SU-1…SU-4 | Alertas con recibo, tablero, sello semanal, premortems | ESPECIFICADO / DISEÑADO |
| SU-5 | Frontend: las 6 pantallas | NO INICIADO |
| GO-2 | Preregistro con hash SHA-256 | OPERATIVO (manual) |
| GO-6 / GO-7 | Epidemiología del error / MODO FRONTERA | DISEÑADO (FB-007) / Declarado |

## 6 · Mapa de documentos (leer bajo demanda — no leer todo en cada sesión)

| Si vas a tocar… | Abre primero… |
|---|---|
| Motor, detectores, cualquier contrato DC-xx | `docs/DOC-01_MAP-S1-mapa-maestro-sistema-v0.2.md` §2–§3 |
| Falsaciones FB-001…FB-008 y preregistros | `docs/DOC-02_MAP-S2-genesis-nueva-generacion-v0.3.md` Apéndice B + `docs/actas/` |
| Anclas científicas C-1…C-23 | DOC-02 Apéndice C |
| Pantallas, demo, reparto Dev A/B/C, banco del jurado | `docs/DOC-03_TONO-pitch-equipo-v0.2.md` §2, §5, §6 |
| LA FUNDICIÓN: contrato E/S del lab, ideas, compromisos | `docs/DOC-04_LA-FUNDICION-laboratorio-v0.2.md` §2, §4, §9 |
| Familias de hipótesis FM-1…FM-10 y bestiario | DOC-01 §6 + `docs/inventario-maestro-bestiario.md` (K-1/K-2) |
| Escala honesta vs NASA (T1-T4) | `docs/radar-nasa.md` |
| Convención de numeración y reglas de versionado | `docs/README.md` (DOC-00) |

## 7 · Distribución del repositorio (DOC-01 §1)

```
scripts/          falsaciones y motor en modo script (ya existe; p. ej. falsacion_d4_creo_ocio.py)
src/ingesta/      IN-1..IN-4
src/libro/        LB-1 + schema de DC-04
src/motor/        MO-1..MO-8
src/fabrica/      FA-1..FA-4
src/superficies/  SU-1..SU-5
docs/             los DOC-NN oficiales + bestiario + radar (fuente, no se edita desde el código)
docs/actas/       actas FB-xxx y fichas de preregistro (GO-2)
data/             fixtures, extractos OS-892, fichas de verdad, salidas de corridas
```

## 8 · Protocolo de sesión (obligatorio, en este orden)

1. **Lee `TASKS.md` completo.** Trabaja UN ítem abierto: el de menor número que no esté bloqueado.
2. Abre las referencias del §6 que correspondan al ítem. **No cites números de memoria: ábrelos.**
3. Implementa con test (pytest) y fixture real. Si la tarea no admite test, justifícalo en el commit.
4. Nunca marques un ítem como hecho sin evidencia: tests que pasan + hash del commit, escritos en la línea del ítem.
5. Si el humano pide algo que no está en TASKS.md: **primero añade la fila** (al final de su bloque, con prioridad), luego implementa. Nada vive fuera de la cola.
6. No edites `docs/DOC-*.md` salvo que el humano lo pida explícitamente: el código implementa los docs; los docs no se reescriben desde el código.
7. Antes de terminar la sesión: pytest completo en verde, `git commit` por ítem, TASKS.md actualizado. Un test rojo = sesión no terminada.

## 9 · Definición de hecho (las 4 puertas que pasa toda tarea)

1. Tests verdes con fixture real — **prohibido fake data**: si el dato no existe, el ítem se declara bloqueado, no se simula la felicidad.
2. Sin TODO, sin stub, sin placeholder en el diff.
3. TASKS.md actualizado con evidencia (tests + hash de commit).
4. Si tocaste un contrato DC-xx o una regla de los 3 mandamientos: detente y avisa — es un cambio de versión de DOC-01, no un refactor.

## 10 · Compromisos del submit (el norte; no negociable)

Detalle completo: DOC-04 §9 y DOC-03 §8–§9. Resumen:

- **FB-002 reproducible: 10/10 detecciones, preaviso mediano 21 días** (semillas 20261113/14/15) — test de regresión permanente.
- **LB-1 + El Contrapeso** (cierre de conservación agua/aire/energía) — P0 no negociable.
- **FB-003 y FB-005 ejecutadas con hash publicado ANTES de correr**; demo kill en dos columnas (detector contra manifiesto: ciego / detector contra ley: alarma).
- **LA SALA + EL RESIDUO vivos**; LA TORMENTA con SWPC en vivo.
- **≥5 tarjetas DC-12 acuñadas** (techo: 10) desde K-2 + OS-892, cada una con fuente con identificador y hash antes de probar; **1 predicción del Faro fechada**; **1 escape del Adversario documentado**. Si el tiempo aprieta, el corte es 5 — el lab no infla.

## 11 · Herramientas de contexto (graphify · obsidian · sysmap)

- **graphify** — grafo de la *documentación* (DOC-01…04, CLAUDE.md, TASKS.md). Antes de abrir un DOC entero, consulta `graphify query "<pregunta>"` y abre solo la sección que señale. Salida en `graphify-out/` (no se edita a mano; se regenera con `/graphify . --update`).
- **obsidian** — visor del grafo/vault (`/graphify . --obsidian`); solo lectura humana, no es fuente de verdad.
- **sysmap** (`~/Documentos/sysmap`, comando `sysmap`) — mapa del *código* sacado del propio código. **Antes de codear o tocar un archivo existente**: `sysmap archivo <ruta>`, `sysmap depende <ruta>`, `sysmap impact <ruta>`; antes de cerrar la sesión: `sysmap cierre`. Si avisa de algo (ciclo, trinquete, punto débil), se informa al humano antes de seguir. Cuando exista git y código (M0.2), correr `sysmap empezar` **una vez** (instala ganchos de git y de Claude) — solo con permiso del humano.
- Estas herramientas son contexto, no fuente: ante conflicto manda DOC-01. No sustituyen la regla de oro (§0): para citar un número o contrato, abrir el DOC.
- Stack cerrado en §2 (Django + PostgreSQL + Next.js). sysmap entiende los tres.

## 12 · Política de datos (decisión del humano, 2026-11-15)

Detalle y registros: `docs/politica-de-datos.md`. Resumen: **nada simulado sin etiqueta, nada inventado.** Todo dato real con fuente identificable; si no está en los enlaces NASA/CSA (`docs/recursos-nasa.md`) se buscan papers o datos abiertos y se anotan. Sin dato real el ítem se declara bloqueado. Todo lo simulado/inventado lleva banner `SIMULADO` y una fila en el registro §3 de ese documento; lo que no esté ahí no se escribe: detenerse y avisar.

## 13 · Canal de propuestas de Claude

- Al cerrar cada sesión Claude puede escribir **máximo 2 propuestas** en `docs/propuestas.md` con el formato de DOC-01 §7 (ID, mejora, UNA capa destino, qué compra, ancla verificada, costo, prueba si es claim). Estado inicial: PROPUESTA.
- Nada se implementa en la misma sesión ni salta la cola. El humano acepta o rechaza por escrito; el rechazo también se registra.
- Huecos que Claude vea durante la sesión se señalan y su solución entra como propuesta, nunca como código fuera de la cola.

## 14 · Alcance congelado (decisión del humano, 2026-11-15)

Hasta cerrar **M2.8** (evaluación preregistrada sobre datos reales) **no se añaden módulos nuevos**. Prioridad: LB-1, MO-6 (El Contrapeso, = conciliación de datos aplicada a un hábitat tripulado), MO-1…MO-3 y GO-2. LA FUNDICIÓN queda en segundo plano salvo tarjetas con fuente real. Las ideas nuevas entran por `docs/propuestas.md`, no por código. Registro de decisiones: `docs/decisiones.md`. Parámetros públicos de la simulación: `docs/parametros-publicos.md`.

## 15 · Norte científico (decisión del humano, 2026-11-15)

Objetivo: un proyecto de **nivel de avance científico** — «un pequeño paso para el hombre, un gran salto para la humanidad». Traducido a reglas: toda afirmación **preregistrada con hash antes de correr**, **reproducible** (semillas públicas), con **datos reales** o **simulación etiquetada**, **límites declarados primero**, y **los resultados nulos se publican**. La ejecución técnica la lidera Claude siguiendo la cola; el entregable de largo plazo es un preprint reproducible (M5.5, M5.6). Evaluación honesta de qué es común y qué es original: `docs/evaluacion-paper.md`.
