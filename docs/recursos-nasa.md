# Recursos NASA / CSA — fuentes públicas del proyecto

> Lista de enlaces aportados por el humano (2026-11-14/15) como recursos del reto *Health Monitoring Software for Astronauts*.
> Uso: fuentes con identificador para las tarjetas DC-12 (`fuentes[]`), anclas científicas y datos de ingesta. **No son datos descargables por sí mismos**: antes de citar una cifra de cualquiera de ellos, abrir la página y copiar la cita textual (regla de oro, DOC-00 §4).
> Estado de verificación: "HTTP" = respuesta del enlace comprobada con `curl` el 2026-11-15 (UTC). **Ningún contenido ha sido leído todavía** salvo donde se indique.

## 1 · Enlaces del reto (aportados por el humano)

| # | Recurso | URL | HTTP | Para qué sirve | Contenido leído |
|---|---|---|---|---|---|
| R-1 | NASA HRP — Hazards (los 5 peligros del vuelo espacial) | https://www.nasa.gov/hrp/hazards/ | 200 | Marco de peligros (radiación, aislamiento, distancia, gravedad, ambiente hostil/cerrado). Ancla para decir qué variable de entrada afecta a qué parte del cuerpo. | Sí, ver §4 (resumen, sin cita verbatim) |
| R-2 | NASA HRP — Ongoing HRP research | https://www.nasa.gov/hrp/ongoing-hrp-research/ | 200 | Investigación en curso: dónde NASA admite huecos. Candidata a fuente de tarjetas DC-12. | No |
| R-3 | CSA — Monitoring radiation / astronaut health (2026-02-26) | https://www.asc-csa.gc.ca/eng/news/articles/2026/2026-02-26-monitoring-radiation-astronaut-health.asp | **000 (sin respuesta desde este equipo)** | Monitoreo de radiación y salud del astronauta: presupuesto de dosis (LB-1 `dosis`). | No |
| R-4 | CSA — Why do we conduct science experiments in space? | https://www.asc-csa.gc.ca/eng/iss/science/why-do-we-conduct-science-experiments-in-space.asp | 200 | Contexto general; baja prioridad como ancla. | No |
| R-5 | Space Apps 2026 — reto Health Monitoring Software (pestaña Resources) | https://www.spaceappschallenge.org/2026/challenges/health-monitoring-software/?tab=resources | **000 (falla TLS en este equipo: "unable to get local issuer certificate")** | Lista oficial de recursos y entregables. **Pendiente: el humano debe copiar la pestaña Resources desde su navegador.** | No |

(El humano pasó R-1 dos veces; está una sola vez.)

## 2 · Fuentes de datos ya identificadas (de los archivos de `posible/`, a mover en M0.4)

| Recurso | URL | HTTP | Qué es | Verificación |
|---|---|---|---|---|
| NOAA SWPC — Kp planetario | https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json | 200 | IN-3, Canal C, base de FB-002 | Leído por mí 2026-11-15: último registro `2026-11-15T00:00:00 Kp=2.00`, coincide con `data/SWPC-fuentes.md` |
| NOAA SWPC — otros 5 feeds (plasma, mag, rayos X, protones, alertas) | ver `SWPC-fuentes.md` | — | LA TORMENTA | **No verificados por mí todavía** |
| NASA OSDR — experimento OS-892 | https://osdr.nasa.gov/bio/repo/data/experiments/OS-892 · API https://osdr.nasa.gov/geode-py/ws/repo/experiments/OS-892 | 200 | Experimento real y público; **0 archivos de datos publicados**; cita de antecedentes 1–2 % de masa ósea/mes | **Verificado (API + control negativo)**. Antes: Página responde; la cita textual aún no la he comparado yo |

Regla de uso de OS-892: citable como fenómeno documentado, **no** como archivo de datos (no hay archivos).

## 3 · Páginas adicionales leídas (2026-11-15)

Ambas son **páginas descriptivas, sin datos ni conjuntos descargables**: no enlazan a OSDR, NTRS, informes de evidencia ni estándares. Sirven de **marco y de puerta de entrada** a las páginas de cada riesgo.

| Recurso | URL | HTTP / lectura |
|---|---|---|
| NASA HRP — Risks (17 riesgos, 3 grupos) | https://www.nasa.gov/hrp/risks/ | leída |
| NASA HRP — Hazards (5 peligros) | https://www.nasa.gov/hrp/hazards/ | leída |

