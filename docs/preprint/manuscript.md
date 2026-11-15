# Preregistered falsification of a personal-baseline health monitor for crewed habitats: a negative-results-first, reproducible report

> **STATUS: DRAFT — not submitted.** Every figure below is copied from `docs/actas/RESULTADOS.jsonl` and traces to a preregistered act (table in §8). Gates before any submission: human review of the claims, and a search of **IEEE Xplore and Google Scholar** (not done; PubMed and NTRS were searched directly on 2026-11-15 — see `docs/revision-literatura.md`). No claim of novelty beyond a working method is made.

## Abstract
We describe ALMA, an open-source health-monitoring system for astronauts organised around receipts: every alarm prints its rule, seed and preregistration hash; every "all clear" declares the minimum effect it could have detected. We falsified each component with preregistered, hash-sealed experiments, each executed once on real wearable data (everyday people, **not astronauts**) or on a labelled simulation. Of 21 sealed acts, 16 have been executed. Results are mixed and are all reported: a conservation-of-mass detector sees a 0.30 kg leak that a manifest-based detector scores at 0.53σ; flow-normalising a slow water integrator lowers false alarms from 91% to 4.8% on real household flow; but a variance channel built to catch a documented blind spot produced 9.0% false alarms on real data, and our independent replication of an earlier "10 of 10" detection result reached 8 of 10. We contribute a method of work, not a new statistic.

## 1. Limitations (first, on purpose)
1. **No astronaut data.** Real data come from everyday people wearing consumer devices (LifeSnaps; a Sjögren/SLE/healthy Fitbit cohort; household water use). Habitat data are simulated, anchored to public NASA planning values, and labelled SIMULATED everywhere.
2. **Simulation assumptions are ours** (independent Gaussian noise, linear drift, a human witness with extra noise but no systematic bias). Where we measured real data the assumptions were often optimistic (water-demand correlation across households ≈ 0.13; pulse autocorrelation ≈ 0.18).
3. **Some results are inconclusive by sample size** (e.g. FB-020-v2 validation had 5 windows).
4. **Non-blindness.** Where an act extended earlier work on the same data, the act says so; the validity of such acts rests on parameters being frozen before touching held-out data.
5. **No algorithmic novelty.** CUSUM (Page 1954), individual CUSUM on physiological series (Cornélissen et al. 1997), data reconciliation (Tamhane & Mah 1985), spacecraft mass balance as a diagnostic (Kayatin 2021, NTRS 20210016640) and personal-baseline wearable monitoring (e.g. Cacheda et al. 2026) are established. Our contribution is a *method of work* (§3). The literature search covered PubMed and NTRS but not IEEE Xplore or Google Scholar, and was not a PRISMA-style systematic review.

## 2. System (summary)
A ledger of nine budgets (air, water, energy, dose, rhythm, load, immunity, conduct, time); a book *closes* if |residual| ≤ 2σ of its manifest's uncertainty. Detectors: personal baseline with bilateral CUSUM, conservation-of-mass closure (the "Contrapeso"), a witness-triangulation attributor (world / sensor / human), a slow integrator for water. A "verde" (all clear) is a contract object that carries its power and minimum detectable effect given the days actually observed. A hypothesis "foundry" mints cards that declare what would kill them before testing; survivors compile into detectors. Contracts DC-01…DC-14 are versioned (DOC-01 v0.2.8).

## 3. Methods: how every claim was made
Each act (`docs/actas/FB-xxx.md`) states the question, success rule and kill rule, and is hashed (SHA-256 of its exact bytes) **before** its runner can execute; runners refuse to run on an altered act, on different data, or twice. Public seeds: 20261111–20261115. Every experiment includes a control that can fail. Predictions by the authors are recorded in the act and reported when wrong.

