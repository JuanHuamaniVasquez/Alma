# TONO-LAB · MAP-S1 — Mapa Maestro del Sistema (v0.2.10)

> **Qué es este documento:** el contrato de ingeniería del proyecto. Define las capas del sistema, el registro oficial de módulos, los contratos de datos campo a campo, el protocolo de cambios y la cola de mejoras propuestas. Es el antídoto contra el vibe coding: nada se construye sin fila en el registro, y toda mejora futura tiene exactamente un hogar.
> **Reglas del documento:** (1) nada se codea sin su fila en el registro §2; (2) toda mejora nueva entra por el protocolo §5 y queda como PROPUESTA en §7 hasta ser aceptada; (3) los contratos §3 se versionan con el mapa — cambiar un contrato es cambiar de versión del mapa.
> **Estado:** diseño pre-hackatón (construcción grande inicia 14-nov 9:00 a.m. local). **Fecha:** 2026-11-11. **Semillas públicas del proyecto:** 20261113 · 20261114 · 20261115 · 20261111 · 20261112.
> **v0.1 → v0.2 (11-nov, aprobación del equipo):** se aplicó el parche del Apéndice A de DOC-02 (MO-6…MO-8, GO-6, DC-08…DC-11, filas de trazabilidad §6, semillas nuevas, columna `estado_linea` en DC-04) y, del mismo golpe, las adiciones aprobadas de DOC-04 · LA FUNDICIÓN (**DC-12 Contrato de Fundición, FA-4 El Faro, GO-7 MODO FRONTERA, cola M-L1…M-L5** como roadmap de frontera).
> **v0.2 → v0.2.1 (2026-11-15, decisión del humano; cambio de contrato → bump según §5):** (1) DC-03 `tipo` gana `lectura_clima_espacial` (cada lectura exitosa de SWPC entra como lectura; `tormenta_solar` queda para eventos declarados oficialmente — sin umbral en la ingesta: la ingesta registra, el detector califica) y DC-03 gana `banner`; (2) DC-01/DC-02: la ausencia admite `valor` vacío, solo en ausencia y en ambos sentidos; (3) DC-12: `preregistro_hash` obligatorio desde `en_prueba`; (4) regla de herencia de banner en derivados (convención general).
> **v0.2.1 → v0.2.2 (2026-11-15, MP-4 aceptada por el humano; cambio de contrato → bump según §5):** nuevo contrato **DC-13 · Registro de intento de ingesta** (el fallo de un feed es dato: separa «sin evento» de «no pudimos mirar»).
> **v0.2.2 → v0.2.3 (2026-11-15, decisión del humano; cambio de contrato → bump según §5):** DC-04 fija la fórmula `residuo_contable = emision_observada − emision_esperada` y la regla de cierre de línea `|residuo_contable| ≤ 2 · incertidumbre_del_manifiesto` (mismo umbral que `dos_sigma`). Es una decisión de diseño aún **sin validar con datos reales**.
> **v0.2.3 → v0.2.4 (2026-11-15, D-20; cambio de contrato → bump según §5):** DC-12 `fuentes[]` admite también **NTRS** (id de 11 dígitos) y **PMID**, además de accesión OSDR, DOI y lote. Motivo: DOC-04 §2 lista NTRS como cuerpo público con identificador y DOC-01 no lo admitía (contradicción entre documentos).
> **v0.2.4 → v0.2.5 (2026-11-15, D-30; cambio de contrato → bump según §5):** DC-05 admite `indicador` **como alternativa exclusiva** a `presupuesto_id` (mismo patrón que DC-06): las alarmas de indicadores sin presupuesto documentado (pulso, temperatura…) llevan recibo sin inventar un presupuesto. Se evaluaron y descartaron: mapear indicador→presupuesto (inventa el del pulso), un 10.º presupuesto «cuerpo» (altera el vocabulario central) y dejar esas alarmas sin recibo.
> **v0.2.5 → v0.2.6 (2026-11-15, MP-5 aceptada; cambio de contrato → bump según §5):** nuevo contrato **DC-14 · Recibo de verde** («el verde sin recibo no aparece»): un «sin anomalías» declara su efecto mínimo detectable y su potencia **condicionados a los días válidos observados**, en σ y en unidades físicas; con pocos datos el estado es `sin_datos_suficientes`. Ancla: Altman & Bland 1995, *BMJ*, doi:10.1136/bmj.311.7003.485.
> **v0.2.6 → v0.2.7 (2026-11-15, MP-14 autorizada por el humano; cambio de contrato → bump según §5):** DC-05 `detector` gana **`umbral_personal`** (regla fija contra un valor de referencia personal, p. ej. «sueño < su mediana de la línea base»). Motivo: la tarjeta DC-12 `sueno-corto-cansancio` (sostenida en FB-016 A) no puede circular como detector con solo `dos_sigma`/`cusum` (M4.5). La alarma sigue exigiendo recibo completo (`regla_exacta` ejecutable, semilla, hash de preregistro). **Límite declarado:** la regla probada en FB-016 marca ≈ la mitad de las noches; su uso es de contexto, no de alarma crítica, hasta una acta que fije un umbral más selectivo. DC-14 no cambia (el verde solo admite `dos_sigma`/`cusum`).
> **v0.2.7 → v0.2.8 (2026-11-15, MP-15 aceptada por el humano; cambio de contrato → bump según §5):** DC-05 y DC-14 ganan el detector **`f_varianza`** (razón de varianzas vigilancia/línea base de 28 días) y DC-14 gana el campo **`canal`** (`media` por defecto · `varianza`). Motivo: FB-018/FB-019 mostraron que un zigzag de la misma media escapa al CUSUM (1,8 %) y que el techo es de información: con 28 días de base F detecta el 95 % del zigzag de 2σ. El canal de varianza lleva su propio recibo: con < 28 días de base o < 14 de vigilancia es `sin_datos_suficientes`, nunca verde. Validación en datos reales: FB-020 (la regla de muerte es FPR real > 3 %).
> **v0.2.9 → v0.2.10 (2026-11-15; el humano ordenó expresamente conectar los electrones GOES y los rayos cósmicos; cambio de contrato → bump según §5):** DC-03 `tipo` gana **`lectura_electrones`** (electrones GOES ≥2 MeV, cinturones atrapados; solo de `swpc`) y **`lectura_neutrones`** (monitor de neutrones de Oulu, proxy en tierra de los rayos cósmicos galácticos; solo de `nmdb`), y DC-03/DC-13 `fuente` gana **`nmdb`** (Neutron Monitor Database, www.nmdb.eu; emite solo `lectura_neutrones`). Parámetros: `flujo_electrones_pfu`, `tasa_neutrones_cps`. La alerta ALTEF3 de NOAA SWPC marca 1 000 pfu (≥2 MeV); NMDB exige reconocimiento (texto en `src/ingesta/entorno.py::ACK_NMDB`). El monitor de neutrones es un **proxy, no una dosis**: la dosis de GCR en vuelo no se mide en ALMA.
> **v0.2.8 → v0.2.9 (2026-11-15, auditoría sesión 2; el humano ordenó expresamente editar DOC-01 y los contratos; cambio de contrato → bump según §5):** (1) DC-03 `tipo` gana **`lectura_protones`**, **`lectura_rayosx`** (GOES, vía SWPC) y **`posicion_estacion`** (ISS), y DC-03/DC-13 `fuente` gana **`wheretheiss`**: el entorno en vivo de la tripulación deja de leerse «directo» (mandamiento 1) y entra como evento con `hash_lectura_cruda`; `posicion_estacion` solo viene de `wheretheiss`, las lecturas GOES solo de `swpc`; el parámetro adimensional `luz_solar` (1 = a la luz, 0 = en sombra) se añade a los adimensionales (como `kp`). (2) DC-05 `detector` gana **`e_proceso`** (alarma anytime-valid de FB-021): su `regla_exacta` es la de `src/motor/eproceso.py` y **declara el supuesto** (la garantía P(falsa alarma) ≤ α solo vale si el residuo es s-subgaussiano; FB-021 mostró que con s = 1 el FPR real fue 5,06 %, así que el recibo lleva el `s` calibrado). **No** pasa a DC-14: no hay validación fuera de muestra (FB-021: 5 ventanas, no concluyente).

