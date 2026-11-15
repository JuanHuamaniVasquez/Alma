# Política de datos — nada simulado sin etiqueta, nada inventado

> Decisión del humano (2026-11-15). Vale para todo el código y todos los docs de este repo. Es la aplicación estricta de CLAUDE.md §3 (mandamiento 3) y §9 (puerta 1: prohibido fake data).

## 1 · Reglas

1. **Todo dato es real y tiene fuente identificable** (URL, DOI, accesión OSDR, lote) y fecha de acceso. Sin fuente cargada, el dato no existe en el sistema.
2. **Orden de búsqueda de datos** (la búsqueda es trabajo aparte del código; la hacen el humano y Claude):
   1. Los enlaces de NASA/CSA de `docs/recursos-nasa.md`.
   2. Si ahí no está: otros **papers** o **datos abiertos/libres** (OSDR, NOAA SWPC, NASA NTRS, PubMed/PMC, repositorios con licencia abierta). Se anotan en §2 con licencia.
3. **Si el dato no existe, el ítem se declara bloqueado.** No se rellena, no se supone, no se "aproxima para avanzar".
4. **Lo simulado o inventado se etiqueta SIEMPRE**: banner `SIMULADO` en la salida y una fila en §3 con el motivo. Lo que no está en §3 no está permitido.
5. Una cifra solo se cita tras abrir su fuente y copiar la cita textual. Cifras "de memoria" no entran.
6. Claude avisa al humano ante cualquier duda sobre si algo es real, simulado o inventado, antes de seguir.

## 2 · Registro de fuentes reales

| ID | Fuente | URL / identificador | Licencia | Último acceso | Estado |
|---|---|---|---|---|---|
| S-01 | NOAA SWPC — índice Kp planetario | https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json | Dominio público (agencia federal EE. UU.) — confirmar al cargar | 2026-11-15 | Leído: Kp=2.00 a 2026-11-15T00:00 |
| S-02 | NOAA SWPC — otros 5 feeds | `data/SWPC-fuentes.md` | idem | 2026-11-15 | Verificados por Claude: xrays-1-day y integral-protons-1-day 200; plasma, mag y `/json/alerts.json` **404** → reemplazos `rtsw_wind_1m`, `rtsw_mag_1m` y `products/alerts.json` (200). Detalle al final de `SWPC-fuentes.md` |
| S-03 | NASA OSDR — experimento OS-892 | https://osdr.nasa.gov/bio/repo/data/experiments/OS-892 | confirmar | 2026-11-15 | **VERIFICADO por Claude** vía API oficial `https://osdr.nasa.gov/geode-py/ws/repo/experiments/OS-892` (control `OS-999999` → HTTP 403); respuesta archivada en `data/lecturas/`. Es un *experimento* (accesión OS), no un *study* OSD: por eso `/osdr/data/osd/meta/892` da 0. Sin archivos de datos publicados |
| S-04 | NASA HRP — hazards y risks | https://www.nasa.gov/hrp/hazards/ · https://www.nasa.gov/hrp/risks/ | confirmar | 2026-11-15 | Leídas; descriptivas, sin datos |
| S-05 | NASA HRP — Risk of Spaceflight-Induced Bone Changes | https://www.nasa.gov/reference/risk-of-spaceflight-induced-bone-changes/ | confirmar | 2026-11-15 | **Verificada por Claude.** Cita textual: "on average, bones lose between 1% and 1.5% of their density each month during four-to-six-month missions". **Ancla primaria** de la cifra ósea; la cita 1–2 % de OS-892 es el ancla secundaria |
| S-06 | Bibliografía con identificador (19 citas) | ver `docs/auditoria-de-fuentes.md` §1 | — | 2026-11-15 | Verificadas contra NCBI, Crossref, arXiv y NTRS con `scripts/verificar_fuentes.py` |
| S-07 | **LifeSnaps** — 4 meses, 71 participantes, Fitbit (sueño, pulso, actividad) + autorreportes (ánimo). **No son astronautas** | DOI https://doi.org/10.1038/s41597-022-01764-x · datos: https://zenodo.org/records/7229547 (`rais_anonymized.zip`, 615 037 493 bytes) | CC-BY 4.0 (Crossref y Zenodo) | 2026-11-15 | Fuente verificada por metadatos (Crossref, Zenodo; md5 oficial `726afe263ab4b900a721eac19b2ca13a`). Archivo local en `data/externos/lifesnaps/` (fuera de git): **md5 `726afe263ab4b900a721eac19b2ca13a` COINCIDE con el oficial**; SHA-256 `04e102621d2a998bf31d25c6bdd0ab4cce4d8febc4067d49862aa82e30b418bc`. Contenido leído: `daily_fitbit_sema_df_unprocessed.csv` = 7 410 filas, 71 participantes, 2021-04-08 → 2022-01-22, 63 columnas (sueño, bpm, resting_hr, rmssd, nightly_temperature, spo2, estrés, minutos de actividad, calorías, estados de ánimo). Uso previsto: validar línea base personal + CUSUM sobre datos reales (M2.7/M2.8) |
| S-08 | NASA ICES — Ewert & Stromgren 2019 y perfil metabólico 2021 | https://ntrs.nasa.gov/citations/20190027563 · https://ntrs.nasa.gov/citations/20205010692 | dominio público NASA — confirmar | 2026-11-15 | **PDF leídos por Claude**; cifras y citas en `docs/parametros-publicos.md` |
| S-09 | GFZ Potsdam — índice Kp histórico (desde 1932, 3 h) | https://kp.gfz.de/app/files/Kp_ap_since_1932.txt · cita: Matzka et al. 2021, https://doi.org/10.1029/2020SW002641 (DOI verificado en Crossref) | **CC BY 4.0** (cabecera del propio archivo) | 2026-11-15 | Archivo leído (16,6 MB, hasta 2026-11-14). Uso previsto: cruzar con LifeSnaps (MP-6). Atribución obligatoria |

