# ALMA · PLAN DE ENTREGA (traspaso para el equipo)

> Escrito el 2026-11-15 por Claude para que cualquiera de los 3 devs pueda continuar sin la sesión original. **Antes de citar un número, abre su acta/nota** (regla de oro, CLAUDE.md §0). Estado técnico al escribir: 464 tests en verde, e2e 33/33, 29 actas selladas (24 ejecutadas), 16 tarjetas DC-12.

## 0 · Cómo levantar todo (5 min)

```
cp .env.example .env            # poner usuario/clave de Postgres local (NUNCA subir .env)
uv sync && uv run pytest -q     # debe dar 464 verdes
cd backend && set -a; . ../.env; set +a; uv run python manage.py runserver 8000     # API
cd web && pnpm install && pnpm build && pnpm start                                  # http://localhost:3000
```
Detalles y ruta de 4 minutos: `docs/submit/ruta-de-demostracion.md`. Datos externos grandes están en `data/externos/` (gitignored): se re-descargan con los scripts de `scripts/` (fuentes S-01…S-30 en `docs/politica-de-datos.md`).

> **De dónde sale cada dato, API y cita: [`FUENTES.md`](FUENTES.md)** (obligatorio consultarlo; no se inventan fuentes).

## 1 · Estrategia (mi recomendación): empezar por lo mejor, mostrar lo mejor

Sí: **abre con lo más fuerte y no con la arquitectura.** El jurado decide en los primeros 20 s. El mensaje único que une todo:

> **«ALMA es un monitor que sabe y dice cuándo NO puede ver.»** Cada alarma lleva recibo; cada experimento se selló con hash antes de correr; los fracasos se publican.

### Ranking de lo mejor (en este orden en el video Y en el informe)

| # | Qué | Por qué gana | Evidencia | Honestidad obligatoria |
|---|---|---|---|---|
| 1 | **El Contrapeso / La Fuga**: el detector contra el manifiesto no ve nada (0,53σ), el detector contra la ley de conservación ve 0,30 kg faltantes | Es la demo «matadora» y se entiende en 10 s | `/kill`, FB-003R/FB-005, `src/motor/contrapeso.py` | Es **universo SIMULADO** (se ve el banner); no hay datos de cabina tripulada |
| 2 | **Astronautas REALES: el piso de detección** (Inspiration4, n = 4): con 3 extracciones de base, ninguna banda personal ve una caída mediana de linfocitos del −24 %; el piso es ±70 % | Es el único dato de astronautas reales y revela una idea propia: *antes de alarmar, declara qué puedes ver* | FB-024, FB-025, `NOTA-FB-024/025.md`, sala The Frontier | n = 4; exploratorio; la fila que no cierra (1/28) es probable error de captura |
| 3 | **Recibo + preregistro + nulos publicados** | Diferenciador científico: 29 actas selladas con hash ANTES de correr, y los fallos a la vista | La Bóveda, `docs/actas/`, `tests/test_orden_de_actas.py` | Muestra errores propios (FB-002 «10/10» → 8/10; estrés con polaridad mal) |
| 4 | **LA FUNDICIÓN genera hipótesis y cierra el bucle** (mecanismo → candidato → acta redactada por el generador → hash → 1 ejecución → tarjeta) | «Ideas baratas, sobrevivirlas es el producto». Resultado limpio: sueño corto baja la HRV 0,21 sd (p = 0,0001, placebo nulo) | FB-026…FB-028, `src/fabrica/generador.py` | LifeSnaps/Zenodo no son astronautas; la réplica del pulso se encogió a 0,11 lpm |
| 5 | **Entorno REAL en vivo** (ISS, protones GOES, rayos X, Kp) + ECG real MIT-BIH (99,96 % / 100 %) | Da vida y prueba que no es solo simulación | The Frontier/The Storm, C-01, C-14 | Posición ISS derivada de elementos orbitales; un solo registro ECG |

**Lo que NO hay que decir nunca:** «10/10» (no replicó); «detecta enfermedad»; «valida con astronautas» (n = 4, exploratorio); que ALMA es un LLM (es un narrador determinista). Lista completa: `docs/informe/INVENTARIO-IEEE.md` §9.

## 2 · Qué documentos armar (y quién)

