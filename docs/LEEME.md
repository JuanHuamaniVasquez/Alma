# LEEME — Cómo armar el repo de ALMA para trabajar con Claude Code (5 minutos)

## 1 · Qué va donde

Crea el repo (p. ej. `alma/`), inicializa git, y coloca:

```
alma/
├── CLAUDE.md                      ← del kit (raíz del repo; Claude Code lo carga solo en cada sesión)
├── TASKS.md                       ← del kit (raíz del repo; es la única lista viva de trabajo)
├── .claude/
│   └── commands/
│       ├── implementar.md         ← del kit (comando /implementar)
│       └── auditoria.md           ← del kit (comando /auditoria)
├── docs/
│   ├── README.md                                                        ← DOC-00 Manifiesto (v0.2)
│   ├── DOC-01_MAP-S1-mapa-maestro-sistema-v0.2.md                      ← LA LEY (contratos DC-01…DC-12)
│   ├── DOC-02_MAP-S2-genesis-nueva-generacion-v0.3.md                  ← actas FB-005…008 + anclas C-1…C-23
│   ├── DOC-03_TONO-pitch-equipo-v0.2.md                                ← guion de equipo, pantallas, calendario
│   ├── DOC-04_LA-FUNDICION-laboratorio-v0.2.md                         ← el laboratorio (DC-12, Faro, Adversario)
│   ├── inventario-maestro-bestiario.md                                 ← tu archivo de upload (bestiario K-1/K-2)
│   ├── radar-nasa.md                                                   ← tu archivo de upload (escala honesta T1-T4)
│   ├── ALMA-documento-del-proyecto-v0.3.pdf                            ← DOC-05, fuente fundacional
│   └── actas/                                    (vacía; aquí viven los preregistros FB-xxx con hash)
├── data/                          (vacía; aquí entran SWPC, extracto OS-892, fichas de verdad, fixtures)
└── scripts/ + src/…               (se crean en M0.2 según CLAUDE.md §7)
```

- Los 5 docs oficiales están en `download/` con sus nombres exactos de la tabla de DOC-00 §2. **No los renombres ni los edite Claude:** son la fuente; el código los implementa.
- `v4 (1)(2).docx` de upload: no hace falta para codear (es material histórico anterior al PDF v0.3). Inclúyelo en `docs/` solo si quieres tenerlo a mano.

## 2 · La primera sesión (script literal)

Abre Claude Code en la raíz del repo y pega:

> Lee CLAUDE.md y TASKS.md. No implementes nada todavía: primero cierra conmigo la decisión M0.1 (stack). Después ejecuta /implementar para M0.2.

Claude Code ya habrá leído CLAUDE.md automáticamente (eso hace el archivo: cargarse en cada sesión sin que lo pidas). A partir de ahí:

- **Una sesión = un ítem = un commit.** No pidas "implementa todo": pide el siguiente ítem de la cola.
- Si Claude se va por las ramas, la salida es siempre la misma: *"trabaja el ítem de TASKS.md, no eso"*.
- Entre tareas distintas, usa `/clear` (contexto limpio; CLAUDE.md se recarga solo). Con `/auditoria` cada ciertas sesiones (recomendado: al cerrar cada bloque M).
- Para módulos nuevos grandes (LB-1, LA SALA), deja que proponga el plan antes de codear (plan mode).

## 3 · Por qué esto evita el olvido (la mecánica, no la esperanza)

1. **CLAUDE.md se inyecta en cada sesión** — los mandamientos, los contratos y el protocolo no dependen de que Claude "recuerde": están en su contexto de entrada. Los DOC largos NO van ahí (quemarían el contexto); van como referencia bajo demanda por el mapa §6.
2. **La cola TASKS.md con regla dura** — "primero añade la fila, luego implementa" significa que nada que pidas puede vivir fuera de la lista, y lo marcado con `[x]` lleva tests + hash de commit como evidencia.
3. **El compilador y los tests son la memoria que no falla** — los contratos DC-xx materializados como schemas con tests de rechazo (M0.3) hacen imposible "olvidar" un campo: si falta `regla_exacta` o `fuentes[]`, el test se pone rojo y lo grita. FB-002 (10/10, 21 días) como test de regresión permanente hace imposible "olvidar" el resultado.
4. **/auditoria cada cierre de bloque** — caza stubs, datos fake, implementaciones fuera de la cola y violaciones de los 3 mandamientos. El olvido se detecta, no se presume.
5. **Git por ítem** — el historial es la memoria externa: cada `[x]` es trazable a un commit y un test.

## 4 · Los 3 devs en paralelo (sin pisarse)

- El repo es uno; las sesiones se reparten por frente como DOC-03 §5: **Dev A** → M1 (libro, Contrapeso, endpoints) · **Dev B** → M0.4-M0.5, M2, M4 (motor, falsaciones, FUNDICIÓN) · **Dev C** → M3 (vitrina). Cada quien corre su propio Claude Code en su carpeta (`src/libro/`, `scripts/+src/motor/`, `src/superficies/`).
- Regla de convivencia: nadie toca los contratos (M0.3 es de Dev A y nadie más); el que toca un DC-xx avisa en el commit — es bump de versión de DOC-01, no un refactor (CLAUDE.md §9.4).
- Opcional — `.claude/settings.json` para no aprobar cada comando:

```json
{
  "permissions": {
    "allow": ["Bash(pytest*)", "Bash(python *)", "Bash(git status*)", "Bash(git diff*)", "Bash(git log*)", "Bash(git commit*)"]
  }
}
```

## 5 · Si el tiempo aprieta (orden de sacrificio ya decidido)

El orden de prioridad está en DOC-03 §5 y la cola lo respeta: P0 = M0 → M1 → M2 → M3.1-M3.4. Si hay que cortar, se corta de abajo hacia arriba (M3.6, M4.5, LA MESA…), **nunca** los compromisos de CLAUDE.md §10: FB-002 reproducible, Contrapeso, demo kill, ≥5 tarjetas (corte honesto: 5), 1 Faro, 1 escape.
