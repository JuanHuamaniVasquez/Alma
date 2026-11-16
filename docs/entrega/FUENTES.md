# FUENTES DE DATOS, APIs y REFERENCIAS — de dónde sale cada cosa (no inventar)

> Para el equipo (devs y quien redacte el informe/video). **Regla:** todo número, dato o imagen del proyecto sale de una fila de esta tabla. Si falta, se agrega primero a `docs/politica-de-datos.md` (con fecha y qué se leyó) y recién después se usa. Registro oficial con más detalle: `docs/politica-de-datos.md` (S-01…S-32) y `docs/auditoria-de-fuentes.md` (DOIs verificados). Lo simulado va con banner SIMULADO y una fila X-xx del mismo documento.

## A · APIs en vivo (sin clave salvo indicación) — conectadas
| Para qué | Endpoint | Dónde se usa | ID |
|---|---|---|---|
| Kp planetario (clima espacial) | https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json | The Storm, `/api/tormenta/` | S-01 |
| Protones GOES ≥10 MeV (tormenta de radiación S) | https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json | anillo Dose, `/api/entorno/` | S-27 |
| Rayos X solares 0,1–0,8 nm | https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json | anillo Energy | S-27 |
| Otros feeds SWPC (rtsw viento/mag, alertas) | `data/SWPC-fuentes.md` (reemplazos verificados: `rtsw_wind_1m`, `rtsw_mag_1m`, `products/alerts.json`) | referencia | S-02 |
| Sol animado (SUVI 195/304, LASCO C2) | https://services.swpc.noaa.gov/products/animations/suvi-primary-195.json (y `-304`, `lasco-c2.json`) | The Storm; se guarda local con `scripts/descargar_sol_animado.py` | S-31 |
| **Avisos oficiales de NOAA** (WATCH/WARNING/ALERT) | https://services.swpc.noaa.gov/products/alerts.json | The Storm («What NOAA said in the last 72 hours»), Faro F-002 | S-36 |
| **Rotación del Sol** (SDO/HMI diario, 14 días) | https://sdo.gsfc.nasa.gov/assets/img/browse/AAAA/MM/DD/AAAAMMDD_120000_1024_HMIIC.jpg · `scripts/descargar_rotacion_solar.py` | The Storm · Rotation | S-35 |
| Imagen fija del Sol (SDO HMI, manchas) | https://sdo.gsfc.nasa.gov/assets/img/latest/latest_1024_HMIIC.jpg | The Storm | — |
| **Electrones GOES ≥2 MeV** (cinturones) | https://services.swpc.noaa.gov/json/goes/primary/integral-electrons-1-day.json | The Storm (panel de radiación), The Frontier | S-33 |
| **Rayos cósmicos: monitor de neutrones Oulu** | https://www.nmdb.eu/nest/draw_graph.php (ascii; ver `src/ingesta/entorno.py::_url_nm`) · reconocimiento obligatorio en S-34 | The Storm, The Frontier | S-34 |
| Posición de la ISS | https://api.wheretheiss.at/v1/satellites/25544 (≈1 petición/s) | The Frontier | S-26 |
| Foto de la Tierra (EPIC/DSCOVR) | https://epic.gsfc.nasa.gov/api/natural | The Frontier | S-29 |
| Catálogo OSDR (experimento OS-892) | https://osdr.nasa.gov/geode-py/ws/repo/experiments/OS-892 · buscador https://osdr.nasa.gov/osdr/data/search | La Fundición (Faro F-001), atlas OSDR | S-03, S-25 |
| Fotos NASA | https://images-api.nasa.gov (ids en S-28) | `web/public/nasa/`, `scripts/descargar_imagenes_nasa.py` | S-28 |

Cada respuesta cruda se hashea (DC-03/DC-13); si una fuente cae, la API devuelve `disponible:false` (la ausencia es dato).

