# Extracto OS-892 — ficha de verdad (IN-3 / DC-03)

**Verificación (2026-11-15):** registro leído por Claude desde la **API oficial de OSDR** `https://osdr.nasa.gov/geode-py/ws/repo/experiments/OS-892` (la página web es una app JS: su HTML es idéntico para cualquier accesión y no sirve como prueba). Respuesta cruda archivada en `data/lecturas/osdr_OS-892_20261115T051034Z.json` (SHA-256 `d0aedb056b7761d8ae09ec6926f28de44088c96eccb8fc93acebd32fa6d62f79`, 7407 bytes). **Control negativo:** `OS-999999` → HTTP 403. Verificado: osID `OS-892`, experimentID `80NSSC21K0299`, estado Public, versión 1, release 17-nov-2022, `files: []`, `studies: []`, la cita de §2 literal, y los objetivos mencionan IL-6 / trans-signaling / osteólisis.
**Uso previsto:** carga como cuerpo público con identificador en IN-3 (Canal C) y como materia prima del lab (tarjetas DC-12, FM-3 sueño × hueso).

---

## 1. Identificador y metadatos (verificados)

| Campo | Valor |
|---|---|
| **Identificador** | `OS-892` (accesión de **experimento** en NASA OSDR/ALSDA; los *studies* de OSDR usan formato `OSD-NNN` — no confundir) |
| **URL oficial** | https://osdr.nasa.gov/bio/repo/data/experiments/OS-892 (web) · API: https://osdr.nasa.gov/geode-py/ws/repo/experiments/OS-892 |
| **Título** | *Role of Mesenchymal Stem Cells in Microgravity Induced Bone Loss* |
| **Organismo** | Homo sapiens (humano) |
| **Plataforma** | ISS (payload "To be assigned to a flight") |
| **Estado** | Experimento en curso — **0 archivos de datos publicados** a la fecha (versión 1, actualizada 17-nov-2022) |

## 2. El extracto textual (la cita que sostiene la cifra del bestiario)

De la descripción oficial del experimento (verbatim, inglés):

> (campo `objectives` del experimento — texto de antecedentes, **no un resultado**) "Exercise slows bone loss in microgravity but even when astronauts adopt a rigorous exercise regimen, **they continue to lose about 1 – 2% of their bone mass a month**."

Glosa: el ejercicio frena la pérdida ósea en microgravedad, pero incluso con un régimen riguroso los astronautas siguen perdiendo ~1–2 % de su masa ósea al mes. **Esta es la fuente del "1–2 %/mes (NASA OSDR OS-892)" citado en la fila Hueso del bestiario y en el modelo MABL-B.**

## 3. Limitación honesta (no inflar el color)

- El extracto es de **metadatos + descripción oficial**: OS-892 aún no publica archivos descargables ("results to be available at conclusion of the study").
- El escalón T3 ("ensayo de mena sobre OS-892 con datos reales") requiere datasets con archivos: usar la familia OSD con datos publicados y las anclas humanas ya verificadas (Swanson et al. 2017/2018 — anclas C-18/C-19 de DOC-02), citando OS-892 como fuente del fenómeno documentado, no como archivo.
- Una preprint de dic-2025 y un artículo 2026 (DOI 10.1038/s41526-026-00628-7) citarían "OSD-892" como *study number*: **no verificado** — el registro OS-892 tiene `studies: []` (sin estudio OSD asociado) y el artículo no es legible sin sesión. No citar hasta leer el texto completo.

## 4. Compañeros citados junto a OS-892 (bestiario §Fuentes)

- NASA SVS MABL-B, visualización 31382
- Stavnichuk et al. 2020, *npj Microgravity* 6:13
- Swanson et al. 2017/2018 (anclas C-18/C-19 de DOC-02)

## 5. Cómo entra al contrato DC-03

```python
fuentes=[{"id": "OS-892", "tipo": "accesión OSDR"}]   # ya usado en tests/test_contratos.py
```

El loader debe rechazar cualquier registro que cite OS-892 sin la cita textual de la §2 o sin este extracto como ficha de verdad en `data/`.
