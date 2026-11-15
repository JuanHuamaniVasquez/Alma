# Referencia documentada de FB-001 y FB-002 (los scripts originales NO están en el repo)

> **Fuente:** `docs/ALMA-documento-del-proyecto-v0.3.pdf` (DOC-05, el documento fundacional; copiado a `docs/` el 2026-11-15, sha256 en `docs/politica-de-datos.md`), **Tabla 3 y Tabla 9**, más el bestiario §10/§12 y DOC-02. Lo que sigue es **lo que los documentos afirman**, no algo que yo haya reproducido. Búsqueda local del 2026-11-15: **no hay ningún script original** (`falsacion_d4_*.py`) en este equipo; el repo `alma-repo-m0` de `~/Imágenes` y de `~/Descargas` es una **reimplementación «equivalente»** (su propio README lo dice) y **no sustituye** a los originales.

## FB-001 · caída metabólica (Tabla 3)
| Dato | Valor documentado |
|---|---|
| Hipótesis preregistrada | «Una caída metabólica del 10 % de una tripulante se detecta en menos de 48 horas sin cuestionarios, si el manifiesto está calibrado» |
| Resultado | **24 horas con 100 % de detección** (sin calibrar: 144 horas) |
| Diseño | **400 corridas por escenario**; falsas alarmas de **≈ 1 % en 14 días** |
| Otros (bestiario §10) | caída del 5 %: ≈ 48 h (90 % en 72 h); sin calibrar el manifiesto, 10 %: 144 h (62,5 % en 7 días) |
| Semillas | 20261113/14/15 |

## FB-002 · el contador de ocio anticipa al ánimo (Tabla 3, Figura 1, Tabla 9)
| Dato | Valor documentado |
|---|---|
| Hipótesis preregistrada | «El contador de ocio cruza su alarma **al menos 2 días antes** que la caída del ánimo, en **7 de 10** corridas» |
| Resultado | **10 de 10** corridas · preaviso **mediano 21 días** (rango 11–40; media 21,4; contra cuestionario semanal 19,4) |
| Umbral | calibrado en **200 minutos**, falsas alarmas **1,8 % en 70 días** (**1 000 líneas base falsas**) |
| Rival | ánimo medido a diario (EWMA diario + semanal) |
| Corrida representativa (nº 10) | alarma de ocio día **23**, alarma de ánimo día **45** → preaviso 22 días |
| Semillas | 20261113/14/15 |

**Tabla 9 — preaviso mediano (días) según sensibilidad γ y memoria τ del ánimo** *(el PDF la marca «Exploratorio: propiedad del modelo, no del mundo»)*:
| γ \ τ | τ = 7 d | τ = 3 d | τ = 1 d |
|---|---|---|---|
| 0,06 (nominal) | 22,0 | 19,5 | 17,0 |
| 0,12 | 9,5 | 6,0 | 5,5 |
| 0,20 | 3,0 | 0,5 | 0 |
Zona de validez declarada: γ ≤ 0,12 **o** τ ≥ 3.

## Lo que NO se conoce (y por qué no se puede «reproducir» tal cual)
El **modelo generativo** (cómo erosiona la carga al ocio, ruidos, unidades de γ, regla del ánimo rival) **no está en ningún documento**. Por eso la cifra «10/10, 21 días» **no es verificable** con lo que hay: solo se puede **replicar de forma independiente** (→ MP-13, `docs/propuestas.md`).