---

## §1 · Las capas del sistema y las reglas de dependencia

El proyecto no son 7 ideas en paralelo: es **una columna vertebral con 7 facetas**. El diamante es el ensamblaje, y el ensamblaje se vuelve explícito aquí.

```
CAPA 0 · INGESTA
  IN-1 Canal A (sensores automáticos del hábitat/wearables)
  IN-2 Canal B (autorreporte estructurado en 3 toques)
  IN-3 Canal C (eventos con firma física: SWPC, DONKI, OSDR, EVA)
  IN-4 Gemelo digital / Banco de Falsaciones (escenarios con física anclada)
        ↓
CAPA 1 · EL LIBRO CONTABLE (la columna vertebral)
  LB-1 Los 9 presupuestos (GPV) — el único lugar donde se cruzan cuerpo y máquina
        ↓
CAPA 2 · MOTOR DE DETECCIÓN
  MO-1 Modelo nulo personal (línea base de 14 días, priors OSDR)
  MO-2 Residuo (r = observado − predicho; sorpresa a 2σ)
  MO-3 CUSUM bilateral (deriva lenta; calibrado FPR 1% en 14 d)
  MO-4 Matriz co-deriva (triangulación planta × chip × humano — D6)
  MO-5 Integrador lento del agua (TOC/WRS como censo colectivo — D7)
  MO-6 Cierre de conservación (residuo de LEY agua/aire/energía — D8)
  MO-7 Forma diaria del hábitat (fase/amplitud colectivas — D7-β)
  MO-8 Demografía de testigos (σ del manifiesto computada por edad)
        ↓
CAPA 3 · LA FÁBRICA DE CONOCIMIENTO
  FA-1 H-cards (kanban: nacidas → en prueba → refutadas → confirmadas)
  FA-2 Experimento N-of-1 (A-B-A-B aleatorizado)
  FA-3 Cápsula exportable (veredicto empaquetado + mini-meta-análisis)
  FA-4 El Faro (predicciones fechadas del laboratorio, calificadas cuando el dato llega)
        ↓
CAPA 4 · SUPERFICIES DE DECISIÓN (lo único que la tripulación ve)
  SU-1 Alertas con recibo · SU-2 Tablero del comandante (solo agregados)
  SU-3 Sello semanal (verde/ámbar/rojo) · SU-4 Miner de premortems
  SU-5 [Futuro] Frontend: las 6 pantallas
        ↑
GOBERNANZA (transversal a todo)
  GO-1 Árbitro externo · GO-2 Preregistro con hash · GO-3 Plan médico
  GO-4 Protocolo de decisión del nombre · GO-5 Gobernanza de datos post-misión
  GO-6 Epidemiología del error · GO-7 MODO FRONTERA (divergencia programada del laboratorio)
```

### Reglas de dependencia (inviolables)

1. **Nada lee directo de los sensores.** Todo consumidor (motor, superficies, fábrica) lee del libro contable LB-1 o de los contratos de eventos. Si un módulo necesita un dato crudo, el dato entra por Capa 0 y se contabiliza en Capa 1.
2. **El flujo de conocimiento es unidireccional:** Ingesta → Libro → Motor → Fábrica → Superficies. Ningún módulo de una capa escribe hacia atrás (salvo el ciclo de calibración declarado: Superficies → contestabilidad → recalibración de MO-1, vía GO-1).
3. **Una mejora = una capa.** Si una propuesta toca dos capas, se divide en dos propuestas con dos filas.
4. **Toda prueba de una idea pasa por IN-4** (el Banco de Falsaciones, PLATA desde el 10-nov): sin semilla pública, no hay fila nueva.
5. **La privacidad es arquitectura, no capa agregada:** el contenido individual nunca cruza de Capa 3 a Capa 4 (solo agregados y estados).

### Distribución propuesta del repositorio

```
scripts/          falsaciones y motor en modo script (ya existe; p. ej. falsacion_d4_creo_ocio.py)
src/ingesta/      IN-1..IN-4
src/libro/        LB-1 + schema de DC-04
src/motor/        MO-1..MO-5
src/fabrica/      FA-1..FA-3
src/superficies/  SU-1..SU-4
docs/actas/       actas FB-xxx y fichas de preregistro (GO-2)
docs/mapas/       este documento (MAP-S1) y sus versiones
```

---

## §2 · Registro oficial de módulos

Estados de construcción: **OPERATIVO** (existe y corre) · **ESPECIFICADO** (contrato escrito, sin código) · **DISEÑADO** (concepto con frontera declarada) · **NO INICIADO**. Los tipos: CÓDIGO / PROCESO / CONTENIDO.

### Capa 0 · Ingesta

| ID | Tipo | Qué hace | Entradas | Salidas | Conexiones | Estado | Prioridad |
|---|---|---|---|---|---|---|---|
| IN-1 | CÓDIGO | Normaliza telemetría de sensores existentes | Wearables, sensores de hábitat | DC-01 | → LB-1 | ESPECIFICADO | P0 |
| IN-2 | CÓDIGO | Recoge autorreporte en 3 toques; la ausencia también es dato | Usuario (mínimo esfuerzo) | DC-02 | → LB-1 | ESPECIFICADO | P0 |
| IN-3 | CÓDIGO | Lee clima espacial y datos abiertos en vivo | NOAA SWPC (sin llave, verificado Kp=3,33 el 9-nov), NASA DONKI, OSDR | DC-03 | → IN-4, → MO-5 | OPERATIVO (SWPC) / ESPECIFICADO (OSDR) | P0 |
| IN-4 | CÓDIGO | Gemelo digital: replay histórico, Monte Carlo, modo premortem y modo adversario | DC-03, catálogos NOAA 1976–, parámetros publicados | Escenarios falsables + informes de caso | ← toda idea nueva debe pasar por aquí | OPERATIVO (script) | P0 |

