# Red teaming de ALMA contra ALMA

> Aplicación de los métodos del *Manual de Ideación y Creatividad con IA*: «Alquimia del Error» (5 formas de fallar + defensa para cada una, Parte V 5.14 nº 6), Red Teaming (Aporte 2), las tres muertes de D&R (física, logística, humana; Parte IV) y Must/Should/Could + Plan B (Aporte 4). Estado de cada ataque: ✅ cubierto y probado · 🟡 parcial · ⭕ abierto (se dice, no se esconde).

## A · Las cinco formas en que el Contrapeso puede fallar

| # | Ataque | Muerte (D&R) | Defensa / estado |
|---|---|---|---|
| A1 | **Errores correlacionados:** los 4 consumos comparten el mismo manifiesto; sumar en cuadratura **subestima** σ y da falsas alarmas | física | ✅ `correlaciones` en `contrapeso.py` + 5 tests; sensibilidad posterior en `docs/actas/NOTA-FB-005-D1-sensibilidad.md`: la demo aguanta, el MDE sube 0,11 → 0,205 kg/día. **Pendiente:** qué ρ reales hay (no se conocen; hace falta dato) |
| A2 | **Régimen no estacionario:** Ewert & Stromgren: las entradas y salidas del cuerpo se igualan *«over time, given steady body mass»*; un cierre **diario** del cuerpo no está garantizado | física | ⭕ el almacén corporal no está modelado como línea; hoy el cierre diario del cuerpo no es válido. Entra en MP-10 (la causa «modelo incompleto») |
| A3 | **Reloj desincronizado** entre sensores: una entrada y una salida medidas en horas distintas parecen un desbalance | humana/logística | ⭕ DC-01…03 llevan `ts_utc` pero no hay chequeo de deriva de reloj entre fuentes |
| A4 | **Cuarta causa del residuo:** el modelo de cierre es incompleto (caso Vulcano, `docs/linaje-de-residuos.md`) | física | 🟡 documentado; **MP-10** propone añadir «modelo» a la triangulación de D6 |
| A5 | **Sensor muerto o recalibrado** en mitad del día: la σ de la línea cambia | logística | 🟡 DC-11/MO-8 diseñados, no construidos; hoy el estado `cuarentena` de DC-04 marca la línea pero la σ no se ensancha sola |

## B · Los cinco ataques universales (Aporte 2 del manual) aplicados a ALMA

| Ataque | Defensa real | Estado |
|---|---|---|
| ¿Qué pasa si falla la pieza central? | El dominio es puro (`src/`) y la API es de solo lectura; un día sin libro responde 404, no un cierre inventado | ✅ `test_dia_sin_libro_es_404…`, `test_un_dia_sin_libro_no_cierra` |
| ¿Y si cortan la dependencia crítica (datos)? | El fallo de un feed es dato (DC-13); sin lectura no se rellena nada | ✅ `test_un_feed_caido_o_vacio_se_registra_y_nunca_se_rellena` |
| ¿Y si la demo falla en vivo? | **Plan B** (abajo) | 🟡 el vídeo no existe aún (M5.2) |
| «Esto parece ciencia ficción» | **Ficha de Verdad** (`docs/ficha-de-verdad.md`) clasifica cada pieza | ✅ |
| «¿Por qué no la solución simple y obvia?» | El número: la fuga que el manifiesto **nunca** ve (0,30 kg/día = 8,4 % del O₂ diario; 2,5 días de oxígeno al mes) | ✅ demo FB-005-D1 (SIMULADA) |

## C · Plan anti-frágil de la demo (Aporte 4)
- **MUST:** la demo «kill» en dos columnas (manifiesto ciego vs Contrapeso alarma) con el hash del acta en pantalla — ya funciona como script (`scripts/fb005_demo_kill.py`).
- **SHOULD:** LA SALA + EL RESIDUO consumiendo la API (M3.1/M3.2).
- **COULD:** LA TORMENTA con SWPC en vivo (M3.3), LA MESA (M3.5).
- **PLAN B:** vídeo de 60 s con la narración, **grabado en cuanto funcione**, no la noche anterior (M5.2). Mientras tanto, la captura de pantalla de la salida de `fb005_demo_kill.py` es el respaldo mínimo.

## D · Lo que NO sabemos (Sócrates: «solo sé que no sé nada»; mapa de investigación)
1. Cuánto valen en la realidad las correlaciones ρ entre errores de manifiesto.
2. Si un cierre **diario** del cuerpo es válido sin modelar el almacén corporal.
3. Si las líneas base de datos terrestres (LifeSnaps) se transfieren a microgravedad.
4. Cómo se comporta el Contrapeso con **telemetría real** de hábitat (no hay datos abiertos).
5. Si una tripulación toleraría pruebas centinela (inyecciones de control conocidas).
6. El resultado de FB-002 (el script no está).
