# TONO-LAB · PITCH ALMA — Documento de equipo (v0.2)

> **Qué es este documento:** el guion para que las 3 personas del equipo entiendan ALMA, sepan exactamente qué van a construir, qué van a usar en la demo y qué van a decir ante el jurado el 14-nov.
> **Cómo leerlo:** está escrito en lenguaje claro para gente de software. Cada término técnico se explica la primera vez que aparece, siempre con un ejemplo con números. Los IDs (LB-1, DC-04, MO-3…) son los del proyecto real — aparecen entre paréntesis para que puedas buscar el detalle en los mapas.
> **Relación con los otros documentos:** nada aquí borra o reemplaza nada. La ley del proyecto es MAP-S1 (contrato de ingeniería, **v0.2 desde el 11-nov**), MAP-S2 (propuestas nueva generación) y **DOC-04 · LA FUNDICIÓN** (el laboratorio, v0.2). Este documento los **traduce** a lenguaje de equipo y de escenario. Si hay duda técnica, gana el mapa.
> **El challenge (verificado):** "Create Health Monitoring Software for Astronauts on Space Missions" — NASA Space Apps 2026, 14-15 nov. Los indicadores que sugiere el brief (presión, ritmo cardíaco, azúcar en sangre, temperatura, horas de sueño, ánimo) son **exactamente** los de nuestro contrato DC-01/DC-02. No hay que adaptar nada.
> **Fecha:** 2026-11-11. **Equipo:** 3 personas de software. **Jurado:** 14-nov.
> **v0.1 → v0.2 (11-nov):** los dos corazones entran a la historia y al glosario (Guardián + LA FUNDICIÓN); línea de frontera del caso Proxima b (DOC-04 §7); preguntas 9 y 10 del banco del jurado; compromisos del lab en el calendario y el checklist.

---

## §1 · La historia en 30 segundos (apréndela de memoria, los tres)

**El problema.** En misiones largas, el astronauta es su propio médico — el brief de NASA lo dice literalmente: *"los astronautas cargan con la responsabilidad de detectar estos cambios en sí mismos"*. Y el hardware miente: en la ISS, el mantenimiento real superó en **~60%** lo previsto en el diseño (Russell 2007), y el peor componente de todo el sistema de soporte de vida es el **procesador de orina** (Jones 2019, NASA NTRS). Los manifiestos — las listas de "lo que cada cosa debería consumir o emitir" — envejecen, se quedan cortas o directamente están mal. Un dashboard que solo compara la medida con su manifiesto te dirá **"todo verde"** mientras el hábitat pierde agua por una fuga que nadie contabiliza.

**La solución en una frase.** ALMA es un **libro contable donde el cuerpo y la máquina rinden cuentas**, con un árbitro externo que no se puede sobornar: la física y el preregistro público con hash. Detecta lo que un dashboard normal no puede ver — y cuando se equivoca, la alarma lleva impresa la regla exacta que la provocó, y se retira sola si la regla no se cumple. Y desde el 11-nov ALMA tiene **dos corazones**: el **Guardián** (monitorea y avisa) y **LA FUNDICIÓN** (el laboratorio que acuña preguntas: entra residuo, sale hipótesis con fuente, precio y hash — y las que sobreviven se vuelven detectores nuevos del Guardián).

**La demo kill.** Un experimento en vivo: inyectamos una fuga "invisible" en el hábitat simulado. El detector tradicional (contra el manifiesto) queda **ciego**. El nuestro — **El Contrapeso** (P8/D8), que cuadra el libro contra la **ley de conservación** — lo ve. Y el preregistro del experimento está publicado con hash SHA-256 **antes** de correrlo: nadie puede acusarnos de ajustar la regla después de ver el resultado.

**La frase de memoria:**
> *"Los sensores pueden mentir. La física, no. ALMA hace que el hábitat y el cuerpo rindan cuentas contra leyes verificables — y nos auditamos a nosotros mismos con preregistros públicos."*

---

## §2 · El guion del pitch ante el jurado (5-7 minutos, 3 actos)

### ACTO 1 — El número que duele (90 segundos) · lo cuenta la persona A