### Capa 1 · Libro contable

| ID | Tipo | Qué hace | Entradas | Salidas | Conexiones | Estado | Prioridad |
|---|---|---|---|---|---|---|---|
| LB-1 | CÓDIGO | Los 9 presupuestos (aire, agua, energía, dosis, ritmo, carga, inmunidad, conducta, tiempo); el libro debe cerrar | DC-01, DC-02, DC-03 | DC-04 (residuos contables por presupuesto) | ← Capa 0; → Capa 2 y 4. **Realiza D2** | ESPECIFICADO | **P0 — antes que detectores nuevos** |

### Capa 2 · Motor de detección

| ID | Tipo | Qué hace | Entradas | Salidas | Conexiones | Estado | Prioridad |
|---|---|---|---|---|---|---|---|
| MO-1 | CÓDIGO | Modelo nulo por persona: rango normal propio, modo aprendizaje honesto | DC-04 (14 días), priors OSDR | Predicción + σ_efectiva | → MO-2. **Realiza la base de D1** | OPERATIVO (script) | P0 |
| MO-2 | CÓDIGO | Residuo diario; sorpresa a 2σ; detección sin causa | MO-1 | DC-06 (stream de residuo) | → MO-3, FA-1 | OPERATIVO (script) | P0 |
| MO-3 | CÓDIGO | CUSUM bilateral (caza lo lento en ambas direcciones; la falsación v4 obligó a bilateral) | DC-06 | DC-05 (alarmas con recibo) | → SU-1. **Realiza D1/D4** | OPERATIVO (script; FB-001, FB-002) | P0 |
| MO-4 | CÓDIGO | Matriz co-deriva: localiza la falla entre mundo/sensor/humano | DC-06 de 3 testigos (planta min, chip h–d, humano sesgado) | Diagnóstico de fuente | → FA-1. **Realiza D6** | DISEÑADO — falsación FB-003 programada ≤14-nov | P1 |
| MO-5 | CÓDIGO | Integrador lento del TOC del agua como censo colectivo del grupo | DC-04 (agua, WRS) | Confirmación lenta con retraso característico | → FA-1. **Realiza D7** | DISEÑADO — falsación FB-004 programada ≤14-nov | P1 |
| MO-6 | CÓDIGO | Cierre de conservación diaria de los bucles agua/aire/energía; residuo con unidades físicas y umbral por propagación de incertidumbre. **Realiza D8** | DC-04 (todo) | DC-08 | → MO-3, → FA-1, abre investigaciones D6 | DISEÑADO — FB-005 preregistrada (Apéndice B de DOC-02) | P1 |
| MO-7 | CÓDIGO | Fase/amplitud/residuo de forma de las curvas diarias de consumo. **Realiza el canal D7-β** | DC-04 (energia, agua, aire del hábitat), DC-03 (covariables) | DC-09 | → MO-3, → SU-2 | DISEÑADO — FB-006 preregistrada (Apéndice B de DOC-02) | P2 |
| MO-8 | CÓDIGO | Demografía de sensores: fichas de vida, curvas de supervivencia por clase, σ recomendada para el manifiesto | DC-01 (`incertidumbre_sensor`), DC-04 histórico | DC-11 + recalcula `incertidumbre_del_manifiesto` de DC-04 | → MO-1/MO-2, → MO-6, → EL PRESUPUESTO | DISEÑADO — FB-008 preregistrada (Apéndice B de DOC-02) | P2 |

### Capa 3 · Fábrica

| ID | Tipo | Qué hace | Entradas | Salidas | Conexiones | Estado | Prioridad |
|---|---|---|---|---|---|---|---|
| FA-1 | CÓDIGO | Kanban de H-cards (5 campos, señal refutadora ANTES de probar) | DC-05, DC-06, familias FM-1..FM-10 | Tarjetas con estado | → FA-2 | ESPECIFICADO | P2 |
| FA-2 | CÓDIGO | N-of-1 aleatorizado A-B-A-B; una intervención activa por indicador | H-card aceptada, GO-3 | Veredicto por persona | → FA-3 | ESPECIFICADO | P2 |
| FA-3 | CÓDIGO | Cápsula exportable: hipótesis, prueba, números, semillas, límites; mini-meta-análisis entre cápsulas | FA-2 | DC-07 | → red de tripulaciones. **Realiza el "biofoam"** | ESPECIFICADO | P2 |
| FA-4 | CÓDIGO | El Faro: predicciones fechadas del laboratorio, registradas ANTES del dato y calificadas en público cuando el dato llega (tasa de acierto + días de preaviso) | Tarjetas de FA-1 con predicción declarada | Predicciones con fecha límite + veredicto | → SU-2/SU-3. **El "nos adelantábamos", hecho métrica (DOC-04)** | DISEÑADO | P2 |

### Capa 4 · Superficies

| ID | Tipo | Qué hace | Entradas | Salidas | Conexiones | Estado | Prioridad |
|---|---|---|---|---|---|---|---|
| SU-1 | CÓDIGO | Alertas con recibo: regla exacta impresa, retiro automático si la regla no se cumple | DC-05 | Notificaciones contestables | ← MO-3/MO-4/MO-5 | ESPECIFICADO | P3 |
| SU-2 | CÓDIGO | Tablero del comandante: agregados del hábitat, jamás contenido individual | DC-04, DC-05 | Vista de deriva por presupuesto | ← LB-1 | ESPECIFICADO | P3 |
| SU-3 | CÓDIGO | Sello semanal verde/ámbar/rojo pintado por un tercero (regla `arbitro.proveedor ≠ operador`) | DC-04 agregado semanal + firma GO-1 | Sello legible por un niño de 12 años | ← LB-1, ← GO-1. **Realiza D5** | DISEÑADO | P3 |
| SU-4 | CÓDIGO | Miner de premortems cada 30 días: busca balances no instrumentados | Narrativas de tripulación | Sospechas → DC-03 (eventos) → LB-1 | → LB-1 (punto ciego programado) | ESPECIFICADO | P2 |
| SU-5 | CÓDIGO | Frontend: LA SALA, EL RESIDUO, LA MESA, LA TORMENTA, LA CÁPSULA, EL PRESUPUESTO | Solo contratos (§4) | Interfaz completa | ← Capa 3/4 | NO INICIADO (tras 14-nov) | P4 |

### Gobernanza (proceso — no se codea, se firma)

