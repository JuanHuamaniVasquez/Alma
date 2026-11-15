# Parámetros públicos para anclar la simulación de FB-005 (El Contrapeso)

> **Qué es:** cifras **leídas por Claude en los PDF originales de NASA el 2026-11-15** (no de memoria), con su ubicación. Sirven para que el manifiesto de la simulación SIMULADA (registro X-02) use números citables en vez de inventados.
> **Qué NO es:** mediciones. Son **valores de planificación de modelos** (MetMan, BVAD/HIDH); Ewert & Stromgren advierten que *«perspiration and respiration values this high have not been documented on ISS»*. Cualquier resultado que los use sigue siendo «en silicio».

| ID | Parámetro | Valor | Fuente y ubicación | Cita textual / nota |
|---|---|---|---|---|
| P-01 | Astronauta de referencia | **82 kg** | Ewert & Stromgren 2019, ICES-2019-126, Fig. 1 y 2; ICES 2021 (NTRS 20205010692) «HIDH size individual of 82 kg» | *«Daily mass balance of an 82 kg astronaut for consumables planning»* |
| P-02 | O₂ consumido | **0.89 kg/día** (perfil de ejercicio 90 min/día) · **0.84 kg/día** (protocolo corto, Tabla 2) | Ewert & Stromgren §II; ICES 2021 Tabla 2 «Daily Totals» | *«A daily O2 requirement of 0.89 kg is also predicted by the model.»* |
| P-03 | CO₂ producido | **1.08 kg/día** (90 min) · **1.01 kg/día** (protocolo corto) | ídem | *«daily total outputs of 1.08 kg of CO2, 2.53 kg of combined perspiration and respiration water vapor, and 0.51 kg of liquid sweat»* |
| P-04 | Vapor de agua / sudor líquido | **2.53 / 0.51 kg/día** (90 min) · **2.27 / 0.22 kg/día** (protocolo corto) | ídem | ver P-03 |
| P-05 | Cociente respiratorio (RQ) | **0.86** nominal y sueño · **0.95** aeróbico · **0.96** resistivo | ICES 2021, §II | *«the new RQ was determined to be 0.86 for nominal and sleep, 0.95 for aerobic exercise and 0.96 for resistive exercise»* (antes se asumía 0.92) |
| P-06 | Metabolismo (era Shuttle) | promedio 24 h **472 kJ/h (131 W)**; máx 686 kJ/h; mín (sueño) 317 kJ/h | ICES 2021, §I | SODB: *«nominal 24-hour average was 472 kJ/hr (131 W, 447 BTU/hr)»* |
| P-07 | Metabolismo diario total | **12 027 kJ/día** (protocolo corto, 82 kg, fitness medio) | ICES 2021, Tabla 2 | fila «Daily Totals» |
| P-08 | Suministro de comida (ISS) | **2.39 kg/persona/día** | Ewert & Stromgren, citando BVAD Tabla 4-53 | *«an average food supply planning value of 2.39 kg of individually packaged food delivered per person per day»* |
| P-09 | Agua en orina | 1.63 kg/día (HIDH Tabla 7.4-1) · 1.4 a >2 kg/día (BVAD Tabla 4-38); **se usó 1.40** | Ewert & Stromgren | los autores ajustaron a 1.40 *«to ensure mass closure»* |
| P-10 | **Principio de conservación** | — | Ewert & Stromgren, introducción | *«The principle of mass conservation can be applied to the crew of a spacecraft … Over time, given steady body mass, each individual's mass inputs and outputs will balance.»* |

## Lectura útil (aritmética mía, rotulada como **derivada**)
- Entre los dos protocolos publicados, el CO₂ difiere **0.07 kg/día (≈ 6.9 %)** y el O₂ **0.05 kg/día (≈ 6.0 %)**. Es un orden de magnitud **observable** de cuánto puede variar «lo que emite una persona» según el protocolo asumido: apoya, sin demostrarlo, el hallazgo v4 de que el **piso de detección lo fija el manifiesto** y no el sensor.
- Las cifras del bestiario «≈0,83 kg O₂/día y ≈1 kg CO₂/día (ECLSS NASA)» **quedan ancladas** a estas fuentes: 0.84/1.01 (protocolo corto). El 0.83 del bestiario difiere en 0.01 kg: no se corrige, se anota.

## Fuentes
- Ewert, M. K. & Stromgren, C. (2019). *Astronaut Mass Balance for Long Duration Missions*. ICES-2019-126 · NTRS [20190027563](https://ntrs.nasa.gov/citations/20190027563).
- *Developing a Daily Metabolic Rate Profile for Human Exploration Missions*. ICES 2021 · NTRS [20205010692](https://ntrs.nasa.gov/citations/20205010692).

## Datos reales sobre «el manifiesto miente» (Jones 2019, NTRS 20190027319; leído en el PDF)

| ID | Dato | Cita textual |
|---|---|---|
| P-11 | Error de los manifiestos de fiabilidad de la ISS | *«Of the 20 ORUs with different estimated and flight MTBFs, 14 had lower actual than estimated MTBFs. 7 of the 20 had failure rates between 1.9 and 6.3 times the original failure rates … 4 of the 20 ORUs had failure rates from 7.5 to 22 times the estimated failure rates. These were the four UPA ORUs…»* |
| P-12 | **El cuerpo rompe la máquina** (acoplamiento documentado) | *«The ISS Urine Processor Assembly (UPA) distillation assembly failed due to precipitation of calcium sulfate due to unexpectedly high concentrations of calcium in astronaut urine, due to unanticipated astronaut bone loss in microgravity. (Do, 2016)»* |
| P-13 | Peor componente | *«the worst in ISS life support is a pump in the urine processor. This single highly unreliable component increases the system failure rate to a disastrous level, 98%.»* |

Límite: P-11 cuenta solo las ORU **cuyo MTBF de vuelo difiere del estimado** (no todas las ORU de la ISS). Es un ratio de tasas de fallo, no un error de consumo de recurso: sirve como **prior de lo equivocado que puede estar un manifiesto**, no como σ directa.

## Consistencia interna (aritmética mía, **derivada**, rotulada así)
Cociente de masas CO₂/O₂: Ewert 1,08/0,89 = **1,21** → RQ molar = 1,21 × (32,00/44,01) ≈ **0,88**; ICES 2021 Tabla 2: 1,01/0,84 = **1,20** → RQ ≈ **0,87**. Ambos quedan entre el RQ nominal (0,86) y el aeróbico (0,95), y el de más ejercicio (90 min) es mayor que el de menos: coherente con P-05. Las cifras de NASA son **consistentes entre sí**, lo que da confianza en usarlas como parámetros.
