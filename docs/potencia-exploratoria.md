# Potencia del detector (MO-1 + MO-3) — EXPLORATORIO, SIMULADO

> **Estatus:** exploración, **no preregistrada**: sirve para saber qué esperar y como insumo de MP-5 («verde con potencia», M2.10), cuyo resultado oficial saldrá de un acta registrada ANTES. Datos **SIMULADOS** (registro X-06): ruido gaussiano N(0,1), semilla pública **20261113**, 2 000 corridas por fila. Procedimiento completo: línea base de 14 días estimada de los datos, σ_efectiva = s·√(1+1/14), CUSUM bilateral (k = 0,5) con **h = 10,01 calibrado** para 1 % de falsas alarmas en 14 días (`src/motor/cusum.py`). Supuestos: ruido gaussiano independiente, σ del sensor despreciable, cambio sostenido que empieza justo al terminar la línea base.

| Cambio sostenido (en σ) | Detectado en ≤ 14 días | Mediana de días hasta alarmar |
|---|---|---|
| −0,5σ | 5,8 % | 11 |
| −1,0σ | 35,0 % | 10 |
| −1,5σ | 74,2 % | 9 |
| −2,0σ | 95,7 % | 7 |
| −3,0σ | 100 % | 5 |
| −4,0σ | 100 % | 3 |

**Lectura honesta:** con una línea base de 14 días y exigiendo 1 % de falsas alarmas, el **efecto mínimo detectable al 90 % de potencia es ≈ 1,8σ** en 14 días; un cambio de medio sigma, que a la persona le puede importar, **no se ve** en ese plazo. Es el costo de una base corta: más días de base o una ventana más larga bajan ese piso. Es exactamente el tipo de afirmación que MP-5 quiere hacer parte del recibo de todo «sin anomalías».

**En datos reales (LifeSnaps, 1 participante, sueño; NO es evidencia, no está preregistrado):** línea base 405,8 min, SD intrapersonal 128,3 min, σ_sensor 102,2 min → σ_efectiva 132,8 min (**manda la persona, no el sensor**); 74 días activos, 99 ausencias, 0 alarmas. Una sola persona sin cambio conocido no dice nada sobre el FPR real: eso es M2.8.
