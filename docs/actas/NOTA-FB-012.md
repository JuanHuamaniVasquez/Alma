# NOTA FB-012 · resultado (ejecutado UNA vez; acta hash `a854fa57…`, datos S-12, 31 hogares, 2 116 días observados)

| Hipótesis | Estadístico | IC95 (bootstrap, semilla 20261113) | Veredicto |
|---|---|---|---|
| H1 dependencia temporal (mediana ρ1 > 0,10) | **0,115** | [0,018 ; 0,232] | **INCONCLUSA** |
| H2 magnitud (mediana CV diario ≥ 0,25) | **0,531** | [0,427 ; 0,576] | **SOSTENIDA** |
| H3 independencia entre hogares (mediana corr < 0,10) | **0,126** (200 pares) | [0,081 ; 0,151] | **INCONCLUSA** |
| Control (ρ1 con días barajados en [−0,05; 0,05]) | −0,002 | — | **VÁLIDO** (el estimador no inventa dependencia) |

**Lectura honesta.** (1) La demanda real de una corriente de agua es muy variable (CV ≈ 53 %), mucho más que lo que sugería una σ «pequeña»: el presupuesto `agua` no puede usar una σ relativa de unos pocos %. (2) La dependencia temporal es positiva y pequeña (≈ 0,1) pero con 31 hogares **no se puede afirmar** ni que supere ni que no supere 0,10: el IC lo contiene. Mi predicción (0,0–0,2) acertó. (3) Entre hogares hay una correlación positiva pequeña (0,13): la independencia total **no** es exacta y tampoco se puede cerrar contra 0,10. **No se re-corre** ni se cambia el umbral (HARKing); la conclusión operativa es que el Contrapeso debe declarar `correlaciones` ρ≈0,1–0,15 como supuesto sensible, no ρ=0.
**Límites:** hogares de Utah, no hábitat ni astronautas; días sin eventos tratados como no observados (puede subestimar días de bajo consumo); 2 116 días en total.
