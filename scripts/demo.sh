#!/usr/bin/env bash
# Arranca la demo completa: migra, siembra lo que se puede sembrar con honestidad, levanta la API (:8000) y la vitrina (:3000).
# Uso:  scripts/demo.sh          (Ctrl+C detiene ambos)
set -euo pipefail
cd "$(dirname "$0")/.."

uv run python backend/manage.py migrate --noinput
uv run python backend/manage.py sembrar_demo                       # hábitat SIMULADO (X-13): aire y agua, con banner
if [ -f data/externos/lifesnaps/rais_anonymized/csv_rais_anonymized/daily_fitbit_sema_df_unprocessed.csv ]; then
  uv run python backend/manage.py sembrar_verdes                   # estado REAL de fc y sueño (LifeSnaps, no astronautas)
else
  echo "LifeSnaps no está en data/externos/: fc y sueño quedan vacíos (sin dato real no se simula)."
fi
uv run python backend/manage.py ingestar_swpc || echo "sin red: La Tormenta usará las últimas lecturas guardadas."

uv run python backend/manage.py runserver 127.0.0.1:8000 &
API=$!
trap 'kill $API 2>/dev/null || true' EXIT
cd web
pnpm install --frozen-lockfile
pnpm build
echo "→ http://localhost:3000  (haz un clic para despertar a ALMA; el clic también permite el audio)"
pnpm start
