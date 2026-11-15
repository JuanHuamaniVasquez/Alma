# TONO-LAB · DOC-04 — LA FUNDICIÓN: El Laboratorio del Astronauta (v0.2)

> **Qué es este documento:** la definición completa del **segundo corazón** de ALMA — el laboratorio que acuña hipótesis. Extiende la §1 de DOC-02 (el ciclo de 5 pasos, las H-cards, las canteras) con lo que ahí no estaba: el **contrato de entrada/salida** de la máquina, la **prueba numérica de infinitud**, las **diez ideas de diseño con su porqué**, el **test de originalidad** (qué lo hace distinto de lo que un prompt genérico produce) y la **prueba de estrés a escala interplanetaria/interestelar** (qué sobrevive, qué muere, qué nace).
> **Relación con los demás docs:** este documento extiende a MAP-S1 (DOC-01) y a DOC-02. **Sus propuestas formales (DC-12 Contrato de Fundición, FA-4 El Faro, GO-7 MODO FRONTERA, cola M-L1…M-L5) fueron APROBADAS por el equipo y APLICADAS a MAP-S1 v0.2 el 11-nov-2026.** DC-08…DC-11 quedaron reservados por DOC-02 (Apéndice A, aplicado el mismo día); por eso el contrato del laboratorio es **DC-12**.
> **Disciplina heredada:** nada se codea sin fila en el registro; toda tarjeta lleva preregistro hasheado antes de ejecutar; el rechazo también se escribe.
> **Fecha:** 2026-11-11. **Nombre de trabajo:** LA FUNDICIÓN (entra residuo, sale detector). Decisiones abiertas en §11.
> **Qué cambió de v0.1 a v0.2 (mismo día):** (1) **corrección de fondo en §6** — un viaje largo no significa que no necesitemos a la Tierra: la Tierra queda, con latencia (ida y vuelta de señal ≈ 8,5 años); el lab mantiene la medicina viva mientras la respuesta viaja; (2) nuevo **§7 · EL CASO DE ESTUDIO** (misión a α Centauri / Proxima b): caso, propósito, objetivos medibles y preguntas con su método de resolución; (3) DC-12, FA-4 y GO-7 pasan de PROPUESTA a **APLICADOS** en MAP-S1 v0.2; (4) compromisos del lab recalibrados con corte honesto (≥5 tarjetas, techo 10).

---

## §0 · Una línea

*El Guardián vigila; LA FUNDICIÓN pregunta. Uno responde "¿qué está pasando?"; el otro responde "¿qué no sabemos que está pasando?" — y paga su existencia en detectores nuevos.*

## §1 · Los dos corazones

- **Corazón 1 — El Guardián (monitoreo y aviso).** Es lo que el jurado compra y lo que el challenge de NASA pide palabra por palabra ("health *monitoring* software"). Es LA SALA, EL RESIDUO, LA TORMENTA.
- **Corazón 2 — LA FUNDICIÓN (el laboratorio).** No monitorea ni avisa: **acuña preguntas**. Cruza información y produce hipótesis anticipatorias — el "nos adelantábamos" del laboratorio original del equipo, ahora con disciplina de ingeniería.

Por qué se necesitan los dos y no solo el primero: **un monitor con reglas fijas envejece.** Sus umbrales son estáticos y sus alarmas cubren lo que ya sabíamos vigilar. En una misión larga, lo que daña no es lo sabido — es lo que nadie sabía que había que vigilar. Sin laboratorio, ALMA es un guardia que envejece; con laboratorio, es un tripulante que aprende. Cada hipótesis que sobrevive **compila en un detector nuevo para el Guardián** — esa es la circulación entre los dos corazones. Monitoreo sin laboratorio queda ciego; laboratorio sin monitoreo es estéril.

**La cerradura de enfoque (salud, no hábitat):** el hábitat no es el paciente ni el protagonista — es **variable de entrada del cuerpo**. La radiación importa porque toca el ADN; el CO₂ porque toca la cabeza; el ruido porque toca el sueño. En la ficción (*Pandorum*, 2009) el hábitat se come a la tripulación; en ALMA el hábitat es testigo y el paciente es la persona. El contrato DC-12 (§9) es la cerradura: si una hipótesis no compila en detector **del cuerpo**, es decoración y muere en el acta.