| Entregable | Formato | Estado | Fuente | Responsable sugerido |
|---|---|---|---|---|
| **Video 30–60 s** (obligatorio del formulario) | mp4, inglés | guion listo | `docs/submit/video-guion.md` | Dev C (grabación + voz ALMA) |
| **Video largo 2–3 min** (opcional, para la ronda del jurado) | mp4, inglés | guion listo | mismo archivo, §«Versión extendida» | Dev C |
| **Informe IEEE (LaTeX, inglés)** | PDF ≈ 5–6 pp. | **PRIMER BORRADOR COMPLETO** en `docs/informe/ieee/main.tex` (compilar en Overleaf; ver su README) | `docs/informe/ieee/main.tex` + `INVENTARIO-IEEE.md` + `docs/preprint/manuscript.md` (borrador 1 220 palabras, ya en inglés) | Dev A (resultados) + Dev B (sistema) |
| **Formulario Space Apps** | texto | casi listo | `docs/submit/formulario.md` (faltan URLs repo/PDF) | cualquiera |
| **Demo en vivo (4 min)** | — | lista | `docs/submit/ruta-de-demostracion.md` | quien presente |

### Por qué IEEE en LaTeX y cómo ordenarlo (empezar por lo mejor)
Sí, un informe IEEE conference (`IEEEtran`) es el formato correcto para «nivel científico». Orden recomendado (**invierte el orden clásico: resultados fuertes arriba**):

1. **Abstract** (≤ 200 palabras): el mensaje único + 3 cifras (conservación atrapa la fuga que el manifiesto no ve; piso de detección ±70 % vs −24 % en astronautas reales; 29 actas selladas, fallos publicados).
2. **I. Introducción**: reto, ausencia de datos abiertos por persona, la pregunta («¿cómo monitorear con honestidad cuando casi no hay datos?»).
3. **II. Resultados principales (adelantados)** = ranking 1→4 de arriba, cada uno con su figura y su límite.
4. **III. Sistema** (capas, contratos DC, recibo, banner) · **IV. Métodos** (2σ/CUSUM, conservación, e-proceso, preregistro con hash, MDE).
5. **V. Resultados negativos y errores propios** (`INVENTARIO` §6; son parte del método).
6. **VI. Discusión/límites** · **VII. Reproducibilidad** (semillas públicas 20261113/14/15/11/12, hashes, comandos) · **VIII. Ética** · **IX. Trabajo futuro** · **Referencias** (solo verificadas: `docs/revision-literatura.md`).

Reglas al redactar: cada cifra se copia de su `NOTA-FB-xxx.md` (no de memoria); cada afirmación lleva su ID C-xx del inventario con su límite al lado; figuras desde `docs/screenshots/` y `/api/*`; novedad acotada (el método e-proceso ya existe: Shin–Ramdas–Rinaldo, arXiv:2203.03532; lo propio es medir el hueco en wearables reales).

## 3 · Video: dónde grabar y qué cuidar
- Grabar con el **build de producción** (`pnpm build && pnpm start`), `?awake=1` para saltar la puerta de despertar, subtítulos visibles, 1366×768.
- Banner REAL/SIMULADO visible en ≥ 3 planos. Voz: ALMA (`scripts/voz_alma.py`; variable `ALMA_VOICE`).
- Guion exacto con tiempos: `docs/submit/video-guion.md`.

## 4 · Lista de trabajo para el equipo (en orden)

**Ya hecho por Claude (no repetir):** motor, libro, Contrapeso, 8+1 salas, Fundición con generador, 29 actas, 16 tarjetas, voz, e2e, docs de submit, inventario IEEE, borrador de manuscrito, esqueleto LaTeX.

**Pendiente humano:**
1. Dev C: grabar video corto y (si hay tiempo) el largo; subir y pegar URL en `docs/submit/formulario.md`.
2. Dev A/B: redactar el informe IEEE sobre `docs/informe/ieee/main.tex` (compilar con `pdflatex`/Overleaf; ver README de esa carpeta). Verificar cada referencia antes de citarla.
3. Cualquiera: decidir licencia (`LICENSE`), URL del repo y del PDF, **confirmar la fecha límite real** (CLAUDE.md dice jurado 14-nov-2026).
4. Ensayo de la demo de 4 min con `ruta-de-demostracion.md` (preguntas esperadas incluidas).
5. Revisión móvil (390×844) de las 7 salas pendientes (home y Fundición ya revisadas).
6. Opcional: replicar FB-026 H2 (sueño → HRV) en otra cohorte con rmssd (hoy no hay: bloqueado); M6.5 y M2.22 siguen bloqueados por datos.

## 5 · Reglas del repo que no se rompen (resumen de CLAUDE.md)
Acta con hash SHA-256 **commiteada antes** de correr (`tests/test_orden_de_actas.py` lo exige); ningún dato falso sin banner SIMULADO y fila X-xx; `.env` y `data/externos/` nunca al repo; tests verdes antes de cada commit; cambiar un contrato DC-xx = cambio de versión de DOC-01 (pide permiso).
