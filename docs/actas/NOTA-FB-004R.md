# NOTA FB-004R · integrador lento del agua con normalización por caudal (UNA ejecución; acta `de2d5df7…`; tanque SIMULADO, caudal REAL de Utah)

| Detector | Falsas alarmas (δ=0) | Detección δ=0,10 | Mediana | Detección δ=0,20 |
|---|---|---|---|---|
| R (crudo) | **91,0 %** | 67,8 % | 12 d | 71,0 % |
| **N (MP-3, caudal conocido)** | **4,8 %** | **99,8 %** | **10 d** | 99,8 % (6 d) |
| N con caudal barajado (control) | 78,8 % | 78,8 % | 18 d | 85,5 % |

**H1, H2, H3, H4 SOSTENIDAS.** **Mi predicción falló en H3** (esperaba mediana > 15 d; salió 10 d).
**Lectura honesta, que matiza H2:** el detector crudo **no «detecta menos»: está roto** — con el caudal real (CV ≈ 0,53) tiene **91 % de falsas alarmas**, así que su 67,8 % de «detección» es menor que su tasa de ruido y no significa nada. La normalización no es una mejora fina: es lo que **hace utilizable** la señal del agua. El control (caudal barajado) reproduce el desastre (78,8 % de falsas alarmas), lo que confirma que lo que ayuda es el caudal *correcto* y no el truco del residuo. **Límites:** la FPR de N (4,8 %) roza el techo del 5 % (400 corridas: IC95 ≈ 3–7 %); el tanque, la carga y el ruido son supuestos míos (no hay TOC real abierto de la ISS); el caudal se remuestrea sin su autocorrelación; en un hábitat real el caudal se conoce con error (aquí es exacto). Conclusión operativa para MO-5: **sin el caudal como covariable, el TOC del agua no sirve como censo colectivo**.
