# Demo route & dry-run checklist (M5.3) — 4 minutes, no notes

## Before the room (2 min)
```
uv run python backend/manage.py runserver 127.0.0.1:8000     # backend (Postgres via .env)
cd web && pnpm build && pnpm start                           # frontend on :3000 (production build: faster and steadier than `pnpm dev`)
uv run python backend/manage.py sembrar_demo                 # idempotent
uv run --with kokoro-onnx --with soundfile python scripts/voz_alma.py   # only if the data changed; env ALMA_VOICE (default af_heart) and ALMA_FX=0 (clean voice) — see .env.example
uv run pytest -q                                              # must be green (380+)
(cd web && pnpm e2e)                                          # 15 real-click checks (wake gate, audio, arrows, Body/Mood, leak, storm, foundry); writes nothing
```
Open `http://localhost:3000`, click once to wake ALMA (this also allows audio). Everything works offline (model, fonts, voice, last Sun snapshot).

## The route
1. **Medical Module** (30 s) — "The ship looks calm. Nine books." Click day 11 → orange air ring → click it: the receipt (expected 3.560, observed 4.011, rule 2σ = 0.400 kg).
2. **Machine Room** (30 s) — promised vs observed; the day-11 surprise is a *flag, not an alarm*.
3. **The Leak** (60 s) — the demo kill. Hash preregistered 05:52:17, run 05:52:43. "A manifest detector would have stayed silent."
4. **The Vault + The Foundry** (45 s) — 21 sealed acts, 2 refuted cards, 1 detector compiled. "Refuted ideas are our metric."
5. **The Storm** (45 s) — real Sun, real Kp; press G3 → "SIMULATED UNIVERSE". "Real and simulated never mix."
6. **The Budget / The Capsule** (30 s, if asked) — empty books are shown empty; capsules refuse to export without limits.

## Questions to expect (30-second answers)
- *Real or simulated?* Both, stamped on every screen; the habitat is simulated from public NASA figures.
- *Is the assistant an LLM?* No: a deterministic narrator; every sentence = template + a data value + its source.
- *Did you reproduce the 10/10 result?* No — 8/10 in our independent replication; we say so ("documented, not replicated").
- *What fails?* The variance channel (9% false alarms on real data), pulse whitening (inconclusive), solar storms × sleep/HRV (refuted).
