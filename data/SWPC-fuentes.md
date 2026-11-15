# SWPC en vivo — fuentes sin API key (IN-3 / DC-03)

**Verificado:** 2026-11-15, lectura directa sin llave ni registro.
**Regla DOC-01:** "NOAA SWPC (sin llave)" — contrato DC-03: `fuente: swpc`, `parametros` con unidades en el nombre del campo, `hash_lectura_cruda` (SHA-256 del JSON crudo).

---

## Endpoints (todos públicos, JSON, sin API key)

| # | Canal | URL | Campos clave |
|---|---|---|---|
| 1 | **Índice Kp** (base de FB-002) | `https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json` | `time_tag`, `Kp`, `a_running`, `station_count` |
| 2 | Viento solar — plasma (ACE/DSCOVR) | `https://services.swpc.noaa.gov/products/solar-wind/plasma-2-hour.json` | densidad (n/cm³), velocidad (km/s), temperatura |
| 3 | Viento solar — campo magnético | `https://services.swpc.noaa.gov/products/solar-wind/mag-2-hour.json` | `bt` (nT), `bz_gsm` (nT), lat/lon |
| 4 | Rayos X GOES (clase de llamarada) | `https://services.swpc.noaa.gov/json/goes/primary/xrays-1-day.json` | `flux` (W/m²) por banda 0.05–0.4 y 0.1–0.8 nm |
| 5 | Protones GOES | `https://services.swpc.noaa.gov/json/goes/primary/integral-protons-1-day.json` | flujo integral de protones (pfu) |
| 6 | Alertas oficiales | `https://services.swpc.noaa.gov/json/alerts.json` | mensajes de alerta/warning |

Nota de formato: los endpoints bajo `/products/` entregan un array de arrays (fila 0 = encabezados); los bajo `/json/` entregan array de objetos. El loader debe manejar ambos.

## Lectura de referencia (verificación 2026-11-15)

```
feed Kp → 2026-11-15T00:00:00  Kp=2.00  a_running=7  station_count=8
feed Kp → 2026-11-14T21:00:00  Kp=1.33  a_running=5  station_count=8
```

(Consistente con DOC-01: "verificado Kp=3,33 el 9-nov".)

## Reglas de ingestión (no negociables)

1. **Banner REAL obligatorio**: toda lectura SWPC entra con banner `REAL` visible; el loader **rechaza** registros sin banner, sin `fuente` con id o sin semilla (cuando aplique replay).
2. `parametros` con unidades en el nombre: `kp`, `vel_viento_km_s`, `densidad_n_cm3`, `bz_gsm_nt`, `flujo_x_w_m2`, `flujo_protones_pfu`.
3. `hash_lectura_cruda` = SHA-256 del JSON tal como llegó, antes de cualquier transformación.
4. Si un feed falla o viene vacío: registrar el intento con timestamp y código de error en el libro — nunca rellenar con simulado sin banner `SIMULADO`.

## Mapeo a módulos

- IN-3 (Canal C) consume los feeds 1, 4 y 6 en P0; 2, 3 y 5 para tormenta (LA TORMENTA).
- FB-002 usa la serie de Kp (feed 1) como entrada de replay con semilla pública.
