# Nota posterior (post-hoc) sobre FB-005-D1 — sensibilidad a errores correlacionados

> **Esto NO forma parte del acta registrada ni cambia su resultado** (`RESULTADOS.jsonl`, `FB-005-D1.md` intactas, hash verificado). Es un análisis posterior, declarado como tal, motivado por el red teaming (`docs/red-team.md`, ataque A1): el acta sumó los errores en cuadratura asumiendo **independencia**, pero los consumos de los astronautas comparten el mismo modelo de manifiesto.

Recalculando con los mismos residuos medidos, en el **peor caso** de correlación total (ρ = 1) entre los 4 consumos (aritmética mía, derivada):

| | σ propagada | umbral 2σ | residuo «fuga» (+0,260 kg) | residuo «control» (−0,060 kg) |
|---|---|---|---|---|
| Independientes (acta) | 0,055 kg | 0,110 kg | NO CIERRA ✓ | CIERRA ✓ |
| Correlación total (peor caso) | 0,102 kg | 0,205 kg | **NO CIERRA ✓** | **CIERRA ✓** |

**Conclusión honesta:** la demostración **aguanta** el peor caso. Lo que cambia es el **efecto mínimo detectable**: sube de ≈0,11 a ≈0,205 kg/día (3,1 % → 5,8 % del O₂ diario de la tripulación, 3,56 kg). Una fuga de 0,30 kg/día (8,4 % del consumo) se detecta en ambos; una de 0,15 kg/día **solo si se asume independencia (y entonces sería una falsa alarma si los errores están correlacionados)**. Código: `src/motor/contrapeso.py` (`correlaciones`), 5 tests nuevos.

**El número para el jurado** (derivado, SIMULADO): una fuga invisible de 0,30 kg/día se come **9,0 kg de O₂ en 30 días = 2,5 días de oxígeno de la tripulación**; el manifiesto no la ve nunca, el Contrapeso la ve el primer día.
