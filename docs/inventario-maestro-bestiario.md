# TONO-LAB — Inventario maestro y Bestiario
**Estado:** diseño pre-hackatón (investigación/diseño permitido; construcción inicia 14 nov, 9:00 a.m. local)
**Reto:** #4 Health Monitoring Software — NASA Space Apps Challenge 2026
**Identidad en una frase:** *TONO-LAB es una fábrica de conocimiento médico a bordo: transforma sorpresas en protocolos exportables. Para una civilización novata, no es una biblioteca de conocimiento — es la máquina que fabrica los manuales.*

---

## 1. Las 9 capas del sistema (qué hace, en orden)

### A. Núcleo del motor — el diamante
1. **Modelo nulo por astronauta**: predice el rango normal de cada indicador con σ personal; arranca con priors poblacionales (OSDR) y muestra confianza creciente ("modo aprendizaje", honestidad estadística).
2. **Residuo**: r = observado − predicho. Si |r| > 2σ → sorpresa. Detección **sin causa**: funciona ante eventos inéditos (el motor no necesita conocer la causa para detectarla).
3. **H-card (tarjeta de hipótesis)**: qué observé / predicción / hipótesis candidata / prueba 7–14 días / **señal refutadora definida ANTES de probar**.
4. **Experimento N-of-1**: A-B-A-B alternado aleatorizado (Guyatt 1990, PubMed 2297206; Lillie 2011); solo intervenciones de bajo riesgo y reversibles bajo plan médico.
5. **Veredicto → Protocolo (anticuerpo) → Cápsula exportable**: el "biofoam del conocimiento" — guía pre-empaquetada desplegable al instante (precedente real: XStat FDA 2013, uso civil 2015). Heredera de ESPORAS; definida campo por campo.
6. **Meta-capacidad (H4)**: el software prueba su propia premisa + **punto ciego programado**: cada 30 días la tripulación audita "¿qué balance existe que no medimos?" — el software que sabe lo que no puede ver.