## §2 · Contrato de entrada/salida de la máquina

**CONSUME — cinco clases:**

1. **Los residuos del monitoreo** (alimento principal): alertas sin causa, días "normales pero raros", cruces que no cuadran, discrepancia entre sensor y relato. Los datos conocidos responden preguntas conocidas; el residuo es la huella de lo desconocido.
2. **Cuerpos públicos con identificador:** OSDR/GeneLab (OS-892 y análogos), NTRS, literatura citable (PNAS 2026, Lancet Neurology 2014, Swanson 2017/2018, Mehta 2014/2017, Slack 2015 — las anclas ya verificadas en DOC-02 Apéndice C), informes de incidentes.
3. **El flujo del hábitat como entrada del cuerpo:** CO₂, radiación, ruido, luz, temperatura, ejercicio, menús, agua (los 9 presupuestos de LB-1 ya son este flujo).
4. **El relato de la tripulación:** sueño subjetivo, ánimo, diario — lo que el sensor no ve (Canal B, IN-2).
5. **Su propio cuaderno:** hipótesis pasadas, veredictos, semillas, métodos que funcionaron (LA MESA, LA CÁPSULA).

**DEVUELVE — cinco clases:**

1. **Hipótesis acuñadas, en tarjetas (H-cards extendidas):** par de variables + mecanismo + predicción falsable + señal refutadora escrita antes + **precio** (datos, cómputo, días) + **valor** (qué detector nuevo existe si es cierta) + **fuente con identificador** + hash de preregistro.
2. **Diseños de prueba:** primero in-silico (Banco de Falsaciones, IN-4), luego ensayo sobre datos públicos, luego N-of-1 A-B-A-B de bajo riesgo (FA-2).
3. **Veredictos en acta pública:** refutada / sostenida / sin datos suficientes — las tres respuestas honestas (LA MESA).
4. **Artefactos para el otro corazón:** detectores nuevos DC-xx, umbrales, índices compuestos, reglas de preaviso. **El laboratorio paga renta en capacidad de detección, no en papers.**
5. **La cola priorizada:** top-10 por (novedad × viabilidad × daño-si-es-cierto) ÷ precio. La FUNDICIÓN siempre sabe qué mirar hoy.

## §3 · La infinitud: por qué "respuestas infinitas" es diseño, no poesía

Un lab "para dos o tres respuestas y queda" es una lista, no un laboratorio. La infinitud exige **tres fuentes simultáneas** — si falta una, el lab muere en finitud:

1. **Espacio combinatorio.** 40 señales del cuerpo × 25 señales del hábitat = 1.000 cruces. Con 8 familias de mecanismo × 5 desfases temporales × 6 estratos (sexo, edad, fase de misión, cronotipo, densidad, adaptación) = **240.000 celdas candidatas**. A ritmo humano de 10 hipótesis serias por día son **65,8 años de preguntas**. En ómica (OSDR) las variables se cuentan por decenas de miles: el espacio real es astronómico. Nadie lo agota.
2. **Combustible renovable.** Cada semana el Guardián acumula residuo nuevo y cada mes llega dato público nuevo. El residuo regenera preguntas solo.
3. **Auto-mejora.** Cada ciclo reordena priors: qué mecanismos pagan, qué cruces son baldíos. Se vuelve mejor preguntando (idea 10).

## §4 · Las diez ideas de diseño — cada una con su porqué

