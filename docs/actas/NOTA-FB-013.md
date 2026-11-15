# NOTA FB-013 · validación independiente (UNA ejecución; acta `49cc322d…`; Zenodo 8018238, 66 personas sanas, REAL, no astronautas)

| Indicador | Sin blanquear | Blanqueado (φ congelado de LifeSnaps) | φ propio del dataset |
|---|---|---|---|
| Pulso | FPR 2/66 = 3,0 % (IC95 0,8–10,4) | 2/66 = 3,0 % | **0,185** (LifeSnaps: 0,182) |
| Sueño | 0/60 = 0 % (IC95 0–6,0) | 0/60 = 0 % | −0,048 (LifeSnaps: −0,056) |

**Veredictos (reglas del acta):** **H1 REFUTADA** — el problema de FB-009 (descalibración del pulso) **no se replicó**: x_base = 2 < x_crítico = 3. **H2 NO CONCLUYENTE** — sin problema que corregir, no se puede decir que la corrección generalice. **H3 SOSTENIDA** — potencia con δ = 2σ en pulso, blanqueado: 89,4 % (≥ 80 %); sin blanquear 94 %.

**Lectura honesta.** (1) **Lo que sí replicó, y es lo más sólido:** la **autocorrelación del pulso diario** es 0,185 en datos independientes (0,182 en LifeSnaps) y la del sueño es ≈ 0 en ambos: ese hecho es estable entre cohortes. (2) El **FPR del pulso** en esta cohorte es 3,0 %, **por encima del 1 % nominal pero sin significancia** con n = 66 (la potencia declarada para detectar un 5 % real era ≈ 65 %); es consistente tanto con el 4,9 % de FB-009 como con el 1 %. **No se puede concluir ni que el blanqueado corrige ni que sobra.** (3) En este dataset el blanqueado **no ayudó** (mismo FPR) y **costó potencia a δ ≤ 1,5σ** (62 % vs 77 % a 1,5σ), igual que en FB-010: el coste es consistente, el beneficio no se confirmó. Recomendación operativa: **no activar el blanqueado por defecto**; mantener φ≈0,18 como alternativa documentada para pulso hasta tener más unidades.
**Límites:** cohorte de un estudio de fatiga durante 2020; ≈ 1 unidad por persona; σ proxy; no astronautas. Resultado nulo publicado sin ajustes.