| ID | Tipo | Qué hace | Estado | Prioridad |
|---|---|---|---|---|
| GO-1 | PROCESO | Nombrar árbitro externo real (universidad u organismo); regla Plimsoll hecha regla | Pendiente — candidatas por definir | P2 |
| GO-2 | PROCESO | Preregistro con hash SHA-256 y sello de tiempo estilo OSF en cada acta | OPERATIVO (manual) | P1 |
| GO-3 | PROCESO | Plan médico: solo intervenciones de bajo riesgo y reversibles; una por indicador | Declarado | P2 |
| GO-4 | PROCESO | Decisión del nombre ALMA vs radiotelescopio: protocolo de 3 recibos | Pendiente (recibos sin ejecutar) | P2 |
| GO-5 | PROCESO | Gobernanza post-misión: consentimiento, anonimización, propiedad de cápsulas | Declarado como decisión pendiente | P3 |
| GO-6 | PROCESO | Epidemiología del error: caso con linaje, cuarentena de descendientes, R0 por fuente, acta de brote, publicación semanal de la tasa de autoinmunidad (falsa cuarentena) | DISEÑADO — FB-007 preregistrada (Apéndice B de DOC-02) | P1 |
| GO-7 | PROCESO | MODO FRONTERA: una sesión de divergencia del laboratorio (LA FUNDICIÓN) por cada ciclo de falsación; único output permitido: tarjetas al vivero con fuente, precio y hash | Declarado (DOC-04 §8–§9) | P3 |

### Contenido (datos curados — se mina, no se programa)

| ID | Tipo | Qué es | Estado |
|---|---|---|---|
| K-1 | CONTENIDO | Bestiario: familias de hipótesis minadas de ficción + clase real (BRONCE, andamio) | OPERATIVO |
| K-2 | CONTENIDO | Las familias de casos con ancla citada (FM-1..FM-10, ver §6; FM-10 entra como PROPUESTA con anclas C-20…C-23 de DOC-02) | OPERATIVO |
| K-3 | CONTENIDO | Semillas públicas 20261113/14/15 + 20261111/20261112 (añadidas el 11-nov) y reglas de reproducibilidad | OPERATIVO |
| K-4 | CONTENIDO | Ficha de Verdad (8 CIENCIA REAL + 3 EXTRAPOLACIÓN al cierre de v0.3) | OPERATIVO |
| K-5 | CONTENIDO | Banco de anclas citadas (~45 fuentes verificadas) | OPERATIVO |
| K-6 | CONTENIDO | Ideas dormidas (10 de 17) con razón de muerte escrita | OPERATIVO |

---

## §3 · Contratos de datos (DC-01 … DC-14)

Los contratos son la parte que NO se improvisa. Cada campo abajo es una decisión de schema. Convención: timestamps en ISO 8601 UTC; `persona_id` siempre pseudónimo; todo registro de simulación lleva banner REAL/SIMULADO. **Herencia de banner (v0.2.1):** un registro derivado no declara banner: lo hereda trazando a sus fuentes de ingesta (DC-01/02/03); si alguna entrada es SIMULADO, el derivado muestra SIMULADO — jamás se asciende a REAL en silencio.

### DC-01 · Canal A — sensores automáticos

| Campo | Tipo | Nota |
|---|---|---|
| `persona_id` | string (pseudónimo) | Nunca identidad real en el flujo |
| `ts_utc` | ISO 8601 | |
| `indicador` | enum: presión · fc · glucosa · temperatura · sueño | Los oficiales del reto (ánimo vive en DC-02) |
| `valor` | float | `null` solo si `calidad = ausente` (y viceversa): la ausencia es dato |
| `unidad` | string | |
| `incertidumbre_sensor` | float (σ) | La incertidumbre viaja con el dato, no se supone después; `null` solo si `calidad = ausente` |
| `calidad` | enum: ok · sospechoso · ausente | **La ausencia es dato** (MNAR); una medición faltante se registra, no se ignora |
| `fuente` | string (device_id) | Para cruzamientos de cordura entre sensores |
| `banner` | enum: REAL · SIMULADO | Obligatorio en todo registro |

### DC-02 · Canal B — autorreporte en 3 toques

| Campo | Tipo | Nota |
|---|---|---|
| `persona_id`, `ts_utc`, `banner` | — | Igual que DC-01 |
| `tipo` | enum: ánimo · síntoma | Se **declara**, no se mide — como en medicina real |
| `escala` | string | Declarada por tarjeta (p. ej. Likert 1–5) |
| `valor` | int | `null` solo si `registro_ausencia = true` (y viceversa) |
| `duracion_respuesta_s` | float | Metadato: el tiempo de respuesta es señal, el contenido nunca; `null` si `registro_ausencia = true` |
| `registro_ausencia` | bool | Si nadie respondió en la ventana, el faltante entra como dato |

### DC-03 · Canal C — eventos con firma física

| Campo | Tipo | Nota |
|---|---|---|
| `evento_id`, `ts_utc_inicio`, `ts_utc_fin` | — | |
| `tipo` | enum: tormenta_solar · lectura_clima_espacial · lectura_protones · lectura_rayosx · posicion_estacion · lectura_electrones · lectura_neutrones · eva · eclss · inyeccion_escenario · brote_simulado | `lectura_clima_espacial` = lectura continua de SWPC/DONKI (v0.2.1); `tormenta_solar` solo para eventos declarados oficialmente (alerts.json / DONKI) |
| `fuente` | enum: swpc · donki · osdr · wheretheiss · nmdb · simulador | SWPC sin llave ni registro; `wheretheiss` = posición derivada de elementos orbitales (v0.2.9); `nmdb` = monitor de neutrones (v0.2.10) |
| `parametros` | dict (kp, flujo_protones, dosis, …) | Unidades obligatorias en el nombre del campo |
| `hash_lectura_cruda` | SHA-256 | La lectura cruda es auditable sin guardar todo |
| `banner` | enum: REAL · SIMULADO | Obligatorio (v0.2.1); fuente swpc/donki/osdr ⇒ REAL; fuente simulador ⇒ SIMULADO |

### DC-04 · Libro GPV — los 9 presupuestos (el contrato central)

| Campo | Tipo | Nota |
|---|---|---|
| `dia_habitat` | int | El día contable |
| `presupuesto_id` | enum: aire · agua · energia · dosis · ritmo · carga · inmunidad · conducta · tiempo | El vocabulario común |
| `sujeto` | persona_id · hábitat | Cuerpo o máquina; mismo libro |
| `emision_esperada` | float | El manifiesto: lo que creemos que emite/consume |
| `incertidumbre_del_manifiesto` | float (σ) | **La columna que fija el piso de detección** (hallazgo v4): no el sensor, el manifiesto |
| `emision_observada` | float | |
| `residuo_contable` | float | `emision_observada − emision_esperada` (v0.2.3). Si el libro no cierra, hay una pregunta que hacer |
| `fuente_linea` | ref DC-01/02/03 | Trazabilidad de cada entrada |

