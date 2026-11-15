# Checklist final — qué queda para entregar y qué sigue después

> Actualizado 2026-11-15. Casilla marcada = hecho y verificado. Cada pendiente dice **quién** y **cómo**. Orden recomendado: A → B → grabar.

## A · Antes de entregar (te toca a ti)
- [ ] **Confirmar la fecha límite real de entrega.** `CLAUDE.md` dice jurado el 14-nov-2026 y hoy es 15-nov: si ya pasó, preguntar a la organización si el envío sigue abierto.
- [ ] **Subir el código a GitHub.** Crea un repositorio vacío (sin README) y, en la carpeta del proyecto:
  `git remote add origin <URL-del-repo>` · `git push -u origin main` (el `.env` y los datos externos NO se suben: ya están en `.gitignore`).
- [ ] **Elegir licencia** (MIT o Apache-2.0 son las habituales): crea `LICENSE` en la raíz y borra la última línea del `README.md` («Licence … to be set»).
- [ ] **Pegar las URLs** del repositorio, del PDF y del video en `docs/submit/formulario.md` (sección *Links*). El PDF disponible es `docs/ALMA-documento-del-proyecto-v0.3.pdf`: decide si lo subes tal cual o preparas una v0.4.
- [ ] **Probar la demo con sonido** en tu navegador: `scripts/demo.sh` → `localhost:3000` → clic para despertar a ALMA. Si una frase se corta, anota la sala y qué hiciste justo antes.
- [ ] **Elegir la voz** (ahora `af_heart`): `ALMA_VOICE=bf_emma uv run --with kokoro-onnx --with soundfile python scripts/voz_alma.py` (≈ 5 min). Muestras en el scratchpad de la sesión; `ALMA_FX=0` para voz sin eco.
- [ ] **Ensayo sin notas** con `docs/submit/ruta-de-demostracion.md` (4 min + preguntas del jurado).
- [ ] **Grabar el video** (30–60 s) siguiendo `docs/submit/video-guion.md`. Pantalla completa, subtítulos visibles, sello REAL/SIMULATED en al menos 3 planos, nunca decir «10/10».
- [ ] **Leer y corregir** `docs/submit/formulario.md` y `docs/preprint/manuscript.md`. El preprint **no se envía** todavía (falta IEEE/Scholar y revisión humana).
- [ ] **Rellenar el formulario de Space Apps** con `docs/submit/formulario.md` (descripción de 176 palabras ya dentro del rango 150–200).

## B · Verificación técnica justo antes de grabar
- [ ] `scripts/demo.sh` arranca sin errores (migra, siembra, API :8000, vitrina :3000).
- [ ] `uv run pytest -q` en verde (386+ tests).
- [ ] `cd web && pnpm test:unit` (6) y `pnpm e2e` → 25/25 (con los dos servidores arriba; no escribe en la base).
- [ ] `sysmap --root . check` → «nothing worse than the baseline».
- [ ] `git status` limpio; `git ls-files | grep "\.env$"` no devuelve nada.
- [ ] Capturar la base limpia de reportes de ánimo si quieres empezar «sin reportes» (`Autorreporte` vacío) antes del video.

