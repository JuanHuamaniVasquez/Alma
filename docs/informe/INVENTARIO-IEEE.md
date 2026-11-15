# Inventario para el informe (formato IEEE) — QUÉ INFORMACIÓN IRÁ, con su evidencia

> **Esto NO es el informe.** Es el inventario trazable de lo que hay para contar: cada afirmación apunta a su acta, nota, test o commit. El informe (o el manuscrito IEEE) se redactará después, **solo con lo que figura aquí**; si algo no está aquí, no se escribe.
> Fecha de este inventario: 2026-11-15 · HEAD en el momento de escribirlo: ver `git log -1`. Idioma: este inventario en español; el informe final se decide después (el frontend y los entregables del submit van en inglés).
> Regla de honestidad: nada se afirma por encima de su evidencia; los resultados nulos y los errores propios están incluidos (§6).

## 1 · Mapa de secciones IEEE → qué material hay

| Sección típica | Qué se puede contar | Dónde está la evidencia |
|---|---|---|
| **Abstract** (150–250 palabras) | Un monitor de salud cuerpo+máquina donde cada alarma lleva recibo (regla exacta, semilla, hash de preregistro); un laboratorio que preregistra y publica nulos; 4 ideas de frontera medidas con datos reales y simulados | §2 y §3 |
| **I. Introducción** | Reto NASA Space Apps 2026 «Health Monitoring Software for Astronauts»; la ausencia de datos abiertos de astronautas por persona; la pregunta: ¿cómo monitorear con honestidad cuando casi no hay datos reales? | `docs/politica-de-datos.md`, `docs/recursos-nasa.md`, `docs/radar-nasa.md` |
| **II. Trabajo relacionado** | Revisión de literatura (PubMed, NTRS, Crossref, búsqueda web); qué es nuevo y qué NO (el método e-proceso ya existe) | `docs/revision-literatura.md` (incl. §M6.0), `docs/evaluacion-paper.md` |
| **III. Sistema** | Arquitectura en capas (ingesta → libro → motor → fábrica → superficies), contratos DC-01…DC-14, tres mandamientos, recibo de alarma/verde, banner REAL/SIMULADO, 8 salas + ALMA determinista | `docs/DOC-01…`, `README.md`, `src/`, `backend/`, `web/` |
| **IV. Métodos** | Línea base personal, 2σ, CUSUM (h calibrado por Monte Carlo), blanqueado AR(1), canal de varianza, conservación (El Contrapeso), potencia/MDE declarados (DC-14), preregistro con hash (GO-2), e-proceso (FB-021), consistencia (FB-022), NILM (FB-023), presupuesto ε | `src/motor/`, `src/gobernanza/preregistro.py`, `docs/actas/*.md` |
| **V. Experimentos y resultados** | Tabla de experimentos (§3, generada de los registros sellados) + figuras (§5) | `docs/actas/RESULTADOS.jsonl`, `docs/actas/NOTA-*.md` |
| **VI. Discusión y límites** | §6 (nulos y errores propios) y §9 (lo que NO se afirma) | idem |
| **VII. Reproducibilidad** | Semillas públicas, hashes, comandos, versiones (§7) | §7 |
| **VIII. Ética** | Personas reales = civiles anónimos; tripulación ficticia; privacidad (ε); sin datos médicos de astronautas | `docs/politica-de-datos.md` §12 |
| **IX. Trabajo futuro** | §10 | `TASKS.md`, `docs/propuestas.md` |
| **Referencias** | §8 (solo las verificadas) | §8 |

## 2 · Registro de afirmaciones (cada una con su evidencia y su estado)

