# ¿Vale ALMA como paper / tema de estudio? — evaluación honesta

> 2026-11-15. Pregunta del humano: *«mi idea, como es para la NASA, es crear un paper o algo así; evalúa si lo vale o no»*.
> Método: lo que sigue se apoya en fuentes que **leí o verifiqué contra su base oficial** (enlazadas). La búsqueda bibliográfica fue **rápida y no sistemática**: «no encontré X» **no** significa «X no existe». Antes de afirmar novedad en un manuscrito hay que hacer una revisión sistemática de verdad (§5).

## 1 · Veredicto en una línea

**Sí vale como tema de estudio y puede llegar a ser un paper — pero hoy no lo es.** Hoy es un diseño metodológico muy bueno con **cero resultados sobre datos reales**. El paper defendible no es «el sistema ALMA entero»: es **un recorte de una sola afirmación falsable, preregistrada y validada**.

## 2 · Lo que sostiene el valor (con evidencia)

| Punto | Evidencia verificada |
|---|---|
| El problema es real y NASA lo declara abierto | Las páginas de HRP (riesgos de sueño, conducta, hueso, radiación) y el reto #4 de Space Apps; el gap «Medical-701» que cita el bestiario (por verificar en su fuente) |
| La línea base **personal** ya es una dirección de investigación financiada por NASA | Proyecto de Portland State (Rekabdar): IA que «aprende lo normal de cada astronauta» y lo actualiza durante la misión — [pdx.edu](https://www.pdx.edu/news/when-911-millions-miles-away-psu-researcher-builds-ai-guardian-mars-missions) (leído). **Esto es validación del tema, y también competencia directa en esa pieza.** |
| El balance de masas de soporte de vida se usa como **herramienta de planificación** | Ewert, *Astronaut Mass Balance for Long Duration Missions*, NTRS [20190027563](https://ntrs.nasa.gov/citations/20190027563) (2019); ICES 2026, NTRS [20260005378](https://ntrs.nasa.gov/citations/20260005378) (economía de masa de ECLSS) |
| La **detección de fallos** en ECLSS existe a nivel de sensores de equipo | Takada, *Advanced Oxygen Generation Assembly*, NTRS [20190030425](https://ntrs.nasa.gov/citations/20190030425) (fault detection and isolation del OGA) |
| Hay huecos que **no encontré cubiertos** (por confirmar) | No hallé, en esta búsqueda rápida, trabajo que use el **residuo de cierre de conservación** (agua/aire/energía) como *detector* de flujos no contabilizados junto a líneas base personales, ni una evaluación de CUSUM sobre wearables de astronautas bajo preregistro |

## 3 · Lo que hoy NO sostiene un paper (sin anestesia)

1. **Cero validación con datos reales.** FB-001/FB-002 son simulación («en silicio»). Un revisor pregunta primero: *¿y con datos de verdad?*
2. **Cada pieza es conocida.** CUSUM es de 1954, EWMA de 1959, N-of-1 de 1990, el gemelo digital de la NASA es de 2012. La contribución solo puede ser el **ensamblaje + el protocolo de evaluación**, y eso hay que demostrarlo, no declararlo (el propio `radar-nasa.md` lo admite: «nuestras gemas son autocalificadas»).
3. **Competencia directa en la línea base personal** (PSU). Hay que citarla y diferenciarse con evidencia.
4. **No hay datos de astronautas ni de telemetría ECLSS abierta** accesibles. Cualquier afirmación sobre astronautas es extrapolación; hay que decirlo.
5. **Decisiones de diseño aún sin validar:** regla de cierre 2σ y fórmula del residuo (DOC-01 v0.2.3), umbral CUSUM (h*), `incertidumbre_del_manifiesto`.
6. **Algunas cifras de los docs aún sin fuente enlazada** (ver `auditoria-de-fuentes.md` H-5/H-6).

## 4 · Los recortes publicables (elige UNO como eje)

| Opción | Afirmación única y falsable | Datos | Honestidad del resultado | Encaje |
|---|---|---|---|---|
| **A · El Contrapeso** (FB-005) | El residuo de **conservación** detecta flujos no contabilizados que el residuo de **manifiesto** no ve, con FPR comparable | **Simulación** con parámetros públicos de ECLSS (NTRS arriba). No hay telemetría real abierta | Resultado **«en silicio»**, declarado SIMULADO | Congreso de ingeniería de soporte de vida (p. ej. ICES) o revista de astronáutica — *encaje por verificar, no confirmé alcance ni fechas* |
| **B · Línea base personal + CUSUM bilateral sobre datos reales** | Tasa de falsas alarmas y latencia de detección sobre series diarias **reales** de sueño, pulso y ánimo, con desplazamientos inyectados (híbrido, etiquetado) | **LifeSnaps** (71 participantes, 4 meses, CC-BY 4.0): sueño, pulso, ánimo — verificado, ver `politica-de-datos.md` S-07. **No son astronautas** | Real en la línea base, **semisintético** en las anomalías (se declara) | Salud digital / sensores — novedad baja-media; el valor es el protocolo preregistrado |
| **C · Infraestructura de ciencia reproducible** | Un banco de falsación con preregistro por hash, semillas públicas y alarmas con «recibo» ejecutable permite que un tercero reproduzca los resultados | El propio repo | Contribución **metodológica/de software**, la más defendible hoy | Artículo de software/metodología; evaluar requisitos de cada venue antes |

**Recomendación:** **B + A como núcleo de un preprint**, con **C** como sección de metodología. B aporta lo único real que hoy podemos medir; A aporta la idea más distintiva (cierre de conservación) declarada honestamente como simulación. Nada de «única en el mundo».

## 5 · Plan para convertirlo en paper (en orden; cada paso es una fila de la cola)

1. **Revisión de literatura sistemática** (PubMed, NTRS, IEEE, Google Scholar; términos de balance de masa/ECLSS, líneas base personales, CUSUM en wearables, N-of-1 en espacio). Sin esto no se afirma novedad.
2. **Preregistrar las afirmaciones del paper** (acta nueva, hash de bytes exactos, antes de correr): umbrales, métricas, semillas públicas. *(GO-2 ya está automatizado.)*
3. **Adaptador de LifeSnaps → DC-01/DC-02** y corrida **B** (FPR sobre datos reales sin inyección; latencia con inyección etiquetada).
4. **Correr FB-005 en silicio** con parámetros públicos citados; publicar el resultado aunque sea feo.
5. **Escribir limitaciones primero** (no astronautas; simulación; decisiones sin validar). Un claim acotado sobrevive al escrutinio.
6. **Preprint** (el repositorio como material suplementario reproducible) y recién entonces elegir revista o congreso, **confirmando su alcance y plazos**.

## 6 · Qué NO hacer

- No presentar resultados simulados como evidencia sobre astronautas.
- No reclamar novedad sin la revisión del §5.1.
- No ejecutar nada sin acta registrada (la compuerta `exigir_preregistro` lo impide).
- No cambiar un umbral después de ver resultados (eso es HARKing; sería un acta nueva `-v2`).

## 7 · Posicionamiento: qué es común y qué podría ser original (búsqueda dirigida, 2026-11-15)

> Misma salvedad: búsqueda rápida, **no sistemática**. «No encontré» ≠ «no existe». Las fuentes marcadas con enlace las verifiqué (Crossref / NTRS / arXiv / lectura de la página).

| Pieza de ALMA | Qué encontré | Veredicto |
|---|---|---|
| **Línea base personal** del astronauta | Línea de trabajo activa: PSU/NASA ([pdx.edu](https://www.pdx.edu/news/when-911-millions-miles-away-psu-researcher-builds-ai-guardian-mars-missions)); ORACLE, signos vitales de tripulante como plataforma PHM (Fink et al., [Univ. de Arizona](https://experts.arizona.edu/en/publications/oracle-a-phm-test-validation-platform-for-anomaly-detection-in-cr/)); gemelos digitales de astronautas | **COMÚN.** Lo propio sería el CUSUM bilateral + el piso de detección fijado por el manifiesto + el protocolo preregistrado |
| **Residuo de conservación / cierre de balance** (El Contrapeso) | Es el campo establecido de **conciliación de datos y detección de errores gruesos** de la ingeniería de procesos: Narasimhan & Jordache, *Data Reconciliation and Gross Error Detection* (Gulf, 1999/2000; capítulos en Crossref, p. ej. [10.1016/b978-088415255-2/50008-2](https://doi.org/10.1016/b978-088415255-2/50008-2)), con aplicación industrial a inventarios | **MÉTODO COMÚN.** Hay que citarlo y presentarlo como *aplicación*, no como invención. Su prueba estadística clásica vale estrictamente para restricciones lineales |
| **Metabolismo ↔ balance de cabina** (O₂, CO₂, calor) | Conocido para diseño y planificación: Ewert, [NTRS 20190027563](https://ntrs.nasa.gov/citations/20190027563); perfil metabólico diario, [NTRS 20205010692](https://ntrs.nasa.gov/citations/20205010692) (ICES 2021); métodos de la era Apolo | **COMÚN** como modelo. Usarlo como **detector de salud individual dentro de un libro único**: no lo encontré, es la candidata a novedad |
| **Cuerpo + máquina juntos** | Precedente parcial: ORACLE trata al tripulante como biosensor dentro de un sistema de salud del hábitat (prueba de concepto) | La afirmación «**nadie unifica**» (radar §2, bestiario §8) **no se sostiene tal cual**. Decir: «no encontré uno con un único libro de cierre y protocolo preregistrado» |
| **Evaluación preregistrada con hash y semillas públicas** para detección de anomalías | No encontré ningún benchmark así. Sí está documentado que **los rankings de detectores de anomalías no son fiables** por decisiones de evaluación ([arXiv 2608.04613](https://arxiv.org/abs/2608.04613)) | **Candidata más fuerte a original y oportuna** |
| Alarmas con recibo ejecutable; LA FUNDICIÓN (hipótesis → detector) | **No busqué todavía** | Sin veredicto; entra en M5.5 |

**Cambios recomendados antes de seguir (ninguno obliga a rehacer el diseño):**
1. **Reencuadrar, no renombrar:** el Contrapeso = *conciliación de datos aplicada a un hábitat tripulado*. Se cita la bibliografía y se conserva la idea.
2. **El eje de originalidad a defender**: (a) el protocolo preregistrado y reproducible; (b) un único libro de cierre cuerpo + máquina; (c) el hallazgo «el piso de detección lo fija el manifiesto, no el sensor». Todo lo demás es soporte.
3. **Suavizar las afirmaciones de unicidad** en los docs (notas de verificación añadidas a `radar-nasa.md` y `inventario-maestro-bestiario.md`).
4. **Anclar la simulación a números públicos**: parametrizar el manifiesto de FB-005 con el perfil metabólico de NTRS 20205010692 y las cifras de Ewert. Sigue siendo SIMULADO, pero con parámetros citables.
5. **Validar antes de construir más:** correr M2.7/M2.8 sobre datos reales (LifeSnaps) **antes** de añadir módulos. Congelar el alcance en LB-1 + Contrapeso + MO-1…MO-3 + preregistro; LA FUNDICIÓN queda en segundo plano hasta tener tarjetas con fuente real.
