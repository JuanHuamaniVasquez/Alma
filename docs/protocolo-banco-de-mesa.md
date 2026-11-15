# Protocolo del banco de mesa (MP-9) — El Contrapeso sobre un bucle de agua FÍSICO

> **Estado:** protocolo listo; **el hardware lo monta el humano** (D-25). El acta se registra (hash) **antes** de tomar el primer dato real. Mientras tanto el software (lector de registros y análisis) se puede construir y probar con registros SIMULADOS etiquetados (registro X-07, M2.12a).

## Por qué vale (y qué resuelve)
Hoy el Contrapeso solo se ha probado con simulación y no hay telemetría real de hábitat abierta. Un bucle de agua pequeño, **real**, da: (1) **datos reales de cierre de masa con ruido real de sensores** (el «T3 de mesa»); (2) la **σ empírica en reposo y su autocorrelación**, que son justo los valores desconocidos del red teaming A1 (correlaciones ρ entre errores de manifiesto) y de FB-009; (3) la **potencia medida con picos conocidos** en vez de teórica; (4) un experimento que **cualquier tercero puede repetir** (T4). *Etiqueta honesta:* es un **análogo físico**, no un hábitat ni un humano: banner «REAL (banco de mesa, análogo físico)».

## Aparato (genérico; los precios NO los afirmo: por cotizar)
- **2 o 3 básculas** digitales con salida de datos (o celdas de carga + amplificador + microcontrolador), resolución ≤ 1 g, capacidad adecuada al recipiente.
- **Recipientes:** A (depósito/suministro), B (consumo/colector), C (colector del «pico»: la verdad del suelo).
- **Bomba pequeña o trasvase manual cronometrado** para el flujo programado.
- **Tapas** para reducir la evaporación (la evaporación es una pérdida real que hay que medir o acotar).
- **Ordenador/registrador** con reloj sincronizado; registro a ≥ 1 Hz.
- Solo **agua**; cantidades pequeñas; sin materiales peligrosos.

## Mapeo al Contrapeso (DC-08)
`entradas` = masa que sale del depósito A hacia el circuito · `salidas` = masa recogida en B (flujo programado, «consumo») · `delta_almacen` = cambio de masa retenida en el circuito/depósitos · `pérdida_declarada` = vaciados deliberados y **registrados** · **pico** = una cantidad conocida desviada a C **sin registrarla** (flujo no contabilizado). La verdad del suelo es la masa final de C medida con su propia báscula.

## Fases (cada una con su acta o su sección en el acta)
- **F0 — Reposo (sin picos), ≥ 3 días:** mide el residuo de cierre en reposo → **σ empírica, sesgo y autocorrelación** (alimenta `correlaciones` del Contrapeso y la σ real). *Predicción previa a escribir en el acta:* el residuo en reposo no es gaussiano independiente.
- **F1 — Flujo programado sin picos, ≥ 3 días:** FPR real del Contrapeso con h calibrado y con blanqueado (MP-11).
- **F2 — Picos aleatorizados:** tamaños = fracciones del MDE declarado (p. ej. 0,5×, 1×, 2×), **calendario sembrado con semilla pública y publicado antes**; el análisis no ve la verdad del suelo hasta cerrar. Métricas: **recuperación %R = (residuo con pico − residuo sin pico)/masa añadida × 100** (práctica estándar de química analítica; el criterio 80–120 % es habitual pero **lo fija el acta**), tasa de detección por tamaño, FPR.
- **F3 — Picos declarados (control positivo):** el pico se registra como pérdida declarada ⇒ el cierre debe **CERRAR** (el sistema no alarma por lo que sabe).
- **F4 — Análisis y publicación:** resultado **sea cual sea**, con los datos crudos (CC0/CC BY) y los scripts.

## El acta (a rellenar y REGISTRAR antes de F0)
Pregunta; hipótesis con regla de éxito y **de muerte** (incluida «la señal se pierde en el ruido de las básculas»); semillas públicas; calendario de picos sembrado; criterio de recuperación; reglas de limpieza de datos **fijadas antes**; lo que NO se afirma (no es un hábitat, no son astronautas, evaporación, deriva térmica de las básculas).

## Formato de datos (propuesto)
CSV: `ts_utc` (ISO 8601 UTC), `sensor_id`, `masa_g`, `evento` (vacío / `flujo_programado` / `perdida_declarada`; **nunca `pico`**: la verdad del suelo va en un archivo aparte que se abre al cierre), `banner` = `REAL (banco de mesa, análogo físico)`. Cada archivo crudo se archiva con su SHA-256 (MP-3).

## Qué necesito del humano
Montar el aparato y correr F0–F3; enviarme los CSV. **Qué hago yo mientras:** el lector de registros, el análisis con el código real del Contrapeso y las pruebas con registros SIMULADOS (X-07).
