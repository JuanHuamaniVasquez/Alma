# Auditoría de fuentes — 2026-11-15

> Qué se hizo: se extrajeron **todos los identificadores de cita** de `docs/` y `data/` (PubMed, PMC, DOI, NTRS, arXiv) y se consultó cada uno en su base pública (NCBI, Crossref, arXiv, NTRS). Es reproducible: `uv run python scripts/verificar_fuentes.py --red`.
> Alcance: verifica que el identificador **existe y que su título coincide con lo que el doc dice de él**. No verifica que el doc interprete bien el contenido del paper. **No se editó ningún DOC-0x** (CLAUDE.md §8.6): las correcciones propuestas están en §4 y esperan tu aprobación.

## 1 · Identificadores verificados (existen y coinciden)

| Cita en los docs | Identificador | Enlace | Título real encontrado |
|---|---|---|---|
| Guyatt 1990 (N-of-1) | PMID 2297206 | https://pubmed.ncbi.nlm.nih.gov/2297206/ | *The n-of-1 randomized controlled trial: clinical usefulness. Our three-year experience.* (1990) |
| Basner 2013 (Mars-500) | PMID 23297197 | https://pubmed.ncbi.nlm.nih.gov/23297197/ | *Mars 520-d mission simulation reveals protracted crew hypokinesis and alterations of sleep duration…* (2013) |
| Checinska Sielaff 2019 | PMID 30955503 | https://pubmed.ncbi.nlm.nih.gov/30955503/ | *Characterization of the total and viable bacterial and fungal communities associated with the International Space Station surfaces* (2019) |
| Lazer 2014 (Google Flu) | PMID 24626916 | https://pubmed.ncbi.nlm.nih.gov/24626916/ | *Big data. The parable of Google Flu: traps in big data analysis.* (2014) |
| Cvach 2012 (fatiga de alarmas) | PMID 22839984 | https://pubmed.ncbi.nlm.nih.gov/22839984/ | *Monitor alarm fatigue: an integrative review.* (2012) |
| Hsu 2022 (normalización WBE) | PMC9376872 | https://pmc.ncbi.nlm.nih.gov/articles/PMC9376872/ | *Biomarkers selection for population normalization in SARS-CoV-2 wastewater-based epidemiology.* (2022) |
| Pagano 2010 (LQAS) | PMC2817093 | https://pmc.ncbi.nlm.nih.gov/articles/PMC2817093/ | *Commentary: Understanding practical lot quality assurance sampling.* (2010) |
| Kawada 2016 (actigrafía astronautas) | PMC5022007 | https://pmc.ncbi.nlm.nih.gov/articles/PMC5022007/ | *Applicability of the actigraphy for astronauts in spaceflight.* (2016) |
| Swanson 2018 (circadiano y hueso) | PMC5994176 | https://pmc.ncbi.nlm.nih.gov/articles/PMC5994176/ | *The importance of the circadian system & sleep for bone health.* (2018) |
| Mathunjwa 2025 (sueño doméstico) | PMC11945902 | https://pmc.ncbi.nlm.nih.gov/articles/PMC11945902/ | *A Comprehensive Review of Home Sleep Monitoring Technologies…* (2025) |
| Fahrion 2021 | PMC8281973 | https://pmc.ncbi.nlm.nih.gov/articles/PMC8281973/ | *Use of Photobioreactors in Regenerative Life Support Systems for Human Space Exploration.* (2021) |
| Ramdas et al. 2023 | DOI 10.1214/23-STS894 | https://doi.org/10.1214/23-STS894 | *Game-Theoretic Statistics and Safe Anytime-Valid Inference* (2023) |
| Angelopoulos & Bates 2021 | arXiv 2107.07511 | https://arxiv.org/abs/2107.07511 | *A Gentle Introduction to Conformal Prediction and Distribution-Free Uncertainty Quantification* |
| Review conformal series temporales | arXiv 2511.13608 | https://arxiv.org/abs/2511.13608 | *A Gentle Introduction to Conformal Time Series Forecasting* |
| Ramdas et al. 2020 | arXiv 2009.03167 | https://arxiv.org/abs/2009.03167 | *Admissible anytime-valid sequential inference must rely on nonnegative martingales* |
| Jones 2019 (repuestos) | NTRS 20190027319 | https://ntrs.nasa.gov/citations/20190027319 | *High Reliability Requires More than Providing Spares* (2019) |
| Glaessgen & Stargel 2012 | NTRS 20120008178 | https://ntrs.nasa.gov/citations/20120008178 | *The Digital Twin Paradigm for Future NASA and U.S. Air Force Vehicles* (2012) |
| Slack 2015 (conducta) | NTRS 20150016966 | https://ntrs.nasa.gov/citations/20150016966 | *Risk of Adverse Cognitive or Behavioral Conditions and Psychiatric Disorders* — autores Slack, Schneiderman, Leveton, Whitmire, Picano |
| Riesgo de síndromes de radiación agudos | NTRS 20160003870 | https://ntrs.nasa.gov/citations/20160003870 | *Evidence Report: Risk of Acute Radiation Syndromes Due to Solar Particle Events* (2016) |
| NIAC Torpor | NTRS 20180007195 | https://ntrs.nasa.gov/citations/20180007195 | *Advancing Torpor Inducing Transfer Habitats for Human Stasis to Mars: II – Phase…* (2018) |

