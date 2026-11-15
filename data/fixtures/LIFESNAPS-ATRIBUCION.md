# Atribución — extracto de LifeSnaps

`lifesnaps_diario_extracto.csv` contiene **187 filas reales, sin modificar**, de `daily_fitbit_sema_df_unprocessed.csv` (un solo participante pseudonimizado, `621e2f9167b776a240011ccb`, 2021-05-24 → 2022-01-20), extraídas del dataset completo (7 410 filas, 71 participantes).

- **Dataset:** *LifeSnaps, a 4-month multi-modal dataset capturing unobtrusive snapshots of our lives in the wild* — Yfantidou et al., *Scientific Data* 2022. DOI: https://doi.org/10.1038/s41597-022-01764-x
- **Datos:** Zenodo, registro https://zenodo.org/records/7229547 (`rais_anonymized.zip`; md5 oficial `726afe263ab4b900a721eac19b2ca13a`, verificado — ver `docs/politica-de-datos.md` S-07).
- **Licencia:** Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/
- **Cambios:** solo selección de filas de un participante; ningún valor fue alterado.
- **Aviso:** son datos de **personas en vida cotidiana, no de astronautas**. Su uso en ALMA es validar el método (línea base personal, CUSUM), no hacer afirmaciones sobre vuelo espacial.

## utah_volumen_diario_normalizado.csv
Derivado de *High Resolution Residential Water Use Data in Cache County, Utah, USA* (Bastidas Pacheco, Atallah, Horsburgh; HydroShare, CC BY 4.0, https://www.hydroshare.org/resource/0b72cddfc51c45b188e0e6cd8927227e/): volumen diario interior (suma de `OriginalVolume` de eventos no `irrigation`) dividido por la media de cada hogar; hogares con ≥ 20 días observados. Cambios: agregación diaria y normalización. Registro S-12 de `docs/politica-de-datos.md`.
