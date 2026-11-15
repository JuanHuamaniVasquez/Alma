---
description: Auditoría anti-olvido — verificar que lo declarado hecho está realmente hecho y que nada se implementó fuera de la cola
---

Eres el auditor del repo de ALMA. Tu trabajo es cazar el olvido, el stub y la trampa. No implementes nada: solo audita y reporta.

1. Lee `CLAUDE.md` y `TASKS.md` completos.
2. **Ítems marcados [x]:** para cada uno, localiza la implementación real en el código. Si encuentras stub, TODO, dato fake, valor hardcodeado que simula el resultado, o test que siempre pasa — desmárcalo y anótalo.
3. Corre **pytest completo** y lista los rojos con el archivo y la línea del fallo.
4. **Compromisos del submit (CLAUDE.md §10):** verifica uno a uno y con evidencia:
   - FB-002 reproduce 10/10 detecciones y preaviso mediano 21 días con las semillas 20261113/14/15;
   - LB-1 cierra y el Contrapeso produce `NO CIERRA` ante fuga no contabilizada;
   - FB-003 y FB-005 tienen acta con hash publicado ANTES de correr (el hash del acta precede al commit de ejecución en el historial de git);
   - LA SALA y EL RESIDUO renderizan con datos del banco; LA TORMENTA conecta SWPC;
   - hay ≥5 tarjetas DC-12 con fuente con identificador, precio y preregistro_hash;
   - hay 1 predicción del Faro fechada; hay 1 escape del Adversario documentado.
5. **Los 3 mandamientos en el código (CLAUDE.md §3):** busca violaciones —
   - ¿algo lee directo de sensores sin pasar por LB-1 o contratos de eventos?
   - ¿alguna corrida/experimento ejecuta sin preregistro hasheado previo?
   - ¿algún color/semaforo en UI sin regla contestable que lo autorice?
   - ¿algún registro sin banner REAL/SIMULADO? ¿alguna pantalla con contenido individual?
6. **Contratos:** ¿alguna fila creada sin usar los schemas de DC-01…DC-12? ¿algún campo de los "no pueden faltar" (CLAUDE.md §4) ausente en código nuevo?
7. Reporta al final, en una tabla: **ítem → estado real → evidencia → hueco**. Cierra con la lista de ítems desmarcados y el número mínimo de sesiones para recuperar el verde.