Fuentes por buscar (datos con archivos reales para el motor y las tarjetas): se añaden aquí **cuando se encuentren**, con licencia, fecha de acceso y hash del archivo.

## 3 · Registro de lo simulado o inventado

| ID | Qué es | Por qué existe | Dónde | Etiqueta |
|---|---|---|---|---|
| X-01 | Instancias **estructurales** de test: registros válidos construidos para ejercitar cada schema (`tests/test_contratos.py`) y casos negativos a propósito inválidos (sin banner, sin fuente, sin semilla, sin `regla_exacta`…) | Los tests de validación y de rechazo exigidos por TASKS.md M0.3/M0.4 necesitan entradas; **no son datos de salud**, no se persisten ni se muestran. Lo único real en ellas es la fuente OS-892 de DC-12 | `tests/` | Nombre de test `*_rechaza_*`; no se persisten ni se muestran |
| X-02 | Banco de Falsaciones IN-4: universo simulado, inyección de anomalías, modo adversario | Es el método de falsación del diseño (DOC-01/DOC-02): detectar anomalías conocidas exige sembrarlas | `src/motor`, `scripts/` | Banner `UNIVERSO SIMULADO — DÍA N` + semilla pública en toda salida |
| X-03 | FB-001/FB-002: tripulación sintética de las falsaciones ya ejecutadas | Falsaciones preregistradas del diseño (DOC-02 Ap. B), con semillas 20261113/14/15 | `scripts/` | Banner SIMULADO; los resultados se citan como "en silicio", nunca como datos reales |
| X-04 | LA TORMENTA: escenarios de perturbación | Motor de escenarios del diseño (DOC-03) | `src/superficies` | Banner `UNIVERSO SIMULADO — DÍA N`; el modo en vivo usa solo SWPC real |
| X-05 | Fixtures del Contrapeso (`tests/test_contrapeso.py`): lazo de O₂ de una tripulación SIMULADA | Probar el cierre de conservación exige flujos conocidos; se parametrizan con cifras **leídas** de NASA (`parametros-publicos.md` P-02) y supuestos declarados (tripulación de 4; σ por persona = semirrango de dos protocolos publicados; σ de suministro y almacén) | `tests/`, `src/motor/contrapeso.py` | Todas las corrientes con banner SIMULADO; resultados «en silicio», nunca como datos de salud ni de hábitat reales |

> Si el código necesita algo simulado o inventado que no esté aquí: **detenerse, añadir la fila y avisar al humano** antes de escribirlo.
