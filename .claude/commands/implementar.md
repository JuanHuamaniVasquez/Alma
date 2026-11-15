---
description: Implementar el siguiente ítem de TASKS.md con el protocolo completo del proyecto
---

Estás en el repo de ALMA. Ejecuta el protocolo de sesión de CLAUDE.md §8, paso a paso:

1. Lee `TASKS.md` completo y elige el ítem abierto de menor número no bloqueado. Anúncialo: "Trabajo el ítem X: <texto>". Si el ítem depende de una decisión del humano (bloqueo declarado al final de TASKS.md), detente y pregunta eso y solo eso.
2. Abre las referencias de CLAUDE.md §6 que apliquen al ítem y lee las secciones señaladas (no cites números de memoria: ábrelos).
3. Planifica en 5 líneas máximas los archivos que crearás/modificarás y el test que probará el ítem. Si el ítem crea un módulo nuevo, usa plan mode antes de escribir código.
4. Implementa con test primero cuando sea posible: fixture real de `data/`, semillas públicas (20261113/14/15/1111/1112), banner REAL/SIMULADO en toda salida.
5. Respeta los 3 mandamientos de CLAUDE.md §3. Si la implementación natural viola alguno (p. ej. leer sensores directo), detente y rediseña.
6. Corre **pytest completo**. Si algo está rojo, arregla antes de continuar — nunca marques un ítem con la suite roja.
7. Actualiza `TASKS.md`: marca `[x]` tu ítem y añade la evidencia en la línea (tests que pasan + hash corto del commit). No reordenes ni borres nada.
8. Si descubriste trabajo nuevo durante la tarea, añádelo como ítem nuevo al final de su bloque — no lo implementes fuera de la cola.
9. Termina con un `git commit` por ítem (mensaje: `M1.2 MO-6 Contrapeso: DC-08 + test NO CIERRA`) y un resumen de 3 líneas: qué hiciste, qué test lo prueba, qué quedó abierto.
