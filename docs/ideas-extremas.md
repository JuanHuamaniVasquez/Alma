# Ideas extremas — divergencia creativa (ESPECULATIVAS)

> **Estatus de todo este documento: ESPECULATIVO.** Son ideas, no hechos ni compromisos. **No entran a la cola ni al código** (CLAUDE.md §14: alcance congelado hasta M2.8); solo las dos marcadas ★ suben a `docs/propuestas.md` (MP-5, MP-6). Ninguna cita está inventada: las que llevan enlace las verifiqué; las que no, lo dicen.
> Cada idea trae su **primera prueba barata y falsable**. Si no se puede falsar con datos reales o con simulación etiquetada, no vale.

## Las que ya tienen un primer dato real

### I-01 ★ **Verde con potencia** — cada «todo bien» publica lo que habría podido ver
*La idea:* hoy «el verde sin recibo no aparece». Extremo: un verde debe decir **«no detecté nada; habría detectado un cambio ≥ X con potencia ≥ 90 %»** (efecto mínimo detectable, MDE, calculado desde `incertidumbre_del_manifiesto`, el CUSUM calibrado y la ventana). Un «no veo nada» sin MDE es una ausencia de evidencia disfrazada de evidencia de ausencia.
*Por qué es fuerte:* convierte la honestidad en un campo del contrato; generaliza el «atlas de ceguera» (I-06).
*Primera prueba:* sobre LifeSnaps (real) inyectar desplazamientos etiquetados SIMULADO de tamaño = MDE declarado; **si la tasa real de detección < la potencia declarada, la idea muere**. → **MP-5**.

### I-02 **El tiempo como ley exacta (1 440 min)** — *prueba ya hecha*
*La idea:* de los 9 presupuestos, el tiempo es el único con **σ = 0**: el día tiene 1 440 minutos. Todo día debe cerrar; el residuo = minutos sin contabilizar (datos faltantes, sensor sin llevar, actividad encubierta).
*Resultado real (2026-11-15, `scripts/cierre_tiempo_lifesnaps.py`, LifeSnaps, 3 549 días con actividad y sueño):* **84,8 % cierran a 1 440 ±1 min (2 995 con residuo 0)**; 497 días quedan por debajo de 1 440 y 42 por encima. En los 3 534 días **sin** registro de sueño, la actividad sola suma 1 440 (mediana).
*Cuidado (honestidad):* es una **identidad contable del export de Fitbit, no una ley fisiológica**. Sirve como **compuerta de calidad de datos** (`estado_linea = sospechoso` para el 15 % que no cierra), no como detector de salud.
*Siguiente:* usarlo como regla de LB-1 para el presupuesto `tiempo` (fila M2.9).

