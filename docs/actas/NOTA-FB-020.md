# NOTA FB-020 · canal de varianza en series REALES (UNA ejecución; acta `c3bca4e3…`, registrada 2026-11-15T10:42:03Z; LifeSnaps REAL, no astronautas, + zigzag SIMULADO)

**Sueño:** 100 ventanas (28 d de base + 14 d de vigilancia) de 43 personas.

| Medida | Resultado | Regla preregistrada |
|---|---|---|
| **FPR real (sin inyección)** | **9/100 = 9,0 %**, Wilson95 [4,8 %; 16,2 %]; 8 personas con ≥ 1 alarma | ≤ 3 % → **H1 REFUTADA** (el intervalo excluye 3 %) |
| Potencia con zigzag H=1,5σ / 1,75σ / **2,0σ** / 3,0σ | 75 % / 96 % / **99 %** / 100 % | H2 (≥ 80 % a 2σ) **SOSTENIDA**; control positivo H4 válido |
| CUSUM de media sobre el mismo zigzag (1,5 / 1,75 / **2,0** / 3,0σ) | 2 % / 3 % / **3 %** / 4 % | H3 (≤ 10 % a 2σ) **SOSTENIDA**: sigue ciego |
| Pulso (secundario), FPR | 13/157 = 8,3 %, Wilson95 [4,9 %; 13,7 %] | solo informativo |

**Predicción mía (acta):** H1 refutada (esperaba 4–10 %), H2, H3 sostenidas, H4 válido → **acertó en las cuatro**.

**Lectura honesta.**
1. **El canal ve lo que el CUSUM no ve** (99 % frente a 3 % en datos reales con zigzag simulado): la idea de MP-15 es correcta como detección.
2. **Pero con el crítico gaussiano (c = 2,85) no puede emitir alarmas ni verdes en datos reales:** 9 % de falsas alarmas, el mismo defecto que el CUSUM de media tenía en el pulso (FB-009). La calibración «normal e independiente» NO transfiere (sueño y pulso reales: colas pesadas y autocorrelación). La potencia de 99 % está inflada por ese mismo exceso de varianza ruidosa: no es un mérito.
3. **Consecuencia aplicada ya:** el canal queda en el contrato (DC-05/DC-14, v0.2.8) pero **no debe emitir verde ni alarma contra datos reales hasta FB-020-v2**; con datos reales, su recibo debe declarar el FPR observado (9 %), no el nominal.

**Siguiente (abierto como M2.21, no se arregla en esta acta):** `FB-020-v2` con un estadístico robusto (p. ej. razón de varianzas por rangos / Brown–Forsythe) o un crítico calibrado por el nulo empírico, **ajustado en LifeSnaps y validado fuera de muestra en Zenodo 8018238** (S-13, independiente), con no-ceguera declarada.

**Límites:** no son astronautas; las ventanas de una persona están correlacionadas (IC optimista); zigzag simulado; unilateral al alza; solo sueño y pulso; n = 100 ventanas.