> **Columna añadida en v0.2 (P10, GO-6):** `estado_linea` (enum: limpio · sospechoso · cuarentena) — el estado sanitario del dato viaja con la línea; un error detectado marca a sus descendientes sin borrar nada.

### DC-05 · Evento de alarma con recibo

| Campo | Tipo | Nota |
|---|---|---|
| `alarma_id`, `ts_utc` | — | |
| `presupuesto_id` / `indicador` | enum (como DC-04) / enum (como DC-06) | **Exactamente uno** (v0.2.5): presupuesto si tiene presupuesto documentado; si no, indicador |
| `detector` | enum: dos_sigma · cusum · umbral_personal · f_varianza · e_proceso | Y el sentido (alza/caída — bilateral obligatorio) |
| `umbral`, `valor_cruzado` | float | |
| `regla_exacta` | texto ejecutable | Si la regla no se cumple, la alarma se retira sola |
| `semilla` | int | La semilla que reproduce la corrida |
| `hash_preregistro` | SHA-256 | Enlace a GO-2 |
| `estado` | enum: activa · retirada · apelada | Contestabilidad incluida en el contrato |

### DC-06 · Stream de residuo (lo que mira EL RESIDUO)

| Campo | Tipo | Nota |
|---|---|---|
| `sujeto`, `ts_utc`, `indicador`/`presupuesto_id` | — | |
| `observado`, `predicho`, `residuo`, `sigma_efectiva` | float | |
| `cusum_acumulado` | float | |
| `bandas` | par de floats (opcional) | Si MP-1 (predicción conformal) se acepta, aquí viven las bandas calibradas |
| `bandera` | enum: normal · sorpresa · deriva | |

### DC-07 · Cápsula exportable

| Campo | Tipo | Nota |
|---|---|---|
| `version`, `banner` | — | |
| `hipotesis`, `prueba_protocolo` | texto | Con el diseño A-B-A-B declarado |
| `preregistro` | hash + semilla | Antes de mirar datos |
| `numeros` | dict | Resultado completo, sin redacción publicitaria |
| `senal_refutadora` | texto | Escrita antes; viaja con el veredicto |
| `veredicto`, `limites` | texto | Los límites son obligatorios: sin frontera, no hay cápsula |
| `mapa_frontera` | dict (γ, τ) | Cuando aplique (p. ej. D4) |
| `empaquetado` | ref MP-4 | RO-Crate si se acepta la propuesta |
| `gobernanza` | ref GO-5 | Consentimiento/anonimización declarados |

### DC-08 · Cierre de conservación — lo que mira el Contrapeso (MO-6, D8)

| Campo | Tipo | Nota |
|---|---|---|
| `dia_habitat` | int | El día contable |
| `bucle` | enum: agua · aire · energia | Un cierre por bucle y día |
| `entradas` | float (kg / kWh) | Suma contabilizada del lado entrada |
| `salidas` | float | Suma contabilizada del lado salida |
| `delta_almacen` | float | Cambio de tanque/batería/atmósfera |
| `perdida_declarada` | float | Fuga o venteo declarado (si no está declarado, no existe) |
| `residuo_conservacion` | float | entradas − salidas − Δalmacén − pérdida declarada |
| `incertidumbre_propagada` | float (σ) | Propagación de `incertidumbre_del_manifiesto` de las líneas implicadas |
| `veredicto` | enum: CIERRA · NO CIERRA | `NO CIERRA` abre investigación D6 el mismo día |
| `banner` | enum: REAL · SIMULADO | Obligatorio |

### DC-09 · Forma diaria del hábitat — lo que mira El Hábitat Sueña (MO-7, D7-β)

| Campo | Tipo | Nota |
|---|---|---|
| `dia_habitat`, `banner` | — | Convención general |
| `curva` | enum: potencia · agua · aire | Tres formas por día |
| `fase_valle_local` | hh:mm UTC | Hora del valle colectivo (la "noche" del hábitat) |
| `amplitud_relativa` | float | Razón pico/valle del día |
| `residuo_forma` | float (σ) | Contra la ventana de calibración |
| `covariables` | ref DC-03 | Eventos que explican desviaciones benignas (acoplamiento, EVA, ops) |

### DC-10 · Casos de error y contagio — lo que mira el Sistema Inmune (GO-6)

| Campo | Tipo | Nota |
|---|---|---|
| `caso_id`, `ts_utc_deteccion` | — | |
| `nodo_origen` | ref DC-01/02/03/04 | Dónde nació el error |
| `clase_error` | enum: faltante · timestamp · unidad · sensor_muerto · duplicado | El bestiario mínimo de errores |
| `descendientes` | lista de refs de línea | Las líneas que consumieron el dato corrupto |
| `estado` | enum: abierto · en_cuarentena · cerrado · corregido_estructural | "Corregido estructural" = inmunidad adquirida |
| `r0_fuente` | float | Media de líneas corruptas por fallo de esa fuente |
| `brote` | bool (+ k declarado) | Caso con >k descendientes → acta GO-6 automática |

### DC-11 · Ficha de vida de sensor — lo que mira la Demografía de los Testigos (MO-8)

| Campo | Tipo | Nota |
|---|---|---|
| `device_id`, `clase_sensor` | — | La clase define la curva de supervivencia |
| `nacimiento` | ts_utc | Primera línea del instrumento en el libro |
| `calibraciones[]` | lista de ts_utc | Vacía o vencida = hazard sube |
| `edad_dias`, `dias_desde_calibracion` | int | |
| `hazard_dia` | float | Probabilidad instantánea de fallo (Weibull ajustada por clase) |
| `sigma_manifiesto_recomendada` | float (σ) | Lo que alimenta `incertidumbre_del_manifiesto` de DC-04 |
| `estado` | enum: vivo · convaleciente · muerto | Muerto = el presupuesto pierde testigo y su σ se ensancha |

### DC-12 · Contrato de Fundición — el contrato del laboratorio (FA-1/FA-4, LA FUNDICIÓN)

| Campo | Tipo | Nota |
|---|---|---|
| `tarjeta_id` | uuid | Toda tarjeta vive o muere con este id |
| `par_variables` | ref × ref | Señal del cuerpo × señal (cuerpo/hábitat/relato) |
| `mecanismo` | ref biblioteca FA | Obligatorio; "correlación sin mecanismo" no pasa la puerta |
| `prediccion` | texto falsable | Qué debería observarse, cuándo, con qué tamaño de efecto mínimo |
| `senal_refutadora` | texto | Escrita antes de probar (heredada de las H-cards) |
| `fuentes[]` | lista de ids externos | Accesión OSDR / DOI / NTRS / PMID / lote con semilla (v0.2.4). **Sin fuente cargada, la tarjeta no existe** |
| `precio` | {datos, cómputo, días} | Incluye costo de instrumento vía DC-11 |
| `valor_si_cierta` | detector(es) DC-xx nuevos | El único modo de pagar renta |
| `estado` | enum: vivero · en_prueba · refutada · sostenida · sin_datos | Tres veredictos honestos + dos estados de trabajo |
| `preregistro_hash` | SHA-256 | Antes de ejecutar (GO-2). Obligatorio desde `en_prueba` (v0.2.1); opcional en `vivero` |
| `vencimiento` | ts_utc (opcional) | M-L3: preguntas perecederas |


