# TONO-LAB · MAP-S2 — GÉNESIS: Propuestas de Nueva Generación (v0.3)

> **Qué es este documento:** el veredicto de nivel del proyecto ALMA, la **balanza salud–hábitat**, el **laboratorio del astronauta** y las **cuatro propuestas nuevas originales** que no pertenecen a las 7 ideas existentes, con anatomía completa, falsaciones preregistradas y el parche literal que esperan del MAP-S1.
> **Relación con MAP-S1:** este documento no modificaba el mapa maestro. **El parche del Apéndice A fue APROBADO por el equipo el 11-nov-2026 y APLICADO el mismo día** — MAP-S1 es v0.2 desde entonces (DC-08…DC-11, MO-6…MO-8, GO-6, filas de trazabilidad, semillas nuevas), junto con las adiciones de DOC-04 · LA FUNDICIÓN (DC-12, FA-4, GO-7, cola M-L).
> **Disciplina heredada:** nada se codea sin fila en el registro; toda prueba pasa por IN-4 con semilla pública; una mejora = una capa; el rechazo también se escribe.
> **Fecha:** 2026-11-11. **Semillas nuevas declaradas hoy:** 20261111 · 20261112 (se suman a las fundacionales 20261113 · 20261114 · 20261115).
> **Firma de preregistros (GO-2, hash SHA-256):** los cuatro diseños de falsación de este documento fueron preregistrados y hasheados **antes** de ejecutar nada. Los hashes están en el Apéndice B.
> **Qué cambió de v0.1 a v0.2 (mismo día, 11-nov-2026):** (1) se retiró la narrativa de método interno — la historia de cómo se originaron las propuestas queda en v0.1 como acta interna y ya no se presenta; (2) se añaden §0.6 (la balanza salud–hábitat) y §1 (el laboratorio del astronauta); (3) cada propuesta abre ahora con su **traducción a salud**; (4) FM-3 (sueño × hueso) se reancla con ciencia real publicada; (5) se propone FM-10 (el síndrome Pandorum — familia minada de ficción con anclas reales). Nada más cambió: preregistros, hashes y anclas C-1…C-17 son idénticos a v0.1.
> **Qué cambió de v0.2 a v0.3 (mismo día, 11-nov):** se registró la aprobación y aplicación del Apéndice A (MAP-S1 v0.2); se añade el puente a DOC-04 · LA FUNDICIÓN en §1; estado de ejecución actualizado en §5 y en "Cómo vive este documento".

---

## §0 · Veredicto de nivel — ¿dónde está ALMA hoy, exactamente?

### 0.1 La escalera de evidencia, idea por idea

La escala del proyecto es T1 (concepto) → T2 (simulación/script con semilla pública) → T3 (datos reales) → T4 (tercero reproduce). El propio PDF v0.3 lo declara: ALMA tiene **dos ideas cuantificadas en simulación** (T2). Este es el desglose completo con lo que falta:

| Idea | Escala hoy (MAP-S1 §6) | Qué falta para T3 | Qué falta para T4 |
|---|---|---|---|
| D1 Residuo personal | **T2** (FB-001: ~24 h, 400 corridas) | Ensayo de mena OSDR OS-892 con datos reales | Tercero replique con semillas |
| D2 Los 9 presupuestos | **T2** (spec abierta; demostrada vía FB-001/002) | LB-1 construido y el libro cerrando | Tercero audita el cierre |
| D3 Árbitro externo | T1 (decisión, no experimento) | GO-1: árbitro nombrado + primer recibo | Firma de tercero en acta |
| D4 Presupuesto de tiempo | **T2** (FB-002: 10/10, preaviso mediano 21 d) | Ídem D1 | Ídem D1 |
| D5 Sello visible | T1 (pendiente árbitro y prototipo) | Prototipo de sello + firma GO-1 | Tercero pinta el sello |
| D6 Triangulación | T1 (FB-003 programada ≤14-nov) | FB-003 ejecutada + datos reales | Tercero reproduce |
| D7 Señal colectiva | T1 (FB-004 programada ≤14-nov; la más frágil, declarada) | FB-004 + normalización WBE (MP-3) | Tercero reproduce |

**Veredicto numérico: ALMA está en T2 de 4.** Dos ideas sólidas en simulación, tres diseñadas con falsación programada, dos simbólicas/procesales. No es mal nivel para un hackatón — es, probablemente, el nivel más alto de la sala. Pero no es el techo.

### 0.2 Los tres techos y cuál está sin tocar

1. **El techo de concepto: tocado.** El PDF v0.3 no puede crecer mucho más sin diluirse. 21 páginas, 8.900 palabras, 7 ideas, 2 actas ejecutadas. Añadir ideas débiles ahora baja el nivel, no lo sube. *Conclusión: solo una idea nueva puede entrar al documento, y solo si es de una clase distinta a todas las anteriores.*
2. **El techo de evidencia: intacto.** Las 7 ideas tienen espacio para subir (T2→T3 con OSDR OS-892; T3→T4 con replicación de terceros, que es el criterio de victoria ya declarado). Este techo se rompe con trabajo, no con ideas.
3. **El techo de clase de detector: ni siquiera estaba declarado.** Aquí está el hallazgo central de este documento.

### 0.3 El supuesto oculto de las 7 ideas (el agujero que ninguna tapa)

Las 7 ideas comparten una premisa que nadie escribió: **el manifiesto es una referencia confiable.** Todo detector existente mide desviación *respecto a una expectativa*:

- D1: observado − predicho (el modelo nulo personal).
- D4: minutos prometidos − minutos gastados (el presupuesto de tiempo).
- D6: triangula mundo/sensor/humano — pero triangula *anclado a expectativas*.
- D7: TOC del agua contra línea base (el integrador lento).

Si la referencia misma está enferma, **los 7 detectores pueden ser cegados a la vez**. Tres puntos ciegos concretos:

| Punto ciego | Descripción | Estado actual |
|---|---|---|
| **Flujo no contabilizado** | Alguien consume algo que no está en ningún presupuesto. Todos los residuos de manifiesto quedan en 0 *por construcción*: el sistema solo ve lo que prometió ver. | La familia FM-1 ("emisor no contabilizado") lo **nombra** pero ningún detector lo **caza**. |
| **Sistema de medición enfermo** | Un sensor miente de forma coherente, o la incertidumbre del manifiesto está mal estimada. D6 triangula testigos, pero no tiene referencia *por encima* de los testigos. | Declarado como riesgo, sin órgano que lo vigile. |
| **ALMA no se audita a sí misma** | El proyecto audita el cuerpo y audita la máquina. El libro contable, la ingesta y los propios detectores no tienen órgano de autoauditoría. | La observación más dura de la auditoría del 11-nov; sin respuesta hasta hoy. |

### 0.4 La ley del nodo upstream, ahora mecanizada

FB-001 y FB-002 probaron juntas una ley empírica: **ALMA gana cuando coloca el detector en el nodo más upstream medible de la cadena causal.** La conclusión que nadie extrajo hasta ahora: *el nodo más upstream posible no es un sensor — es una ley física.*

- Un sensor puede mentir. Una ley de conservación no puede ser violada: solo puede estar **desequilibrada por algo que nadie contabilizó** — y eso es exactamente lo que queremos ver.
- D3 quería un árbitro externo humano. **La física es el árbitro externo de coste cero que responde todos los días.** D3 no muere: queda como la capa humana *encima* del árbitro físico.

