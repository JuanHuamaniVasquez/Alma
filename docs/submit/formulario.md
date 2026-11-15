# NASA Space Apps 2026 · Challenge 4 — submission form (draft, English)

**Project name:** ALMA — a ship that keeps its own books

## Description (150–200 words)
ALMA is health-monitoring software for astronauts built around one rule: no colour without a contestable rule behind it. Every alarm prints its receipt — the exact rule, the seed that reproduces it, and the hash of the preregistration it came from. Every "all clear" states what the detector could actually have seen, given the days really observed. Instead of trusting a manifest, ALMA reconciles each habitat book (air, water…) against conservation of mass, so a leak the manifest cannot see still shows up as a loop that does not close. The astronaut is the patient; the habitat is an input to the body, never the patient on screen. Behind the interface sits a foundry that tests hypotheses: each one is preregistered with a hash before it runs, and refuted ideas are published exactly like sustained ones. Real data (wearables from everyday people, NOAA space weather, NASA's Sun) and a labelled simulated universe are never mixed: every screen carries a REAL or SIMULATED stamp. An assistant, ALMA, speaks only sentences built from those data, each with its source.

## How it works
1. **Ledger** — nine budgets (air, water, energy, dose, rhythm, load, immunity, conduct, time); a book closes if |residual| ≤ 2σ of its manifest's own uncertainty.
2. **Detectors with receipts** — personal baselines, bilateral CUSUM, conservation-of-mass reconciliation; each alarm withdraws itself if its rule stops holding.
3. **Foundry** — hypothesis cards declare what would kill them *before* testing; survivors compile into new detectors (one so far).
4. **Interface** — eight rooms in English with a deterministic narrator (no free-text AI), subtitles always visible, and a NASA Z-2 suit model.

## Data (all linked and registered in `docs/politica-de-datos.md`)
- LifeSnaps wearable dataset — Zenodo 7229547 (everyday people, not astronauts).
- Sjögren/SLE/healthy Fitbit study — Zenodo 8018238, doi:10.5281/zenodo.8018238 (CC BY 4.0).
- NOAA SWPC planetary K index and NOAA Space Weather Scales; NASA SDO solar images.
- Utah residential water use — HydroShare (CC BY).
- NASA NTRS: Ewert & Stromgren 2019 (mass balance), Jones 2019 (ISS reliability manifests).
- NASA 3D Resources — Z-2 spacesuit model (no copyright).

## Honest limits
Not astronaut data. The habitat is a labelled simulation anchored to public NASA figures. Our replication of an earlier 10/10 detection result reached 8/10 and is reported as "documented, not replicated". The variance channel failed its real-data test (9% false alarms) and is not enabled for alarms.

## Links (to be filled by the team)
- Code repository: `<TEAM: add public repo URL>`
- Project document (PDF v0.4): `<TEAM: add link>`
- Demo video (30–60 s): `<TEAM: add link after recording — see video-guion.md>`