1. **Apertura con la frase del brief:** "NASA pide software de monitoreo de salud para misiones largas, donde el astronauta es su propio médico. ¿Y si el problema no fuera falta de datos, sino que los datos que tenemos pueden mentir?"
2. **Las dos cifras:** mantenimiento real **+60% sobre lo diseñado** (ISS real) y el procesador de orina como peor componente — el hardware de soporte de vida es lo más frágil de la misión, y sus manifiestos envejecen.
3. **El ejemplo que todos entienden** (ejemplo didáctico, el escenario de la demo): "Imagina que la lavadora del hábitat consume 10 litros al día según el fabricante, pero un día empieza a consumir 12 sin que nadie lo registre. El dashboard compara cada sensor con su manifiesto y todo está verde. El libro de conservación, no: entra 100 L, salen 95 L registrados, el tanque solo subió 2 L — **faltan 3 litros que están en algún lado**. Los átomos no desaparecen."
4. **El hueco oficial:** NASA sigue listando el monitoreo médico y ambiental como capacidad insuficiente en sus documentos de brechas tecnológicas (Feb-2025). Nadie está uniendo el libro del cuerpo con el libro de la máquina.

### ACTO 2 — La demo en vivo (3 minutos) · opera la persona B

1. **LA SALA** (pantalla principal): la silueta del hábitat con el anillo de los 9 presupuestos. Todo verde — **y ese es el punto**: lo verde hoy no prueba nada, porque el detector que lo pinta solo compara contra el manifiesto.
2. **LA TORMENTA:** inyectamos una anomalía en el hábitat simulado (o conectamos la actividad solar real en vivo — NOAA SWPC ya corre sin API key; verificamos Kp=3,33 el 9-nov).
3. **EL RESIDUO:** se ve la corriente observado vs. predicho y nace la primera alerta con recibo: regla exacta impresa, semilla que reproduce la corrida, hash del preregistro.
4. **EL CONTRAPESO (el momento que recuerdan):** dos columnas lado a lado — "detector de residuo de manifiesto": ciego; "detector de residuo de ley": alarma. El hash SHA-256 publicado antes de correr, en pantalla.

### ACTO 3 — La credibilidad (2 minutos) · la cierra la persona C

1. **Preregistros con hash:** cada experimento se firma SHA-256 **antes** de ejecutar. Es el estándar de la ciencia real contra el autoengaño (HARKing — inventar la hipótesis después del resultado). Tenemos 8 actas: FB-001 a FB-008.
2. **Resultados reales ya logrados:** FB-002 detectó deriva lenta en **10 de 10** corridas con **preaviso mediano de 21 días** (semillas públicas 20261113/14/15 — cualquiera puede reproducirlo).
3. **La escalera de evidencia T1→T4:** concepto → simulación con semilla → datos reales → tercero replica. Estamos en T2, y el paso T3 ya está en marcha: hay un **estudio registrado en el OSDR** (el repositorio abierto de biociencia de NASA, OS-892).
4. **El cierre:** "No les pedimos confiar en nuestra IA. Les pedimos reproducirnos. Las semillas son públicas, los preregistros tienen hash, y la física es el árbitro."
5. **La frontera (una línea, no un módulo):** "La misma arquitectura vigila a 400 km o a 4,25 años luz: umbrales vivos, líneas base por generación, conocimiento con procedencia." Nuestro horno de estrés es la misión a **Proxima b** — el sistema estelar más cercano (DOC-04 §7).
6. **Las categorías que aspiramos:** Best Use of Science (el método) y Best Mission Concept (El Contrapeso).

---

## §3 · Los conceptos que el equipo debe entender (glosario con ejemplos)

Nadie necesita ser estadístico para construir ALMA. Estos son los conceptos mínimos, cada uno con su ejemplo:

**Manifiesto** — la lista de lo que creemos que cada cosa consume/emite. Ejemplo: "la planta de lechugas transpira 2,5 L/día". Puede estar mal: el fabricante mintió, el hardware envejeció, o la planta está estresada.