Esto define la única clase de detector que ALMA no tiene: **residuos de ley** (violar la física) en lugar de **residuos de manifiesto** (violar la expectativa). Las propuestas nuevas de este documento construyen esa clase y cierran los tres puntos ciegos.

### 0.5 La ventana competitiva (11-nov-2026)

- El gemelo digital de la **máquina** está siendo colonizado (Gratius et al., AIAA 2024; línea "autonomy in orbit" 2025; FMEA-ECLSS 2020 pide explícitamente que el sistema "se detecte y diagnostique a sí mismo en tiempo real").
- El libro que une **cuerpo + máquina** sigue sin dueño, pero la ventana se estrecha.
- El hueco que **nadie** ocupa: la línea **contable-forense** — no modelar el hábitat, *auditarlo*. La frase de campaña: **"ALMA no necesita un gemelo digital; necesita un tenedor de libros que sabe física."** Las propuestas P8–P11 son la materialización de esa frase.

### 0.6 La balanza salud–hábitat — qué es producto y qué es instrumento

Una precisión que este documento debe hacer explícita: **el producto de ALMA es la salud del astronauta; el hábitat es el instrumento con el que se mide sin ponerle nada encima.** El reto oficial lo pide literalmente — *"software de monitoreo de salud que reúna indicadores de salud y permita al astronauta evaluar y actuar sobre su estado"* — y sus indicadores sugeridos (presión, ritmo cardíaco, azúcar, temperatura, horas de sueño, ánimo) son exactamente los de los contratos DC-01/DC-02.

Los 9 presupuestos no son ingeniería de nave: son **indicadores de salud traducidos a recursos finitos**. Tabla de traducción:

