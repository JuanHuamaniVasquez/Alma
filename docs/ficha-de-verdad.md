# Ficha de Verdad de ALMA (K-4) — ciencia vs. extrapolación vs. ficción

> Reconstrucción del K-4 que DOC-01 declara y que **no estaba en el repo** (no recupero la original: esta se rehace con lo verificado). Plantilla: Aporte 6 del *Manual de Ideación y Creatividad con IA* (4 clases) **+ una clase propia: SIN VERIFICAR**, porque la honestidad exige separar «no es cierto» de «no lo pude comprobar». Regla de uso: ante «¿esto es real?», se responde con esta tabla.
> CIENCIA REAL = hecho o dato que leí/verifiqué en su fuente · EXTRAPOLACIÓN = ciencia real llevada más allá de lo medido · FICCIÓN CON BASE = base real, uso narrativo · INSPIRACIÓN REAL = campo existente, implementación propia simplificada · SIN VERIFICAR = no pude comprobarlo.

| # | Elemento | Clase | Por qué / evidencia |
|---|---|---|---|
| 1 | Las entradas y salidas de masa de un tripulante se igualan en el tiempo (82 kg: ≈0,84–0,89 kg O₂ y ≈1,01–1,08 kg CO₂ al día) | **CIENCIA REAL** (modelos de planificación) | Ewert & Stromgren 2019 y NASA ICES 2021, leídos (`parametros-publicos.md` P-01…P-10). **Son valores de modelo, no mediciones** |
| 2 | Esas cifras de NASA son coherentes entre sí (RQ implícito ≈0,87–0,88) | **CIENCIA REAL** (aritmética derivada) | `parametros-publicos.md`, «Consistencia interna» |
| 3 | Los manifiestos de fiabilidad de la ISS erraron entre 1,9× y 22× | **CIENCIA REAL** | Jones 2019, NTRS 20190027319 (cita textual P-11) |
| 4 | El cuerpo puede romper la máquina (pérdida ósea → calcio → fallo del procesador de orina) | **CIENCIA REAL** | Jones 2019 citando a Do 2016 (P-12) |
| 5 | Cerrar un balance de masas para detectar errores gruesos es un campo establecido | **CIENCIA REAL** | Narasimhan & Jordache, *Data Reconciliation and Gross Error Detection*; capítulos en Crossref |
| 6 | Un residuo de conservación reveló Neptuno, el radio y el neutrino | **CIENCIA REAL** (historia) | `linaje-de-residuos.md` |
| 7 | …pero también produjo un falso positivo (Vulcano) | **CIENCIA REAL** (historia) | `linaje-de-residuos.md` |
| 8 | El Kp del 9-nov era 3,33 | **CIENCIA REAL** (dato) | archivo de GFZ, CC BY 4.0 (`afirmaciones-por-verificar.md` A-03) |
| 9 | OS-892 existe, es público y no tiene archivos de datos | **CIENCIA REAL** (dato) | API de OSDR + control negativo (`auditoria-de-fuentes.md`) |
| 10 | El 84,8 % de los días de LifeSnaps cierran a 1 440 min | **CIENCIA REAL** (dato) pero **no es una ley fisiológica** | identidad contable del export de Fitbit (`ideas-extremas.md` I-02); personas, **no astronautas** |
| 11 | La σ de sueño/FC de la ingesta (102,2 min; 3,95 lpm) | **EXTRAPOLACIÓN** | límites de acuerdo publicados de **otro** modelo (Charge 2) y otra población; declarada PROXY |
| 12 | La fuga de 0,30 kg/día «invisible» al manifiesto y vista por el Contrapeso | **EXTRAPOLACIÓN** | simulación (SIMULADO): la ceguera del manifiesto es **por construcción**; 1 corrida; la prueba estadística es FB-005 |
| 13 | Detectar en ~24 h una caída metabólica del 10 % de una tripulante | **EXTRAPOLACIÓN** | resultado en silicio de la «Prueba v4», supuestos de manifiesto calibrado; el script no está en el repo |
| 14 | Sensibilidad personal a la actividad geomagnética (sueño/HRV × Kp) | **EXTRAPOLACIÓN** débil | un estudio de 10 personas, 31 días (McCraty 2017); sin replicación; MP-6 la pondrá a prueba |
| 15 | La nave como cámara calorimétrica: la dirección del residuo O₂–CO₂ identifica la causa | **INSPIRACIÓN REAL** | campos establecidos (aislamiento de fallos por firma de residuos; calorimetría indirecta) **sin citar aún**; no implementado |
| 16 | Línea base personal + CUSUM bilateral | **INSPIRACIÓN REAL** | CUSUM es clásico (identificador pendiente, M0.12); la línea base personal es línea activa (PSU/ORACLE) |
| 17 | Preregistro con hash SHA-256 de los bytes del acta | **INSPIRACIÓN REAL** | SHA-256 es real y reproducible (`sha256sum`); la práctica viene del preregistro científico |
| 18 | La misma arquitectura sirve a 4,25 años luz (Proxima b a 0,1c) | **FICCIÓN CON BASE** | la distancia y el planeta son reales; **la nave y la velocidad son supuestos de ejercicio**, declarados en DOC-04 §7 |
| 19 | FB-002: «10/10 detecciones, preaviso mediano 21 días» | **SIN VERIFICAR** | el script y el acta no están en el repo (`afirmaciones-por-verificar.md` A-08) |
| 20 | «NASA lista el monitoreo médico como capacidad insuficiente (feb-2025)» | **SIN VERIFICAR** | no hallé el documento (A-05) |
| 21 | «Nadie unifica cuerpo y máquina» | **SIN VERIFICAR** (probablemente falsa tal cual) | ORACLE es un precedente parcial (`evaluacion-paper.md` §7) |
| 22 | El detector con h calibrado a 1 % de falsas alarmas **se transfiere a datos reales** | **EXTRAPOLACIÓN refutada en parte** | FB-009: en sueño 0/97 (pero por el piso del sensor proxy, que lo hace conservador); en pulso **4,9 % (≈5× el nominal)** por autocorrelación (ρ ≈ 0,18). `NOTA-FB-009-posthoc.md` |
| 22b | El blanqueado AR(1) corrige la descalibración del pulso | **EXTRAPOLACIÓN** (en simulación y en muestra; **no demostrada fuera de muestra**) | FB-010: pulso/prueba 2/77 con y sin blanquear (la prueba no discriminaba); en entrenamiento 7,5 % → 3,0 %; simulación AR(1) ρ=0,4: 7,7 % → <2,5 %. `NOTA-FB-010.md` |
| 23 | «Detección del 100 % a 2σ» en 14 días | **CIENCIA REAL (dato) pero engañosa en σ** | en unidades físicas 2σ ≈ **204 min** de sueño (≈ 3,4 h) o ≈ 10,6 lpm; el MDE al 90 % ≈ 163 min de sueño está dictado por el proxy del sensor |

**Cómo se usa ante el jurado:** las filas 1–10 se dicen con seguridad y fuente; 11–14 se dicen **con su etiqueta** («es una extrapolación»); 15–18 se presentan como diseño/inspiración; **19–21 no se dicen como hechos**.