| ID | Afirmación que el informe podrá hacer | Estado | Evidencia | Datos | Límite que debe acompañarla |
|---|---|---|---|---|---|
| C-01 | Un detector de onda R propio recupera 2 272 de 2 273 latidos anotados por humanos (sensibilidad 99,96 %, VPP 100 %) en 30 min de ECG real | medida | `tests/test_ecg_vitales.py`, `src/motor/ecg_vitales.py`, S-20 | REAL (MIT-BIH reg. 100) | **un solo registro**, paciente ambulatorio anonimizado, no astronauta; registro limpio |
| C-02 | La garantía teórica de falsa alarma de un e-proceso falla 5× en wearables reales (5,06 % frente a 1 % pedido con s = 1); calibrada s = 1,5 da 0 % pero la potencia a 2σ baja de 99 % a 71 % | medida (dentro de muestra) | acta FB-021 `5072d872…`, `docs/actas/NOTA-FB-021.md` | REAL (LifeSnaps) + escalón SIMULADO | validación fuera de muestra con **5 ventanas: no concluyente**; el método no es nuestro |
| C-03 | Temperatura nocturna, respiración y rmssd se acoplan con el pulso en reposo dentro de la persona, fuera de muestra (ρ = +0,24; +0,27; −0,53) | sostenida | acta FB-022 `1a8d7c6e…`, `NOTA-FB-022.md` | REAL (LifeSnaps) | modesto; sin conjunto externo; correlación ≠ causalidad |
| C-04 | Un clasificador «sensor roto / cuerpo cambiado» basado en ese acoplamiento NO funciona (66 %; 44 % de bloques reales sin inyección marcados) | **refutada** | FB-022 | REAL + eventos SIMULADOS | rmssd y pulso salen del mismo sensor óptico |
| C-05 | Atribuir a un tripulante un exceso de CO₂ de la cabina solo es identificable con turnos escalonados; con 4 h de desfase y 20 % de exceso acierta 71 % (azar 20 %); H1 de 80 % refutada | medida (simulación) | acta FB-023 `09bb108c…`, `NOTA-FB-023.md`, `tests/test_nilm_cabina.py` | **SIMULADO (X-17)** | no hay datos de cabina tripulada; es una curva de diseño |
| C-06 | Con 5 personas, un agregado exacto + una resta reidentifica a un tripulante; con ruido de Laplace ε = 0,5 por consulta el atacante falla > 12 % | probada en test | `tests/test_privacidad.py`, `src/superficies/privacidad.py` | estructural | ε = 2,0 es ilustrativo, no política NASA; la política de datos NASA/LSAH **no está verificada** |
| C-07 | El canal de varianza (MP-15) tiene FPR real 9,0 % en LifeSnaps: refutado; la versión robusta (MAD con crítico empírico) quedó no concluyente por 5 ventanas en validación | refutada / no concluyente | FB-020, FB-020-v2, `NOTA-FB-020*.md` | REAL | M2.22 bloqueada por datos |
| C-08 | «FB-002: 10/10 detecciones, preaviso mediano 21 días» **no se replicó**: la réplica propia da 8/10 (umbral ≈ 200 min) | no replicada | FB-015-v2, `tests/test_banco_ocio_v2.py`, `docs/decisiones.md` D-35 | SIMULADO (réplica) | el script original no existe en este equipo |
| C-09 | Cada alarma/verde lleva recibo con regla exacta ejecutable, semilla y hash de preregistro; un verde declara potencia y MDE (en σ y en unidades físicas) o es `sin_datos_suficientes` | implementada y testeada | DC-05, DC-14, `tests/test_contratos.py`, `tests/test_checklist_honestidad.py` | — | los verdes REALES cubren solo `fc` y `sueño` (LifeSnaps) |
| C-10 | Los hechos de vuelo mostrados (sueño 6,09 h en la ISS; pulso sin cambio en vuelo; hueso 1–1,5 %/mes; retardo 0–22 min) están **copiados de sus fuentes** con cita | verificado | S-21, S-22, S-05, S-23; `data/referencias/*.json` | REAL (literatura) | promedios de grupo publicados, no predicciones individuales |
| C-11 | Las pantallas dicen en cada sala qué es real y qué es simulado; hay un test que impide afirmar lo no demostrado | implementada | `web/src/components/Origins.tsx`, `tests/test_checklist_honestidad.py` | — | la lista se mantiene a mano |
| C-13 | Reconciliar el hemograma de astronautas reales consigo mismo (absoluto = % × leucocitos) encuentra 1 fila de 28 que no cierra (un error de captura probable en datos públicos de NASA); con 3 extracciones de base la banda personal es tan ancha que ninguna persona sale de ella pese a una caída mediana de linfocitos de −24 % en R+1 | medida (mixta) | acta FB-024 `41f0413d…`, `NOTA-FB-024.md`, `tests/test_hematologia_i4.py` | **REAL, astronautas (n = 4, Inspiration4, OSD-569)** | civiles, sin muestras en vuelo, sin causalidad; «sin alarma» ≠ «sin efecto» |
| C-14 | La nave muestra el entorno REAL de la tripulación en vivo (órbita de la ISS, protones GOES, rayos X) y declara `disponible:false` si una fuente cae | implementada y testeada con respuestas reales guardadas | `src/ingesta/entorno.py`, `tests/fixtures/entorno/`, S-26, S-27 | REAL (NASA/NOAA) | la posición de la ISS es derivada de elementos orbitales, no telemetría |
| C-12 | FB-014 (sueño/HRV × Kp) REFUTADA; FB-016 A (sueño corto → cansancio) SOSTENIDA | medida | `NOTA-FB-014.md`, `NOTA-FB-016.md` | REAL | LifeSnaps no son astronautas |