## C · Hecho (ya no hay que acordarse)
- [x] Backend completo hasta donde hay datos reales (M0–M2, M4); 21 actas selladas, 16 ejecutadas una vez.
- [x] Vitrina en inglés: 8 salas, figura clicable con 6 indicadores, ALMA con voz determinista, escenarios de tormenta simulados.
- [x] Captura del ánimo en 3 toques (DC-02, tiempo de respuesta medido).
- [x] Checklist de honestidad ejecutable, README, `scripts/demo.sh`, higiene del repo.
- [x] **Ronda «poco tiempo»:** subtítulos compactos (se desvanecen a los 5 s; interruptor *subtitles on/off*; el sello y la fuente siguen visibles) · **ALMA habla al tocar** un anillo, un marcador del cuerpo o el astronauta · **«Verifícalo tú mismo»** en La Bóveda (recalcula el SHA-256 de cada acta en tu navegador).
- [x] **Tripulación de 5** (versión estilizada): selector, dentro/fuera, estado corporal de un sustituto real y anónimo mostrado solo como estado y rotulado «stand-in».
- [x] **Buscador por voz en La Bóveda**: escribir o hablar; ALMA responde con su voz componiendo clips de un vocabulario cerrado (80 clips: ids, números, veredictos, salas); la búsqueda tolera erratas y sinónimos; sin resultados dice lo más parecido; «open F B zero two zero», «show refuted experiments», «go to the foundry», «verify everything». Pruebas: `pnpm test:unit` (6) y e2e (25, con reconocimiento simulado).
- [x] Arreglos de audio: la voz pedida antes del primer clic se encola; sin reinicios por doble disparo; el recibo ya no se cierra solo.

## D · Siguiente ronda (si hay tiempo; de más a menos impacto ante el jurado)
| # | Idea | Esfuerzo | Nota |
|---|---|---|---|
| 1 | **Intenta engañar a ALMA** (el jurado dibuja una anomalía y ve qué detector la caza; incluye el zigzag que el CUSUM no ve) | medio | Reutiliza el Adversario (FB-018) |
| 2 | ~~Buscador en La Bóveda~~ **HECHO**: texto + voz, filtros, paginación, «nothing like that; the closest are…», abrir un acta o ir a una sala hablando | — | La voz usa el reconocimiento del navegador (Chrome envía el audio a Google). Pendiente 2b: reconocimiento LOCAL (Whisper) para funcionar sin red |
| 3 | **Preguntas habladas/escritas** respondidas solo desde nuestras actas, tarjetas y libro, con fuente (el modelo, si se usa, solo interpreta la pregunta) | alto | Ya existe la base (intérprete `web/src/lib/search.ts`); falta ampliarlo a tarjetas, libro y literatura, y a todas las salas |
| 4 | ~~Tripulación de 5~~ **HECHO (versión estilizada)**: 5 ficticios con indicativo, rol y color; dentro (uniforme + cara) y fuera (Z-2). Falta: realismo (ver D4b) | — | Decidido: 5. El simulador y `sembrar_demo` usan 5; FB-005-D1 conserva sus 4 (acta sellada) |
| 4b | **Mejorar el realismo de los tripulantes**: descargar «Universal Base Characters» de Quaternius (CC0, itch.io: requiere navegador) y yo lo integro con uniforme | medio | Lo descargas tú y lo dejas en `web/public/models/`; yo adapto cara/uniforme/colores |
| 5 | **Repetición de misión** (deslizador de los 14 días con ALMA narrando) | medio | |
| 6 | **Hábitat 3D** (modelo de la ISS de NASA) con los bucles de aire y agua iluminados | alto | Licencia NASA 3D Resources |
| 7 | **Exportar la cápsula en PDF** con enlace al repositorio | bajo | |

## E · Bloqueado por datos o acceso (no depende del código)
- [ ] **M2.22 / GLOBEM:** solicitar acceso (PhysioNet) → con los datos, acta FB-020-v3.
- [ ] **IEEE Xplore y Google Scholar** en la revisión de literatura (no tienen acceso programático abierto).
- [ ] **OSDR OS-892:** sin archivos de datos publicados (Faro F-001).
- [ ] **Presión, glucosa y temperatura:** sin incertidumbre de sensor verificada → siguen vacíos, no se simulan.

## F · Qué decir con honestidad (video y preguntas)
No hay datos de astronautas · el hábitat es simulado y rotulado · el canal de varianza falló con datos reales (9 % de falsas alarmas) y no emite alarmas · nuestra réplica del «10/10» dio 8/10 («documentado, no replicado») · ALMA no es un modelo de lenguaje: cada frase es plantilla + dato + fuente · la novedad que defendemos es el **método de trabajo** (preregistro con hash, resultados negativos publicados, verde con recibo), no un algoritmo nuevo.