**Residuo (r = observado − predicho)** — la diferencia entre lo que pasó y lo que esperábamos. Ejemplo: manifiesto 2,5 L; medimos 3,4 L → residuo = **+0,9 L**. Un residuo grande y repetido es una pregunta que hacer, no un diagnóstico.

**σ (sigma)** — la incertidumbre, el margen normal de ruido. Ejemplo: "±0,3 L". Regla práctica: un día con residuo de 2σ es ruido normal; tres días seguidos a más de 2σ, ya no.

**2σ y CUSUM** — nuestros dos detectores, uno para lo repentino y otro para lo lento. Analogía: el 2σ es el **radar** (ve el pico de ahora mismo); el CUSUM es el **acumulador** (va sumando días apenas-anómalos hasta que la suma grita). FB-002 probó el acumulador: 10/10, preaviso 21 días. (MO-2, MO-3)

**Los 9 presupuestos (LB-1, DC-04)** — el libro contable. La nave y el cuerpo comparten el mismo libro: aire, agua, energía, dosis (radiación), ritmo (sueño/tiempo), carga (física), inmunidad, conducta, tiempo. Regla de oro: **el libro debe cerrar** — como en contabilidad, entradas − salidas = acumulación, dentro del margen.

**Residuo de manifiesto vs. residuo de ley (El Contrapeso, P8/D8)** — la idea que compite por ser la #8 del proyecto. Un detector puede cuadrar sus cuentas contra el manifiesto (que puede mentir) o contra la **ley de conservación** (que no puede mentir: la masa ni aparece ni desaparece). Son clases distintas de detector — la segunda es nueva, y por eso vale.

**Preregistro con hash SHA-256** — el escudo anti-trampa. Como un commit firmado **antes** de correr el experimento: el diseño completo (hipótesis, regla de éxito, regla de muerte, semillas) se escribe primero, se hashea, y el hash se publica. Si después cambias algo, el hash ya no cuadra y se nota. Es lo que hace la ciencia seria desde hace una década; en hackathons, literalmente nadie lo hace.

**Escalera T1-T4** — la escala de honestidad del proyecto: T1 concepto → T2 simulación con semilla pública → T3 datos reales → T4 un tercero replica. El criterio de victoria del proyecto es T4, no ganar el hackatón.

**Los 3 testigos (D6, FB-003)** — cuando algo deriva, ¿quién miente: el mundo, el sensor o el humano? ALMA triangula tres fuentes independientes (planta × chip × humano) antes de acusar. (MO-4)

**H-cards y señal refutadora** — cada hipótesis es una tarjeta del kanban, y **antes de probarla** se escribe qué señal la mataría. Si esa señal aparece, la tarjeta muere y se celebra: encontrar la verdad vale más que tener razón. (FA-1)

**Banner REAL/SIMULADO** — todo dato en pantalla lleva su banner. La honestidad es arquitectura, no marketing.

**Los dos corazones (Guardián + LA FUNDICIÓN)** — el Guardián responde "¿qué está pasando?"; la FUNDICIÓN responde "¿qué NO sabemos que está pasando?". No publica "insights": solo hipótesis con fuente con identificador, precio y hash — y las que sobreviven compilan en detectores nuevos. Un monitor sin lab envejece; un lab sin monitor es estéril. (DOC-04)

**El caso de estudio (Proxima b)** — nuestra respuesta a "¿esto escala?": la misión al sistema estelar más cercano (4,25 años luz; ~42,5 años a 0,1c de crucero) como horno de invariantes. No se construye nada para ella en el hackatón; sirve para demostrar que cada módulo enchufa en el registro existente. La Tierra no se descarta: queda, con latencia (ida y vuelta de señal ≈ 8,5 años). (DOC-04 §6–§7)

---

## §4 · Qué vamos a usar en la demo (los casos concretos)

**Fuente 1 — datos reales en vivo (hoy, sin API key):** NOAA SWPC (Space Weather Prediction Center) para LA TORMENTA — actividad solar real. Ya operativo.

**Fuente 2 — hábitat simulado con física anclada (el Banco de Falsaciones, IN-4):** genera el hábitat sintético con anomalías inyectadas de 3 tipos: (a) deriva coherente (algo envejece despacio), (b) flujo no contabilizado (el caso estrella del Contrapeso), (c) fuga física. Cada corrida lleva su semilla pública.