(Las cifras de C-07/C-08/C-12 se citan de las notas; antes de usarlas en el informe, **releer la nota** — regla de oro del proyecto.)

## 3 · Experimentos sellados (tabla generada de los registros; no se edita a mano)

<!-- TABLA-EXPERIMENTOS:INICIO -->
| Acta | Hash (8) | Registrada (UTC) | Ejecutada | Datos | Resultado (EN) | Nota interna |
|---|---|---|---|---|---|---|
| FB-005 | `58d0ff17` | 2026-11-15T05:22:16Z | no ejecutada | simulated | not_run | re-registro 2026-11-15: el hash publicado en DOC-02 Ap. B no es reproducible desde el texto del documento |
| FB-006 | `027ae6f6` | 2026-11-15T05:22:16Z | no ejecutada | simulated | not_run | re-registro 2026-11-15: el hash publicado en DOC-02 Ap. B no es reproducible desde el texto del documento |
| FB-007 | `57937ffc` | 2026-11-15T05:22:16Z | no ejecutada | simulated | not_run | re-registro 2026-11-15: el hash publicado en DOC-02 Ap. B no es reproducible desde el texto del documento |
| FB-008 | `88f483e1` | 2026-11-15T05:22:16Z | no ejecutada | simulated | not_run | re-registro 2026-11-15: el hash publicado en DOC-02 Ap. B no es reproducible desde el texto del documento |
| FB-005-D1 | `e0d28c09` | 2026-11-15T05:52:17Z | 2026-11-15T05:52:43Z | simulated | sustained | demo kill de M1.4; no sustituye a FB-005 (400 corridas, M2.6); registrada antes de escribir el runner |
| FB-009 | `1bc9c11f` | 2026-11-15T06:31:37Z | 2026-11-15T06:32:59Z | real+simulated | mixed | M2.8 evaluación sobre LifeSnaps; registrada antes de escribir el runner ni ejecutar el detector sobre estos da |
| FB-010 | `a30a73d5` | 2026-11-15T06:39:50Z | 2026-11-15T06:40:08Z | real+simulated | inconclusive | MP-11 prewhitening AR(1) con validación cruzada por personas; registrada antes de ejecutar el detector blanque |
| FB-011 | `faf5614b` | 2026-11-15T06:52:29Z | 2026-11-15T06:53:18Z | real+simulated | mixed | M2.10 / MP-5: contraste del recibo de verde en datos reales; control negativo y predicción de fallo en pulso i |
| FB-012 | `a854fa57` | 2026-11-15T07:10:19Z | ejecutada | real | mixed | M2.17: variabilidad real del agua (Utah, S-12); registrada antes de calcular estadísticas |
| FB-013 | `49cc322d` | 2026-11-15T07:13:27Z | 2026-11-15T07:13:44Z | real+simulated | mixed | M2.15/MP-12: validación independiente de FB-009/FB-010 en Zenodo 8018238 (sanos); φ y h congelados; registrada |
| FB-014 | `12f1844f` | 2026-11-15T07:17:27Z | 2026-11-15T07:17:48Z | real | refuted | M4.6/MP-6: tarjeta DC-12 exploratoria sueño/HRV × Kp (LifeSnaps × GFZ); registrada antes de ejecutar |
| FB-015 | `71128f4b` | 2026-11-15T07:27:46Z | 2026-11-15T07:28:15Z | simulated | not_replicated | M2.16/M2.3/MP-13: réplica independiente de FB-002 con predicción de la Tabla 9; modelo mío, SIMULADO; registra |
| FB-015-v2 | `78c66d73` | 2026-11-15T07:29:34Z | 2026-11-15T07:29:47Z | simulated | partial | v2 tras v1 NO REPLICADA (mala especificación); 2 parámetros, 7 celdas predichas; no ciega; sin v3 |
| FB-016 | `ec4a82e0` | 2026-11-15T07:32:20Z | 2026-11-15T07:32:20Z | real | mixed | M4.2: dos tarjetas DC-12 cuerpo↔cuerpo (sueño→cansancio control positivo; tensión→HRV) con LifeSnaps real; reg |
| FB-017 | `c45c3a4e` | 2026-11-15T07:33:41Z | no ejecutada | none | no_data | M4.7 tarjeta carga ósea↔UPA (sin_datos) + predicción del Faro OS-892; acta de especificación |
| FB-003R | `f7172765` | 2026-11-15T07:36:43Z | 2026-11-15T07:36:55Z | simulated | mixed | M2.4+M2.13: triangulación de 3 testigos y cuarta causa modelo; SIMULADO; registrada antes de ejecutar |
| FB-004R | `de2d5df7` | 2026-11-15T07:41:40Z | 2026-11-15T07:41:40Z | real+simulated | sustained | M2.5: integrador lento del agua con normalización MP-3 y dilución real (Utah); registrada antes de ejecutar |
| FB-018 | `c6127543` | 2026-11-15T07:44:00Z | 2026-11-15T07:44:00Z | simulated | mixed | M4.4: Adversario (perfiles que evaden al CUSUM) y contramedida de varianza; SIMULADO; registrada antes de ejec |
| FB-019 | `5a38124d` | 2026-11-15T07:45:54Z | 2026-11-15T07:45:54Z | simulated | sustained | M2.18: techo de información de la prueba de varianza (F14, F28, oráculo, |z|-CUSUM) frente al zigzag; SIMULADO |
| FB-020 | `c3bca4e3` | 2026-11-15T10:42:03Z | 2026-11-15T10:42:38Z | real+simulated | refuted | M2.20/MP-15: canal de varianza en LifeSnaps real (FPR, potencia con zigzag simulado, CUSUM de media ciego); re |
| FB-020-v2 | `bed7bc32` | 2026-11-15T10:56:25Z | 2026-11-15T10:57:30Z | real+simulated | inconclusive | M2.21: canal de varianza robusto, ajuste en LifeSnaps y validacion fuera de muestra en Zenodo 8018238; registr |
| FB-021 | `5072d872` | 2026-11-15T18:43:55Z | 2026-11-15T18:44:16Z | real+simulated | inconclusive | M6.1/MP-16: e-proceso anytime-valid; ajuste LifeSnaps, validación Zenodo 8018238 |
| FB-022 | `1a8d7c6e` | 2026-11-15T18:47:36Z | 2026-11-15T18:48:02Z | real+simulated | mixed | M6.3/MP-18: consistencia física cruzada, LifeSnaps columnas no analizadas antes |
| FB-023 | `09bb108c` | 2026-11-15T19:21:02Z | 2026-11-15T19:21:16Z | simulated | partial | M6.2/MP-17: NILM metabólico de cabina, identificabilidad SIMULADA (X-17) |
| FB-024 | `41f0413d` | 2026-11-15T20:27:32Z | 2026-11-15T20:28:13Z | real | mixed | M7.2: hematología REAL de astronautas (Inspiration4, OSD-569): conciliación interna, banda personal y retorno |
<!-- TABLA-EXPERIMENTOS:FIN -->