| # | Idea | Qué es | Por qué |
|---|---|---|---|
| 1 | **Minería de residuos** | El lab empieza donde el Guardián terminó: la materia prima es lo no explicado | Única mina de preguntas nuevas; todo lo demás son respuestas recicladas |
| 2 | **El Cruzador sistemático** | La matriz de cruces con mecanismo, desfase y estrato; preregistro por celda | Un humano prueba 10 hipótesis; la máquina enumera 240.000 y elige las 10 que valen atención. El lab no responde preguntas: **acuña preguntas** |
| 3 | **Mecanismo obligatorio** | Toda hipótesis cabalga un camino fisiológico de la biblioteca (eje HPA, cambio de fluidos, resorción ósea, circadiano, inmunidad, microbioma) | Minería de correlaciones a escala produce basura industrial; el mecanismo la convierte en ciencia defendible — y poda 240.000 celdas a unas miles |
| 4 | **Hipótesis con precio** | Nada entra a la cola sin costo (días/datos/cómputo) y valor (detectores nuevos) | Antídoto contra el lab-fantasía; conecta la exploración con la realidad de 3 devs; métrica jurable: detectores nuevos por ciclo |
| 5 | **La piara de gemelos digitales** | Población de tripulaciones simuladas (fisiología + conducta + horarios) en el mismo esquema de telemetría | El n real del espacio es de un dígito (los gemelos Kelly fueron 2); la simulación da potencia estadística y falsa sin poner a nadie en riesgo. Ya existe la cultura de semillas — extenderla de "detectar" a "experimentar" |
| 6 | **El Adversario** | El lab también juega en contra: genera tripulaciones sintéticas enfermas que evaden detectores; cada escape se vuelve pregunta de investigación | Casos adversarios infinitos sin astronautas; evolución natural de la demo kill / El Contrapeso |
| 7 | **La Materia Oscura** | Cruzar lo poco sexy: ciclos del scrubber de CO₂ vs cefaleas (ancla: 19 de 49 astronautas, familia 5 de K-2), ruido vs sueño, reuso del agua vs microbioma, menús vs ánimo | Novedad barata y enorme; nadie la está haciendo; es la resolución operativa de la balanza salud–hábitat |
| 8 | **El cuaderno que se escribe solo** | Cada corrida deja su preregistro con hash: pregunta, datos, método, veredicto | Salida infinita sin procedencia = ruido infinito; la auditabilidad es lo que separa al explorador del delirante |
| 9 | **El Faro** | Predicciones fechadas ANTES de que lleguen los datos; cuando el dato llega, el lab se califica en público | Cada predicción es un experimento gratis; convierte la anticipación — la intuición original del equipo — en métrica: tasa de acierto y días de preaviso |
| 10 | **El meta-lab** | Tras cada ciclo reescribe sus priors: qué mecanismos pagan, qué cruces no valen | La infinitud profunda: no solo respuestas infinitas — **preguntas infinitas mejores**. Es el movimiento de los co-científicos de IA y labs autónomos, sin precedentes conocido en salud espacial con datos abiertos |

**Sinergias con el registro existente (MAP-S1):** la idea 5 vive en IN-4 (Banco de Falsaciones); la 6 estresa a MO-1…MO-4; la 1 consume el residuo de MO-2; la 7 cruza LB-1 con DC-08/DC-09; la 11 de DOC-11 (hazard de sensor) alimenta la idea 4 con el costo real de instrumento; la 9 y la 8 viven en LA MESA y LA CÁPSULA.

## §5 · Test de originalidad — qué lo hace único (y qué no)

**El test del prompt (reproducible).** Pedir a cualquier IA "diseña un laboratorio de hipótesis para salud de astronautas" produce, con alta confianza: ingestión de datos → ML de anomalías → LLM acuña hipótesis → dashboard de "insights". Eso es la respuesta de primera mano — y es exactamente lo que el equipo teme parecer. La FUNDICIÓN difiere de ese molde en **cinco lugares verificables**:

1. **El contrato de salida.** El molde genérico publica "insights" (texto). La FUNDICIÓN solo publica lo que **compila en detector** (DC-12: tarjeta → DC-xx o muerte). "Insight" no-compilable es decoración y muere en acta.
2. **El combustible.** El molde mina el corpus. La FUNDICIÓN mina el **residuo del Guardián** — y ahí está el punto estructural: *el residuo no existe para quien no construyó primero el monitor*. Un prompt aislado no tiene Guardián; ni siquiera puede formular esta fuente. La originalidad no está en una pieza: está en la **posición en el pipeline** (el lab vive aguas abajo de un detector que ya miente de forma medible).
3. **La disciplina como arquitectura.** Preregistro hasheado antes de ejecutar; tres veredictos honestos; precio por tarjeta; Faro con fecha. El molde optimiza hipótesis que suenan bien; la FUNDICIÓN optimiza **hipótesis baratas de matar**. La presión de selección es distinta, y por eso el organismo es distinto.
4. **La escala de pobreza.** 3 devs, cero laboratorio físico, cero astronautas, datos públicos, días de reloj. Toda tarjeta pasa el filtro "¿la falsa una persona con laptop en una semana con lo que hay en la bodega?". El molde genérico asume recursos empresariales; esto es diseño bajo restricción real — y al jurado le encanta porque es creíble.
5. **El Adversario interno.** El molde "valida con datos de test". La FUNDICIÓN institucionaliza el ataque: el lab genera evasiones contra el propio Guardián y cada escape entra como pregunta de investigación. El fracaso se vuelve combustible.