**Caso estrella — guion paso a paso de la demo kill (FB-005):**
1. Días 1-14: hábitat normal, todo verde en las dos columnas (los dos detectores duermen).
2. Día 15: se inyecta un flujo no contabilizado (ejemplo: una fuga hacia un punto no instrumentado del circuito de agua).
3. Columna A — detector contra el manifiesto: **todo sigue verde** (cada sensor cuadra con su manifiesto; es ciego por construcción).
4. Columna B — El Contrapeso: el libro de conservación no cierra → alarma con recibo (regla exacta + semilla + hash del preregistro FB-005: `6c923ac5…2567b9b`).
5. La frase del momento: "No es un algoritmo mejor. Es una **clase distinta de detector**: cuadrar cuentas con el universo, no con el fabricante."

**Caso segundo — la deriva lenta (FB-002, ya ejecutado):** el presupuesto de ritmo (sueño) del grupo se degrada día a día apenas perceptible; el CUSUM da el preaviso 21 días antes. Resultado histórico: 10/10.

**Ancla al brief:** los 6 indicadores del challenge (presión, fc, glucosa, temperatura, sueño, ánimo) son los de DC-01/DC-02 — el autorreporte de ánimo entra en 3 toques (IN-2), y la ausencia de respuesta también es dato.

---

## §5 · ¿Podemos hacerlo? Factibilidad real para 3 devs en 48 horas

**Sí — porque ya existe el 60% y no hay que codearlo.** Lo que ya corre (motor de residuo + CUSUM, banco de falsaciones, SWPC en vivo, contratos de datos DC-01…07, preregistros firmados) solo hay que **materializarlo en el repositorio** y conectarle la superficie visual.

### Reparto (una persona por frente, sin solaparse)

| Quién | Frente | Qué construye | Criterio de "hecho" |
|---|---|---|---|
| **Dev A — El libro** | Backend núcleo | LB-1 mínimo: los 9 presupuestos sobre DC-04 + **El Contrapeso** (cierre de conservación agua/aire/energía) + endpoints REST que exponen DC-04/DC-05/DC-06 | El libro cierra contra la física; la alarma del Contrapeso sale con recibo completo |
| **Dev B — El motor** | Ciencia/scripts | Materializar MO-1/MO-2/MO-3 en `scripts/`, correr **FB-003** y **FB-005**, generar los JSON de la demo (con banner REAL/SIMULADO y semillas) | Los 2 actas ejecutadas con hash publicado antes; JSONs de demo reproducibles |
| **Dev C — La vitrina** | Frontend | Las 6 pantallas (§6) consumiendo los contratos de A — **jamás toca el motor** | LA SALA + EL RESIDUO vivos con datos del banco; demo kill en pantalla |

### Prioridad de construcción si falta tiempo (la del registro MAP-S1, ya ordenada)

- **P0 (no negociable):** El libro + Contrapeso + LA SALA + EL RESIDUO.
- **P1 (el momento memorable):** LA TORMENTA + la demo kill en dos columnas.
- **P2 (si alcanza):** LA MESA (kanban de H-cards).
- **P3 (puede mostrarse con datos fijos del banco):** LA CÁPSULA + EL PRESUPUESTO.

### Lo que NO vamos a hacer (y por qué)

- No entrenamos modelos de ML pesados — el valor no está ahí, está en la clase de detector y la disciplina. (Si alguien pregunta por IA: la IA se usa como instrumento auditable, con preregistros.)
- No añadimos features fuera de las 8 ideas — la disciplina anti-dilución del proyecto: el techo de concepto está tocado, lo que entra tiene que ser módulo, proceso o clase nueva de detector.
- No mostramos contenido individual de la tripulación en las pantallas — solo agregados (regla de privacidad del mapa, inviolable).

---

## §6 · Cómo debe verse el frontend (6 pantallas + reglas duras)