Cada acta se preregistró con SHA-256 **antes** de correr; el hash de cada una se puede recalcular (`docs/actas/INDEX.jsonl`, `src/gobernanza/preregistro.py`). Una sola ejecución por acta.

## 4 · Fuentes de datos y su estado

| Fuente | Qué es | Estado de verificación | Uso en el informe |
|---|---|---|---|
| LifeSnaps (Zenodo 7229547, S-07) | 71 civiles, Fitbit, 4 meses | md5 oficial coincide; sha256 en los runners | datos REALES de pulso, sueño, rmssd, temperatura, respiración, SpO₂ (no astronautas) |
| Zenodo 8018238 (S-13) | cohorte independiente | sha256 en los runners | validación fuera de muestra (solo 5 ventanas largas) |
| GFZ Kp (S-09), NOAA SWPC (S-xx) | clima espacial | verificado | La Tormenta; FB-014 |
| Utah agua (S-12) | consumo real de agua | verificado | FB-012 |
| NASA OSDR OSD-569 CBC (S-24) y catálogo OSDR (S-25) | hemograma real de 4 astronautas; 52 estudios humanos | sha256 del CSV; instantánea fechada | C-13, atlas de la sala Frontier |
| ISS en vivo y GOES (S-26, S-27) | entorno real | fixtures reales | C-14 |
| MIT-BIH reg. 100 (S-20) | ECG real | sha256 + licencia ODC-By leída | monitor de constantes (C-01) |
| Ewert & Stromgren (P-01…P-09) | balance de masa del astronauta de referencia | citas textuales en `docs/parametros-publicos.md` | hábitat simulado y NILM |
| Barger 2014; Hughson 2012; NASA HRP hueso; McBrayer et al. (S-21, S-22, S-05, S-23) | hechos de vuelo y retardo | cifras copiadas de PubMed/PDF | «Expected in flight» y «Earth link» |
| **SIMULADO** (X-01…X-17) | hábitat ficticio, tripulación ficticia, escenarios G1–G5, inyecciones | cada uno con fila en `docs/politica-de-datos.md` §3 | siempre con banner SIMULADO |