**El test de la cita (anti-alucinación por construcción).** La FUNDICIÓN no acuña de memoria: **solo acuña de fuentes cargadas con identificador** (número de accesión OSDR, DOI, lote de telemetría con semilla). Sin fuente cargada, no hay tarjeta — la puerta rechaza la cita inventada. La alucinación no se "reduce": no tiene entrada.

**Admisión honesta (lo que NO es único).** Cada pieza existe en la frontera: hay co-científicos de IA, laboratorios autónomos, minería de residuos clínica y premortems institucionales. El foso no es el inventario de piezas — es (a) el **contrato entre piezas** (residuo → tarjeta con precio → detector, con hashes en cada tramo), (b) el **estado acumulado**: un prompt no tiene memoria ni residuo; la FUNDICIÓN acumula veredictos y se compone semana a semana. La semana 1 y la semana 52 no son el mismo laboratorio. Ese es el activo que un prompt no puede regalar.

**La línea que resume la postura:** *quedarse con lo primero que da una IA es tomar la hipótesis más cara de todas — la que todos comparten. La originalidad en un jurado es diferencial: vale lo que nadie más pueda obtener con el mismo atajo.*

## §6 · Prueba de estrés — misión a otro sistema solar

**El escenario.** El sistema α Centauri; destino concreto del caso de estudio (§7): **Proxima b, 4,25 años luz**. A 0,1c de crucero son ~42,5 años de vuelo; a 0,01c, ~425. Sin reabastecimiento ni retorno; la Tierra sigue escuchando, pero cada pregunta cuesta una ida y vuelta de señal de ~8,5 años; sensores que mueren sin repuesto; el único n humano es la tripulación y sus hijos. Se lleva la arquitectura de ALMA entera a ese caso y se mira qué sobrevive.

**Lo que sobrevive sin cambios (los invariantes):** el metabolismo de dos corazones; el residuo como combustible (una nave genera residuo eterno); el mecanismo obligatorio; el precio por tarjeta; el preregistro y el Faro; el Adversario. *Si algo de esto sobrevive a ~425 años, es porque es arquitectura y no feature.*

**Lo que muere — y hay que destruirlo a conciencia:**

1. **El paciente-individuo.** En ~42,5–425 años el paciente es la **estirpe**: cuello de botella genético fundacional, deriva epigenética, presión selectiva (radiación, ecología cerrada). La salud se vuelve transmisiva: estás sano si le entregas a la próxima generación una línea base no degradada.
2. **El umbral estático.** Todo umbral fósilizado por generaciones se vuelve la enfermedad: cada cohorte normaliza un poco peor (ejemplo ilustrativo: la generación 1 acepta 6,2 h de sueño promedio; la generación 4 acepta 5,4 y lo llama normal — nadie lo ve porque nadie recuerda todas las líneas base… excepto el lab). Umbrales con vida media y re-acuñación programada.
3. **La consulta instantánea muere — la Tierra no.** Corrección importante de v0.2: un viaje largo **no significa que no necesitemos a la Tierra**. El uplink y el downlink siguen: la nave envía sus datos y recibe ciencia nueva, y la Tierra sigue siendo la fuente de verdad y la auditora independiente — lo que cambia es el **precio temporal de cada pregunta**: a 4,25 años luz, la ida y vuelta de señal es ≈ **8,5 años**. La consulta es posible; ya no es operativa en el momento clínico. Por eso el lab no reemplaza a la Tierra: **mantiene la medicina viva mientras la respuesta viaja** — y un error suyo, mientras tanto, no se corrige con una revisión de la literatura sino en años: se fósiliza en doctrina por décadas. La alucinación a escala secular no es un bug: es una **mutación del acervo de conocimiento de la especie** — por eso la disciplina (procedencia, refutaciones, preregistro) es sistema inmune, no higiene académica.

**Lo que nace — cinco módulos frontera (roadmap, no comprometidos; encajan en el registro existente):**