### DC-13 · Registro de intento de ingesta — la ausencia del feed es dato (IN-3, v0.2.2)

| Campo | Tipo | Nota |
|---|---|---|
| `intento_id`, `ts_utc` | — | Un registro por cada intento de leer una fuente externa, también el fallido |
| `fuente` | enum: swpc · donki · osdr · wheretheiss · nmdb · simulador | Igual que DC-03 |
| `url` | string (http/https) | Qué se intentó leer |
| `resultado` | enum: ok · fallo · vacio | `vacio` = respondió 2xx pero sin registros |
| `http_status` | int \| null | `null` si no hubo respuesta HTTP (red caída). `ok` y `vacio` exigen 2xx |
| `hash_lectura_cruda` | SHA-256 | **Solo si `ok`**: apunta a la lectura archivada (`data/lecturas/`) |
| `error` | texto | **Solo si `fallo`**: la causa, nunca omitida |
| `banner` | enum: REAL · SIMULADO | Obligatorio; fuente swpc/donki/osdr ⇒ REAL; simulador ⇒ SIMULADO |


### DC-14 · Recibo de verde — «sin anomalías» + lo que el detector habría visto (MO-3, v0.2.6)

| Campo | Tipo | Nota |
|---|---|---|
| `recibo_id`, `ts_utc`, `sujeto` | — | `ts_utc` = fin de la ventana |
| `presupuesto_id` / `indicador` | enum (como DC-04) / enum (como DC-06) | **Exactamente uno**, igual que DC-05 |
| `canal` | enum: media · varianza | v0.2.8 (MP-15): por defecto `media`; el canal de varianza exige ≥ 28 días de línea base y 14 de vigilancia |
| `estado` | enum: verde · sin_datos_suficientes · retirado | `sin_datos_suficientes` no declara nada; `retirado` = la regla alarmó al reevaluar con datos corregidos |
| `ventana_dias`, `dias_validos` | int | La **cobertura** viaja con el recibo (la ausencia es dato) |
| `detector` | enum: dos_sigma · cusum · f_varianza | `f_varianza` solo con `canal = varianza` |
| `k`, `h` | float | Parámetros del CUSUM; `h` calibrado, no artesanal |
| `potencia_declarada` | float (0–1) | Solo si `verde` |
| `mde_sigma` | float (σ) | Efecto mínimo detectable con esa potencia **dados los `dias_validos`**; solo si `verde` |
| `mde_fisico` | float | `mde_sigma` × σ_efectiva, en la `unidad` del indicador; solo si `verde` |
| `unidad` | string | min, lpm… |
| `supuesto` | texto | Supuesto estadístico declarado (p. ej. ruido independiente; tabla simulada) |
| `regla_exacta` | texto ejecutable | Verde ⇔ la regla NO alarma sobre los datos de la ventana |
| `semilla`, `hash_preregistro` | int, SHA-256 | Recibo completo, como DC-05 |
| `banner` | enum: REAL · SIMULADO | Obligatorio |

---

## §4 · Mapeo pantalla → contrato (el frontend futuro no toca el motor)

| Pantalla | Qué muestra | Consume | Regla dura |
|---|---|---|---|
| LA SALA | El hábitat como paciente: siluetas + anillo de presupuestos | DC-04 (agregados) + DC-05 (activas) + DC-08 (CIERRA/NO CIERRA agregado) | Jamás contenido individual |
| EL RESIDUO | Corriente observado/predicho; nacimiento de H-cards | DC-06 | Banner REAL/SIMULADO visible |
| LA MESA | Kanban de la fábrica (4 columnas) | Estado de FA-1 | La tarjeta muestra su señal refutadora |
| LA TORMENTA | Motor de escenarios + informe de caso | IN-4 + DC-03 | Banner UNIVERSO SIMULADO — DÍA N |
| LA CÁPSULA | Exportación de veredictos | DC-07 | Sin límites declarados, no exporta |
| EL PRESUPUESTO | Libros que deben cerrar (metabolismo de la nave) + readout del piso de detección (σ del manifiesto, computada por MO-8) | DC-04, DC-08 | Cuentas, no gráficas de personas |
| (Sello semanal) | Verde/ámbar/rojo | DC-04 agregado + firma GO-1 | `arbitro.proveedor ≠ operador` |

---

## §5 · Protocolo de cambios (dónde cae cada mejora futura)

**Cómo se propone una mejora:** (1) escribir la fila PROPUESTA en §7 con ancla verificable y, si es un claim, su prueba y señal refutadora; (2) clasificarla en exactamente una capa; (3) solo entonces codear. El registro decide la aceptación, no la conversación.

| Tipo de cambio | Capa destino | Qué se exige antes de codear |
|---|---|---|
| Nueva fuente de datos | Capa 0 | Adaptador + extensión de contrato (nueva versión de DC) |
| Nuevo indicador | DC-01/DC-04 + MO-1 | Prior de población (OSDR) + incertidumbre declarada |
| Nueva matemática de detección | Capa 2 | Falsación en IN-4 con semilla pública, ANTES de integrar |
| Nueva familia de hipótesis | K-2 / FA-1 | H-card completa con ancla citada y señal refutadora |
| Nueva pantalla o vista | Capa 4 | Que consuma contratos existentes; si exige datos nuevos, es además una fila de Capa 0–2 |
| Nueva regla ética o de gobernanza | GO-x | Redacción falsable + precedente citado (estilo Plimsoll) |
| Cambio de contrato DC-x | Este mapa | Bump de versión del mapa + fila en trazabilidad §6 |

**Regla de oro:** una mejora = una capa. Si toca dos, se divide en dos propuestas.

---

## §6 · Trazabilidad idea ↔ módulos ↔ actas ↔ semillas

