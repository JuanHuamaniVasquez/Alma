# NOTA FB-019 · techo de información de la detección de varianza (UNA ejecución; acta `5a38124d…`; SIMULADO)

Potencia frente al zigzag (400 corridas, α nominal 1 %, FPR reales 0,5–1,25 %):

| Prueba | H = 1,0 | H = 1,5 | H = 2,0 |
|---|---|---|---|
| F con línea base de 14 días | 13,0 % | **40,2 %** | 76,8 % |
| F con línea base de 28 días | 23,8 % | 67,8 % | **95,0 %** |
| **Oráculo** (σ² conocida; el techo) | 41,5 % | **91,2 %** | 99,8 % |
| |z|-CUSUM (línea base 14 d) | 10,8 % | 35,2 % | 73,2 % |

**H1, H2, H3, H4 SOSTENIDAS** (mis cuatro predicciones acertaron).
**Conclusión (ingeniosa y útil):** el punto ciego de FB-018 **no es sobre todo un problema de detector** sino de **información**: con una línea base de 14 días, hasta el mejor estadístico posible (F) solo detecta el 40 % de un zigzag de 1,5σ; el oráculo que conociera σ² llegaría al 91 %, así que **el cuello de botella es estimar la varianza personal con 14 datos**. Cambiar de CUSUM (z², |z|) no lo arregla (35–67 %). Lo que sí lo arregla es **más línea base: con 28 días, F detecta el 95 % del zigzag de 2σ y el 68 % del de 1,5σ.** Esto conecta con FB-011 (el recibo de verde ya declara el MDE según los días disponibles): el canal de **varianza** necesita su propio mínimo de días (≥ 28 en la línea base) y su propio recibo; con menos, debe emitir `sin_datos_suficientes`, no verde.
**Límites:** SIMULADO; ruido normal independiente (la autocorrelación real del pulso, ρ≈0,18, empeora la estimación de la varianza); zigzag perfecto; α = 1 %. Propuesta **MP-15** (canal de varianza con línea base de 28 días y recibo propio) en `propuestas.md`.