| Módulo | Qué hace | Dónde enchufa en MAP-S1 |
|---|---|---|
| **M-L1 · EL ARCHIVO DE GENERACIONES** | Líneas base por cohorte; detección de deriva entre generaciones (la rana hirviendo es el peligro operativo #1 de la nave) | Extensión multi-cohorte de MO-1 (modelo nulo personal) |
| **M-L2 · UMBRAL VIVO** | Reglas del Guardián con fecha de vencimiento y re-acuñación programada por el lab | Configuración de MO-2/MO-3 con TTL y auditoría |
| **M-L3 · HIPÓTESIS PERECEDERAS** | Toda tarjeta lleva plan de muerte del sensor; preguntas con fecha de caducidad ("probable solo hasta el año X"); la cola se ordena por vida media instrumental | Consume `hazard_dia` y `estado` de DC-11 |
| **M-L4 · SENADO EPISTÉMICO** | Decisión con confianza explícita ante evidencia conflictiva; re-litigación programada; doctrina versionada y refutable | Extensión de LA MESA (actas) con columna de confianza y fecha de re-apertura |
| **M-L5 · GENOMA DE CONOCIMIENTO** | Procedencia total, libro de refutaciones, integridad del cuaderno como carga crítica de la nave | Extensión de LA CÁPSULA + actas GO existentes |

**Veredicto del estrés.** La arquitectura **sirve**. El extremo no la derriba: la demostró. Lo único que murió bajo estrés era lo que el proyecto ya quería matar (umbrales estáticos, paciente único, verdad importada). Y el Faro, a esta escala, se vuelve institucional: predicciones con horizonte de años, calificadas cuando el dato madura.

## §7 · EL CASO DE ESTUDIO — la misión a α Centauri (Proxima b)

> Una línea: *el caso no se construye: se usa como horno — una misión real hacia el sistema estelar más cercano pone cada módulo de ALMA bajo el estrés máximo, y lo que sobrevive es arquitectura, no feature.*

**Por qué este caso y no otro.** No es poesía elegida al azar:

1. **Es el destino más cercano que existe:** Proxima Centauri, **4,25 años luz** (medido por paralaje; la estrella más cercana al Sol). Tiene un planeta conocido en zona habitable: **Proxima b** (Anglada-Escudé et al., *Nature*, 2016; periodo orbital ~11,2 días; masa del orden de la terrestre).
2. **Su estrella es una fábrica de tormentas:** Proxima es una enana roja con llamaradas extremas documentadas (incluida la superllamarada de marzo de 2017, observada por múltiples observatorios). El problema #1 de radiación de la misión es **exactamente la física que LA TORMENTA ya calibra con el Sol** (NOAA SWPC): misma clase de detector, otra estrella. La invariancia deja de ser eslogan y se vuelve plan de reanclaje.
3. **Es la escala que rompe todos los supuestos cómodos:** 4,25 años luz a 0,1c de crucero ≈ **42,5 años** de vuelo. Sin reabastecimiento, sin retorno, ida y vuelta de señal ≈ **8,5 años**. Lo que sobrevive a esto es arquitectura (§6).

**El caso (supuestos declarados):** nave tripulada con crucero de 0,1c (**supuesto de ejercicio, no un claim de propulsión**); tripulación fundadora + descendientes (el n humano de la misión crece, no se repone); destino Proxima b; la Tierra sigue existiendo y escuchando — con latencia de años (§6, corrección de v0.2).

**El propósito (para qué sirve ALMA ahí):** que la tripulación y su estirpe lleguen **sanas, no solo vivas** — y que la nave llegue sabiendo más medicina que cuando salió. El primer objetivo sin el segundo es una cárcel sana; el segundo sin el primero es un laboratorio con pasajeros.

**Los objetivos (medibles):**

| # | Objetivo | Métrica |
|---|---|---|
| O1 | Salud no degradada entre generaciones | Deriva de línea base inter-cohorte detectada y corregida (M-L1); cero "normalización del empeoramiento" |
| O2 | Preaviso de tormentas y derivas | Días de preaviso ≥ 21 para tormenta estelar (heredado de FB-002 con el Sol; reanclado a llamaradas de Proxima) y para derivas de salud (CUSUM) |
| O3 | Conocimiento que crece | ≥1 tarjeta acuñada por semana de la FUNDICIÓN; doctrina clínica versionada con procedencia (M-L5) |
| O4 | Honestidad como piso | Cero alarmas sin recibo; cero doctrina sin hash; tasa de falsa cuarentena publicada (GO-6) |
| O5 | Autonomía bajo latencia | Toda decisión clínica conflictiva con confianza explícita y fecha de re-litigación (M-L4); cero doctrina de época sin fecha de caducidad (M-L2) |

**Las preguntas del caso y quién las resuelve:**

| Pregunta | Resolución (módulo/contrato) |
|---|---|
| Q1 ¿Cómo se vigila la salud sin repuestos ni vuelta? | Demografía de testigos (DC-11/MO-8) + hipótesis perecederas (M-L3): la cola se ordena por vida media instrumental |
| Q2 ¿Se detecta la tormenta de una estrella que no es el Sol? | Sí, por clase: la física de la llamarada es la misma; LA TORMENTA re-ancla sus catálogos del Sol (SWPC) a llamaradas de Proxima; el detector no cambia, la fuente sí |
| Q3 ¿Cómo se ve la deriva si cada generación renormaliza su "normal"? | M-L1 Archivo de Generaciones (extensión multi-cohorte de MO-1): el lab es el único que recuerda todas las líneas base |
| Q4 ¿Qué se hace cuando la evidencia se contradice y la Tierra tarda 8,5 años? | M-L4 Senado Epistémico: decisión con confianza explícita, re-litigación programada, doctrina versionada — medicina bajo latencia |
| Q5 ¿Cómo se evita que un error del lab se vuelva verdad por décadas? | M-L5 Genoma de Conocimiento: procedencia, libro de refutaciones, preregistros GO-2 — la alucinación es mutación del acervo, la disciplina es el sistema inmune |
| Q6 ¿Qué prueba que esto es arquitectura y no poesía? | La prueba de enchufe: cada M-L consume contratos que ya existen (M-L3 ← DC-11; M-L1 ← MO-1; M-L4 ← LA MESA). Lo que no enchufa, es decoración |
| Q7 ¿Y qué hace esto por la misión real de hoy (ISS/OSDR, 14-nov)? | Nada se construye para α Centauri hoy. El caso es el horno que expone invariantes y la respuesta dura ante "¿y en Marte?": la misma arquitectura, un reanclaje de catálogos |

**Honestidad del caso:** la velocidad de crucero y la nave son supuestos de ejercicio (declarados). Las anclas reales: la distancia (paralaje de Proxima), el planeta (Anglada-Escudé et al. 2016, *Nature*) y las llamaradas (observaciones 2016–2017). El caso no genera claims científicos; genera requisitos de diseño.

## §8 · Los dos modos — visión sin delirio

El equipo pidió "extremo, sin límites ni reglas". La resolución correcta no es elegir entre límites y frontera — es separarlos en **dos modos con puertas entre sí**:

- **MODO DIVERGENCIA (acuñar): sin límites.** Todo cabe: mecanismos raros, cruces prohibidos, preguntas de ficción (cantera K-1), escalas absurdas, un sistema solar entero como paciente. Regla única de salida: nada entra a la cola sin fuente con identificador, precio y hash. **Una alucinación con hash y precio deja de ser alucinación: es hipótesis.**
- **MODO CONVERGENCIA (verificar): sin piedad.** Falsar barato, calificar el Faro en público, matar tarjetas por escrito. **Una frontera sin falsación es ciencia ficción** — la ficción es cantera legítima (FM-10 ya lo prueba), pero lo que sale de ella debe pagar el mismo peaje que lo demás.

**MODO FRONTERA** (aplicado como **GO-7** en MAP-S1 v0.2): sesión programada de divergencia tras cada ciclo de falsación — la ventana donde el equipo "se adelanta" con método y sin culpa. Su único output permitido: tarjetas al vivero.

## §9 · Propuestas formales — APROBADAS y APLICADAS a MAP-S1 v0.2 (11-nov-2026)

1. **DC-12 · Contrato de Fundición** (campo a campo — **aplicado a MAP-S1 v0.2, fila en §3**):

| Campo | Tipo | Nota |
|---|---|---|
| `tarjeta_id` | uuid | Toda tarjeta vive o muere con este id |
| `par_variables` | ref × ref | Señal del cuerpo × señal (cuerpo/hábitat/relato) |
| `mecanismo` | ref biblioteca FA | Obligatorio (idea 3); "correlación sin mecanismo" no pasa la puerta |
| `prediccion` | texto falsable | Qué debería observarse, cuándo, con qué tamaño de efecto mínimo |
| `senal_refutadora` | texto | Escrita antes de probar (heredada de las H-cards de DOC-02 §1) |
| `fuentes[]` | lista de ids externos | Accesión OSDR / DOI / lote con semilla. Sin fuente cargada, la tarjeta no existe |
| `precio` | {datos, cómputo, días} | Idea 4; incluye costo de instrumento vía DC-11 |
| `valor_si_cierta` | detector(es) DC-xx nuevos | El único modo de pagar renta |
| `estado` | enum: vivero · en_prueba · refutada · sostenida · sin_datos | Tres veredictos honestos + dos estados de trabajo |
| `preregistro_hash` | sha-256 | Antes de ejecutar (GO-2) |
| `vencimiento` | ts_utc (opcional) | M-L3: preguntas perecederas |

2. **Módulos M-L1…M-L5** → añadidos a la cola §7 de MAP-S1 v0.2 como **ROADMAP DE FRONTERA** (no comprometidos para el submit; su valor hoy es la prueba de enchufe).
3. **MODO FRONTERA** → aplicado como **GO-7** en el registro de MAP-S1 v0.2.
4. **Compromisos medibles del lab para el submit (14–15 nov), recalibrados con corte honesto:** **≥5 tarjetas acuñadas** (techo: 10) desde K-2 + OS-892, **1 predicción del Faro fechada**, **1 escape del Adversario documentado**. Todo con hash antes de ejecutar. Si el tiempo aprieta, el corte es 5 — el lab no infla.
5. **FA-4 · El Faro** y **GO-7 · MODO FRONTERA** — filas nuevas del registro (Capa 3 y Gobernanza de MAP-S1 v0.2), creadas durante la aplicación.

## §10 · Guardarraíles para el submit

- La vitrina del jurado es **salud del astronauta** (el challenge); el hábitat entra solo como variable de entrada (cerradura de §1).
- Una sola línea de frontera en la demo, no un módulo: *"la misma arquitectura vigila a 400 km o a 4,25 años luz: umbrales vivos, líneas base por generación, conocimiento con procedencia"* — el caso completo está en §7.
- No construir M-L1…M-L5 ahora: su valor hoy es **prueba de invariancia** de lo ya diseñado.
- El lab muestra su métrica, no su poesía: tarjetas nacidas → en prueba → refutadas → sostenidas → **detectores nuevos** (LA MESA ya pinta esto).

## §11 · Decisiones abiertas

1. **Nombre del lab:** LA FUNDICIÓN (preferente — es el que ya usan este doc y el pitch v0.2) / EL VIVERO / EL CRUCE / SEGUNDO CORAZÓN. Firma pendiente del equipo.
2. **Primera tarjeta del Faro:** elegir par y fecha límite de calificación (candidata natural: FM-3 sueño × hueso sobre OS-892, reanclada con Swanson 2017/2018 — anclas C-18/C-19).
3. **Presentación del caso de estudio (§7) ante el jurado:** ¿una línea en la demo + defensa de preguntas (recomendación), o una diapositiva propia? Recomendación: línea + defensa — el caso convence, no decora.

---

### Registro de cambios

| Versión | Fecha | Qué cambió |
|---|---|---|
| v0.1 | 2026-11-11 | Primera acuñación: dos corazones, contrato E/S, infinitud (240.000 celdas / 65,8 años), diez ideas, test de originalidad (5 deltas + test de la cita), prueba de estrés interestelar (invariantes/muertes/M-L1…L5), dos modos, DC-12, guardarraíles de submit |
| v0.2 | 2026-11-11 | Corrección de la Tierra (latencia ≠ ausencia; ida y vuelta ≈ 8,5 años); nuevo §7 caso de estudio Proxima b (propósito, objetivos O1–O5, preguntas Q1–Q7); DC-12/FA-4/GO-7 aplicados a MAP-S1 v0.2; compromisos del lab con corte honesto (≥5 tarjetas) |