### B. Indicadores (6 oficiales + 2 diferenciales)
| Indicador | Fuente / número |
|---|---|
| Presión, FC, glucosa, temperatura, sueño, ánimo | Los 6 oficiales del reto |
| Hueso | Mechanostat Frost 2003 (1500–3000 με modelado / <100–300 με reabsorción); pérdida de densidad ósea **1–1,5 %/mes** en misiones de 4–6 meses (ancla primaria: [NASA HRP](https://www.nasa.gov/reference/risk-of-spaceflight-induced-bone-changes/)); cita secundaria: *"they continue to lose about 1 – 2% of their bone mass a month"* ([NASA OSDR OS-892](https://osdr.nasa.gov/geode-py/ws/repo/experiments/OS-892), texto de antecedentes del experimento, no un resultado); B(t+1)=B(t)·e^(−k)+α·carga(t); k=1 %/mes → −5,8 % semestre |
| Radiación | 600 mSv carrera (NASA-STD-3001); 250 mSv/evento (OCHMO-TB-020); Hassler 2014: 1,84 mSv/día tránsito, 0,64 mSv/día superficie |

### C. Tres canales de entrada
- **A — Sensores automáticos**: wearables, dosímetro (presión, FC, glucosa, temperatura, sueño).
- **B — Autorreporte estructurado**: ánimo y síntomas en 3 toques (el dolor de cabeza se *declara*, no se mide — igual que en medicina real).
- **C — Eventos con firma física**: tormentas solares, EVAs, soporte de vida + **capa de contexto ambiental** (CO₂, ECLSS).
- **Recordatorios** = requisito oficial del reto, no parche.

### D. Los 8 balances finitos (la respuesta al infinito)
*Los eventos son infinitos; los balances son finitos. Cualquier evento inédito viola al menos un balance.*
1. **Masa-aire** — presupuesto de vida, detector **bidireccional**: emisor no contabilizado (hongos ISS: Cladosporium/Penicillium/Aspergillus, Checinska Sielaff 2019; jardín nocturno; fuego latente) y miembro del manifiesto que no emite (el "Ash" — consumo no declarado). Ancla numérica: ~0,83 kg O₂/día y ~1 kg CO₂/día por persona (ECLSS NASA).
2. **Energía** — calor/potencia (fuente térmica no declarada).
3. **Dosis** — presupuesto de radiación por evento y de carrera.
4. **Ritmo** — coherencia circadiana personal y de tripulación (Mars-500: Basner 2013, PNAS).
5. **Carga** — mechanostat óseo.
6. **Conducta** — red de ánimos/comunicación; residuo de tripulación = "la nave como paciente".
7. **Inventario** — botiquín como sensor agregado (la ISS lleva antidepresivos, antipsicóticos, ansiolíticos ×2).
8. **Biología interna** — síntomas declarados + ventana de estrés → reactivación viral (Mehta et al. 2014/2017: EBV/CMV/VZV en astronautas; 6 de 14 eliminaron los tres virus; no cesa hasta 180 días).

### E. Bestiario — familias de hipótesis minadas de la ficción
| # | Familia | Origen ficción | Clase real | Fuente |
|---|---|---|---|---|
| 1 | El 8º/11º pasajero (presupuesto bidireccional) | *Alien* (título español 1979) + *11-nin Iru!* (Hagio, 1975) | Biomasa no contabilizada / emisor invisible | Checinska Sielaff 2019 |
| 2 | Ventana de estrés → reactivación viral | La Flood (Halo) | Estrés → shedding EBV/CMV/VZV | Mehta 2014/2017 |
| 3 | H2 sueño × hueso (prueba inédita) | — | Interacción no probada en literatura | EXTRAPOLACIÓN honesta |
| 4 | H1 ventana post-EVA (timing del experimento) | The Expanse | Factor 6,1× lunar bajo la ventana de Frost | Frost 2003 + cálculo propio |
| 5 | CO₂ → dolor de cabeza (certificado de calibración) | — | 19/49 astronautas con cefalea; CO₂ 7-días < 2,5 mmHg | OCHMO-TB-004; estudio 2014 |
| 6 | H3 ejercicio × IL-6 osteolítica | — | El N-of-1 en vuelo que OS-892 escribió y no ejecutó | OS-892 / MABL-B |
| 7 | El jardín como tripulante | Nausicaä / El Marciano | Respiración nocturna + etileno (Wheeler 1996) | Veggie/zinnias moho 2015 |
| 8 | Farmacia como sensor | — | Consumo agregado del botiquín | MIT Angles 2019 |
| 9 | Conductual: disforia de segunda mitad | Pandorum (2009) | Psiquiatras NASA: disforia crece en 2ª mitad | Slack et al. 2015 (NTRS) |
| 10 | Torpor/despertar (futura) | Halo criotubos / Ripley 57 años | NIAC Torpor (NTRS 2018); Choukèr 2018 | REAL en investigación |

### F. Motor de escenarios (perturbaciones con física anclada)
- **Replay histórico**: catálogo NOAA de eventos de protones 1976–presente; tormenta de agosto 1972 entre Apolo 16/17 (Parsons & Townsend, Radiation Research 2000: dosis más altas registradas).
- **Monte Carlo de misión**: muestreo de distribuciones reales (frecuencia/espectro NOAA + atenuación de blindaje); la aleatoriedad está en cuándo/severidad, nunca en la física.
- **LLM solo narrador, nunca fuente**: escribe el diario y el informe de caso; el cerebro es el simulador.
- **Banner de honestidad**: "UNIVERSO SIMULADO — DÍA 12"; jamás contamina el registro real.

### G. Los 3 registros de la fotografía
1. **Certificado de calibración** (30 s del demo): el motor recupera casos ya publicados (CO₂→cefalea) → instrumento confiable.
2. **Fotografía propia**: N-of-1 vivo sobre la tripulación — contexto irrepetible, veredicto inédito.
3. **Cruces no estudiados**: H2 y ventana viral — pruebas que nadie ha corrido.

### H. Arquitectura ética — anti-David / anti-rampancy
No diagnostica · no oculta información (anti-Orden 937) · no promete generalización · **confianza refutable** (Cortana/rampancy como advertencia: una IA cuya confianza no se cuestiona se vuelve loca) · intervenciones reversibles · consentimiento siempre (Newt/Spartans) · transparencia total · atrofia de widgets · banner de simulación · punto ciego programado.

### I. Interfaz — navegación en bucle, 5 pantallas
**LA SALA** (siluetas vivas + anillo 6+2) → **EL RESIDUO** (corriente observado/predicho; nacimiento de H-cards) → **LA MESA** (kanban de H-cards) → **LA TORMENTA** (motor de escenarios + informe de caso estilo case report) → **LA CÁPSULA** (exportación). Gamificación con dignidad: rachas de medición, nunca puntos por "estar sano". Núcleo de demo: pantallas 1, 2 y 4.

---

## 2. NASA ante lo repentino — y el hueco que ocupamos
Lo que existe hoy (real): **flight rules** (cientos de reglas if-then pre-acordadas), **CHeCS** (Crew Health Care System) + **CMO** (Crew Medical Officers entrenados), telemedicina con flight surgeons, conferencias médicas privadas (semanales), refugio de tormenta en la ISS (bolsas de agua/sandbags), botiquines pre-empaquetados.
**El hueco:** todo eso es *recuperación* de conocimiento conocido. Ante un evento sin regla de vuelo, la deliberación ocurre en Tierra — y más allá de la órbita baja terrestre hay retraso de luz (Marte: 4–24 min solo ida). **TONO-LAB genera el primer conocimiento a bordo en el hueco entre "no existe regla de vuelo" y "la Tierra puede responder". Cada veredicto del N-of-1 es una candidata a regla de vuelo nueva. Somos una fábrica de reglas de vuelo para lo inédito.**

## 3. Cruces transversales (papers no espaciales con contenido aplicable)
1. **Biosphere 2 (1991–93) — DIAMANTE**: O₂ cayó de 20,9 % a ~14 % en 16 meses (como respirar a 4.300 m) y el CO₂ NO subió — el misterio se resolvió con balance de masas: los microbios del suelo comieron el O₂ y **el hormigón absorbió el CO₂** (Severinghaus et al., 1994). *El octavo pasajero ya ocurrió en la Tierra: el pasajero invisible era el hormigón.* Precedente real de nuestro detector de presupuesto — puede encontrar hasta "geología" como tripulante.
2. **La parábola de Google Flu (Lazer et al., Science 2014)**: "big data hubris" + drift → nuestro anti-rampancy tiene modo de fallo documentado y citable; el punto ciego programado se vuelve obligación, no adorno.
3. **Seth Roberts, Behavioral and Brain Sciences 2004**: "Self-experimentation as a source of new ideas" — la premisa de TONO-LAB ya está argumentada fuera de la ciencia espacial: los autoexperimentos generan hipótesis que la ciencia oficial ignora. No inventamos un género: lo industrializamos.
4. **NEWS2/MEWS (escalas de alerta temprana, UK RCP)**: pocos parámetros + escalonamiento pre-acordado → gramática de alertas (verde/amarillo/rojo con acciones) compatible con flight rules.
5. **PVT — Psychomotor Vigilance Test (3 min; usado en Mars-500 por Basner)**: señal refutadora *objetiva* para H-cards de CO₂/sueño — convierte "me duele la cabeza" en vigilancia medible.
6. **CRM aéreo + checklists + cockpit estéril** (nace del accidente United 173, 1978; Gawande 2009): la cápsula = cultura de checklist; el refugio de tormenta = regla de cockpit estéril.
7. **EMA/ESM (evaluación ecológica momentánea)**: gramática de diseño del registro de síntomas en 3 toques + recordatorios.

## 4. Los 6 diamantes tras el fuego (destruir y reconstruir)
1. **Presupuesto de vida bidireccional** (el 8º pasajero y Ash) — con precedente Biosphere 2.
2. **Ventana de estrés → reactivación viral** (la Flood real: Herpesviridae) — la hipótesis más anclada en fuente.
3. **Balances finitos + punto ciego programado** — la respuesta al infinito.
4. **Anti-David / anti-rampancy** — arquitectura, no diapositiva.
5. **Cápsula = biofoam del conocimiento** — precedentes FDA (XStat).
6. **H2 sueño×hueso** — la prueba inédita que nadie ha corrido.

## 5. Pendientes de decisión
- [ ] Las 5 H-cards del demo (propuesta: 8º pasajero apertura · ventana viral ancla · H2 fotografía · H1 timing · CO₂-calibración)
- [ ] Contrato de datos campo por campo (canales A/B/C)
- [ ] Bocetos de las 3 pantallas núcleo
- [ ] Pre-curaduría de recursos (OS-892, NOAA, Hassler, OCHMO-TB-004/020, NTRS torpor, Mehta, Checinska) lista para el día 1
- [ ] [NUEVA RONDA] CUSUM/EWMA como segunda constante de tiempo del residuo
- [ ] [NUEVA RONDA] Modo premortem del motor de escenarios
- [ ] [NUEVA RONDA] 6ª pantalla: EL PRESUPUESTO (metabolismo de la nave)
- [ ] [NUEVA RONDA] Automedicición del motor (latencia/tasa de detección en replay)
- [ ] [NUEVA RONDA] Gobernanza de la cápsula (consentimiento, anonimización, propiedad)

## 6. Ronda de superación — lo que bate a lo que teníamos (verificado)
*Pregunta que guió la ronda: ¿existe algo verificado que SUPERA cada componente? Si nada lo supera, se declara.*

### 6.1 Motor de escenarios → se renombra GEMELO DIGITAL (linaje NASA) y gana un 3er modo
- **Glaessgen & Stargel 2012** (AIAA 2012-1818, NTRS 20120008178, ~4.500 citas): NASA acuñó "digital twin" — simulación integrada con el sistema de salud del vehículo a bordo, calibrada por telemetría. Nuestro replay/Monte Carlo no se tira: **se renombra y hereda el linaje**. El gemelo digital del sistema de salud de la tripulación.
- **Tercer modo — el PREMORTEM** (Mitchell, Russo & Pennington 1989, *J. Behavioral Decision Making*; popularizado por Klein): la retrospectiva prospectiva (imaginar el fallo ya ocurrido y escribir su historia) identifica más causas que el análisis hacia adelante (~30 % en el estudio original). La tripulación escribe su premortem cada 30 días y el motor mina esas narrativas para encontrar **balances no instrumentados** — el premortem es el generador humano del punto ciego programado.

### 6.2 Detección → el residuo lento (la mayor brecha técnica encontrada)
- Nuestro |r| > 2σ solo caza anomalías **agudas**. Las lentas — pérdida ósea de ~1–1,5 %/mes (NASA HRP), una colonia de moho creciendo, CO₂ crónicamente alto — pasan bajo el umbral punto a punto.
- Solución con 70 años de vigencia: **CUSUM (Page 1954, Biometrika)** y EWMA — estadísticamente más eficientes para desplazamientos pequeños y sostenidos (NIST/NCSS; usado en control de calidad quirúrgica).
- **Veredicto: el motor gana dos constantes de tiempo — 2σ (agudo) + CUSUM (lento). El 8º pasajero real (el hongo) es una firma CUSUM, no un pico.**

### 6.3 Los 3 registros → nace el 4º: la RED de cápsulas
- La metodología de combinar N-of-1 en mini-meta-análisis existe (Zucker et al., 1997). La cápsula deja de ser formato de exportación y se vuelve **nodo**: veredictos de tripulaciones distintas se combinan — el poder estadístico de los novatos.
- Y verificación del diseño existente: la H-card (señal refutadora definida ANTES) **ya es el estándar dorado** de la ciencia reproducible — preregistración. **Nada la supera; el diseño coincide con él.**

### 6.4 Anti-David → de principios a MECANISMOS citables
- **Contestable AI by design (Alfrink)**: el sistema responde a la contradicción humana durante todo su ciclo de vida → la tripulación puede disputar el modelo nulo mismo (disputa → recalibración). Transparencia era un principio; contestabilidad es un mecanismo.
- **Specification gaming (DeepMind/Krakovna 2020, ~60 casos documentados)**: nuestras rachas de gamificación pueden ser hackeadas → verificación cruzada declaración-sensor. El anti-rampancy tiene catálogo de modos de fallo.
- **Taxonomía militar de autonomía**: nuestra posición exacta tiene nombre — *human-in-command* (la tripulación decide, el software propone).
- **NHS DCB0129/DCB0160**: gestión de riesgo clínico de health IT con *hazard log* — registro de peligros propio para nuestro software (¿qué pasa si TONO-LAB está equivocado?).

### 6.5 Las 5 pantallas → faltaba la 6ª: EL PRESUPUESTO
- El detector del 8º pasajero **no tiene pantalla**. Nueva: **EL PRESUPUESTO** — el metabolismo de la nave: libros contables de aire, agua, dosis, ritmo, carga con sus residuos. La anti-dashboard absoluta: no muestra personas ni gráficas, muestra *cuentas que deben cerrar*.
- **Fatiga de alarmas (Cvach 2012, "peligro #1 de dispositivos médicos" según ECRI)**: justifica con cita nuestro presupuesto de atención (Ley de la Interfaz) — sin él, el motor ahoga a la tripulación en alertas y muere de desensibilización.
- El bucle observar→protocolar ya tiene linaje: **PDSA/Deming** (Plan-Do-Study-Act). Y LA TORMENTA puede ser explorable (arrastrar blindaje y ver la curva de dosis — *Explorable Explanations*, Victor 2011).
- **Veredicto: el bucle sostiene; faltaba una pantalla.**

### 6.6 Aspectos que NO estábamos abordando (lista directa)
1. **El residuo lento** (CUSUM/EWMA) — la mayor brecha técnica.
2. **El premortem** como generador humano de puntos ciegos.
3. **La fatiga de alarmas** y el presupuesto de atención con cita (Cvach 2012).
4. **La ausencia como dato**: una medición faltante no es neutra (MNAR, Little & Rubin) — la adherencia misma es un indicador del motor.
5. **Gobernanza de la cápsula**: consentimiento, anonimización, propiedad de los datos post-misión.
6. **Deriva del sensor vs. deriva del cuerpo**: cruces de cordura entre sensores para no aprender la deriva del instrumento como "normalidad biológica".
7. **Automedición del motor**: en modo replay, medir latencia y tasa de detección de anomalías inyectadas → el demo gana números propios ("el motor detectó X de Y anomalías inyectadas, latencia media Z horas").
8. **Aislamiento de intervenciones**: una intervención activa por indicador a la vez, para que el A-B-A-B no se contamine.

## 7. Banco de fuentes del almacén
- Guyatt 1990 (N-of-1): PubMed 2297206 · Lillie 2011 · Frost 2003 · Tero 2007/2010 · Murray 1926
- NASA OSDR OS-892 · NASA SVS MABL-B 31382 · Stavnichuk 2020 (npj Microgravity 6:13)
- NASA-STD-3001 · OCHMO-TB-020 (radiación, 250 mSv/evento) · OCHMO-TB-004 (CO₂, 2,5 mmHg) · OCHMO ECLSS brief (~0,83 kg O₂/día)
- Hassler 2014 (Science) · Parsons & Townsend 2000 (Radiation Research 153:729) · catálogo NOAA SEP 1976–
- NASA HRP: Riesgo de Cambios Cognitivos/Conductuales (HSRB record) · Slack 2015 (NTRS 20150016966) · NTRS 20160003870 (ARS) · ARS Cliff (100–200 cGy náuseas/vómito)
- Basner 2013 (PNAS, Mars-500, PubMed 23297197) · Mehta 2014/2017 (reactivación viral) · Checinska Sielaff 2019 (PubMed 30955503) · Fahrion 2021 (BIOS-3, PMC8281973) · Wheeler 1996 (etileno) · NIAC Torpor (NTRS 20180007195) · Choukèr 2018
- Severinghaus et al. 1994 (Biosphere 2) · Lazer et al. 2014 (Science, PubMed 24626916) · Roberts 2004 (BBS) · NEWS2 (UK RCP) · XStat FDA K130218 · MIT Angles 2019 (botiquín ISS)
- [Ronda superación] Glaessgen & Stargel 2012 (AIAA 2012-1818, digital twin, NTRS 20120008178) · Mitchell/Russo/Pennington 1989 (J. Behavioral Decision Making, premortem) · Page 1954 (Biometrika, CUSUM) · Roberts 1959 (EWMA) · Cvach 2012 (fatiga de alarmas, PubMed 22839984) · Alfrink (Contestable AI by Design) · Krakovna et al. 2020 (DeepMind, specification gaming, 60 casos) · NHS DCB0129/DCB0160 · Zucker et al. 1997 (combinar N-of-1) · Little & Rubin (MNAR) · Victor 2011 (Explorable Explanations) · Deming (PDSA)
- Ficción citada como INSPIRACIÓN: Alien/El octavo pasajero (1979) y saga · 11-nin Iru! (Hagio 1975) · Pandorum (2009) · The Martian · The Expanse · Planetes · Space Brothers · Nausicaä · 2001 · Sunshine · Halo (Cortana, biofoam, criotubos, Flood)

## 8. Respuestas duras: ¿ya lo tiene NASA? Utilidad y originalidad (verificado 2026)

### 8.1 Lo que NASA YA tiene (honestidad primero)
- **CMO-DA (Crew Medical Officer Digital Assistant)**: prototipo real NASA JSC + Google Cloud, probado para apoyo del CMO cuando no hay contacto directo con Tierra (Google Cloud Blog, ago 2025). Es un asistente LLM de consulta/diagnóstico — una biblioteca médica conversacional.
- **IMCA (Intelligent Medical Crew Assistant)**: proyecto en NASA TechPort (102806) — integra EHR e inventario médico para monitorear salud.
- **Proyecto Clinical Decision Support (Krihak 2021; Pletcher 2023, NTRS)**: trabaja el **gap Medical-701** del riesgo de Condiciones Médicas en vuelo.
- **Programa Autonomous Medical Operations (STMD/GCD)**: existe porque "minimizar el impacto de los retrasos de comunicación con expertos" es un desafío declarado.

### 8.2 Lo que la PROPIA literatura de NASA admite que falta
- El gap **Medical-701** existe y está abierto: "necesitamos aumentar las capacidades médicas en vuelo" — los papers de 2021–2023 lo *argumentan*, no lo resuelven.
- Russell et al. 2023 (npj Microgravity, s41526-023-00284-1): publican "el VALOR de" un sistema de soporte de decisiones clínico espacial — o sea: la necesidad se sigue justificando. El asiento está vacío y ellos mismos lo escriben.
- El reto #4 de Space Apps ES la invitación formal al exterior.

### 8.3 Nuestra capa diferencial frente a CMO-DA (no competir, ocupar el hueco)
CMO-DA responde "¿qué puede ser y qué dice el manual?" — **recuperación**. TONO-LAB **fabrica** conocimiento: modelo nulo por persona → residuo con dos constantes de tiempo (2σ + CUSUM) → H-card preregistrada → experimento N-of-1 → veredicto → cápsula → candidata a regla de vuelo. Más: los 8 balances (detector del 8º pasajero), la nave como paciente, el premortem y el punto ciego programado, la contestabilidad. **Ningún paper o prototipo de NASA describe ese ensamblaje.**

### 8.4 Auditoría de originalidad (sin maquillaje)
- Piezas que EXISTEN: wearables y detección de anomalías (industria), CDS (proyectos activos de NASA), N-of-1 (Guyatt 1990), CUSUM (1954), gemelo digital (NASA 2012).
- Pieza que NO existe: el ensamblaje y el marco — la fábrica de reglas de vuelo para lo inédito.
- Frase del pitch: *"No inventamos las piezas; inventamos el ensamblaje — como los Wright: el ala y el motor existían; el control en 3 ejes era el diamante."*

### 8.5 Utilidad en 3 niveles
1. **Tripulación**: líneas base personales → menos falsas alarmas (fatiga de alarmas = peligro #1, Cvach 2012) · CUSUM caza lo lento (hueso, moho, CO₂) · quejas vagas → evidencia y acción en días · autonomía bajo retraso de luz 4–24 min.
2. **Misión**: veredictos → candidatas a regla de vuelo · cápsulas acumulan evidencia · premortem + punto ciego = aprendizaje institucional barato · el balance de vida duplica como red de seguridad ambiental (fuego/moho/jardín).
3. **Tierra**: el mismo motor sirve a comunidades aisladas con "retraso de luz terrestre" — clínicas rurales (Perú), estaciones antárticas, submarinos. El N-of-1 de autogestión está subdesarrollado en la Tierra también.

### 8.6 El escenario "nosotros ya tenemos una versión pequeña"
No es derrota: es **validación por las personas exactas cuya validación importa**. La respuesta preparada: *"Perfecto — entonces ustedes confirman que funciona. Nuestro aporte es la capa que su CDS no tiene: el bucle que convierte sorpresas individuales en reglas de vuelo nuevas. ¿Puede su asistente diseñar un experimento A-B-A-B, detectar un emisor no contabilizado y auditar su propio punto ciego? Eso es lo que demostramos."*

*Reglas vivas: Ficha de Verdad clasifica cada afirmación · P14 documenta todo · P15 convergencia · nada de construcción antes del 14 nov.*

## 9. MÓDULO FRONTERA v3 (9 nov 2026) — ver `TONO-LAB-modulo-frontera-v3.md`

La elevación "única en el mundo": **miniaturizamos el MÉTODO, no el instrumento** (metáfora ENIAC→chip hecha literal). Todo verificado el mismo día:

- **La tesis:** los instrumentos ya se miniaturizaron en medicina espacial (MOXIE 12 g/h O₂ marciano · MinION ~100 g secuenció ADN en órbita 2016 · tissue chips con órganos humanos en la ISS · Spaceborne-2 COTS desde 2021 · CGM en Polaris Dawn 2024). El método que los orquesta sigue pesando toneladas. Ese es el hueco.
- **6 elevaciones:** E1 TONO-CHIP (kit <$500) · E2 Coro de Canarios (manifiesto multi-especie: humano+planta+tejido-en-chip+microbioma+edificio) · E3 Motor Celestial EN VIVO (NOAA SWPC JSON sin key + NASA DONKI; la demo lee al Sol real) · E4 ISRU de datos (el residuo es mineral) · E5 Árbitro invariante (deriva vs física: peso patrón $20 en tierra, CAL en órbita) · E6 Gramática de Presupuestos (GPV, estándar abierto — de proyecto a movimiento).
- **D&R del diamante #1:** 3 muertes (no hay balanzas en microgravedad → SLAMMD-class; certificación imposible → penetración inversa tierra-primero; fatiga de alarmas → silencio por diseño + balance de confianza). 5 fases (F0 GPV → F4 expediente espacial).
- **12 preguntas de frontera respondidas** + guion de 3 min ("Nosotros somos el chip") + Ficha de Verdad del módulo completo.
- **Respuesta a "¿y si NASA lo copia?":** que lo copie ES la victoria — es un estándar, no un producto.

## 10. MÓDULO PRUEBA v4 (9 nov 2026) — ver `TONO-LAB-modulo-prueba-v4.md`

La primera prueba computacional falsable del proyecto (paso 6 del D&R ejecutado). Monte Carlo con física anclada, ruido de manifiesto incluido, CUSUM bilateral calibrado (FPR 14d ≈ 1%), 400 corridas/escenario, semilla fija 20261114. Tres descubrimientos de diseño que el análisis conceptual no podía dar:

1. **El eslabón débil NO es el sensor de $30, es el manifiesto** (incertidumbre de "cuánto emite una persona" domina ×4 al ruido del sensor). Calibrar al tripulante semanalmente (SLAMMD + VO₂ en ejercicio) acelera el detector ×5–6: caída metabólica del 10% de UNA tripulante pasa de 144 h (62,5% en 7 d) a **24 h (100%)**; caída del 5% de "casi invisible" a 48 h (90% en 72 h).
2. **El detector unilateral era ciego a las caídas** (una caída metabólica reduce emisión; el CUSUM solo miraba alzas) — el Monte Carlo lo expuso y obligó al CUSUM bilateral. El diseño se rompió y reconstruyó en la misma sesión.
3. **La señal vive en el actuador, no en la concentración**: con cabina regulada, un fantasma del 10% (0,35 kg CO₂/día) solo mueve la concentración ~62 ppm en 3300 — el paciente habla por el termostato (deber del scrubber).

**Titular clínico:** "Una tripulante que cae metabólicamente 10% — anorexia o depresión temprana — se detecta en ~24 horas sin un solo cuestionario, con un sensor de ~$30" (bajo manifiesto calibrado; supuestos declarados en el informe).

**Dato vivo:** Kp = 3,33 observado a las 2026-11-09 03:00 UTC (NOAA SWPC, sin key) — modo LIVE del Motor de Perturbaciones verificado con el Sol real.

**Nivel de descubrimiento:** v3 = T1+ (hueco documentado) · v4 = T2 (caracterización cuantitativa propia; rúbrica 6,4 → 8,4). Para T3: ajustar σ_manifiesto con datos NASA OSDR (OS-892), replay sobre telemetría ECLSS real, y el ataque del "impostor elegante" (fantasma que imita el patrón circadiano).

**Actualizaciones de diseño que v4 impone:** CUSUM bilateral obligatorio · detector a escala diaria (no horaria) · nueva columna en la GPV: `incertidumbre_del_manifiesto` — ese campo, no el sensor, fija el piso de detección.

## 11. MÓDULO FORJA v5 (10 nov 2026) — ver `TONO-LAB-forja-diamantes-v5.md`

Elevación de elección libre: **"de 3 a 7 diamantes"**. Rúbrica de 6 puertas (pesa 0 g · único verificable · ciencia real · falsable ≤30 días · cabe en GPV · narrativa) y método de forja en 4 pasos. Caza por curiosidad en **7 campos nuevos** (etología de aislamiento, fenotipado digital, redes con wearables, WBE, historia de estándares, alarmas clínicas, bioelectricidad vegetal) — **11 anclas nuevas verificadas, 0 invented**.

**Los 4 diamantes nuevos:**
- **D4 Presupuesto 9 — El Tiempo:** el tiempo de tripulación como recurso GPV con CUSUM personal (agenda + grafo de contacto, metadatos nunca contenido). Anclas: Tafforin 2013 (Mars-500), NASA 2020 (Skylab 4 = crisis de cronograma), Cantisani 2026 PNAS (cohesión antártica degrada, wearables), fenotipado digital (Onnela & Rauch 2016; Bufano 2023 JMIR).
- **D5 Línea Plimsoll** (E1→diamante): TONO-OK como sello visible de cumplimiento, no como kit de sensores. Lección 1876→1894: el regulado no pinta su propia línea (algunos la pintaron en la chimenea) → nueva regla de gramática `arbitro.proveedor ≠ operador`, que blinda a D3.
- **D6 Triangulación Viva** (E2→diamante): planta (min) × chip/microbioma (h–d) × humano (sesgado) — la matriz co-deriva localiza la falla (mundo/sensor/humano). Anclas: Vivent/PhytlSigns (sensores vegetales COMERCIALES), Zhou 2025.
- **D7 Sangre Colectiva:** el TOC del WRS ya se mide en la ISS pero se lee como salud de los filtros (Williamson 2024; Volpin 2020) — re-lectura como sensor fisiológico colectivo con métodos WBE (CDC/Broad). **El diamante más frágil: declarado EXTRAPOLACIÓN.**

**Facetas sobre gemas existentes:** D1 + banco rápido-lento (APSF: −77% falsas alarmas, precisión 84%; NCBI 2020) · D3 + regla Plimsoll. Las facetas de la Prueba v4 (CUSUM bilateral, detector diario, `incertidumbre_del_manifiesto`) quedan intactas.

**Elevaciones honestas:** E4→ORO vía "ensayo de mena" sobre NASA OSDR · Ficha de Verdad→ORO vía preregistro con hash público · Motor→ORO+ con modo ADVERSARIO (el impostor elegante ya era ruta T3 de v4) · bestiario/auditoría/gemelo = BRONCE para siempre (andamio).

**Inventario:** 💎 3→7 · 🥇 4→6 · 🥈 4→1 · 🥉 3→3 (17 ideas, 41% diamante; antes 21%).

**Nivel de descubrimiento:** v4 = T2 (una gema cuantificada) · v5 = T2 en amplitud (D4–D7 en T1 con falsación pre-registrada; nota global 8,4 → 8,9). **Puente v5→v6: ejecutar las 3 falsaciones en F0** (D4 creep→ocio, D6 matriz co-deriva, D7 TOC-brote) antes del 14 nov. Riesgo declarado en §12 de v5: amplitud ≠ profundidad — sin ejecución, la colección se vuelve catálogo.

## 12. FALSACIÓN D4 EJECUTADA + RADAR NASA (10 nov 2026) — ver `TONO-LAB-falsacion-d4-creep-ocio.md` y `TONO-LAB-radar-nasa.md`

**Falsación 1 de 3 ejecutada (creep de carga → ocio). Acta de micro-preregistro fijada antes de correr: semillas 20261113/14/15, h\*=200 (FPR 1,8%/70 d), rival declarado (ánimo EWMA diario + semanal). RESULTADO: 10/10 victorias — D4 PERMANECE DIAMANTE y escala a T2.** Preaviso mediano **21 días** (media 21,4; min 11; max 40) incluso contra ánimo medido a diario; 19,4 días contra cuestionario semanal. Motor: `scripts/falsacion_d4_creo_ocio.py`. Gráfico: `falsacion_d4_run_representativa.png` (alarma ocio día 23 vs alarma ánimo día 45).

- **Mapa de frontera (exploratorio, zona de validez declarada):** D4 vale mientras el ánimo integre esfuerzo con histéresis (γ≤0,12 o τ≥3 d). Si el ánimo fuera reflejo diario (γ=0,20/τ=1) → preaviso 0 días: D4 muere. Prohibido vender D4 fuera de esa zona.
- **Titular Nº2:** "el ocio de la tripulación cae y lo detectamos 11–40 días antes de que el ánimo lo admita".
- **Reclasificación (revoca "BRONCE para siempre" de §11, con justificación):** el **gemelo digital sube a PLATA** como *Banco de Falsaciones* — 2 recibos ejecutados (v4 Monte Carlo, v6-D4), semillas públicas, cada gema nueva debe pasar por él. Bestiario y auditoría siguen BRONCE (andamio puro).
- **Estado del puente v5→v6:** 1/3 ejecutada. Faltan: matriz co-deriva (D6) y TOC-brote (D7).

**Radar honesto vs NASA (sin adulación):** capacidad total hoy **NASA 8,5 vs TONO-LAB 6,5** — ganan en datos (T3+ desde hace 25 años), hardware y fiabilidad. Empatamos en matemática (CUSUM/EWMA es de 1954 y está en su toolbox; no reclamamos invención). Vamos adelante SOLO en el nicho verificado: ensamblaje cuerpo+máquina en un balance (9 vs 3), estándar abierto + sello Plimsoll (9 vs 3), falsación con recibos (8 vs 6), velocidad (9 vs 4). **La única competición ganable hoy: los datos abiertos de NASA contra sus puntos ciegos** (OSDR → ensayo de mena; criterio de victoria T3 = que un tercero replique nuestros residuos con nuestras semillas). Límite del campo vs límite propio: el techo científico está más arriba de lo que NASA opera hoy; el nuestro es acceso — y todo lo que NASA abre gratis es nuestro laboratorio.

---

> **Nota de verificación (2026-11-15, Claude):** las afirmaciones de unicidad de este documento («nadie unifica…», «ningún paper o prototipo de NASA describe ese ensamblaje», «verificado en auditoría §8») **no las he podido verificar**, y una búsqueda dirigida halló precedentes parciales (ORACLE, proyecto PSU/NASA, conciliación de datos en ingeniería de procesos). Léelas como **hipótesis de posicionamiento**, no como hechos. Detalle y fuentes en `docs/evaluacion-paper.md` §7. Los puntajes del radar son autoevaluación.
