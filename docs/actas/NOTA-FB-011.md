# Nota sobre el resultado de FB-011 — el recibo de verde, contrastado en datos reales

## Resultado oficial (preregistrado, 1 ejecución; LifeSnaps REAL, no astronautas; caída SIMULADA)
| m días válidos | MDE declarado (90 % de potencia) | **Sueño** (97 unidades): potencia observada | control (MDE/2) | **Pulso** (144 unidades): potencia observada | control (MDE/2) |
|---|---|---|---|---|---|
| 14 | 1,75σ | **94/97 = 96,9 %** [91,3, 98,9] | 15,5 % | **132/144 = 91,7 %** [86,0, 95,2] | 30,6 % |
| 10 | 2,25σ | **96/97 = 99,0 %** [94,4, 99,8] | 18,6 % | **134/144 = 93,1 %** [87,7, 96,2] | 29,9 % |
| 7 | 2,75σ | **96/97 = 99,0 %** [94,4, 99,8] | 10,3 % | **135/144 = 93,8 %** [88,5, 96,7] | 20,1 % |

**Veredictos (reglas del acta):** **H1 SOSTENIDA** (en ningún m se refuta «potencia ≥ 90 %»; el umbral de refutación era ≤ 80/97) · **H2 CONTROL VÁLIDO** (con la mitad del MDE la tasa es 10–19 % ≪ 90 %: la prueba **sí distingue** una afirmación falsa de una verdadera, justo la lección de FB-010) · **H3 REFUTADA: mi predicción preregistrada era equivocada.**

## Lo que dice y lo que no dice
1. **El recibo de verde cumple lo que declara, también con menos días observados** (en estos datos y con días quitados al azar): la cobertura endurece el MDE (1,75σ → 2,75σ) **y la potencia declarada se sigue cumpliendo**. Eso es lo que hace honesto un «sin anomalías con 7 de 14 días».
2. **Me equivoqué en H3:** predije que la tabla iid sería optimista en pulso (potencia < 90 % a 1,75σ) por la autocorrelación, apoyándome en una interpolación lineal de FB-009 (≈ 85 %). Salió **91,7 %** [86,0, 95,2], que incluye el 90 % declarado. La interpolación era mala (la curva de potencia es no lineal entre 1,5σ y 2σ). La autocorrelación que descalibra los **falsos positivos** (FB-009) **no** estropea aquí la **potencia**.
3. **En sueño el 97–99 % es en parte conservadurismo del proxy del sensor:** σ_efectiva (102 min) supera la variabilidad real de la persona (70 min), así que una caída de δ·σ_efectiva es, en términos de la persona, mayor que δ·SD. **El resultado informativo es el de pulso**, donde σ_efectiva ≈ SD de la persona y la potencia observada (91,7 %) coincide con la declarada (90 %).
4. **MDE en unidades físicas** (descriptivo): con 14 días válidos, ≈ **179 minutos** de sueño y ≈ **9,3 lpm** de pulso; con 7 días, ≈ 281 min y ≈ 14,6 lpm.
5. **Límites:** no son astronautas; σ de sensor proxy; los días ausentes se simularon MCAR (la ausencia real probablemente no lo es); bloques de una persona correlacionados; la prueba solo refuta una potencia claramente menor (con potencia real 0,85 se refutaba el 28 % de las veces).
