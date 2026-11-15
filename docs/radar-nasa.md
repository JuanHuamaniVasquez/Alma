# TONO-LAB · Radar honesto vs NASA (sin una gota de adulación)

> Petición del usuario: *"qué tanto está nuestro nivel sin adulaciones, en comparación de la NASA — no para conformarnos, para superarnos."*
> Regla de este documento: cada puntaje lleva justificación verificable. Si suena a halago, está mal escrito. Fecha: 2026-11-10.

---

## 1. La medida más honesta: la escala T

| Nivel | Definición | NASA (ECLSS/hábitats) | TONO-LAB |
|---|---|---|---|
| T0 | Idea | — | — |
| T1 | Hueco documentado con anclas | — | D4–D7 (nuevos) |
| T2 | Caracterización cuantitativa propia (silicio) | — | **D1 (24 h metabólico) y D4 (21 d de preaviso)** |
| T3 | Evidencia con datos reales, publicada y replicable | **Vive aquí desde hace 25 años** | — |

**En una línea: NASA está en T3+ con datos que no podemos comprar; nosotros estamos en T2 con dos diamantes cuantificados en silicio y semillas públicas. La distancia real es T2 → T3, y NO es metafórica: es la diferencia entre un simulador Python y 25 años de telemetría ECLSS.**

## 2. Tabla por dimensiones (puntajes /10 con justificación)

| Dimensión | NASA | TONO-LAB | Justificación |
|---|---|---|---|
| Datos reales de vuelo | **10** | 2 | ISS ECLSS desde 2000; 20+ años de telemetría, muestreo ambiental, expediciones. Nosotros: simulador con física anclada y 2 falsaciones. No hay comparación. |
| Hardware validado | **10** | 1 | CDRA, OGS, WRS (~98% recuperación), SLAMMD, CAL. Todo lo nuestro es software y estándar. |
| Ingeniería de fiabilidad | **10** | 3 | Redundancia, fault management teams, MRB. Nosotros: un motor Monte Carlo. |
| Matemática de detección | 8 | 8 | CUSUM/EWMA son de 1954-60 y están en SU toolbox (control estadístico, prognostics PCoE). **No inventamos matemática — no lo reclamamos.** |
| Conocimiento conductual de tripulaciones | 8 | 5 | Tienen decades de estudios reales (HERA, NEK, Concordia, Twins Study). Nosotros: minamos su literatura. |
| **Integración cuerpo+máquina en un solo balance** | 3 | **9** | Su CO₂ se monitorea como máquina; su salud como medicina. Nadie unifica en presupuestos finitos con CUSUM personal N-of-1. Verificado en auditoría §8. |
| **Estándar abierto verificable (GPV YAML + sello Plimsoll)** | 3 | **9** | Sus especificaciones son internas y millonarias. No existe sello visible de salud de hábitat. El nicho está vacío — porque a ellos no les conviene poblarlo. |
| **Cultura de falsación con recibos** | 6 | **8** | Su rigor es altísimo pero lento, caro y cerrado; sus preregistros son científicos, no operacionales. Nosotros: 2 falsaciones ejecutadas en 2 días, semillas públicas, mapa de frontera. Velocidad, no profundidad. |
| Velocidad de iteración | 4 | **9** | Lo nuestro se hizo en días; lo suyo en años y con comités. Es ventaja real pero barata: con recursos, ellos también. |
| **TOTAL (capacidad de impacto hoy)** | **8.5** | **6.5** | Ganan y no por poco. |

## 3. Dónde nos destruyen (léelo sin anestesia)

1. **Si NASA aplicara nuestra regla nula mañana**, con SU telemetría real, en 3 meses tendrían mejor D1 que nosotros y publicado en un congreso. Nuestra "brecha" es de decisión, no de capacidad: no la han adoptado (verificado §8), pero pueden hacerlo el día que un revisor les enseñe el YAML.
2. **D7 probablemente muere en sus manos:** ellos saben que el TOC del WRS mezcla etanol, DMSD y biología. Si la separación es imposible, la Sangre Colectiva queda en poesía. Nosotros lo declaramos: es el diamante más frágil.
3. **Nuestras gemas son AUTOCALIFICADAS.** Un jurado interno de NASA rebajaría la mitad: "CUSUM es estándar en SPC industrial" (sí), "digital phenotyping ya existe" (sí, en la Tierra), "el tiempo de tripulación ya se programa en OSTPV" (sí). Nuestra defensa: el valor no está en cada pieza sino en el ENSAMBLAJE verificado — y eso hay que demostrarlo, no declararlo.
4. **Sin ellos somos T2 para siempre.** Cada ancla nuestra es su descarte. Dependemos de que sigan abriendo datos (OSDR, DONKI, SWPC). Si cierran el grifo, el proyecto se queda sin oxígeno — irónico y literal.