**Estética global:** sala de control de misión + libro contable. Fondo oscuro de consola, números en monoespaciada, semáforo (verde/ámbar/rojo) **solo** donde existe una regla que lo justifica, banner REAL/SIMULADO siempre visible, hash SHA-256 visible en cada veredicto. La honestidad ES el diseño.

| Pantalla | Qué muestra | Contrato que consume | Regla dura |
|---|---|---|---|
| **LA SALA** | La silueta/hábitat como paciente: figura clicable + anillo de 9 presupuestos | DC-04 agregado + DC-05 activas | Jamás contenido individual |
| **EL RESIDUO** | Corriente observado vs. predicho, bandas σ, nacimiento de alertas | DC-06 | Banner REAL/SIMULADO visible |
| **LA MESA** | Kanban de hipótesis: nacidas → en prueba → refutadas → confirmadas | Estado de FA-1 | Cada tarjeta muestra su señal refutadora |
| **LA TORMENTA** | Motor de escenarios + actividad solar real | IN-4 + DC-03 | Banner "UNIVERSO SIMULADO — DÍA N" cuando aplique |
| **LA CÁPSULA** | Veredicto exportable: hipótesis, prueba, números, límites, hash | DC-07 | Sin límites declarados, no exporta |
| **EL PRESUPUESTO** | Los 9 libros que deben cerrar — el metabolismo de la nave | DC-04 | Cuentas, nunca gráficas de personas |
| **Demo kill** (transversal, momento final) | Las dos columnas: manifiesto (ciego) vs. ley (ve la fuga) | FB-005 | El hash del preregistro en pantalla, publicado antes de correr |

El brief de NASA pide literalmente: figura humana clicable, código de colores a primera vista, gráficos dinámicos, instrucciones simples — **las cumplimos todas**, pero con nuestra regla: los colores solo aparecen cuando una regla contestable los autoriza. Esa diferencia se explica en la demo y es un punto a favor, no una limitación.

---

## §7 · Banco de preguntas del jurado (respuesta de 30 segundos cada una)

1. **"¿Datos reales o simulados?"** — Ambos, con banner visible siempre. La actividad solar es real y en vivo (NOAA SWPC). El hábitat es simulado con física anclada y semillas públicas. El paso a datos reales ya está en marcha: estudio registrado en el OSDR de NASA (OS-892).
2. **"¿Por qué no basta un dashboard normal?"** — Porque el dashboard compara contra el manifiesto, y el manifiesto puede mentir (+60% de mantenimiento sobre diseño en la ISS real). Mostramos en vivo el caso donde queda ciego. (→ demo kill)
3. **"¿Qué pasa si El Contrapeso se equivoca?"** — Puede pasar, y está previsto: la alarma no es un veredicto, es una **pregunta contestable** con recibo — regla exacta impresa, y si la regla no se cumple, la alarma se retira sola. Además existe la falsa cuarentena publicada (el sistema se atreve a admitir sus errores en actas).
4. **"¿Un sistema así diagnostica a la tripulación?"** — No. Fabrica preguntas contestables y guía de bajo riesgo y reversible (una intervención por indicador). El diagnóstico lo aprueba el médico; nosotros hacemos que las preguntas sean las correctas.
5. **"¿Y la privacidad?"** — Arquitectura, no parche: el contenido individual jamás cruza a las superficies de decisión; solo agregados y estados.
6. **"¿Por qué hashes? ¿Qué demuestra un hash?"** — Que el experimento fue diseñado antes de mirar los datos. El hash SHA-256 del diseño se publica antes de ejecutar; si alguien cambia la regla después, el hash no cuadra. Es el antídoto contra el autoengaño científico.
7. **"¿Tres personas sin médico ni científico de datos pueden esto?"** — El método no es una biblioteca que instalamos: es una disciplina de 48 horas que cualquiera puede seguir — preregistrar, correr con semilla, publicar el resultado aunque sea feo. Y toda la parte científica del motor ya está ejecutada y documentada.
8. **"¿Escala a una tripulación de 8?"** — El libro es contable: suma líneas, no personas. La proyección está en el mapa; el límite real es el inventario del hábitat y lo declaramos como punto ciego programado.
9. **"¿Y esto escala a Marte o más allá?"** — No lo decimos como promesa: la arquitectura tiene una prueba de estrés documentada hasta α Centauri (4,25 años luz). Los invariantes (residuo, procedencia, umbrales con vida media, líneas base por cohorte) sobreviven; lo que muere a esa escala (el umbral estático, la consulta instantánea a Tierra) ya está identificado con su sustituto. (DOC-04 §6–§7)
10. **"¿El laboratorio no es ciencia ficción?"** — Todo lo que construimos para el submit es del challenge: monitoreo de salud. El lab solo publica hipótesis con fuente, precio y hash, y su único output permitido hoy son tarjetas y una predicción fechada. La frontera (Proxima b) es una línea en la demo, no un módulo. (DOC-04 §8–§10)

