# Revisión de literatura (M5.5 v1 + M5.5b) — qué existe y qué podemos afirmar

> **Alcance honesto:** v1 = 6 consultas web (2026-11-15). **M5.5b (misma fecha) = búsqueda directa por API en PubMed (E-utilities, 13 consultas) y NTRS (API pública, 8 consultas)**; **IEEE Xplore y Google Scholar NO se consultaron** (sin acceso programático abierto): el preprint debe decirlo. Sigue sin ser una revisión sistemática (sin doble cribado ni protocolo PRISMA). «No encontré X» **no** significa «X no existe». Cada identificador citado abajo fue **verificado contra Crossref** (o la página del editor/arXiv) el mismo día; un DOI que supuse de memoria y resultó ser de otro artículo se corrigió antes de citarlo.

## Consultas
| # | Consulta (resumen) | Qué devolvió |
|---|---|---|
| 1 | reconciliación de datos / error grueso / balance de masa en soporte vital | Literatura de ingeniería de procesos (Tamhane & Mah; pruebas globales, nodales, de medición). **Nada específico de ECLSS espacial.** |
| 2 | CUSUM + línea base personal + wearables + tasa de falsas alarmas | Patentes y material comercial; **ningún estudio arbitrado** que mida FPR por persona. |
| 3 | N-of-1 / línea base individual en astronautas | Monitoreo individual multi-astronauta (Zheng 2023), revisiones de medicina personalizada; **ningún N-of-1 espacial**. |
| 4 | salud de la tripulación autónoma en espacio profundo | Marcos conceptuales (Scott 2023; Cypko 2025): piden autonomía y líneas base por persona; **ningún sistema validado en vuelo**. |
| 5 | actividad geomagnética (Kp) × HRV / sueño | Evidencia **mixta**, pequeña y observacional (McCraty 2017; Zenchenko 2024); **ningún estudio Kp × sueño** encontrado. |
| 6 | deriva de sensor vs fuga física con residuo de balance | Fuga como término del balance de masa en reconciliación robusta (control de procesos); **ningún caso de hábitat sellado**. |

## Trabajos relacionados (identificadores verificados)
| Trabajo | Identificador | Qué aporta | Relación con ALMA |
|---|---|---|---|
| Tamhane & Mah (1985), *Data Reconciliation and Gross Error Detection in Chemical Process Networks*, Technometrics | doi:10.1080/00401706.1985.10488080 | Reconciliar medidas contra balances y detectar errores gruesos con los residuos | **Es el método del Contrapeso (MO-6).** No es nuestro: lo aplicamos |
| Page (1954), *Continuous Inspection Schemes*, Biometrika | doi:10.1093/biomet/41.1-2.100 | El CUSUM | **Es el detector MO-3.** No es nuestro |
| Cvach (2012), *Monitor Alarm Fatigue: An Integrative Review*, Biomed Instrum Technol | doi:10.2345/0899-8205-46.4.268 | La fatiga de alarmas como problema central | Motiva «verde con recibo», alertas ámbar antes que rojas |
| Scott et al. (2023), *Biomonitoring and precision health in deep space supported by AI*, Nat Mach Intell | doi:10.1038/s42256-023-00617-5 (preprint: arXiv:2112.12554) | Pide un sistema de salud espacial autónomo y personalizado | **Define el problema que abordamos**; no propone ni valida detectores concretos |
| Zheng et al. (2023), *Time-resolved molecular measurements reveal changes in astronauts during spaceflight*, Front Physiol | doi:10.3389/fphys.2023.1219221 | Primer monitoreo individual multi-astronauta (27); recomienda línea base por tripulante y detección de desvíos | Respalda la premisa «cada persona contra su propia firma» |
| Pavez Loriè et al. (2021), *The Future of Personalized Medicine in Space*, Front Bioeng Biotechnol | doi:10.3389/fbioe.2021.739747 | Variabilidad interindividual y medicina personalizada en espacio | Contexto |
| Cypko et al. (2025), *Digital Health for Space*, SpaceCHI (OASIcs) | https://drops.dagstuhl.de/storage/01oasics/oasics-vol130-spacechi2025/html/OASIcs.SpaceCHI.2025.33/OASIcs.SpaceCHI.2025.33.html (DOI no resuelto en Crossref) | Niveles de autonomía según la distancia de la misión | Contexto |
| McCraty et al. (2017), *Synchronization of Human ANS Rhythms with Geomagnetic Activity*, Int J Environ Res Public Health | doi:10.3390/ijerph14070770 | HRV acompasada con actividad geomagnética en 10 personas | Hipótesis de la tarjeta Kp × sueño/HRV |
| Zenchenko et al. (2024), *Long-Term Study of the Synchronization Effect between Geomagnetic Field Variations and Minute-Scale HRV*, Atmosphere | doi:10.3390/atmos15010134 | Efecto de sincronización que no depende del nivel de actividad | Evidencia mixta: **nuestro nulo FB-014 es coherente con que el efecto sea pequeño o inexistente a nivel personal** |
| Jones (2019), NTRS 20190027319 | verificado en S-14 | Los manifiestos de fiabilidad de la ISS erraron 1,9–22× | La premisa «el manifiesto miente» |