| Idea | Módulos que la realizan | Contratos | Acta de falsación | Semillas | Escala hoy |
|---|---|---|---|---|---|
| D1 Residuo personal | MO-1, MO-2, MO-3 | DC-04, DC-05, DC-06 | FB-001 (24 h; sin calibrar 144 h) | 20261113 | T2 |
| D2 Los 9 presupuestos | LB-1 | DC-04 | Usa FB-001/002 como demostración | — | T2 (spec abierta) |
| D3 Árbitro externo | GO-1 (+hash en GO-2) | DC-05 (`hash_preregistro`) | — (es decisión, no experimento) | — | T1 |
| D4 Presupuesto de tiempo | MO-3 sobre presupuesto `tiempo` | DC-04, DC-05 | FB-002 (10/10; preaviso mediano 21 d) | 20261113/14/15 | T2 |
| D5 Sello visible | SU-3 | DC-04 + firma GO-1 | — (pendiente árbitro y prototipo) | — | T1 |
| D6 Triangulación | MO-4 | DC-06 (3 testigos) | FB-003 programada ≤14-nov | por fijar | T1 |
| D7 Señal colectiva | MO-5 | DC-04 (agua) | FB-004 programada ≤14-nov | por fijar | T1 (la más frágil; declarada) |
| D8 El Contrapeso | MO-6 | DC-08 | FB-005 (preregistrada) | 20261113/14/15 | T1→T2 al ejecutar (DISEÑADO) |
| D7-β canal temporal | MO-7 | DC-09 | FB-006 (preregistrada) | 20261112 | T1 (DISEÑADO) |
| IN-3 lectura continua clima espacial | IN-3 | DC-03 (`lectura_clima_espacial`) | — (ingesta, no experimento) | — | T3 (datos reales en vivo) |
| MP-4 registro de intentos de ingesta | IN-3 | DC-13 | — (ingesta, no experimento) | — | T3 (la ausencia del feed es dato) |
| LB-1 regla de cierre del libro (residuo = observada − esperada; cierra si \|r\| ≤ 2σ) | LB-1 | DC-04 | — (decisión de diseño; se falsa con FB-005 y datos reales) | — | T1 (sin validar) |
| MP-5 verde con potencia | MO-3 | DC-14 | FB-011 (preregistrada antes de correr) | 20261113 | T2 (en silicio y contrastado en datos reales de LifeSnaps, no astronautas) |

Familias de casos (contenido para FA-1): FM-1 emisor no contabilizado · FM-2 ventana de estrés viral · FM-3 sueño×hueso (reanclada con Swanson 2017/2018 — C-18/C-19) · FM-4 ventana post-EVA · FM-5 CO₂→cefalea (calibración) · FM-6 ejercicio×IL-6 · FM-7 jardín como tripulante · FM-8 farmacia como sensor · FM-9 disforia de segunda mitad · FM-10 el síndrome Pandorum (PROPUESTA — anclas C-20…C-23 de DOC-02: cascada sueño → ocio → farmacia → conducta, sin leer jamás contenido).

**Criterio de victoria T3 (recordatorio):** que una persona ajena, con las mismas semillas y datos públicos, replique nuestros residuos. Los contratos §3 son la condición técnica para que eso sea posible — por eso existen.

---

## §7 · Cola de mejoras propuestas (estado: PROPUESTA — ninguna aceptada todavía)

Cada fila sigue el protocolo §5: una capa destino, ancla verificada, prueba cuando es un claim. **Nada de esto entra al build hasta que el registro la acepte.**