**Las 3 preguntas que hoy no podemos responder (decirlas con honestidad si aparecen):** árbitro externo humano (en búsqueda activa — hasta entonces el árbitro es matemático: hash + semilla), inventario completo del hábitat real (fuente declarada, se audita con el miner de premortems), y validación en datos reales (T3 en curso, OS-892).

---

## §8 · Calendario 12-14 nov (quién hace qué)

**12-nov (jueves):**
- Los tres juntos (mañana): materializar `scripts/` del motor al repo + regenerar ficheros de preregistros FB-005…008 en el proyecto (GO-2).
- Dev B: FB-003 + FB-005 ejecutadas con hash publicado antes de correr.
- Dev A: LB-1 + Contrapeso + endpoints.
- Dev C: LA SALA + EL RESIDUO con datos del banco.

**13-nov (viernes):**
- Dev B: FB-004 (con la normalización MP-3 integrada en el diseño).
- Dev B (tarde): acuñar las tarjetas del lab en LA MESA (**≥5 desde K-2 + OS-892, techo 10** — corte honesto de DOC-04) y registrar **1 predicción del Faro** con fecha de calificación (GO-7/DC-12).
- Dev A + Dev C: LA TORMENTA + demo kill en pantalla + LA MESA si alcanza.
- Todos: PDF del proyecto v0.4 (v0.3 + Apéndice A de MAP-S2 + reanclaje 2025-2026) + **leer la guía de juzgamiento oficial (se publica ese día)** + ensayo 1 del pitch con cronómetro.

**14-nov (sábado — jurado):**
- Ensayo 2 (una pasada, sin notas).
- Llenar el formulario de submit de Space Apps (checklist §9) y grabar el video corto.
- Demo en vivo con el guion de §2.

---

## §9 · Checklist del submit de Space Apps (para el 14)

- [ ] Descripción del proyecto (150-200 palabras — partir de §1, adaptada al formulario)
- [ ] "How it works" con los contratos y el método (partir de §4 y §6)
- [ ] Datos usados: NOAA SWPC + hábitat simulado con física anclada + OSDR (OS-892) — con links
- [ ] Link al repositorio (con `scripts/` del motor y los preregistros con hash)
- [ ] Link al PDF del proyecto v0.4
- [ ] Video corto (30-60 s): la frase de memoria (§1) + la demo kill en dos columnas + la escalera T1-T4. Cuatro líneas de guion: problema (10 s) → método (15 s) → demo (20 s) → reproducibilidad (15 s)
- [ ] LA MESA con las tarjetas del lab (≥5) + 1 predicción del Faro fechada + 1 escape del Adversario documentado (compromisos de DOC-04 §9)
- [ ] Créditos del equipo y menciones (semillas públicas, OSDR, NOAA)
- [ ] Leer la guía de juzgamiento (publicada el 13-nov) y ajustar keywords del submit

---

## §10 · Las 3 reglas que el equipo no rompe (ni por deadline)

1. **Nada lee directo de los sensores** — todo pasa por el libro (LB-1). Sin excepciones: es lo que hace auditable al sistema entero.
2. **Nada se prueba sin preregistro con hash ANTES de correr** — si se descubrió el resultado y luego se escribe el diseño, ya no es ciencia y no va al pitch.
3. **Los colores solo con regla contestable** — el verde sin recibo no aparece en pantalla. "Todo verde" sin prueba es exactamente el problema que venimos a resolver.
