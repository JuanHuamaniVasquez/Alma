# NOTA FB-021 · alarma anytime-valid (e-proceso), ajuste en LifeSnaps y validación fuera de muestra (UNA ejecución; acta `5072d872…`, registrada 2026-11-15T18:43:55Z)

**Entrenamiento (LifeSnaps, sueño + pulso: 257 ventanas sin inyección; potencia en sueño con escalón H = 2,0σ):**

| s (inflación) | FPR entrenamiento (α nominal = 1 %) | Potencia H=2,0 | Apto |
|---|---|---|---|
| 1,0 | **13/257 = 5,06 %** | 99,0 % | no (FPR) |
| 1,25 | 3/257 = 1,17 % | 89,0 % | no (FPR apenas > 1 %) |
| **1,5** | **0/257 = 0,00 %** | **71,0 %** | **sí → elegido** |
| 2,0 | 0/257 = 0,00 % | 15,0 % | no (potencia) |

**Hallazgo de entrenamiento (lo importante):** con `s = 1` — la teoría tal cual — el FPR real es **5,06 %, cinco veces el α prometido**. La garantía de Ville no sobrevive a los datos reales cuando se ignora la autocorrelación y el error de estimar μ y sd con 28 días. La garantía **solo existe tras calibrar `s`**, y calibrarla cuesta potencia (99 % → 71 % a 2σ). Predicción mía acertada (s = 1,25 o 1,5).

**Validación (Zenodo 8018238, `s` = 1,5 congelado):** otra vez **solo 5 ventanas de 5 personas** (como en FB-020-v2): FPR 0/5, Wilson95 [0 %; 43,5 %]. Escalón: H=2,0σ 100 % (retardo mediano 13 d) y H=3,0σ 100 % (retardo 8 d); CUSUM de media 100 % en ambos.

| Hipótesis | Veredicto |
|---|---|
| H1 FPR fuera de muestra (sueño) | **NO CONCLUYENTE** (n = 5) |
| H2 no inferioridad a 2,0σ | SOSTENIDA (5/5 frente a 5/5, **sin valor probatorio con n = 5**) |
| H3 retardo mediano a 3,0σ ≤ 7 d | **REFUTADA** (8 d) |
| H4 control positivo | válido |
| H5 FPR pulso | NO CONCLUYENTE (n = 5) |

**Lectura honesta.** (1) Igual que FB-020-v2, **la validación fuera de muestra no pudo contestar** por falta de ventanas largas en Zenodo: sigue haciendo falta un conjunto con ≥ 300 ventanas (M2.22). (2) Lo que sí mostró el experimento es **dentro de muestra**: la garantía teórica del e-proceso es **optimista 5×** en wearables reales y la calibración empírica es obligatoria; el resultado es un **caso de estudio de cómo falla la garantía**, no una prueba de que funcione. (3) H3 refutada: el e-proceso calibrado reacciona más lento que el CUSUM (8 d frente a menos de una semana), coste del conservadurismo. (4) El método **no es nuestro** (M6.0); lo publicable es la medición del hueco teoría→datos reales.
**Siguiente:** M2.22 (dataset con ≥ 300 ventanas) o FB-021-v2 con blanqueado AR(1) previo y retardo como criterio de selección. **No** pasa a recibo DC-05: requiere decisión del humano (DOC-01 v0.2.9) y una validación que hoy no existe.
**Límites:** no son astronautas; n = 5 en validación; escalón simulado; ventanas por persona correlacionadas; `s` calibrado en el mismo LifeSnaps visto desde FB-009.