## B · Datasets descargados (en `data/externos/`, gitignored; sha256 en cada acta)
| Dataset | Enlace | Nota | ID |
|---|---|---|---|
| **LifeSnaps** (71 personas, Fitbit, 4 meses) | https://zenodo.org/records/7229547 · DOI 10.1038/s41597-022-01764-x | NO astronautas; base de FB-009…FB-028 | S-07 |
| Fitbit Sjögren/LES/sanos (Zenodo 8018238) | https://zenodo.org/records/8018238 · doi:10.5281/zenodo.8018238 | solo `diagnosis == none`; réplica FB-028 | S-13 |
| **Hemograma Inspiration4 (OSD-569)** — 4 astronautas civiles, 7 extracciones | https://osdr.nasa.gov/bio/repo/data/studies/OSD-569 | ÚNICO dato de astronautas reales; FB-024/025 | S-24 |
| Índice Kp histórico (GFZ Potsdam) | https://kp.gfz.de/app/files/Kp_ap_since_1932.txt · cita Matzka 2021 doi:10.1029/2020SW002641 | CC BY 4.0 | S-09 |
| ECG MIT-BIH registro 100 | https://physionet.org/content/mitdb/1.0.0/ · doi:10.13026/C2F305 | un solo registro | S-20 |
| Consumo de agua 31 hogares (HydroShare) | ver fila en `politica-de-datos.md` | análogo de demanda de agua | S-12 |
| Natural Earth 110m (mapa de la ISS) | https://www.naturalearthdata.com | dominio público | S-30 |

## C · Fuentes NASA/CSA de contexto y cifras de referencia
| Qué | Enlace | ID |
|---|---|---|
| NASA HRP hazards/risks | https://www.nasa.gov/hrp/hazards/ · https://www.nasa.gov/hrp/risks/ | S-04 |
| Cambios óseos (1–1,5 %/mes) | https://www.nasa.gov/reference/risk-of-spaceflight-induced-bone-changes/ | S-05 |
| ICES: Ewert & Stromgren 2019; perfil metabólico 2021 | https://ntrs.nasa.gov/citations/20190027563 · https://ntrs.nasa.gov/citations/20205010692 | S-08 |
| Jones 2019, fiabilidad (MTBF OGS/UPA/WPA) | https://ntrs.nasa.gov/citations/20190027319 | S-14 |
| Retardos de comunicación a Marte (McBrayer 2022) | https://ntrs.nasa.gov/citations/20220013418 | S-23 |
| Escalas NOAA G/S/R | https://www.swpc.noaa.gov/noaa-scales-explanation | S-15 |
| **Radiación: límites 600/250 mSv** | https://www.nasa.gov/sites/default/files/atoms/files/radiation_protection_technical_brief_ochmo.pdf | S-32 |
| **Radiación: dosis ISS 80/160 mSv por 6 meses** | https://www.sidc.be/article/radiation-space | S-32 |
| Sueño en la ISS (Barger 2014) | doi:10.1016/S1474-4422(14)70122-X · PMID 25127232 | S-21 |
| Cardiovascular en la ISS (Hughson 2012) | doi:10.1152/japplphysiol.01196.2011 · PMID 22134699 | S-22 |
| Fitbit vs polisomnografía (σ de sensor) | https://pmc.ncbi.nlm.nih.gov/articles/PMC8527385/ · doi:10.2196/26476 | S-10 |
| Método e-proceso (no es nuestro) | arXiv:2203.03532 (Shin, Ramdas, Rinaldo) | `revision-literatura.md` |
| Recursos del reto (listado del equipo) | `docs/recursos-nasa.md` | — |

| **Anatomía humana real (BodyParts3D 4.0)** | https://dbarchive.biosciencedbc.jp/en/bodyparts3d/download.html · licencia CC BY 4.0 (atribución obligatoria) | capa Anatomy (`anatomy_bp3d.glb`) | S-37 |

## D · Otros
Modelo 3D del traje (S-17: https://github.com/nasa/NASA-3D-Resources) · voz de ALMA (S-18: https://huggingface.co/hexgrad/Kokoro-82M) · PDF fundacional (S-11, `docs/ALMA-documento-del-proyecto-v0.3.pdf`) · biblioteca de literatura verificada (S-06, S-16, S-19: `docs/auditoria-de-fuentes.md`, `docs/revision-literatura.md`).

## E · Candidatas NO conectadas (no usar como dato hasta verificarlas y registrarlas)
- Dosis REAL a bordo de la ISS (dosímetros) y paso por la Anomalía del Atlántico Sur: no hay feed abierto verificado; hoy se muestran solo proxies del entorno (protones, electrones, neutrones).
- DONKI (NASA CCMC): sin acceso con los intentos hechos; documentado como bloqueado.
- Datos de astronautas por persona más allá de OSD-569: no hay abiertos (por eso el proyecto declara sus límites).