| ID | Mejora | Destino | Qué compra (concreto) | Ancla verificada | Costo | Prueba si es claim |
|---|---|---|---|---|---|---|
| MP-1 | **Predicción conformal** para la línea base personal: reemplazar σ asumida por bandas con garantía de cobertura, válidas para series temporales no intercambiables | MO-1/MO-2 (campo `bandas` de DC-06) | Responde con estadística la pregunta "¿de dónde sale σ?" — falsas alarmas calibradas por garantía, no por suposición | Angelopoulos & Bates 2021 (arXiv:2107.07511, ~4.300 citas); review de conformal para series temporales 2025 (arXiv:2511.13608) | Medio | En silicio, 1 día: comparar FPR y latencia de detección con σ fija vs bandas conformales en FB-001/002 |
| MP-2 | **BOCPD** (detección bayesiana online de cambios): tercera constante de tiempo — probabilidad de "cambio aquí y ahora" con distribución de run-length | MO-3 | Complementa 2σ (agudo) y CUSUM (lento) con el tercero: el cambio estructural; útil ante deriva de régimen (inicio de invierno antártico, cambio de rutina de misión) | Adams & MacKay 2007 (Bayesian Online Changepoint Detection) | Medio-alto | Solo si FB-003/004 muestran huecos del binomio 2σ+CUSUM; mismo banco de comparación que MP-1 |
| MP-3 | **Normalización WBE estándar para D7**: separar dilución/química de biología con creatinina, flujo y marcadores químicos antes de leer el TOC como censo | MO-5 + DC-04 (agua) | La idea más frágil deja de ser poesía: método citable del campo antes de la falsación; la normalización es exactamente la separación que D7 necesita | Verani et al. 2025 (Viruses 17:672); Hsu et al. 2022 (PMC9376872); Foladori et al. 2024 | Bajo (es diseño del experimento, no código) | **Se integra DIRECTAMENTE en el diseño de FB-004** (recomendada antes del 14-nov) |
| MP-4 | **RO-Crate para la cápsula**: empaquetado JSON-LD con provenance FAIR en lugar de formato propio | FA-3 (DC-07 `empaquetado`) | La cápsula se vuelve un objeto de datos que terceros ya saben leer con herramientas estándar; precede la red de cápsulas y el mini-meta-análisis | Especificación RO-Crate (JSON-LD, FAIR, provenance) | Bajo-medio | Comparar: ¿un tercero abre la cápsula con librerías estándar sin leer nuestro código? |
| MP-5 | **Anclaje criptográfico de actas**: OpenTimestamps (prueba .ots portable) + DOI por versión de acta/preregistro | GO-2 | El preregistro deja de confiar en nosotros: el hash es verificable por cualquiera contra el tiempo; el árbitro puede ser matemático hasta que haya uno humano | OpenTimestamps (Todd 2016); práctica Zenodo DOI + .ots verificada | Mínimo (script) | — (infraestructura, sin claim científico) |
| MP-6 | **CI de falsación**: cada acta re-ejecuta su falsación con sus semillas en cada cambio de código; incluye la automedición del motor (latencia/tasa de detección sobre anomalías inyectadas — pendiente del bestiario §6.6) | IN-4 (Banco de Falsaciones) | El criterio de victoria T3 se vuelve un botón: "reproduce todo" en cada push; la regresión de detectores se caza sola | Práctica de ingeniería (sin ancla académica necesaria) | Bajo | — |
| MP-7 | **Reanclaje 2025–2026 del PDF v0.4**: refrescar anclas con lo publicado este año | K-4/K-5 | El documento sale con recibos del mes: fatiga de alarmas (scoping review 2025), fenotipado digital (review 112 papers, 2025), gemelo digital ECLSS (AIAA 2024), autonomía médica (Frontiers 2026) | Michels et al. 2025 (BMC Nurs 24:664); Linardon et al. 2025; Gratius et al. 2024 (AIAA J. Aerosp. Inf. Syst.); Frontiers in Space Technologies 2026 | Mínimo | — |
| MP-8 | **E-procesos anytime-valid**: el libro acumula evidencia multiplicativa (una apuesta por día) en lugar de umbrales CUSUM de ventana fija; mirada diaria sin inflación de error | MO-2/MO-3 + campo nuevo `e_acumulado` en DC-06 | El contrato estadístico deja de depender de una ventana elegida a mano | Ramdas et al. 2020 (arXiv:2009.03167); Ramdas et al. 2023 (Statistical Science 38(4)) | Medio | Mismo banco que MP-1: FPR y latencia vs CUSUM en replay FB-001/002 |
| MP-9 | **CUSUM de red (multivariante)**: cambia el punto estructural sobre el **vector** de residuos, no sobre residuos aislados | Extensión de MO-3 | Una tormenta que mueve a 3 de 4 tripulantes dispara UNA alarma de red, no 3 falsas → ataque directo a la fatiga de alarmas (Michels 2025) | Harle & Chatelain (C-16); changepoint multivariante | Medio | Posterior a FB-003/004: deriva colectiva vs individual |
| MP-10 | **LQAS para n pequeño**: clasificar con presupuesto de error precomprometido (α, β) en lugar de estimar medias imposibles con n=4–8 | MO-1/MO-2 (capa de decisión) | Convierte "no puedo estimar con 4 personas" de debilidad en disciplina; responde la crítica del sesgo OSDR | Lanata et al. 1991 (WHO/IRIS, C-14); Pagano et al. 2010 (C-15) | Bajo (diseño de decisión) | En silicio: clasificación LQAS vs umbral de media en escenarios FB-002 |
| MP-11 | **Preregistro de anomalías (anti-HARKing operativo)**: la firma esperada de una investigación se hashea ANTES de abrirla; lo ocurrido se puntúa contra lo firmado | Extensión de GO-2 (proceso) | La atribución deja de ser narrativa posterior: score predicho/observado publicado | Práctica de preregistro clínico (GO-2 ya opera) | Mínimo | — (proceso; se audita en cada acta) |
| M-L1 | **EL ARCHIVO DE GENERACIONES** (frontera, DOC-04 §7): líneas base por cohorte y detección de deriva intergeneracional | MO-1 (extensión multi-cohorte) | La "normalización del empeoramiento" entre generaciones deja de ser invisible: el lab es el único que recuerda todas las líneas base | Diseño de frontera sin ancla aún — declarado (caso Proxima b) | Bajo (diseño) | — (roadmap de frontera) |
| M-L2 | **UMBRAL VIVO** (frontera): reglas de detección con fecha de vencimiento y re-acuñación programada | MO-2/MO-3 (configuración) | El umbral fósil deja de envejecer en secreto: toda regla tiene vida media y auditoría | DOC-04 §6 | Bajo | — (roadmap de frontera) |
| M-L3 | **HIPÓTESIS PERECEDERAS** (frontera): tarjetas con plan de muerte del sensor y fecha de caducidad; cola ordenada por vida media instrumental | FA-1 + DC-12 (campo `vencimiento`) | Las preguntas mueren cuando muere el instrumento que las podía responder — y la cola lo sabe | Consume `hazard_dia` de DC-11 (MO-8) | Bajo | — (roadmap de frontera) |
| M-L4 | **SENADO EPISTÉMICO** (frontera): decisión con confianza explícita ante evidencia conflictiva; re-litigación programada; doctrina versionada | LA MESA (actas, Capa 4) | Medicina bajo latencia: la nave decide hoy y agenda su propia revisión | DOC-04 §6–§7 | Bajo (proceso) | — (roadmap de frontera) |
| M-L5 | **GENOMA DE CONOCIMIENTO** (frontera): procedencia total y libro de refutaciones del cuaderno del lab | FA-3/DC-07 + GO-2 | El cuaderno como carga crítica: ningún error se fósiliza en doctrina sin dejar rastro refutable | DOC-04 §6 | Bajo | — (roadmap de frontera) |

**Estado especial de las filas M-L:** ROADMAP DE FRONTERA (DOC-04, caso de estudio Proxima b §7). No compiten por el submit del 14-nov; existen como **prueba de invariancia**: cada uno enchufa en el registro existente, y lo que no enchufa es decoración.

**Recomendación de orden:** MP-3 ahora (refuerza la falsación más frágil antes del 14) → MP-5 y MP-6 en la semana del hackatón (horas, no días) → MP-1 como primera falsación post-hackatón → MP-2 y MP-4 según resultados.

---

## §8 · Intel de paisaje (verificado 11-nov-2026) — lo que se movió alrededor

1. **La vecindad se acelera:** NASA y Google prueban un robot médico autónomo para misiones profundas (prototipo, oct-2026). Sigue siendo **recuperación** de conocimiento (responde con lo que ya existe). El hueco de ALMA — **fabricar** el conocimiento que ningún manual tiene — sigue abierto, y un paper de Frontiers in Space Technologies (oct-2026) vuelve a declarar la necesidad de autonomía médica.
2. **La mitad máquina ya tiene competencia:** existe un gemelo digital para ECLSS autónoma (Gratius et al., AIAA 2024; línea "autonomy in orbit" 2025). El gemelo de la MÁQUINA está siendo colonizado. El libro que une cuerpo+máquina (LB-1) sigue sin dueño — pero la ventana se estrecha. **Implicación para el mapa:** la prioridad absoluta sigue siendo el ensayo de mena (T2→T3) antes de que alguien una los dos libros con más recursos.
3. **El hueco oficial persiste:** la NASA sigue listando el monitoreo médico y ambiental como capacidad insuficiente en sus documentos de brechas tecnológicas (Feb-2025) y riesgos de sistemas humanos.
4. **Conclusión para el registro:** ninguna de estas novedades invalida una fila del mapa; todas suben la urgencia de las filas P1 (MO-4, MO-5, ensayo de mena OSDR). El mapa no cambia; el calendario sí.

---

## Cómo vive este documento

- Se versiona como todo el proyecto (**v0.2.6 hoy**: parche Apéndice A de DOC-02 + adiciones de DOC-04 aplicados el 11-nov; próximo bump cuando cambie un contrato DC-x o se acepte/rechace una MP).
- Cada acta FB-xxx nueva añade su fila en §6 el mismo día que se ejecuta.
- Cada mejora propuesta entra como fila en §7 con estado PROPUESTA; el rechazo también se escribe (como las 10 ideas dormidas: nada muere sin razón).
- Antes de cada sesión de código se abre §2; después de cada sesión se actualiza el estado de las filas tocadas. El mapa es el primer punto ciego programado del software: sabe dónde está todo, y por eso sabe qué falta.