## Qué podemos afirmar y qué no (declaración de novedad acotada)
1. **No afirmamos métodos estadísticos nuevos.** CUSUM, reconciliación de datos y pruebas intrapersona son conocidos.
2. **No afirmamos «primer sistema…»**: no tenemos una revisión que lo respalde.
3. **Lo que sí defendemos (y es verificable en el repo):** una *práctica*, no un algoritmo — cada componente del sistema se falsó con un acta hasheada **antes** de correr, los resultados negativos se publican (FB-010, FB-014, FB-015, FB-016 B, FB-020, FB-020-v2), el «verde» lleva recibo con su potencia (DC-14), y la demo kill contrapone un detector contra el manifiesto y otro contra una ley en el mismo día. En las búsquedas no apareció una **aplicación explícita de reconciliación de datos a ECLSS de hábitat tripulado con la unidad del manifiesto como piso de detección**, pero eso es ausencia de evidencia, no evidencia de ausencia.
4. **Antes de cualquier afirmación de novedad en el preprint:** M5.5b (PubMed, IEEE Xplore, Scholar y NTRS directos, con los mismos términos) y mostrar el resultado de esa búsqueda.

## M5.5b · Búsqueda directa (PubMed + NTRS, 2026-11-15) y su efecto sobre lo que afirmamos
Las consultas estrictas con todos los conceptos a la vez devolvieron casi nada (reconciliación + espacio: 0; CUSUM + wearable + línea base: 0; N-of-1 + astronauta: 7, todos estudios de caso de rendimiento sensorimotor 1993–2010, **ningún diseño N-of-1 de salud**). Las consultas más amplias sí devolvieron literatura relevante, que **cambia nuestra declaración**:

| Hallazgo | Identificador (verificado en Crossref/NTRS) | Efecto |
|---|---|---|
| El **balance de masa de la nave como herramienta de diagnóstico** ya existe en NASA (aire de cabina, contaminantes traza) — Kayatin 2021 | NTRS 20210016640 (público) | **Quita cualquier insinuación de que el diagnóstico por balance de masa en naves es nuevo.** Lo nuestro es otra cosa: cierre diario por bucle con la **incertidumbre del manifiesto como piso de detección** y su contraste contra un detector de manifiesto |
| Un **CUSUM individual** sobre una respuesta fisiológica personal (presión arterial) — Cornélissen et al. 1997 | doi:10.3109/03091909709031156 | **El CUSUM personal sobre series fisiológicas no es nuevo** (hace casi 30 años) |
| **Líneas base personales + wearables para detectar desviaciones** es un área activa — Cacheda 2026; Krieger 2026 | doi:10.1177/20552076261477919 · doi:10.3389/fdgth.2026.1998814 | No es nuevo; cada vez más común |
| Monitoreo de astronautas con wearables: Gupta 2025 (revisión), Roda 2018 (biosensores), Bellisle 2020 (IVA); NASA Astroskin (HERA) | doi:10.1016/j.lssr.2025.06.011 · doi:10.1016/j.bios.2018.03.062 · doi:10.1109/EMBC44109.2020.9175674 · NTRS 20190000238 | Contexto y prototipos analógicos; la parte de **detección con recibo y potencia declarada** no apareció |
| Kp/geomagnético × HRV: **32 resultados** en PubMed; efectos reportados en cohortes (Zilli Vieira 2022, Normative Aging Study; Alabdulgader 2018; Mattoni 2020) y un experimento de laboratorio aleatorizado (Gurfinkel 2018) | doi:10.1016/j.scitotenv.2022.156235 · doi:10.1038/s41598-018-20932-x · doi:10.1007/s00421-020-04369-7 · doi:10.1007/s00484-017-1460-8 | Nuestro nulo FB-014 (51 personas, desplazamiento circular intrapersona, Kp global) **no contradice** esos trabajos (otro diseño, otra cohorte y no descartamos efectos pequeños), pero **no podemos presentarlo como «la tormenta no afecta»**: es un nulo acotado |
| Kp × **sueño**: 14 resultados, ninguno midió sueño de wearable contra Kp (temas de ritmo circadiano e hipomagnetismo, bipolaridad, etc.) | PubMed (consulta B4) | Sin hallazgo directo; el nulo de FB-014 en sueño tampoco tiene comparador directo |
| Reconciliación de datos / error grueso en soporte vital: 0 en PubMed y 0 en NTRS; fallo de sensores en soporte vital sí aparece como detección de fallos (NTRS 20110024002 BSP, 19960017281) | NTRS | Hay literatura NASA de **detección de fallos** en sensores; **no apareció** reconciliación formal de balances sobre ECLSS tripulado |

### Declaración de novedad v2 (sustituye al punto 3 de arriba)
- **Se retira** cualquier lectura de «aplicar balance de masa a una nave» como novedad (Kayatin 2021) y de «CUSUM personal sobre fisiología» (Cornélissen 1997).
- **Lo que queda como contribución defendible es de método de trabajo, no de algoritmo:** (a) una cadena completa de preregistro con hash antes de correr y una sola ejecución por acta; (b) publicación sistemática de resultados negativos propios (FB-010, FB-014, FB-015, FB-016 B, FB-020, FB-020-v2); (c) el «verde con recibo» (potencia/MDE declarados dados los días observados); (d) la demo contra un detector de manifiesto con el cierre diario como contraste.
- **No se afirma** que (d) sea nuevo: solo que **no apareció** en PubMed ni NTRS. Ausencia en una búsqueda sin IEEE/Scholar y sin protocolo PRISMA no es evidencia de ausencia.
