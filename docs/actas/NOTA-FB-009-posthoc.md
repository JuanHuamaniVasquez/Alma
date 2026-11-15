# Nota POSTERIOR (post-hoc) de FB-009 — por qué la calibración transfiere en sueño y no en pulso

> **No forma parte del acta registrada ni cambia sus veredictos** (`RESULTADOS.jsonl` intacto). Diagnóstico declarado como tal, con `scripts/fb009_posthoc.py` (datos reales + simulación X-06, semilla pública 20261113).

## Resultado oficial (preregistrado, 1 ejecución)
| | Sueño (primario) | Pulso (S2, solo descriptivo) |
|---|---|---|
| Unidades / personas | 97 / 51 | 144 / 65 |
| FPR natural (M1) | **0 / 97 = 0 %**, Wilson95 [0, 3,8 %] | **7 / 144 = 4,9 %**, Wilson95 [2,4 %, 9,7 %], por-persona95 [1,9 %, 8,6 %] |
| Detección a 1,0σ / 1,5σ / 2,0σ / 3,0σ | 27,8 / 86,6 / **100** / 100 % | 40,3 / 77,1 / 92,4 / 100 % |
| **Veredicto** | **H1 NO REFUTADA · H2 SOSTENIDA** | (no decide; con la regla del acta habría sido H1 *refutada*: 7 ≥ 5) |

## Diagnóstico (post-hoc)
| | σ_efectiva mediana | SD intrapersonal mediana | σ_sensor (proxy) | Autocorrelación lag-1 entre días válidos |
|---|---|---|---|---|
| Sueño | 102,19 min | 69,88 min | 102,19 min | −0,02 |
| Pulso | 5,31 lpm | 5,13 lpm | 3,95 lpm | **+0,18** |

**Simulación AR(1) del MISMO pipeline** (3 000 corridas por fila): ρ = 0 → FPR **1,10 %** (la calibración es correcta para ruido independiente) · ρ = 0,2 → **2,87 %** · ρ = 0,4 → **7,67 %** · ρ = 0,6 → **18,67 %**.

## Lectura honesta
1. **En sueño, «no refutada» NO prueba que la calibración se transfiera.** El piso del sensor (proxy de 102 min) supera a la variabilidad de la persona (70 min), lo que infla σ y hace al detector **conservador**: 0 falsas alarmas es en buena parte un efecto del proxy.
2. **En pulso, donde manda la variabilidad de la persona, el FPR real es ≈ 5 veces el nominal.** Se explica por la **autocorrelación** (lag-1 ≈ 0,18): la simulación AR(1) da 2,9 % con ρ = 0,2 y 7,7 % con ρ = 0,4, y lo observado cae entre ambos (además de colas pesadas y rutina semanal sin modelar).
3. **«100 % a 2σ» hay que leerlo en unidades físicas.** En sueño 2σ_efectiva ≈ **204 minutos** de pérdida sostenida de sueño (≈ 3,4 h); en pulso ≈ 10,6 lpm. El efecto mínimo detectable al 90 % es ≈ 1,6σ_efectiva ≈ **163 min** en sueño: **muy grande**, y está dictado por el proxy del sensor, no por la persona.
4. **La calibración es frágil ante la autocorrelación:** un ρ de 0,2 (modesto) triplica las falsas alarmas.

## Qué se hace con esto
- Solución estándar (verificada): **vigilar los residuos blanqueados de un modelo de series temporales** — Alwan & Roberts 1988, *J. Bus. Econ. Stat.*, doi:[10.1080/07350015.1988.10509640](https://doi.org/10.1080/07350015.1988.10509640); Lu & Reynolds 2001, *J. Qual. Technol.*, doi:[10.1080/00224065.2001.11980082](https://doi.org/10.1080/00224065.2001.11980082). → **MP-11** y su evaluación **FB-010** (con validación cruzada por personas, porque estos datos ya se vieron).
- **MP-5 / M2.10 (verde con potencia)** debe expresar la potencia en **unidades físicas**, no solo en σ.
