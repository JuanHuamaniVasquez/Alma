# Research report (IEEE conference format, English)

`main.tex` is the **complete first draft** (≈ 5 pages in two columns): abstract, introduction, related work, system, methods, results (strongest first), negative results and own errors, limitations, reproducibility and ethics, future work, 16 verified references. Class `IEEEtran`.

## Compile
- **Overleaf (easiest):** New project → Upload → this folder → compile with pdfLaTeX. No other file is needed (the bibliography is inside `main.tex`).
- **Local:** needs a full TeX Live (`texlive-publishers` for `IEEEtran`): `pdflatex main && pdflatex main`. (The machine where this was written has a minimal TeX Live without IEEEtran/fonts, so the PDF was **not** compiled there: the syntax was checked by script — every `\cite` has an entry, every `\ref` a label, no unescaped `%`. Compile it first and fix any warning.)

## How every number was checked
Each figure in the text comes from `docs/actas/RESULTADOS.jsonl` and its note `docs/actas/NOTA-FB-xxx.md`; the claims table is `docs/informe/INVENTARIO-IEEE.md` (C-01…C-22). Before submitting, a person must re-open the note of each act cited (rule of gold: never from memory).

## To do before submitting (human)
1. Compile and read the PDF; fix overfull lines.
2. Add 2–3 figures (screenshots in `docs/screenshots/`: the Leak, the Frontier, the Vault) with `\includegraphics` and captions.
3. Replace the placeholder author block by the real names/affiliations.
4. Search IEEE Xplore and Google Scholar (not done) and update *Related Work* with the result.
5. Verify the three references whose bibliographic details are minimal (Corn\'elissen 1997, Gupta 2025, Kayatin 2021) against Crossref/NTRS and complete authors/titles.
6. Re-run `uv run python scripts/generar_inventario.py` and make sure "30 acts, 25 executed" and "475 tests" are still true.
7. The Spanish version (if the jury asks) can be produced by translating the file; keep numbers identical.