| Presupuesto | Indicador de salud que sostiene | Indicador del reto |
|---|---|---|
| aire | exposición a CO₂ (cefalea, cognición — familia 5) | entorno hostil cerrado |
| agua | censo químico colectivo (ventana viral — familia 2) | — |
| dosis | **radiación acumulada** (peligro #1 del brief) | radiación espacial |
| ritmo | **sueño y fase circadiana** (familias 3/9) | horas de sueño diarias |
| carga | **hueso y músculo** (carga mecánica — familias 3/4/6) | pérdida de densidad ósea |
| inmunidad | reactivación viral por estrés (familia 2) | cambios inmunes |
| conducta | **ánimo y salud mental** (familias 8/9/10) | ánimo |
| tiempo | ocio y carga de trabajo (Skylab; FB-002) | carga de trabajo |
| energía | el termómetro del entorno que envuelve al cuerpo | — |

**Por qué el hábitat domina el vocabulario de este documento:** porque la ventaja competitiva del proyecto es medir al astronauta **sin wearables** — leyendo la telemetría que la nave ya produce. La conjetura del actuador (FB-001) lo probó: en una cabina regulada, el emisor fantasma es invisible en la lectura pero visible en el trabajo del limpiador — *"el paciente habla por el termostato"*. El campo es citable: la revisión 2025 de monitoreo de sueño multi-sensor (Sensors 25(6):1771) confirma que el monitoreo pasivo por sensores del entorno es una línea establecida — P9 la traslada al hábitat tripulado sin hardware nuevo. Y la salud conductual es oficialmente un factor operativo con 4 dominios declarados por el programa de NASA (sueño/circadiano, salud conductual, adaptación psicológica, interfaz humano-sistema — Flynn 2005): los 9 presupuestos cubren los cuatro.

Regla para el equipo y para el jurado: cuando una pantalla o un contrato hable de "agua" o "energía", la pregunta de salud detrás es siempre la misma — **¿qué le está pasando al cuerpo que este recurso está midiendo?**

---

## §1 · El laboratorio del astronauta — de la sorpresa a la hipótesis, del veredicto a la regla

> Una línea: *el laboratorio no es un edificio: es el ciclo que convierte una sorpresa repetida en una hipótesis falsable, y un veredicto confirmado en una regla de vuelo nueva.*

Este es el órgano que convierte a ALMA de aviso en **fábrica de conocimiento médico a bordo** — el hueco que ningún asistente médico cubre: la NASA prototipa bibliotecas conversacionales que responden con el manual que ya existe; el laboratorio fabrica los manuales que aún no existen.

La máquina completa detrás de este ciclo — el **contrato de entrada/salida**, la **prueba numérica de infinitud** (240.000 celdas / 65,8 años de preguntas), las **diez ideas de diseño con su porqué**, el **test de originalidad** (qué lo distingue de la salida genérica de un prompt) y el **caso de estudio** (misión a α Centauri / Proxima b) — vive en **DOC-04 · LA FUNDICIÓN**. Su contrato de datos es el **DC-12 · Contrato de Fundición**, ya añadido al registro de MAP-S1 v0.2.

**El ciclo, en cinco pasos** (definido en el PDF v0.3 §8; aquí queda expuesto como órgano de primera clase):

1. **Algo no cuadra** — un residuo persistente que ningún detector explica (pantalla EL RESIDUO).
2. **H-card de 5 campos** — observado, predicción del modelo nulo, hipótesis candidata, prueba de 7–14 días con herramientas de la nave, y la **señal refutadora escrita antes de probar** (el seguro de honestidad del laboratorio).
3. **Prueba** — cruce de información entre indicadores, escenario estresado con física anclada (LA TORMENTA) o ensayo N-of-1 A-B-A-B aleatorizado (solo intervenciones de bajo riesgo y reversibles).
4. **Veredicto en acta pública** — confirmado o refutado, con números exactos y semillas (LA MESA: nacidas → en prueba → refutadas → confirmadas).
5. **Cápsula exportable** — hipótesis, prueba, números, semillas, señal refutadora, veredicto y límites viajan juntos; otra tripulación la germina en sus propios datos; las cápsulas coincidentes se combinan en mini-meta-análisis y los veredictos confirmados son candidatas a regla de vuelo (LA CÁPSULA).

**Dónde vive en el registro:** la Capa 3 completa (FA-1 kanban de H-cards, FA-2 N-of-1, FA-3 cápsula) + el contenido K-1/K-2 (bestiario y familias de casos) + SU-4 (premortem mensual: el punto ciego programado del propio laboratorio). Y su certificado de calibración: antes de fabricar conocimiento nuevo, el motor debe **recuperar los casos que la ciencia ya publicó** — p. ej., la cefalea en 19 de 49 astronautas con CO₂ bajo el límite (familia 5). Si el motor recupera lo publicado, la fotografía propia merece confianza.

**Las dos canteras de hipótesis del laboratorio:**

| Cantera | Qué aporta | Ejemplos |
|---|---|---|
| **Literatura real** | casos publicados, anclas citables, calibración del motor | OSDR (OS-892), NTRS, PNAS 2026, Lancet Neurology 2014 |
| **Ficción** (bestiario K-1) | la pregunta dramatizada que la ciencia aún no corrió — siempre con ancla real ANTES de probar | la peli *Pandorum* (2009) → FM-10 propuesta abajo |

**Propuesta FM-10 · El síndrome Pandorum** (fila nueva para K-2, sigue el protocolo §5 de MAP-S1 — estado: PROPUESTA):

- **Origen (cantera ficción):** *Pandorum* (2009) dramatiza la descompensación psicótica lenta de una tripulación en misión profunda — paranoia, delirio, pérdida de identidad. La pregunta de salud real detrás: **¿cómo se ve por fuera — en telemetría, sin leer contenido — una descompensación conductual lenta?**
- **Hipótesis de estudio:** la descompensación no llega sola: llega en **cascada** — el sueño se acorta primero, el ocio se erosiona después, el consumo de la farmacia sube, y el ánimo lo admite al final. Si la cascada es real, cada eslabón es el sensor del siguiente: sueño → ocio → farmacia → conducta — todo medible con lo que el hábitat ya produce, sin leer jamás el contenido de lo que la gente escribe o dice.
- **Anclas reales:** la salud conductual es factor operativo declarado con necesidad de datos objetivos para decisiones de terminación de misión (Flynn 2005); el programa NASA declara privacidad, carga de trabajo y separación como factores de riesgo (HH&P 2023); la disforia de segunda mitad está documentada (Slack et al. 2015); el estrés reactiva virus latentes (Mehta 2014/2017); la cohesión degrada mediblemente en invierno antártico (Cantisani 2026). La ficción pone la pregunta; la literatura pone el ancla.
- **Señal refutadora (antes de probar):** si en los datos de análogo aislado la cascada no muestra orden temporal (el ánimo decae antes que el ocio, o la farmacia no se mueve junto al resto), la familia muere documentada.
- **Por qué importa al reto:** es la traducción más directa del miedo del jurado ("¿qué pasa si alguien se descompensa?") a un sistema que **no espía**: patrones y agregados, jamás contenido. La regla de privacidad del proyecto se vuelve aquí una ventaja, no un límite.

**Actualización de FM-3 (sueño × hueso) — reanclaje con ciencia real (11-nov):**

La familia entró al PDF como "cruce inédito". La investigación de hoy lo reancla: la biología ya está publicada — la interrupción de sueño/circadiana deteriora la formación ósea en ratas y en hombres sanos (Swanson et al. 2017/2018, ~222 citas; Endocrine Society 2017: 3 semanas de sueño alterado → marcador de formación ósea reducido; supresión rápida del marcador por restricción de sueño, Osteoporos Int 2019; reviews 2025–2026 en Frontiers in Endocrinology y Trends in Molecular Medicine). Lo inédito ya no es la biología: **es el ensayo en hábitat cerrado con telemetría continua sobre OS-892** — la ventana del laboratorio se mantiene, y la familia sube de "apuesta ciega" a "replicación espacial de un efecto conocido". Mejor ciencia y mejor historia.

---

## §2 · Las cuatro propuestas nuevas — anatomía completa

Ninguna pertenece a D1–D7 ni a B1–B9. Cada una pasa por el protocolo §5 de MAP-S1: una capa destino, ancla verificable, falsación preregistrada en IN-4 con semilla pública.

### P8 · **El Contrapeso** — la física como árbitro final

> Una línea: *los libros de la nave no solo cuadran consigo mismos — cuadran con la física; y cuando no cuadran, existe algo que nadie contabilizó.*

| Sección | Contenido |
|---|---|
| **Por qué importa — traducción a salud** | El residuo de ley es el único detector que caza **vida no contabilizada**: los hongos Cladosporium, Penicillium y Aspergillus que ya colonizaron la ISS (familia 1) consumen y emiten sin estar en ningún manifiesto — y el cierre de conservación es lo primero que los nota, sin cámara ni inspección. Y la deriva de consumo por bucle es el primer censo de **conducta colectiva** del hábitat (cambios de rutina, racionamientos, horarios). El paciente habla por el termostato: si el cuerpo del hábitat cambia de metabolismo, alguien está mal — o algo vivo llegó. La física no reemplaza al médico: lo despierta antes. |
| **Qué hace (mecanismo)** | Cada día contable, el libro cierra las ecuaciones de conservación por bucle: **agua** (potable = consumo + grisa + salmuera + Δtanque + pérdida declarada), **aire** (O₂ generado = consumido + Δtanque; CO₂ generado = retirado + Δatmósfera), **energía** (generada = consumida + Δbatería + radiada/perdida declarada). El sobrante es el **residuo de conservación**: una cantidad con unidades físicas (kg, kWh). El umbral de alarma no sale de la media de la tripulación: sale de la **propagación de la incertidumbre del manifiesto** de las líneas implicadas (la columna que el hallazgo v4 ya declaró soberana). |
| **De dónde saca los datos** | Exclusivamente **DC-04** (el libro GPV). Cero hardware nuevo, cero ingesta nueva, cero sensores nuevos. Es el detector más barato posible de construir y el más caro de engañar. |
| **Qué devuelve** | Contrato nuevo **DC-08 · Cierre de conservación**: día × bucle × residuo (kg/kWh) × incertidumbre propagada × veredicto `CIERRA`/`NO CIERRA`. |
| **Dónde se conecta** | Lee LB-1 (regla de dependencia 1: nada lee sensores). Sus residuos entran al mismo CUSUM bilateral (MO-3) que cualquier otro residuo. Un `NO CIERRA` **abre una investigación D6** (¿mundo, sensor o persona?). Le da a D2 su auditor interno y a D3 su árbitro físico. Alimenta LA SALA (agregados) y EL PRESUPUESTO. |
| **Por qué es nueva** | D1–D7 miden desviación de *expectativas estimadas*; P8 mide violación de *leyes*. Es una clase de detector que no existe en el proyecto. Distinción fina con B8: B8 exigía que el libro cuadrara **consigo mismo** (aritmética interna); P8 exige que cuadre **con el universo**. Un libro internamente coherente y físicamente falso es exactamente el caso que B8 no ve y P8 caza. |
| **Anclas verificables** | El bucle de agua de la ISS cierra al 98% (logro ECLSS anunciado por NASA, 2023 — el cierre es un hecho operativo, no poesía); Broyan et al., *NASA ECLSS Technology*; *Status of the ISS Regenerative ECLSS Water Recovery and Oxygen Generation Systems*; el FMEA para auto-conocimiento de ECLSS (2020) pide exactamente detección y diagnóstico de salud del sistema en tiempo real. |
| **Falsación (FB-005, preregistrada)** | Mismo banco Monte Carlo de FB-002. Tres clases de anomalía inyectada: (a) deriva coherente de sensor, (b) **flujo no contabilizado**, (c) fuga física real. Comparación directa contra el residuo de manifiesto estilo FB-001: horas hasta alarma + FPR en 14 días. **Predicción previa:** en (b) el residuo de manifiesto es ciego por construcción y P8 ve. **Criterio de muerte:** si P8 no supera al residuo de manifiesto en ≥1 clase con FPR comparable (±20%), muere con acta pública. Semillas: 20261113 · 20261114 · 20261115 (mismas que FB-002 → comparabilidad exacta). Hash en Apéndice B. |
| **Las seis puertas** | ① pesa 0 g ✓ (solo lee DC-04) · ② única y verificable ✓ (cierre de conservación es verificable por cualquiera) · ③ ciencia real ✓ (el 98% de la ISS es operación documentada) · ④ falsable <30 días ✓ (el banco de FB-002 ya existe) · ⑤ gramática de presupuestos ✓ **(no solo cabe en la gramática: la cierra — es el cierre de los propios presupuestos)** · ⑥ historia memorable ✓ ("cuando los libros no cuadran con la física, algo existe que nadie contabilizó"). |
| **Escalera** | T2 al ejecutar FB-005. **T3:** recomputar el cierre con datos reales diarios de ECLSS de la ISS (publicados). **T4:** un tercero reproduce el cierre con las semillas. |
| **Coste (minutos de hábitat)** | ~15 min/día automáticos (el cálculo del cierre); 0 min humanos en operación. El hábitat paga el cierre de sus propios libros — como toda contabilidad digna. |
| **Riesgo de dilución** | Bajo. No añade una familia de casos ni una pantalla: añade una **referencia**. Es el único candidato a idea #8 (D8) — ver §4. |

### P9 · **El Hábitat Sueña** — la fase circadiana colectiva que ya está en el libro

> Una línea: *la curva de potencia de la nave es el polisomnograma de toda la tripulación — sin un solo wearable nuevo.*

| Sección | Contenido |
|---|---|
| **Por qué importa — traducción a salud** | Esta propuesta **es salud directa del astronauta**: el sueño es indicador literal del reto ("horas de sueño diarias") y el sueño/circadiano es el primero de los 4 factores operativos de salud conductual de NASA (Flynn 2005). Hoy ese dominio solo se mide con actigrafía (wearables); P9 lo mide por la curva del hábitat — fase y amplitud colectivas sin tocar a nadie. Un corrimiento de fase sostenido de la tripulación entera es exactamente el primer eslabón de la cascada FM-10 (sueño → ocio → farmacia → ánimo): P9 es el sensor del eslabón más temprano. El sueño deficiente en vuelo está documentado con actigrafía (Barger et al., *Lancet Neurology* 2014; Kawada 2016), y el monitoreo pasivo por sensores del entorno es campo establecido (Sensors 25(6):1771, 2025). |
| **Qué hace (mecanismo)** | Las curvas diarias de consumo (potencia, agua, CO₂ generado) llevan dentro el ritmo colectivo de la tripulación. Cada día contable se extraen tres números: **fase** (hora del valle colectivo), **amplitud** (razón pico/valle), **residuo de forma** (contra la ventana de calibración, en σ). Un corrimiento sostenido de fase o un colapso de amplitud = el hábitat está "soñando distinto": cambio del patrón colectivo de descanso y actividad, visible sin tocar a nadie. |
| **De dónde saca los datos** | **DC-04** (presupuestos energia/agua/aire del sujeto *hábitat*) + **DC-03** como covariables declaradas (acoplamientos, EVA, días de operaciones explican desviaciones benignas — el ledger ya las tiene). |
| **Qué devuelve** | Contrato nuevo **DC-09 · Forma diaria del hábitat**: día × curva × fase (hh:mm) × amplitud relativa × residuo de forma (σ) × covariables. |
| **Dónde se conecta** | Lee LB-1. Su residuo entra a MO-3 (CUSUM sobre la forma). **Cruce con D1:** si el residuo personal y la fase colectiva se mueven juntos, hay historia de familia; si el individual se mueve solo, hay historia personal — la triangulación ahora tiene un eje temporal. Alimenta SU-2 (tablero del comandante, agregados) y LA SALA. |
| **Por qué es nueva** | No es D7: D7 es el canal **químico** (TOC del agua → censo de biología, integrador lento). P9 es el canal **temporal** (forma de curvas → censo de comportamiento, latencia diaria). Son hermanos de familia, no duplicados: dos canales sensoriales distintos bajo el mismo principio de señal colectiva. Y ataca el dominio más grande sin vigilar del PDF — sueño/ritmo — con coste cero de hardware, respetando la regla de privacidad por construcción (solo agregados, jamás contenido individual). |
| **Anclas verificables** | Chen et al. 2013 (*Non-Intrusive Occupancy Monitoring using Smart Meters*); Devlin 2019 (NILM → actividades de la vida diaria); Barger et al. 2014 (déficit de sueño en vuelo, medido con actigrafía); Kawada 2016 (aplicabilidad de la actigrafía en vuelo espacial). |
| **Falsación (FB-006, preregistrada)** | 30 días de calibración estable; inyecciones: (a) corrimiento de fase colectivo +2 h durante 7 días; (b) semana de apatía colectiva (amplitud −30%). Pregunta: ¿detecta fase/amplitud antes que los residuos individuales D1 crucen 2σ? **Criterio de muerte:** si σ(residuo de forma) ≥ σ de fase en calibración, el ruido domina a la señal y P9 muere con acta pública. Semilla: 20261112. Hash en Apéndice B. |
| **Las seis puertas** | ① 0 g ✓ · ② única ✓ (NILM vigila edificios; nadie vigila hábitats tripulados por fase colectiva) · ③ ciencia real ✓ (las tres anclas) · ④ falsable <30 días ✓ · ⑤ gramática de presupuestos ✓ (lee los presupuestos directamente) · ⑥ historia memorable ✓ ("la nave sueña; le tomamos la polisomnografía a la curva de consumo"). |
| **Escalera** | T1→T2 con FB-006. **T3:** datasets OSDR que aparean telemetría de consumo con actigrafía — validar la fase colectiva contra la verdad de suelo wearable. |
| **Coste** | ~5 min/día automáticos; 0 humanos. |
| **Riesgo de dilución** | Nulo como idea: entra como **segundo canal de D7 (D7-β)**, no como idea nueva (§4). |

### P10 · **El Sistema Inmune** — epidemiología del error sobre el propio libro

> Una línea: *el libro tiene sistema inmune — y medimos sus enfermedades autoinmunes.*

| Sección | Contenido |
|---|---|
| **Por qué importa — traducción a salud** | Protege la salud de los datos de salud: si el libro que vigila al astronauta está envenenado, toda alarma médica es sospechosa. Con la epidemiología del error (caso, cuarentena, R0 sobre el linaje que ya existe en `fuente_linea` de DC-04), cada alarma de salud lleva consigo el estado sanitario de los datos que la produjeron — confianza medible, no prometida. |
| **Qué hace (mecanismo)** | Cada error hallado en el libro (faltante, timestamp roto, unidad mal convertida, sensor muerto sin marcar, línea duplicada) se registra como **CASO** con su linaje. Todos los descendientes (las líneas que consumieron el dato corrupto) pasan a **CUARENTENA** (columna de estado: limpio / sospechoso / cuarentena). Cada fuente acumula su **R0**: cuántas líneas corrompe en promedio cuando falla. Las fuentes de R0 alto entran en auditoría prioritaria. Un brote (caso con >k descendientes) abre acta de gobernanza automáticamente. Vocabulario deliberado: *infección* (error propagando), *cuarentena* (contención), *inmunidad* (corrección estructural: la clase de error no puede volver a ocurrir), ***autoinmunidad*** (un detector marcando datos sanos — se mide y se penaliza; la tasa de falsa cuarentena se publica cada semana). |
| **De dónde saca los datos** | `fuente_linea` de DC-04 + provenance de DC-01/02/03. Cero hardware, cero ingesta nueva. |
| **Qué devuelve** | Contrato nuevo **DC-10 · Casos de error y contagio** (caso_id × nodo origen × clase × descendientes × estado × R0 de la fuente × bandera de brote) + columna `estado_linea` en DC-04. |
| **Dónde se conecta** | Es **GO-6** (proceso de gobernanza: cuarentena y acta de brote). Alimenta K-6 (los errores también mueren con razón escrita) y MP-6 (la cobertura de cuarentena se vuelve métrica de CI). Cierra el punto ciego 3 de §0.3: es el órgano de autoauditoría que el proyecto no tenía. |
| **Por qué es nueva** | B8 verificaba aritmética (que las partidas cuadren entre sí). P10 rastrea **dinámica de propagación** (cómo se mueven los errores por el grafo). El proyecto audita cuerpo y máquina desde el día 1; el día que se audita a sí misma es hoy. Es la respuesta operativa a la observación más dura de la auditoría del 11-nov. |
| **Anclas verificables** | Práctica de linaje de datos para calidad y contención de errores (documentación estándar de la ingeniería de datos); el marco epidemiológico (caso/contacto/cuarentena/R0) es conocimiento clásico de salud pública. Ancla de *proceso*, no de paper — y se declara honesta como tal (tipo PROCESO en el registro). |
| **Falsación (FB-007, preregistrada)** | 5 errores inyectados en nodos distintos del grafo ingesta/libro: (d1) faltante canal A, (d2) timestamp roto, (d3) unidad mal convertida, (d4) sensor muerto sin marcar, (d5) línea GPV duplicada. Métricas: cobertura de cuarentena (% de descendientes reales marcados), tasa de falsa cuarentena (líneas sanas marcadas), latencia de brote. **Criterio de muerte:** cobertura <90% o falsa cuarentena >5%. Semilla: 20261111. Hash en Apéndice B. |
| **Las seis puertas** | ① 0 g ✓ · ② única ✓ · ③ ciencia real ~ (ancla de práctica de ingeniería, declarada; es PROCESO) · ④ falsable <30 días ✓ · ⑤ gramática de presupuestos ✓ (opera sobre el propio libro) · ⑥ historia memorable ✓ ("hasta el contador tiene sistema inmune, y publicamos sus enfermedades autoinmunes"). |
| **Escalera** | T2 al ejecutar FB-007. Como proceso, su T4 es natural: cualquiera puede inyectar los 5 errores con la semilla y medir la contención. |
| **Coste** | ~10 min/día automáticos (recorrido del grafo en el cierre) + ~30 min/semana de revisión de brotes (gobernanza humana, la única parte no automática). |
| **Riesgo de dilución** | Nulo como idea: entra como GO-6 (proceso), no como idea (§4). |

### P11 · **La Demografía de los Testigos** — los sensores tienen tablas de supervivencia

> Una línea: *el manifiesto sabe la edad de sus testigos — y sube su piso de detección con honestidad cuando envejecen.*

| Sección | Contenido |
|---|---|
| **Por qué importa — traducción a salud** | Cada indicador de salud del astronauta (fc, presión, glucosa, sueño, ánimo) se mide con sensores que envejecen. Si el sensor que vigila el sueño muere y nadie lo sabe, la "salud" reportada es ficción con forma de dashboard. La demografía de testigos (curvas de supervivencia por clase, hazard con la edad) hace que el libro **confiese** la edad de sus instrumentos y ensanche su incertidumbre antes de mentir — honestidad de piso para todas las alarmas de salud. |
| **Qué hace (mecanismo)** | Cada instrumento tiene ficha de vida: nacimiento (su primera línea en el libro), calibraciones, derivas observadas, muerte. Por clase de sensor: **curva de supervivencia**. La incertidumbre del manifiesto deja de ser artesanal: se **computa** desde la edad del sensor testigo (el hazard crece con la edad y con las calibraciones vencidas). Sensor muerto → su presupuesto pierde testigo → la incertidumbre de esas líneas se ensancha automáticamente → **todos los umbrales de todos los detectores se reancalan solos** y el piso de detección sube de forma honesta y visible en lugar de fingir precisión muerta. |
| **De dónde saca los datos** | `incertidumbre_sensor` de DC-01 (viaja con cada línea desde el día 1) + historial de DC-04 + metadatos de IN-1. |
| **Qué devuelve** | Contrato nuevo **DC-11 · Fichas de vida de sensor** (device_id × clase × edad × días desde calibración × hazard diario × σ recomendada para el manifiesto × estado vivo/convaleciente/muerto) + la función que recalcula la columna `incertidumbre_del_manifiesto` de DC-04. |
| **Dónde se conecta** | Es **MO-8** (Capa 2). Alimenta a MO-1/MO-2 (σ efectiva), a P8 (la incertidumbre propagada del cierre usa su σ), y al readout del piso de detección de EL PRESUPUESTO. Cierra el punto ciego 2 de §0.3: la referencia por encima de los testigos. |
| **Por qué es nueva** | El hallazgo v4 declaró la columna soberana pero dejó su procedencia artesanal. Nadie en el proyecto (ni en la literatura de gemelos digitales) conecta fiabilidad de componentes con la incertidumbre del manifiesto contable. El campo de fiabilidad ECLSS existe y está publicado — nadie lo ha usado para *anchoring epistémico del libro*. |
| **Anclas verificables** | Jones, H.W. 2019, *High Reliability Requires More Than Providing Spares* (NASA NTRS 20190027319): la bomba del procesador de orina es el peor componente de soporte vital de la ISS — exactamente el tipo de componente cuya muerte debería ensanchar la incertidumbre **antes** de morir. Russell et al. 2007 (*Reliability Engineering & System Safety*): desviaciones de mantenimiento ISS sobre tiempo de diseño. Miyajima: diseño de fiabilidad ECLSS con MTBF operativo. FMEA-ECLSS 2020: el sistema "deberá detectar y diagnosticar su salud en tiempo real". |
| **Falsación (FB-008, preregistrada)** | Vidas sintéticas con las tasas MTBF publicadas (Jones 2019; Russell 2007), 1000 vidas por clase, semilla 20261111. Pregunta: ¿la σ computada desde la demografía calibra mejor (diagrama de fiabilidad, error de calibración esperado) que una constante artesanal? **Criterio de muerte:** si ECE(computada) ≥ ECE(fija), P11 muere con acta pública. Hash en Apéndice B. |
| **Las seis puertas** | ① 0 g ✓ · ② única ✓ · ③ ciencia real ✓ (fiabilidad ECLSS publicada por NASA) · ④ falsable <30 días ✓ · ⑤ gramática de presupuestos ✓ (su salida ES una columna del contrato central) · ⑥ historia memorable ✓ ("sabemos qué testigo está enfermo antes de que muera, y los libros lo confiesan"). |
| **Escalera** | T1→T2 con FB-008. **T3:** historiales reales de fallos (la literatura ISS ya los publica; OSDR contiene estados de instrumentos). |
| **Coste** | ~20 min/semana de recalibración automática de hazard; 0 humanos en operación. |
| **Riesgo de dilución** | Nulo como idea: entra como MO-8 (módulo), no como idea (§4). |

---

## §3 · Segunda ola — mejoras estadísticas y de proceso (MP-8 … MP-11)

No son ideas nuevas: son actualizaciones del motor y del proceso que salieron de la revisión de los puntos ciegos (§0.3). Entran a la cola de MAP-S1 §7 como PROPUESTA, con el mismo formato de columnas.

| ID | Mejora | Destino | Qué compra (concreto) | Ancla verificada | Costo | Prueba si es claim |
|---|---|---|---|---|---|---|
| MP-8 | **E-procesos anytime-valid**: el libro acumula evidencia multiplicativa (una apuesta por día) en lugar de umbrales CUSUM de ventana fija; se puede mirar cada día sin inflación de error, y la garantía vale para cualquier momento de parada | MO-2/MO-3 + campo nuevo `e_acumulado` en DC-06 | El contrato estadístico del libro deja de depender de una ventana elegida a mano; la mirada diaria (que es exactamente como opera un hábitat) se vuelve legal por construcción; encaja con el lenguaje de apuestas que ya usa el proyecto | Ramdas et al. 2020 (arXiv:2009.03167: toda inferencia secuencial anytime-valid admisible requiere martingalas no negativas); Ramdas & Wang, *Hypothesis Testing with E-values* (survey); Ramdas et al. 2023, *Game-Theoretic Statistics and Safe Anytime-Valid Inference* (Statistical Science 38(4)) | Medio | Mismo banco de comparación que MP-1: FPR y latencia vs CUSUM actual en FB-001/002 replay |
| MP-9 | **CUSUM de red (multivariante)**: los detectores están correlacionados → las alarmas están correlacionadas; cambia el punto estructural sobre el **vector** de residuos, no sobre residuos aislados | Extensión de MO-3 | Completa la idea nunca falsada de la auditoría del 11-nov (deriva de red colectiva); una tormenta que mueve a 3 de 4 tripulantes dispara *una* alarma de red, no 3 alarmas falsas individuales → ataque directo a la fatiga de alarmas (Michels 2025) | Harle & Chatelain, *Rank-based multiple change-point detection in multivariate time series*; literatura de changepoint multivariante | Medio | Falsación posterior a FB-003/004: mismo banco, escenario de deriva colectiva vs deriva individual |
| MP-10 | **LQAS (Lot Quality Assurance Sampling) para n pequeño**: con n=4–8, estimar está condenado (la potencia muere); LQAS clasifica con presupuesto de error precomprometido (α, β): "¿este día/lote es aceptable?" en lugar de "¿cuál es la media?" | MO-1/MO-2 (capa de decisión) | Responde con estadística establecida la crítica del sesgo OSDR (población superseleccionada): ALMA no estima la media de una población que no existe — **decide sobre el lote** con errores declarados de antemano; convierte "no puedo estimar con 4 personas" de debilidad en disciplina | Lanata et al. 1991 (WHO/IRIS: LQAS para muestras pequeñas); Pagano et al. 2010 (PMC2817093: comentario práctico sobre clasificación con LQAS) | Bajo (es diseño de decisión, no código nuevo) | En silicio: comparar clasificación correcta (extremos) LQAS vs umbral de media en los escenarios de FB-002 |
| MP-11 | **Preregistro de anomalías (anti-HARKing operativo)**: antes de abrir una investigación, la firma esperada (qué sensores, dirección, magnitud, duración) se firma con hash en el libro; después del evento, lo ocurrido se puntúa contra lo firmado | Extensión de GO-2 (proceso) | La atribución de anomalías deja de ser narrativa posterior: cada investigación termina con el score predicho/observado publicado; ninguna historia se escribe después de ver los datos | Práctica de preregistro clínico (ya es ancla del proyecto: GO-2 opera con hash manual) | Mínimo (es una regla de proceso, no software) | — (proceso; se audita en cada acta futura) |

**Nota de no-duplicación:** MP-11 extiende GO-2 (que hoy preregistra experimentos) a *investigaciones de anomalías*. No crea un órgano nuevo.

**Orden recomendado (se integra con la recomendación existente de MAP-S1 §7):** MP-3 ahora (FB-004) → FB-005 el 12-nov si el banco queda libre → MP-5/MP-6 en la semana del hackatón → MP-8 como primera falsación estadística post-hackatón (junto a MP-1) → MP-10 en el diseño de MO-1 → MP-9 y MP-11 según resultados.

---

## §4 · Veredicto de integración — anti-dilución (la decisión más importante del documento)

El techo de concepto está tocado (§0.2). Por eso el veredicto de integración **no** es "entramos 4 ideas nuevas":

| Propuesta | Entra como | Nivel de idea | Justificación |
|---|---|---|---|
| **P8 El Contrapeso** | **D8, la idea #8** (solo si FB-005 corre antes del 13-nov; si no, entra como diseño preregistrado T1-honesto en la cola) | Idea nueva — la única | Es una clase de detector ausente (residuo de ley). Es la que paga su entrada al PDF: 0 g, historia memorable, y convierte la ley del nodo upstream en mecánica. |
| **P9 El Hábitat Sueña** | **D7-β**, segundo canal de la señal colectiva (canal temporal; D7 queda como canal químico) | Familia existente | La idea "señal colectiva" ya existe; P9 añade un canal sensorial, no una idea. Una familia con dos sensores es más fuerte que dos ideas hermanas diluidas. |
| **P10 El Sistema Inmune** | **GO-6** (proceso) + DC-10 | Órgano, no idea | Los procesos no compiten por el conteo de ideas; compiten por el veredicto del jurado sobre madurez. Es la respuesta a la observación más dura de la auditoría. |
| **P11 La Demografía de los Testigos** | **MO-8** (módulo) + DC-11 | Órgano, no idea | Su producto es una columna que ya existe (`incertidumbre_del_manifiesto`) — le da procedencia principada a lo que hoy se escribe a mano. |

**Resultado neto:** las ideas pasan de 7 a **8** (no a 11). Los módulos del registro pasan de 29 a 33. Los contratos de 7 a 11.

**La narrativa que se vende al jurado (una sola frase):** *"ALMA audita cuatro cuerpos: la persona (D1), la máquina (D2/D6/D7), la física (D8) y a sí misma (GO-6/MO-8) — y su árbitro final es una ley que no se puede mentir."*

**Qué NO entra al PDF v0.4 (disciplina del tope):** P9/P10/P11 no aparecen en el PDF como ideas; aparecen, si acaso, en una línea de la tabla de arquitectura. El PDF solo crece por: (1) las actas FB-003/FB-004 ejecutadas en la Tabla 3, (2) D8 si FB-005 pasa, (3) el anclaje 2025–2026 (MP-7), (4) la nota "qué cambió entre v0.3 y v0.4". Nada más.

---

## §5 · Plan de ejecución — 11 al 14 de noviembre

| Día | Acción | Producto del día |
|---|---|---|
| **Hoy, 11-nov** | MAP-S2 creado; FB-005…008 preregistradas y hasheadas (Apéndice B); semillas 20261111/20261112 declaradas públicas | Este documento + 4 hashes que prueban que la predicción se escribió antes de correr |
| **12-nov** | **FB-003** (D6 matriz co-deriva) con el banco compartido. Si el banco queda libre: **FB-005** (El Contrapeso — reutiliza el Monte Carlo de FB-002, coste bajo, comparabilidad directa) | Actas FB-003 y (idealmente) FB-005 con fila en MAP-S1 §6 |
| **13-nov** | **FB-004** (D7 con normalización WBE de MP-3). **PDF v0.4**: Tabla 3 + actas ejecutadas, Tabla 8 actualizada, nota "qué cambió entre v0.3 y v0.4", recibos de GO-4 (decisión del nombre). Si FB-005 pasó: D8 entra como idea #8; si no: "preregistrado, falsación el 15-nov" — ambas opciones son honorables | PDF v0.4 + MAP-S1 v0.2 (parche del Apéndice A **ya aplicado anticipadamente el 11-nov** con aprobación del equipo) |
| **14-nov** | Demo. Guion sugerido: **abrir** con la ley del nodo upstream (dos actas que la probaron sin saberlo) → **cerrar** con la frase: "los libros de la nave no solo cuadran consigo mismos; cuadran con la física — y el libro tiene sistema inmune" | Veredicto del jurado |

**Regla de emergencia:** si el 12-nov solo cabe una falsación entre FB-003 y FB-005, corre **FB-005**: D6 ya tiene falsación programada y estado DISEÑADO declarado; El Contrapeso es la propuesta que compite por entrar al PDF y necesita su acta para no entrar como promesa.

---

## Apéndice A · Parche literal para MAP-S1 v0.2 (APROBADO y APLICADO el 11-nov-2026)

### A.1 · Filas nuevas del registro §2

**Capa 2 · Motor de detección** (añadir bajo MO-5):

| ID | Tipo | Qué hace | Entradas | Salidas | Conexiones | Estado | Prioridad |
|---|---|---|---|---|---|---|---|
| MO-6 | CÓDIGO | Cierre de conservación diaria de los bucles agua/aire/energía; residuo con unidades físicas y umbral por propagación de incertidumbre. **Realiza D8** | DC-04 (todo) | DC-08 | → MO-3, → FA-1, abre investigaciones D6 | DISEÑADO — FB-005 preregistrada (Apéndice B) | P1 |
| MO-7 | CÓDIGO | Fase/amplitud/residuo de forma de las curvas diarias de consumo. **Realiza el canal D7-β** | DC-04 (energia, agua, aire del hábitat), DC-03 (covariables) | DC-09 | → MO-3, → SU-2 | DISEÑADO — FB-006 preregistrada (Apéndice B) | P2 |
| MO-8 | CÓDIGO | Demografía de sensores: fichas de vida, curvas de supervivencia por clase, σ recomendada para el manifiesto | DC-01 (`incertidumbre_sensor`), DC-04 histórico | DC-11 + recalcula `incertidumbre_del_manifiesto` de DC-04 | → MO-1/MO-2, → MO-6, → EL PRESUPUESTO | DISEÑADO — FB-008 preregistrada (Apéndice B) | P2 |

**Gobernanza** (añadir bajo GO-5):

| ID | Tipo | Qué hace | Estado | Prioridad |
|---|---|---|---|---|
| GO-6 | PROCESO | Epidemiología del error: caso con linaje, cuarentena de descendientes, R0 por fuente, acta de brote, publicación semanal de la tasa de autoinmunidad (falsa cuarentena) | DISEÑADO — FB-007 preregistrada (Apéndice B) | P1 |

### A.2 · Contratos nuevos §3 (campo a campo)

**DC-08 · Cierre de conservación** — lo que mira el Contrapeso:

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

**DC-09 · Forma diaria del hábitat** — lo que mira El Hábitat Sueña:

| Campo | Tipo | Nota |
|---|---|---|
| `dia_habitat`, `banner` | — | Convención general |
| `curva` | enum: potencia · agua · aire | Tres formas por día |
| `fase_valle_local` | hh:mm UTC | Hora del valle colectivo (la "noche" del hábitat) |
| `amplitud_relativa` | float | Razón pico/valle del día |
| `residuo_forma` | float (σ) | Contra la ventana de calibración |
| `covariables` | ref DC-03 | Eventos que explican desviaciones benignas (acoplamiento, EVA, ops) |

**DC-10 · Casos de error y contagio** — lo que mira El Sistema Inmune:

| Campo | Tipo | Nota |
|---|---|---|
| `caso_id`, `ts_utc_deteccion` | — | |
| `nodo_origen` | ref DC-01/02/03/04 | Dónde nació el error |
| `clase_error` | enum: faltante · timestamp · unidad · sensor_muerto · duplicado | El bestiario mínimo de errores |
| `descendientes` | lista de refs de línea | Las líneas que consumieron el dato corrupto |
| `estado` | enum: abierto · en_cuarentena · cerrado · corregido_estructural | "Corregido estructural" = inmunidad adquirida |
| `r0_fuente` | float | Media de líneas corruptas por fallo de esa fuente |
| `brote` | bool (+ k declarado) | Caso con >k descendientes → acta GO-6 automática |

**DC-11 · Ficha de vida de sensor** — lo que mira la Demografía de los Testigos:

| Campo | Tipo | Nota |
|---|---|---|
| `device_id`, `clase_sensor` | — | La clase define la curva de supervivencia |
| `nacimiento` | ts_utc | Primera línea del instrumento en el libro |
| `calibraciones[]` | lista de ts_utc | Vacía o vencida = hazard sube |
| `edad_dias`, `dias_desde_calibracion` | int | |
| `hazard_dia` | float | Probabilidad instantánea de fallo (Weibull ajustada por clase) |
| `sigma_manifiesto_recomendada` | float (σ) | Lo que alimenta `incertidumbre_del_manifiesto` de DC-04 |
| `estado` | enum: vivo · convaleciente · muerto | Muerto = el presupuesto pierde testigo y su σ se ensancha |

### A.3 · Cambios menores

- **§4 (pantallas):** LA SALA añade consumo de DC-08 (veredictos CIERRA/NO CIERRA, agregados); EL PRESUPUESTO añade el readout del piso de detección (σ del manifiesto, ahora computada por MO-8).
- **§6 (trazabilidad):** fila nueva `D8 El Contrapeso | MO-6 | DC-08 | FB-005 | 20261113/14/15 | T1→T2`; fila nueva `D7-β canal temporal | MO-7 | DC-09 | FB-006 | 20261112 | T1`.
- **§7 (cola):** filas MP-8…MP-11 tal como están en §3 de este documento.
- **K-3 (semillas):** añadir 20261111 y 20261112 como semillas públicas declaradas el 11-nov.
- **Versionado:** añadir contratos DC-08…DC-11 es cambio de contrato → **MAP-S1 v0.2 obligatorio** (regla §5 de MAP-S1).

---

## Apéndice B · Preregistros firmados (11-nov-2026, GO-2)

Los cuatro diseños se firmaron **antes** de ejecutar nada. Hash SHA-256 calculado sobre el texto exacto del preregistro.

**FB-005 · El Contrapeso** — semillas 20261113 · 20261114 · 20261115 (mismas que FB-002: comparabilidad directa).

> Hipótesis: el residuo de conservación detecta al menos una clase de anomalía antes que el residuo de manifiesto, con FPR comparable. Diseño: banco Monte Carlo de FB-002, 400 corridas por escenario; anomalías (a) deriva coherente de sensor, (b) flujo no contabilizado, (c) fuga física real. Predicción previa: en (b) el residuo de manifiesto es ciego por construcción. Muerte: sin ventaja en ≥1 clase con FPR ±20% relativo.

> **SHA-256:** `6c923ac5237853e8c4ecb66c3a4911f8ec0d4df37513ac0cdcd511a9e2567b9b`

**FB-006 · El Hábitat Sueña** — semilla 20261112 (clase de señal nueva, semilla independiente declarada).

> Hipótesis: la forma diaria de las curvas de consumo es estable en calibración y su residuo de forma detecta un cambio colectivo de descanso antes que D1 cruce 2σ. Diseño: 30 días de calibración; inyecciones (a) fase +2 h × 7 días, (b) amplitud −30%. Muerte: si σ(residuo de forma) ≥ σ de fase en calibración.

> **SHA-256:** `c29e48bb34c19c19add22c5b58302881baf8aa8e63084ce0ebd28114bfef2194`

**FB-007 · El Sistema Inmune** — semilla 20261111 (fecha de preregistro).

> Hipótesis: el linaje (`fuente_linea` de DC-04) contiene un error inyectado con ≥90% de cobertura de descendientes y <5% de falsa cuarentena, detectando el brote en el mismo cierre diario. Diseño: 5 errores en nodos distintos (faltante, timestamp, unidad, sensor muerto, duplicado). Muerte: cobertura <90% o falsa cuarentena >5%.

> **SHA-256:** `3ee6ed7b0a545d7cc838fc9c0884d16538779f8fcd4d97a9c8675c49b17cd75a`

**FB-008 · La Demografía de los Testigos** — semilla 20261111.

> Hipótesis: la incertidumbre del manifiesto computada desde la edad del testigo (supervivencia por clase, MTBF publicado del ECLSS) calibra mejor que una constante. Diseño: 1000 vidas sintéticas por clase con tasas de Jones 2019 y Russell 2007. Muerte: si ECE(computada) ≥ ECE(fija).

> **SHA-256:** `1b3a17ee60c8c6c29b312de94b34950da565be0103f2f57dd8f634fe9d11026d`

---

## Apéndice C · Anclas nuevas verificadas (11-nov-2026)

| # | Ancla | Para qué | Fuente |
|---|---|---|---|
| C-1 | Recuperación de agua del 98% en la ISS (logro ECLSS, 2023) | P8 — el cierre del bucle es operación documentada | NASA vía prensa técnica (hothardware.com/news/nasa-details-tech-that-recycles-urine-into-drinkable-water; thenews.com.pk/latest/1085170) |
| C-2 | *Status of the ISS Regenerative ECLSS Water Recovery and Oxygen Generation Systems* | P8 — estado de los bucles de agua y oxígeno | researchgate.net/publication/24338663 |
| C-3 | Broyan Jr. et al., *NASA Environmental Control and Life Support Technology* | P8 — operación integrada de ECLSS bajo carga humana real | ttu-ir.tdl.org (bitstream 916fa59a) |
| C-4 | Jones, H.W. 2019, *High Reliability Requires More Than Providing Spares* (NASA NTRS 20190027319) | P11 — la bomba del procesador de orina como peor componente; fiabilidad ≠ repuestos | ntrs.nasa.gov/api/citations/20190027319 |
| C-5 | Russell et al. 2007, *Maintenance, reliability and policies for orbital space systems* (Reliability Eng. & System Safety) | P11 — desviaciones de mantenimiento ISS 60,4% sobre tiempo de diseño | sciencedirect.com/science/article/abs/pii/S0951832006001050 |
| C-6 | *Failure Mode and Effects Analysis for ECLSS Self-Awareness* (2020) | P8/P11 — el sistema "deberá detectar y diagnosticar su salud en tiempo real" | researchgate.net/publication/343402989 |
| C-7 | Miyajima, *ECLSS Analysis for Mars Missions* | P11 — diseño de fiabilidad con MTBF operativo ISS | ttu-ir.tdl.org (bitstream db4d7e26) |
| C-8 | Chen, D. et al. 2013, *Non-Intrusive Occupancy Monitoring using Smart Meters* (~273 citas) | P9 — ocupación/actividad desde curva eléctrica | ecs.umass.edu/irwin/niom.pdf |
| C-9 | Devlin, M.A. 2019, NILM y clasificación de actividades de la vida diaria (~192 citas) | P9 — ADL desde carga eléctrica | cora.ucc.ie/handle/10468/8119 |
| C-10 | Barger, L.K. et al. 2014, *Lancet Neurology* 13(9):904–912 (déficit de sueño en vuelo, actigrafía) | P9 — el dominio sueño está medido y es deficiente | via PMC5022007 |
| C-11 | Kawada, T. 2016, *Applicability of the actigraphy for astronauts in spaceflight* (Sleep Sci.) | P9 — actigrafía en vuelo: el estándar que P9 reemplaza | pmc.ncbi.nlm.nih.gov/articles/PMC5022007 |
| C-12 | Ramdas, A. et al. 2020, *Admissible anytime-valid sequential inference must rely on nonnegative martingales* (arXiv:2009.03167) | MP-8 — fundamento de e-procesos | arxiv.org/abs/2009.03167 |
| C-13 | Ramdas, A. et al. 2023, *Game-Theoretic Statistics and Safe Anytime-Valid Inference* (Statistical Science 38(4)) | MP-8 — el survey del campo | projecteuclid.org (10.1214/23-STS894) |
| C-14 | Lanata, C.F. et al. 1991, *LQAS techniques* (WHO/IRIS, ~115 citas) | MP-10 — LQAS con muestras pequeñas | iris.who.int/bitstreams/6966cb92 |
| C-15 | Pagano, M. et al. 2010, comentario práctico sobre LQAS (PMC2817093) | MP-10 — clasificación correcta en extremos, potencia de muestras pequeñas | pmc.ncbi.nlm.nih.gov/articles/PMC2817093 |
| C-16 | Harle, M. & Chatelain, F., *Rank-based multiple change-point detection in multivariate time series* | MP-9 — changepoint sobre vector de residuos | semanticscholar.org (979dd419c2bd) |
| C-17 | *ECLSS Analysis for Mars Missions: Addressing Failure and Maintenance* | P11 — fiabilidad regenerativa con datos operativos ISS | ttu-ir.tdl.org |
| C-18 | Swanson, C.M. et al. 2017/2018, *The importance of the circadian system & sleep for bone health* (~222 citas) | FM-3 reanclado — la interrupción circadiana deteriora la formación ósea | pmc.ncbi.nlm.nih.gov/articles/PMC5994176 |
| C-19 | Endocrine Society 2017, *Prolonged sleep disturbance can lead to lower bone formation* (hombres sanos, 3 semanas) | FM-3 reanclado — el efecto en humanos, con marcador medible en sangre | endocrine.org/news-and-advocacy/news-room/2017 |
| C-20 | Flynn, C.F. 2005, *An operational approach to long-duration mission behavioral health and performance factors* (~57 citas) | FM-10 — salud conductual como factor operativo con 4 dominios; datos objetivos para decisiones de misión | pubmed.ncbi.nlm.nih.gov/15943194 |
| C-21 | NASA HH&P, *Behavioral Health* (2023) | FM-10 — privacidad, carga y separación declaradas factores de riesgo | nasa.gov/directorates/esdmd/hhp/behavioral-health |
| C-22 | Mathunjwa, M. et al. 2025, *A Comprehensive Review of Home Sleep Monitoring Technologies* (Sensors 25(6):1771) | P9 / §0.6 — el monitoreo pasivo multi-sensor del sueño es campo establecido | pmc.ncbi.nlm.nih.gov/articles/PMC11945902 |
| C-23 | *Pandorum* (2009, dir. Christian Alvart) — fuente de ficción declarada | FM-10 — la pregunta dramatizada; la ficción es cantera declarada del bestiario K-1 | en.wikipedia.org/wiki/Pandorum |

*(Las anclas heredadas de MAP-S1 —Angelopoulos & Bates, Adams & MacKay, WBE/Verani/Hsu/Foladori, Gratius AIAA 2024, Michels 2025, Linardon 2025— siguen vigentes en K-5 y no se repiten aquí.)*

---

## Cómo vive este documento

- Es hermano de MAP-S1: no lo modifica por sí mismo. Su salida operativa era el parche del Apéndice A — **aplicado el 11-nov-2026 con aprobación explícita del equipo (MAP-S1 v0.2)**.
- **v0.1 → v0.2 (11-nov):** se retiró la narrativa de método interno (las tablas de destrucción y fusión quedan en v0.1 como acta — nada se perdió); se añadieron §0.6 (balanza salud–hábitat) y §1 (laboratorio del astronauta); las propuestas abren con su traducción a salud; FM-3 reanclada (C-18/C-19); FM-10 propuesta (C-20…C-23). Los preregistros, hashes y semillas no cambiaron en absoluto.
- MAP-S1 pasó a v0.2 el 11-nov (filas A.1–A.3 + adiciones de DOC-04: DC-12, FA-4, GO-7, cola M-L). Las cuatro falsaciones FB-005…008 se ejecutan en IN-4 en el orden del §5.
- Si una falsación mata a su propuesta: el acta pública se escribe y la propuesta pasa a la sección de ideas dormidas con su razón — este documento ya lo anticipa: **la muerte con acta vale más que la supervivencia sin prueba.**
- Después del 14-nov, este documento se congela como acta fundacional de la nueva generación; su contenido vivo migra a MAP-S1 v0.2.