Las 5 páginas por peligro: [radiación](https://www.nasa.gov/hrp/hazard-space-radiation/) · [aislamiento y confinamiento](https://www.nasa.gov/hrp/hazard-isolation-and-confinement/) · [distancia de la Tierra](https://www.nasa.gov/hrp/hazard-distance-from-earth/) · [campos de gravedad](https://www.nasa.gov/hrp/hazard-gravity-fields/) · [entornos hostiles/cerrados](https://www.nasa.gov/hrp/hazard-hostile-closed-environments/). **No leídas todavía.**

## 4 · Los 5 peligros y los 17 riesgos de NASA HRP (según las páginas, 2026-11-15)

Cita de la página de riesgos: *"NASA's Human Research Program (HRP) seeks to understand specific risks associated with the hazards of human spaceflight."* La página **no** asigna cada riesgo a un peligro; ese cruce está por hacer.

**5 peligros:** radiación espacial · aislamiento y confinamiento · distancia de la Tierra · campos de gravedad · entornos hostiles/cerrados.

**Riesgos — fisiología (11):** sistema inmune alterado · función sensoriomotora y vestibular · adaptaciones cardiovasculares · enfermedad por descompresión · interacción huésped-microorganismo · hipoxia · alimentación y nutrición inadecuadas · lesión/rendimiento en caminatas espaciales (EVA) · menor aptitud cardiorrespiratoria y musculoesquelética · SANS (síndrome neuro-ocular) · cambios óseos inducidos por vuelo.
**Riesgos — conducta y factores humanos (5):** cambios conductuales y trastornos psiquiátricos · trabajo en equipo inadecuado · sueño inadecuado y horarios irregulares · soporte de operaciones de sistemas inadecuado · lesión por cargas dinámicas.
**Riesgos — radiación (1):** cánceres inducidos por radiación.

URLs de cada riesgo (todas bajo `https://www.nasa.gov/reference/`): `risk-of-altered-immune-system-responses/` · `risk-of-altered-sensorimotor-and-vestibular-function/` · `risk-of-cardiovascular-adaptations/` · `risk-of-decompression-sickness/` · `risk-of-host-microorganism-interactions/` · `risk-of-hypoxia/` · `risk-of-inadequate-food-and-nutrition/` · `risk-of-injury-and-compromised-performance-from-extravehicular-activity-eva/` · `risk-of-reduced-cardiorespiratory-and-musculoskeletal-fitness/` · `risk-of-spaceflight-associated-neuro-ocular-syndrome-sans/` · `risk-of-spaceflight-induced-bone-changes/` · `risk-of-behavioral-conditions-and-psychiatric-disorders/` · `risk-of-inadequate-teamwork/` · `risk-from-inadequate-sleep-and-irregular-schedules/` · `risk-of-inadequate-systems-operations-support/` · `risk-of-injury-from-dynamic-loads/` · `risk-of-radiation-induced-cancers/`

**Cruce propuesto con ALMA (inferencia mía, a validar contra cada página de riesgo antes de citar):** sueño (DC-01) ↔ *Inadequate Sleep and Irregular Schedules* · ánimo (DC-02) ↔ *Behavioral Changes and Psychiatric Disorders* · hueso (FM-3, OS-892) ↔ *Spaceflight-Induced Bone Changes* · dosis (LB-1) ↔ *Radiation-Induced Cancers* · inmunidad (LB-1) ↔ *Altered Immune System* + *Host-Microorganism* · aire (LB-1) ↔ *Hypoxia* · conducta (LB-1) ↔ *Inadequate Teamwork* · carga (LB-1) ↔ *Reduced Fitness*.

## 5 · Pendientes

- [ ] R-5: pegar la pestaña Resources del reto (o arreglar el certificado raíz del sistema).
- [ ] R-3: abrir desde el navegador o reintentar (puede ser caída puntual).
- [ ] Leer las páginas de cada riesgo (§4) y R-2, y extraer con cita textual cuáles sirven como fuente de tarjetas DC-12. Prioridad: sueño, hueso, conducta, inmunidad, radiación.
- [ ] Reverificar los 6 feeds de SWPC cuando exista el loader de IN-3 (M0.4).