**No existen** (verificado en la búsqueda): telemetría abierta continua de la ISS por persona; datos abiertos de cabina tripulada por persona. OSDR aloja datos de una misión comercial (Inspiration4) pero acceso y contenido no se verificaron a fondo → no usado.

## 5 · Figuras y tablas candidatas (ya existen o se generan de los registros)

| Candidata | Origen | Nota |
|---|---|---|
| Arquitectura en capas + flujo unidireccional | `README.md`, DOC-01 | redibujar |
| Capturas de las 8 salas, monitor ECG, capa Anatomy, Outside con casco | `docs/screenshots/` (+ `pnpm screenshots`); `web/e2e/*.mjs` generan capturas | las de M6 se hacen con `e2e/zoom.mjs`, `privacy.mjs`, `monitor.mjs` |
| Curva del e-proceso (simulada) + tabla s vs FPR vs potencia | `/api/eproceso/`, FB-021 | tabla real, curva demostrativa SIMULADA |
| Curva atribución NILM (exactitud vs desfase, 3 excesos, línea de azar) | `/api/nilm/`, FB-023 | SIMULADO |
| Presupuesto ε y ataque por diferencias | `tests/test_privacidad.py` | |
| Matriz de acoplamientos (3 pares) y clasificador | FB-022 | |
| ECG con ondas R detectadas + tendencia de pulso con banda ±2σ | `/api/ecg/` | REAL |
| Tabla de «lo prometido vs lo observado» del libro de aire/agua | `/api/libro/`, `/api/residuo/` | SIMULADO |

## 6 · Resultados negativos y errores propios (van en el informe: son parte del método)

1. **Canal de varianza refutado** (FPR real 9,0 %) → FB-020-v2 no concluyente (n = 5).
2. **FB-002 «10/10» no replicó** (8/10).
3. **FB-010**: control de mi acta que no podía fallar (defecto de diseño, publicado).
4. **FB-011**: mi predicción H3 fue refutada (publicada).
5. **FB-021**: la garantía teórica 5× optimista; s calibrado cuesta potencia; H3 (retardo ≤ 7 d) refutada (8 d).
6. **FB-022**: mis predicciones H1/H3 eran erróneas (los acoplamientos sí existían); el clasificador, refutado.
7. **FB-023**: H1 (≥ 80 %) y H4 refutadas; además H1/H2 eran casi conocidas antes de registrar (declarado).
8. **FB-014**: tarjeta sueño/HRV × Kp refutada.
9. **Novedad acotada**: el método e-proceso ya existe; lo propio es la aplicación y la medición del hueco.
10. Bloqueados por datos: M2.22 (≥ 300 ventanas independientes), M6.5 (respiración/SpO₂/HRV sin σ de sensor verificada), tarjeta hueso↔UPA sin datos.

