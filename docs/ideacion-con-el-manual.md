# Cómo se aplicó el *Manual de Ideación y Creatividad con IA* a ALMA (2026-11-15)

> Se leyó **solo** ese manual (indicación del humano). Esto es el registro honesto de qué método se aplicó, qué salió y qué **no** se tomó. Los productos son: `linaje-de-residuos.md`, `red-team.md`, `ficha-de-verdad.md`, la corrección del Contrapeso (D-23) y las propuestas MP-9 y MP-10.

## Ficha de inicio (Parte VI, 6.1)
- **Problema real en una frase:** en una misión larga la tripulación debe detectar sola cambios de salud mientras los sensores y los manifiestos pueden mentir, y no hay una forma barata de saber **qué parte del libro no cuadra ni por culpa de qué**.
- **Quién lo sufre y cuánto:** la tripulación (salud) y la misión (recursos): en la ISS, 14 de 20 componentes con MTBF distinto del estimado fallaron más de lo previsto, entre 1,9× y 22× (Jones 2019).
- **Inspiraciones lejanas traídas:** historia de la ciencia (residuos de conservación), química analítica (recuperación de picos), ingeniería de procesos (conciliación de datos), teoría de juegos (el número de intercambio), cibernética (alarmas contestables).
- **Con qué se demuestra:** datos reales (SWPC, LifeSnaps, OSDR), tests, y un banco de mesa físico (MP-9).

## M.A.E. (Parte III): fusión
**Fusión elegida:** *conciliación de datos* (ingeniería de procesos) × *recuperación de picos* (química analítica) × *historia de los residuos* (Neptuno/neutrino) → **un Contrapeso que no solo detecta, sino que mide su propio poder de detección inyectando cantidades conocidas, y que sabe que puede equivocarse de causa.**
Metodologías radicales del manual que **viven** en ALMA: *termodinámica* (conservación de masa/energía), *cibernética* (alarmas contestables que se retiran solas; bucle de recalibración), *teoría de juegos* (el Adversario; el número de intercambio). Las que **no** se usan: topología, fractalismo, caos (no aportan aquí; forzarlas sería decoración).

## D&R (Parte IV): las tres muertes de las dos ideas nuevas
| | MP-9 Banco de mesa con recuperación de picos | MP-10 Cuarta causa: el modelo |
|---|---|---|
| **Muerte física** | la evaporación y la deriva de las básculas comen la señal | el almacén corporal/atmosférico no es estacionario |
| **Muerte logística** | requiere hardware (básculas, bomba, registrador): lo ha de montar una persona | requiere modelar el almacén: más líneas en el libro |
| **Muerte humana** | exige disciplina de registro; riesgo de «arreglar» el protocolo tras ver datos (HARKing) | el equipo puede sobre-explicar cualquier residuo con «el modelo» |
| **Papers** | recuperación de picos: práctica estándar de química analítica (varias fuentes; %R = (con pico − sin pico)/añadido) | Le Verrier/Vulcano y relatividad (arXiv 2205.03228) |
| **Reconstrucción por fases** | F0 acta + protocolo → F1 registrador → F2 corrida base → F3 picos → F4 análisis | F0 definir el almacén → F1 línea de libro → F2 test |
| **Simulación con modos de fallo** | los tests del Contrapeso ya incluyen fallos (A1) | idem |

## Arquetipos y dimensiones usados
- **Marie Curie** («¿qué información invisible lo resuelve?») → el residuo que no cierra es la información invisible → `linaje-de-residuos.md`.
- **Sócrates** («solo sé que no sé nada») → el mapa de lo que NO sabemos en `red-team.md` §D.
- **Feynman** (primeros principios) → conservación de masa con unidades físicas.
- **Dimensiones:** *Alquimia del Error* (→ red team A1–A5), *Arqueología del Futuro* (→ linaje), *Ingeniería del Azar* (→ picos centinela aleatorios, MP-9), *Dialéctica del Opuesto* (→ verde con potencia, MP-5), *Topología del Tiempo* (→ 3 futuros: ISS/Luna/Marte; idea I-08).
- **Aporte 2** (Red Teaming), **Aporte 4** (Must/Should/Could + Plan B), **Aporte 6** (Ficha de Verdad) → `red-team.md`, `ficha-de-verdad.md`.

## Lo que NO se tomó del manual (y por qué)
- **«Genera datos sintéticos cuando no tengas datos reales»** (5.6 nº 4): **choca con la política de datos** de este proyecto. Aquí solo se simula con la etiqueta SIMULADO y registro; nunca se presenta como dato.
- **Aporte 3 (CER con «costos ficticios pero consistentes»)**: se sustituye por un número **derivado de datos de NASA** (0,30 kg/día = 8,4 % del O₂ diario), no por costos inventados.
- **Aporte 1 (entropía)**: no se usa; no hay aquí una medida de entropía computable (I-11 queda como experimento mental).
- **Three.js / marco militar**: otra aplicación; ALMA no lo necesita.