## 4. Results
| Act | Question | Outcome (exact numbers from the act) |
|---|---|---|
| FB-005-D1 | Does a conservation law see a leak a manifest detector misses? (simulated) | Leak 0.30 kg: manifest score 0.53σ, no alarm; law residual +0.260 kg with σ 0.0548 kg → "does not close". Control day: both quiet. Prediction confirmed. |
| FB-004R | Does flow-normalising a slow water integrator help? (simulated tank, real Utah flow) | False alarms 91.0% (raw) vs 4.8% (normalised); detection at δ=0.10: 67.8% vs 99.8%; shuffled-flow control 78.8% false alarms. |
| FB-003R | Can three witnesses attribute an anomaly? (simulated) | Accuracy world 1.00, sensor 0.88, human 0.91, nothing 0.83 (H2 refuted: 0.83 < 0.85). Leak vs unmodelled storage: 0.87 / 1.00 at 30 d. |
| FB-012 | Real household water demand variability | Median daily CV 0.53 (31 households) — sustained; ρ₁ 0.115 and between-household correlation 0.126 — inconclusive. |
| FB-013 | Does the pulse-detector problem replicate in an independent cohort? | H1 refuted (2/66); H2 inconclusive; H3 power 89.4% sustained. |
| FB-014 | Solar storms (Kp) × sleep / HRV | Refuted: mean ρ sleep +0.016 (p 0.47), rmssd +0.037 (p 0.18); small effects not excluded. |
| FB-016 | Within-person sleep→tiredness; tension→HRV | A sustained (+7.9 points, 27 people, p 0.001, positive control); B refuted (+0.030 SD, 13 people, p 0.62). |
| FB-015-v2 | Independent replication of a "10 of 10" detection result (simulated) | Table structure replicated 6/7 cells; detection **8 of 10 — not replicated** (H4 refuted). |
| FB-018 | Is there an input that evades the CUSUM? (simulated) | Zigzag (zero mean, more variance) detected 1.8% at H=2σ vs 95.2% for a step of equal "damage"; variance-CUSUM reached 67.0% (H2 refuted). |
| FB-019 | Is the blind spot detector- or information-limited? (simulated) | With a 14-day baseline even an F test detects about 40% at H=1.5σ (oracle about 91%); with a 28-day baseline F detects 95.0% at H=2σ. |
| FB-020 | Variance channel (28-d baseline) on real data | **False alarms 9.0% (9/100, Wilson 95% 4.8–16.2%) — refuted**; power at 2σ 99% and mean-CUSUM blind (3%), sustained. |
| FB-020-v2 | Robust variant (MAD ratio, empirical critical) validated out of sample | Selected in training (FPR 1.95%, power 94%); validation had **5 windows** → inconclusive. |

## 5. Discussion
The consistent pattern is that calibrations made under Gaussian-independence assumptions do not transfer to real wearable series (FB-009, FB-013, FB-020), and that normalising by a measured covariate (FB-004R) matters more than a sharper detector. We therefore ship "all clear" only with its declared power, and we keep the variance channel disabled for real-data alarms until it passes an independent validation (needs ≥ 300 independent windows; open, M2.22).

## 6. Reproducibility
Public code and seeds; `uv run pytest` (372+ tests) re-derives the contracts; each runner script reproduces its act exactly (`scripts/fbNNN_*.py`); the full interface runs offline (`docs/submit/ruta-de-demostracion.md`). All data sources, licences and simulated components are listed in `docs/politica-de-datos.md` (S-01…S-19, X-01…X-14).

## 7. Related work
See `docs/revision-literatura.md` (all identifiers verified against Crossref/NTRS): Tamhane & Mah 1985; Page 1954; Cornélissen et al. 1997; Cvach 2012; Kayatin 2021 (NTRS 20210016640); Scott et al. 2023; Zheng et al. 2023; Gupta et al. 2025; Cacheda et al. 2026; McCraty et al. 2017; Alabdulgader et al. 2018; Zilli Vieira et al. 2022; Zenchenko et al. 2024; Jones 2019. Our solar-storm null (FB-014) does not contradict reports of geomagnetic–HRV associations in other cohorts and designs; small effects are not excluded.

## 8. Traceability (figure → act → file)
Every row of §4 → `docs/actas/<act>.md` (preregistered text, hash in `docs/actas/INDEX.jsonl`) → numbers in `docs/actas/RESULTADOS.jsonl` → interpretation in `docs/actas/NOTA-<act>.md`. Repository state at drafting: see `git log` (HEAD at the time of writing is recorded in TASKS.md).