## 7 · Reproducibilidad (lo que un revisor podrá repetir)

- Semillas públicas: **20261113 · 20261114 · 20261115 · 20261111 · 20261112**.
- Stack: Python 3.12 (`uv`) + Django 5.2/DRF + PostgreSQL; Next.js 15 + TypeScript; Blender 5.2 + MPFB para los modelos 3D (`scripts/blender/`).
- Pruebas: `uv run pytest` (416 en verde al cerrar M6.11) y `pnpm e2e` (28 comprobaciones de navegador).
- Comandos de cada experimento: `scripts/fbNNN_*.py` (se niegan a correr sin acta intacta o por segunda vez).
- Datos externos: descargas con sha256 en los runners (`data/externos/`, fuera de git; fuentes en `docs/politica-de-datos.md`).
- Voz de ALMA: Kokoro-82M local (`scripts/voz_alma.py`); el narrador es determinista (plantilla + dato + fuente), no un LLM.

## 8 · Referencias verificadas (Crossref/PubMed/lectura directa) y por verificar

**Verificadas:** Ramdas, Grünwald, Vovk, Shafer 2023, *Stat. Sci.*, doi:10.1214/23-STS894 · Waudby-Smith et al. 2024, *Ann. Stat.*, doi:10.1214/24-AOS2408 · Moody & Mark 2001, *IEEE EMB Mag.*, doi:10.1109/51.932724 · Goldberger et al. 2000, *Circulation*, doi:10.1161/01.CIR.101.23.e215 · Barger et al. 2014, *Lancet Neurol*, doi:10.1016/S1474-4422(14)70122-X · Hughson et al. 2012, *J Appl Physiol*, doi:10.1152/japplphysiol.01196.2011 · McBrayer, Chai, Judd, NTRS 20220013418 · Yfantidou et al. 2022 (LifeSnaps), doi:10.1038/s41597-022-01764-x · Jones 2019, NTRS 20190027319 · Ewert & Stromgren 2019, ICES-2019-126 · Altman & Bland 1995, doi:10.1136/bmj.311.7003.485.
**Verificadas en la API de arXiv (título, autores, fecha) el 2026-11-15:** Shin, Ramdas & Rinaldo, *E-detectors: a nonparametric framework for sequential change detection*, arXiv:2203.03532 (2022) — nota: el nombre «Shekhar» que figuraba antes en este inventario era erróneo; los autores son Shin, Ramdas y Rinaldo · Regis & Serra, *Return-to-Baseline Testing via Empirically Calibrated e-processes*, arXiv:2606.01960 (2026) · Batra, Kelly, Parson et al., *NILMTK*, arXiv:1404.3878 (2014). **Pendiente:** son preprints; confirmar si hay versión publicada antes de citar.
**IEEE/Scholar no consultados** (declarado en `docs/revision-literatura.md`).

## 9 · Lo que el informe NO afirma (lista de límites que debe repetir)

No son astronautas (datos reales = civiles; la tripulación y el hábitat son ficticios). No hay validación en cabina tripulada. El ECG es de un solo paciente hospitalario anonimizado. El detector de picos R está medido en un registro limpio. Los hechos de vuelo son promedios de grupo de estudios pequeños. ε = 2,0 y el modelo de producción de CO₂ por hora son supuestos declarados. FB-021 no pasa a recibo DC-05 sin decisión del humano (DOC-01 v0.2.9). La política de datos de NASA/LSAH no está verificada. El anatómico (órganos/huesos) es ilustrativo.

## 10 · Pendientes antes de escribir el informe (los decide el equipo)

- Confirmar la **fecha límite real** de entrega (CLAUDE.md dice 14‑nov‑2026).
- M6.5 (respiración, rmssd, SpO₂ como indicadores) sigue **bloqueado**: la búsqueda en PubMed (2026-11-15) no halló una validación del Fitbit Sense con error de medida utilizable para estas tres señales; sin σ verificada no se emiten (política de datos).
- Consultar IEEE Xplore / Google Scholar (las referencias de §8 ya están verificadas; los preprints de arXiv pueden tener versión publicada).
- Elegir qué resultados van en el cuerpo y cuáles en material suplementario (el repositorio completo).
- Licencia del repositorio y URLs (repo, PDF v0.4) para el formulario.
