# NOTA FB-020-v2 · canal de varianza robusto, ajuste en LifeSnaps y validación fuera de muestra (UNA ejecución; acta `bed7bc32…`, registrada 2026-11-15T10:56:25Z)

**Entrenamiento (LifeSnaps, sueño + pulso: 257 ventanas; potencia en sueño con zigzag H = 2,0):**

| Candidato | Crítico | FPR entrenamiento | Potencia H=2,0 |
|---|---|---|---|
| C2 · MAD, crítico normal | 2,2780 | 8/257 = 3,11 % (no apto: > 3 %) | 95,0 % |
| C3 · F, crítico empírico | 5,0081 | 5/257 = 1,95 % | 65,0 % (no apto: < 80 %) |
| **C4 · MAD, crítico empírico** | **2,3445** | **5/257 = 1,95 %** | **94,0 %** |

**Elegido: C4** (único apto; mi predicción de C3 o C4 fue acertada en parte). Dato de interés: pasar de la varianza a la **MAD** conserva la potencia (94 % frente a 65 % del F con el mismo ajuste empírico): el estadístico robusto es la mejora, no el umbral.

**Validación (Zenodo 8018238, crítico congelado 2,3445):** **solo 5 ventanas de 5 personas en sueño** (y 5 en pulso). FPR 0/5, Wilson95 [0 %; 43,5 %]. Con zigzag: H=2,0σ 100 %, H=3,0σ 100 %; CUSUM de media 0 %.

| Hipótesis | Veredicto |
|---|---|
| H1 FPR fuera de muestra (sueño) | **NO CONCLUYENTE** (0/5; límite superior 43 % ≫ 6 %): la muestra no puede ni sostener ni refutar |
| H2 potencia a 2,5σ | SOSTENIDA (5/5), con la misma salvedad de n |
| H3 CUSUM de media ciego | SOSTENIDA (0/5), idem |
| H4 control positivo | válido (5/5 a 3σ) |
| H5 FPR pulso | SOSTENIDA (0/5) — sin valor probatorio con n = 5 |

**Lectura honesta.** (1) **El experimento no pudo contestar su pregunta central:** Zenodo 8018238 casi no tiene tramos de ≥ 42 días válidos dentro de 60 días (las series tienen huecos), así que la validación fuera de muestra tiene **potencia estadística nula**. Es un fallo de **disponibilidad de datos**, no del canal; yo no medí el número de ventanas antes de preregistrar (la no-ceguera del acta lo declaraba). (2) **No se sustituye el canal gaussiano** (regla del acta: solo si H1 y H2 se sostienen): sigue **sin emitir verde ni alarma con datos reales**. (3) Lo que sí queda establecido en datos reales de entrenamiento: C4 (MAD + crítico empírico al 98 %) tiene FPR 1,95 % y potencia 94 % a 2σ **dentro de muestra**, es decir, un candidato prometedor, no validado.
**Siguiente:** M2.22 — necesita un conjunto independiente con **≥ 300 ventanas** de 42 días válidos (el límite superior de Wilson ≤ 6 % exige ~0/100 como mínimo; con FPR verdadero 2 %, ~300). Candidato por verificar: PMData (no verificado en esta cuenta) u otro Fitbit longitudinal abierto; hasta entonces bloqueado por dato (política: no se simula la felicidad).
**Límites:** no son astronautas; n = 5 en validación; el crítico empírico se ajusta en el mismo LifeSnaps visto en FB-020; zigzag simulado; unilateral al alza.