Matiz: Fahrion 2021 es un artículo sobre fotobiorreactores en soporte de vida; los docs lo citan por BIOS-3, y no he comprobado que el artículo trate BIOS-3 a fondo.

## 2 · Hallazgos (lo que NO cuadra o no se pudo verificar)

| ID | Hallazgo | Gravedad | Evidencia |
|---|---|---|---|
| H-1 | ~~**No pude verificar OS-892.** La API pública de OSDR devuelve 0 resultados para el estudio 892 (`/osdr/data/osd/meta/892` → `hits: 0`). La página `osdr.nasa.gov/bio/repo/data/experiments/OS-892` responde 200, pero es una aplicación JavaScript que responde 200 a cualquier ruta, así que **ese 200 no prueba que el experimento exista** ni que la cita textual sea real. Esto contradice lo que dice `data/OS-892-extracto.md` ("fetch directo de la página oficial")~~ **RETRACTADO (2026-11-15, mismo día).** Error mío: consulté la API de *studies* (OSD-NNN) y OS-892 es un *experimento* (accesión OS), por eso daba 0. Con la API de experimentos `https://osdr.nasa.gov/geode-py/ws/repo/experiments/OS-892`: registro real (osID OS-892, 80NSSC21K0299, Public, `files: []`), cita literal coincide, y el control `OS-999999` da HTTP 403. Lo señaló la otra IA y lo comprobé yo | Resuelta | `data/lecturas/osdr_OS-892_20261115T051034Z.json` |
| H-2 | **La cifra ósea tiene dos anclas verificadas, no contradictorias:** HRP dice 1–1,5 % de *densidad*/mes (misiones de 4–6 meses) y OS-892 dice ~1–2 % de *masa*/mes (texto de antecedentes). Se aplicó el doble anclaje en el bestiario. Antes decía: **la cifra 1–2 %/mes atribuida a OS-892 no coincide con la fuente que sí verifiqué.** La página de NASA HRP *Risk of Spaceflight-Induced Bone Changes* dice, textual: *"Consequently, on average, bones lose between 1% and 1.5% of their density each month during four-to-six-month missions."* Los docs (bestiario, extracto OS-892, FM-3) dicen 1–2 %/mes y no enlazan esta página | **Alta** | https://www.nasa.gov/reference/risk-of-spaceflight-induced-bone-changes/ (leída 2026-11-15). La página no precisa sitio óseo ni ejercicio |
| H-3 | El DOI `10.1038/s41526-026-00628-7` existe (Bowman et al., 2026-07-15, npj Microgravity: *Persistent cognitive impairment and bone health following helium ion exposure…*), pero **no pude comprobar que cite "OSD-892"**, como afirma el extracto (el artículo está tras una redirección con cookie). Por su título no trata de pérdida ósea en astronautas por MSC | Media | Crossref; la página de nature.com no es legible sin sesión |
| H-4 | 3 de los 6 endpoints de SWPC listados daban 404 (ya corregido en `data/SWPC-fuentes.md`) | Resuelta | ver `data/SWPC-fuentes.md` |
| H-5 | La mayoría de las citas de los DOC-0x son **por nombre, sin identificador ni enlace** (Frost 2003, Mehta 2014/2017, Hassler 2014, Parsons & Townsend 2000, Severinghaus 1994, Wheeler 1996, Page 1954, Roberts 1959, Mitchell et al. 1989, Little & Rubin, Zucker 1997, Roberts 2004, NASA-STD-3001, OCHMO-TB-004/-020, XStat K130218, Tafforin 2013, Cantisani 2026…). No son necesariamente falsas, pero hoy **no se pueden comprobar** | Media | `scripts/verificar_fuentes.py` solo ve las que traen identificador |
| H-6 | Cifras sin fuente enlazada: ~0,83 kg O₂/día y ~1 kg CO₂/día por persona ("ECLSS NASA"), 600 mSv carrera, 250 mSv/evento, 1,84/0,64 mSv/día (Hassler), "19/49 astronautas con cefalea", "~4.300 citas", "~98 % de recuperación de agua" | Media | por nombre en el bestiario; sin enlace |
| H-7 | Contenido **autocalificado o simulado** dentro de los docs (no es dato real, y los propios docs lo admiten en parte): las puntuaciones del radar (NASA 8,5 vs TONO-LAB 6,5; "rúbrica 6,4 → 8,9"), los resultados de FB-001/FB-002 (preaviso 24 h, 21 días: son **en silicio**) y el "Kp=3,33 del 9-nov" (ya fuera de la ventana de 7 días del feed; no se puede reverificar) | Media | `docs/politica-de-datos.md` §3 (X-03); `radar-nasa.md` §2–§3 |
| H-8 | Ejemplo de que "HTTP 200" no basta: OSDR (SPA) y también el enlace de la CSA sobre radiación 2026-02-26, que **no respondió** (000) | Baja | `docs/recursos-nasa.md` |