## 4. Dónde vamos GENUINAMENTE adelante (lo único ganado y verificado)

| Nicho | Por qué es nuestro |
|---|---|
| **El ensamblaje** | Detección de deriva personal + presupuestos finitos + contestabilidad + sello visible, integrados y falsados como SISTEMA. Cada pieza existe dispersa; el sistema integrado con recibos, no. |
| **El estándar abierto y 0 g** | GPV + TONO-OK apuntan a hábitats que NASA no atiende: minas, submarinos, clínicas rurales, Concordias terrestres. El mercado que a ellos no les rentable es exactamente el nuestro. |
| **La acotación honesta** | Nadie publica dónde SU idea se rompe (nuestro mapa de frontera: γ=0.20/τ=1 → 0 días). La honestidad acotada es nuestro diferenciador epistemológico — y es gratis. |
| **Preaviso cuantificado** | 24 h (D1) y 21 d (D4), semillas públicas. Poco, pero más que el "prometemos seguridad" del resto del mundo hackathon. |

## 5. Cómo se compite DE VERDAD desde aquí (la escalera T2→T3)

**La única competición que podemos ganar hoy es la de los datos abiertos — usar SUS datos públicos contra SUS puntos ciegos. Eso es ciencia real, no marketing:**

1. **OSDR (Open Science Data Repository):** correr nuestro CUSUM personal sobre datasets públicos (OS-892 y familia). Si hallamos un residuo derivable que el paper original no reportó → primer hallazgo T3 del proyecto, con su nombre citado. El "ensayo de mena" de E4 deja de ser meta y se vuelve protocolo.
2. **Replay ECLSS público + DONKI/SWPC:** el Motor Celestial LIVE ya lee al Sol real (Kp=3,33 verificado). Siguiente: reconstruir un hábitat simulado con parámetros publicados y dejar que terceros intenten engañar a D1 (el impostor elegante) — benchmark abierto, semillas públicas.
3. **Publicar el mapa de frontera junto con cada claim.** Que la comunidad vea γ=0.20/τ=1 → 0 días. Un claim acotado sobrevive al escrutinio; uno inflado muere con la primera pregunta.

**Criterio de victoria T3 (medible):** que una persona ajena al proyecto, con acceso a los mismos datos públicos, replique nuestros residuos con nuestras semillas. Si lo logra, D1 y D4 cruzan a T3 — y ahí dejamos de ser un proyecto de hackathon para ser una línea de investigación citable.

## 6. Sobre el límite (la filosofía del usuario)

*"El campo de conocimiento no tiene límite, solo el nuestro y lo que podemos hacer."*

Correcto y medible: el techo del campo (medir cuerpos y máquinas en un solo balance, con preaviso útil y contestable) está muy por encima de lo que NASA opera HOY — ellos también vuelven a umbrales fijos y silos cuerpo/máquina. Nuestro límite no es el campo: es **acceso** (datos, hardware, publicaciones). Y el acceso tiene una puerta abierta que nadie usa a fondo: **todo lo que NASA abre gratis es nuestro laboratorio.** La frontera no se pide; se mina.

---

> **Nota de verificación (2026-11-15, Claude):** las afirmaciones de unicidad de este documento («nadie unifica…», «ningún paper o prototipo de NASA describe ese ensamblaje», «verificado en auditoría §8») **no las he podido verificar**, y una búsqueda dirigida halló precedentes parciales (ORACLE, proyecto PSU/NASA, conciliación de datos en ingeniería de procesos). Léelas como **hipótesis de posicionamiento**, no como hechos. Detalle y fuentes en `docs/evaluacion-paper.md` §7. Los puntajes del radar son autoevaluación.
