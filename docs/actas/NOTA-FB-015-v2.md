# NOTA FB-015-v2 · réplica reconstruida de FB-002 — **PARCIAL** (UNA ejecución; acta `78c66d73…`; SIMULADO, modelo propio, NO ciega)

Parámetros ajustados: **r = 9 min/día, σ_obs = 0,2**; h calibrado = **201 min** (FPR 1,80 %; el documento dice 200 — consistencia de escala, ya que σ_L se fijó para eso).

| γ \ τ | τ=7 | τ=3 | τ=1 |
|---|---|---|---|
| 0,06 | **20,0** (doc 22,0)* | 17,0 (19,5) | 14,0 (17,0) |
| 0,12 | 12,0 (9,5) | 9,0 (6,0) | 6,0 (5,5) |
| 0,20 | **7,0** (3,0)* | 5,0 (0,5) ✗ | 3,0 (0,0) |
\* celdas usadas en el ajuste. ✗ única celda predicha fuera de ±4 d (criterio de 0,5: ≤ 4,5; salió 5,0).

**Veredictos:** H1 (≥ 5/7 predichas) **SOSTENIDA** — **6/7**; H2 (monotonía en γ y τ) **SOSTENIDA**; H3 (escala de h) **SOSTENIDA**; **H4 REFUTADA**: solo **8/10** corridas con preaviso ≥ 2 d (dos corridas dieron preaviso −1: el ánimo alarmó antes por ruido), y el ajuste no pudo llevar la celda γ=0,20 a 3,0 (queda en 7,0; pérdida 29). **Estado: PARCIAL.**

**Lectura honesta.** (1) Un modelo mecanístico mínimo (ocio que erosiona → ánimo como integrador con memoria τ y sensibilidad γ) reproduce **la estructura** de la Tabla 9: el preaviso decrece con γ y crece con τ, a escala correcta (h≈200 min, mediana nominal ≈ 20 d). Eso es compatible con el documento. (2) **No** reproduce el «10/10»: con ruido real de medida hay corridas donde el ánimo gana. El 10/10 del documento puede ser cierto para su modelo, pero **no** queda replicado: se cita como «documentado, no replicado; reconstrucción propia con 8/10». (3) La mediana nominal (20 d) y la del documento (21–22 d) son compatibles **porque se ajustó** a ella: no cuenta como confirmación. (4) r = 9 min/día con σ_L = 14 es una escala del modelo, no una afirmación sobre tripulaciones.
**Consecuencia para el pitch:** la frase honesta es «una réplica independiente y no ciega de nuestra propia simulación reproduce la estructura del mapa de frontera (6/7 celdas) y el umbral de 200 min; el 10/10 original no se pudo replicar (8/10)». Nada de datos reales de astronautas respalda esto: es un resultado en silicio.