## 3 · Lo que sí está sólido (para presumir con razón)

- 19 identificadores de literatura científica comprobados contra sus bases oficiales: la bibliografía con identificador **no tiene una sola cita inventada** en lo comprobado.
- Una cifra ósea ahora anclada a una fuente verificada y enlazada de NASA HRP.
- El método (script reproducible + registro) es repetible por un tercero, que es exactamente el criterio T3 del propio radar.

## 4 · Correcciones propuestas (NO aplicadas; los DOC no se editan sin tu orden)

1. **Hueso (H-2):** donde los docs digan "1–2 %/mes (NASA OSDR OS-892)", citar como fuente verificada *"1–1,5 % de densidad por mes en misiones de 4–6 meses"* con el enlace de NASA HRP, y dejar el 1–2 % de OS-892 como **no verificado** hasta que alguien abra el experimento en un navegador. El modelo B(t+1)=B(t)·e^(−k) con k = 1 %/mes sigue cayendo dentro del rango verificado.
2. **OS-892 (H-1, H-3):** rebajar `data/OS-892-extracto.*` a "pendiente de verificación manual"; no usarlo como fuente de tarjetas DC-12 hasta confirmarlo. Para ti: ábrelo en el navegador y pega la descripción exacta; si coincide, lo subo a verificado.
3. **Citas por nombre (H-5, H-6):** resolver cada una a un identificador (DOI/PMID/URL) y añadirlo al registro de fuentes. Puedo hacerlo con Crossref por lotes y verificarlas con el mismo script.
4. **Autocalificaciones (H-7):** marcarlas en los docs como "estimación propia, no verificada externamente", sin cambiar el contenido.
