# ALMA — a ship that keeps its own books

Health-monitoring software for astronauts (NASA Space Apps 2026 · Challenge 4). One rule runs through everything: **no colour without a contestable rule behind it.** Every alarm prints its receipt (the exact rule, the seed that reproduces it, the hash of its preregistration); every "all clear" states what the detector could actually have seen.

> **Honest scope.** There is no astronaut data here. Real data come from everyday people (wearables), NOAA space weather and NASA's Sun; the habitat is a **labelled simulation** anchored to public NASA figures. Every screen carries a REAL or SIMULATED stamp. Our results include failures, all published: see [`docs/actas/`](docs/actas/).

## What it does
- **Ledger of nine budgets** (air, water, energy, dose, rhythm, load, immunity, conduct, time). A book *closes* if |residual| ≤ 2σ of its manifest's own uncertainty; books without a real anchor stay empty instead of being simulated.
- **Detectors with receipts:** personal baseline + bilateral CUSUM, conservation-of-mass reconciliation (a leak the manifest cannot see still shows up as a loop that does not close), witness triangulation, flow-normalised water integrator.
- **A foundry** that mints hypotheses; each declares *what would kill it* before testing. Refuted ideas are published like sustained ones.
- **An interface in English** (`web/`): eight rooms and ALMA, a deterministic narrator — every sentence is a template + a data value + its source (no free-text AI), with subtitles always visible.

## Run it (offline-capable)
One command once `.env` and `uv sync` are done: `scripts/demo.sh`. Step by step:
```bash
cp .env.example .env            # fill in your local PostgreSQL credentials (never committed)
uv sync                         # Python 3.12 environment
uv run python backend/manage.py migrate
uv run python backend/manage.py sembrar_demo          # 14 days of SIMULATED habitat (aire, agua)
uv run python backend/manage.py runserver 127.0.0.1:8000
cd web && pnpm install && pnpm build && pnpm start    # http://localhost:3000 — click once to wake ALMA
uv run pytest -q                                      # 385 tests
cd web && pnpm e2e                                    # 15 real-click checks in headless Chrome (needs both servers running; writes nothing)
```
Demo route and checklist: [`docs/submit/ruta-de-demostracion.md`](docs/submit/ruta-de-demostracion.md). ALMA's voice is pre-rendered (`scripts/voz_alma.py`, Kokoro-82M, local); see `.env.example` for `ALMA_VOICE`.

## Reproduce the science
Each experiment is an *act* ([`docs/actas/FB-xxx.md`](docs/actas/)) hashed with SHA-256 **before** its runner can execute; runners refuse to run on an altered act, on different data, or twice. Seeds are public (20261111–20261115). Numbers are in [`docs/actas/RESULTADOS.jsonl`](docs/actas/RESULTADOS.jsonl), readings in `docs/actas/NOTA-*.md`. A draft report is in [`docs/preprint/manuscript.md`](docs/preprint/manuscript.md) (negative results first).

## Where things are
| Path | What |
|---|---|
| `src/` | Pure domain (contracts DC-01…DC-14, ingestion, ledger, motor, foundry, narrator) — imports neither Django nor Next |
| `backend/` | Django + DRF read-only API over PostgreSQL |
| `web/` | Next.js interface (English) |
| `scripts/` | Experiment runners (`fbNNN_*.py`), voice pre-render, source verification |
| `docs/` | Contracts (DOC-01), data policy with every source (`politica-de-datos.md`), acts, literature review, submission drafts |

## Data, sources and credits
Every source, licence and simulated component is registered in [`docs/politica-de-datos.md`](docs/politica-de-datos.md) (S-01…S-19 real, X-01…X-14 simulated). Highlights: LifeSnaps (Zenodo 7229547); Sjögren/SLE/healthy Fitbit study (Zenodo 8018238, CC BY 4.0); NOAA SWPC and NOAA Space Weather Scales; NASA SDO images; Utah residential water use (HydroShare, CC BY); NASA NTRS reports; **NASA Z-2 spacesuit 3D model** (NASA 3D Resources, "free and without copyright"); voice model Kokoro-82M (Apache-2.0); fonts Instrument Serif, Schibsted Grotesk and IBM Plex Mono (SIL OFL).

## Known limits
The variance channel failed its real-data test (9.0% false alarms) and is disabled for alarms; our replication of an earlier "10 of 10" detection result reached 8 of 10 ("documented, not replicated"); several validations are inconclusive by sample size. See the preprint draft, §1.

*Licence of this repository: to be set by the team before publication.*
