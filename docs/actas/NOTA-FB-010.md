# Nota sobre el resultado de FB-010 — el veredicto y lo que de verdad demuestra

## Resultado oficial (preregistrado, 1 ejecución; pulso, personas de PRUEBA, n = 77 unidades de 33 personas)
| | Sin blanquear (control) | Blanqueado (φ̂ = 0,182, estimado solo en entrenamiento) |
|---|---|---|
| Falsas alarmas | **2 / 77 = 2,60 %** (Wilson95 [0,7, 9,0]) | **2 / 77 = 2,60 %** (idéntico) |
| Potencia a 1,0σ / 1,5σ / **2,0σ** / 3,0σ | 38 / 78 / **92** / 100 % | 22 / 65 / **92** / 100 % |

**Veredictos (reglas del acta):** **H1′ SOSTENIDA** (x_pw = 2 < x crítico = 3 y x_pw ≤ x_base) · **H2′ SOSTENIDA** (92 % ≥ 80 % a 2σ).

## Lo que el veredicto NO demuestra (honestidad)
1. **El blanqueado no cambió nada en las personas de prueba** (2 vs 2). Y el control sin blanquear **también pasó** la regla de H1′ (2 < 3). **Defecto de diseño de mi acta:** la regla «no refutado y no peor que el control» se cumple trivialmente cuando el control ya está bien, así que **la prueba no podía distinguir** el detector corregido del original. Lección: una hipótesis de «mejora» debe exigir una diferencia demostrable, o la prueba debe diseñarse con un control que falle.
2. **La mejora solo aparece en muestra** (descriptivo, no decide nada): en las personas de entrenamiento el FPR baja de **5/67 = 7,5 %** a **2/67 = 3,0 %**, coherente con la simulación AR(1). Es sugestivo, **no evidencia fuera de muestra**. Las dos mitades suman los 7/144 de FB-009 (5 + 2).
3. **El blanqueado tiene un costo real en potencia a cambios pequeños** (1,5σ: 78 % → 65 %; 1,0σ: 38 % → 22 %), previsto por la teoría (la señal se atenúa por √((1−φ)/(1+φ))). A 2σ no se nota (92 % en ambos).
4. En sueño (φ̂ = −0,056) no hay nada que corregir y no cambia el FPR (0 en ambos).
5. **No es una confirmación independiente:** son los mismos datos de FB-009.

## Qué se concluye
La **evidencia a favor del blanqueado es la simulación (ρ = 0,4: 7,7 % → <2,5 %) y la mejora en muestra (7,5 % → 3,0 %)**, no el veredicto de FB-010. Para afirmarlo hace falta un **dataset independiente** → **MP-12**. Mientras tanto, la afirmación honesta es: *«el CUSUM sin blanquear se descalibra con autocorrelación (demostrado en simulación y visto en pulso real); el blanqueado AR(1) lo corrige en simulación y en muestra; su efecto fuera de muestra no se pudo demostrar con estos datos»*.
