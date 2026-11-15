# NOTA FB-022 · consistencia física cruzada (UNA ejecución; acta `1a8d7c6e…`, registrada 2026-11-15T18:47:36Z)

Datos: LifeSnaps (REAL, no astronautas), columnas `resting_hr`, `rmssd`, `nightly_temperature`, `full_sleep_breathing_rate`; mitad de entrenamiento / mitad de prueba por persona; eventos inyectados SIMULADOS.

| Par | Personas | Mediana ρ (prueba) | ρ > 0 en |
|---|---|---|---|
| P1 temperatura nocturna ~ pulso en reposo | 47 | **+0,241** | 72 % |
| P2 rmssd ~ pulso en reposo (control positivo) | 33 | **−0,530** | 6 % |
| P3 respiración nocturna ~ pulso en reposo | 33 | **+0,271** | 79 % |

Clasificación sensor/cuerpo con P2 (66 bloques de prueba de 14 días): exactitud balanceada **56,8 %** (h=1,0σ) · **65,9 %** (h=2,0σ) · **67,4 %** (h=3,0σ). El fallo se detecta en 76 % (h=2,0) pero **el 43,9 % de los bloques REALES sin inyección se marcan «incoherentes»**.

| Hipótesis | Veredicto |
|---|---|
| H1 temperatura–pulso | **SOSTENIDA** (ρ = 0,24; 72 % positivos) — **mi predicción REFUTADA fue errónea** |
| H2 control positivo | VÁLIDO |
| H3 respiración–pulso | **SOSTENIDA** (ρ = 0,27; 79 % positivos) — predicción errónea |
| H4 clasificación ≥ 80 % | **REFUTADA** (65,9 %) |

**Lectura honesta.** (1) Los acoplamientos fisiológicos **sí existen** y se sostienen fuera de muestra, con tamaño modesto: temperatura nocturna y respiración se mueven con el pulso en reposo en la mayoría de las personas. Eso respalda usar la respiración, la variabilidad y la temperatura como indicadores acoplados (M6.5). (2) El **clasificador** no sirve tal cual: el residuo no es estacionario (autocorrelación y deriva de la línea base entre mitades), por lo que casi la mitad de los bloques reales parecen «incoherentes»; la exactitud 66 % no justifica ninguna afirmación. (3) Límite de fondo: rmssd y pulso salen del mismo sensor óptico, así que esta prueba no puede decir nada sobre fallos del sensor entero. **Siguiente:** FB-022-v2 con residuos blanqueados AR(1) y bloques con línea base móvil; no antes de decidir el valor del ítem.
**Límites:** no son astronautas; sin conjunto externo; 33–47 personas; inyección simulada define la «verdad» del clasificador; Spearman no prueba causalidad.