### I-03 ★ **Experimento natural: clima espacial × cuerpo** — la primera tarjeta DC-12 con datos reales
*La idea:* LifeSnaps (71 personas, 2021-04-08 → 2022-01-22; sueño, pulso, HRV `rmssd`, temperatura) + el **Kp histórico de GFZ** (CC BY 4.0, 3 h, hasta ayer) = dos fuentes **reales** y de acceso abierto que ya tenemos. La tormenta geomagnética es una exposición **exógena** que afecta a todos por igual en el mismo día: se puede estimar la **sensibilidad personal** (cada persona contra sí misma, N-of-1 con control natural).
*Evidencia previa (débil, discutida):* un estudio pequeño de 31 días con 10 personas halló correlaciones entre HRV y actividad geomagnética (McCraty et al., [PMC5551208](https://pmc.ncbi.nlm.nih.gov/articles/PMC5551208/), 2017; verificado). La búsqueda no halló estudios grandes, preregistrados ni replicados con sueño objetivo.
*Primera prueba:* acta preregistrada **antes** de mirar; hipótesis y regla de muerte escritas; si la sensibilidad no supera el azar (permutaciones de fechas con semilla pública), **la tarjeta muere y se publica**. Un resultado nulo también es contribución. → **MP-6**.
*Límite:* sin mecanismo citable fuerte la tarjeta no pasa la puerta de DC-12; se registraría como **exploratoria** con mecanismo «hipotético».

## Ideas de diseño (sin dato todavía)

### I-04 **Contrapeso personal** — el balance de masa/energía del propio cuerpo
Ewert & Stromgren: *«given steady body mass, each individual's mass inputs and outputs will balance»* (`parametros-publicos.md` P-10). Extremo: un cierre **por persona** (ingesta − gasto − Δ masa). Un residuo persistente = enfermedad oculta, deshidratación, anorexia (el titular de v4). *Bloqueo:* requiere ingesta registrada; LifeSnaps trae calorías gastadas pero no la ingesta (por confirmar). Sin dato real, queda en idea.

### I-05 **Cadena de preregistros con sello de tiempo externo**
Cada acta incluye el hash de la anterior (cadena solo-anexar) y se ancla a un **sello de tiempo de tercero** (el estándar RFC 3161 existe: [rfc-editor.org/rfc/rfc3161](https://www.rfc-editor.org/rfc/rfc3161), página comprobada) o a un registro público. Hoy el hash prueba *qué* se escribió, no *cuándo*; el sello de un tercero prueba el «antes de correr» de forma verificable por cualquiera. *Primera prueba:* sellar las actas FB-005…008 y verificar que el sello valida sin confiar en nosotros.

### I-06 **Atlas de ceguera**
Para cada presupuesto publicar la curva **efecto mínimo detectable vs σ del manifiesto**: «esto es lo que ALMA NO puede ver». La honestidad acotada como producto (el propio radar la nombra «mapa de frontera»). Es el entregable gráfico de I-01.

### I-07 **Presupuesto de alarmas (Neyman–Pearson con límite de atención)**
La fatiga de alarmas es peligro #1 (Cvach 2012, PMID 22839984, verificado). Extremo: fijar de antemano **≤ k alarmas por tripulación-día** y *optimizar* el detector para maximizar la detección dentro de ese presupuesto, en vez de fijar un umbral. *Primera prueba:* en silicio, comparar detección con umbral fijo vs con presupuesto de alarmas a igual número de alarmas.

### I-08 **Autonomía escalonada por retraso de luz**
El umbral de severidad para escalar a la Tierra depende del retardo (cuanto mayor, más autonomía local). El bestiario cita 4–24 min de ida a Marte (**sin verificar por mí**). Formalizar «human-in-command» con la latencia como parámetro del recibo. *Primera prueba:* simulación de política de decisión; requiere fuente verificada del retardo.

### I-09 **Chaos engineering del libro: «día sin sensor»**
Apagar a propósito un testigo al azar (ablación planificada, SIMULADA) y medir cuánto se ensancha σ del manifiesto y cuánto cae la potencia del cierre (ata con MO-8). Mide la **resiliencia** del libro, no solo su exactitud. *Primera prueba:* en silicio con la semilla pública; criterio de muerte: el cierre no degrada de forma graduada.

### I-10 **El adversario evolutivo → frontera de evasión**
Un algoritmo evolutivo busca la **perturbación más pequeña** que evade los detectores (el «impostor elegante»), y publica la **frontera de evasión**. Convierte El Adversario (M4.4) en un resultado cuantitativo reproducible. *Primera prueba:* en silicio, SIMULADO, semilla pública.

## Salto extremo (alucinación controlada — no pasa la puerta hoy)

### I-11 **Residuo de producción de entropía**
Pensar tripulación + hábitat como un sistema termodinámico y usar el **desbalance de producción de entropía** como un residuo universal (la «fiebre» del hábitat). **Es puramente especulativo:** no tiene ancla, y con los sensores disponibles no sería computable. Se deja escrito como experimento mental; si algún día hay telemetría termodinámica real, se revisa.

### I-12 **Ley de conservación de la confianza**
Si cada detector reparte una «masa de confianza» finita entre hipótesis, ninguna alarma puede aumentar su confianza sin que otra baje (suma conservada) → cierra el hueco de las alarmas que «siempre suben». **Sin ancla ni prueba definida:** idea para pensar, no para construir.

---
**Reglas de este documento:** una idea sin prueba falsable no sube de aquí. Lo que sobreviva a su primera prueba entra a `docs/propuestas.md` y, si el humano la acepta, a la cola.
