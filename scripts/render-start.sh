#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
uv run --frozen --no-dev python backend/manage.py migrate --noinput
uv run --frozen --no-dev python backend/manage.py sembrar_demo
uv run --frozen --no-dev python backend/manage.py sembrar_cierres
# Extracto REAL ya versionado y atribuido; no requiere subir el dataset completo.
uv run --frozen --no-dev python backend/manage.py sembrar_verdes --csv data/fixtures/lifesnaps_diario_extracto.csv
exec uv run --frozen --no-dev gunicorn --chdir backend config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" --workers "${WEB_CONCURRENCY:-1}" \
  --threads 2 --timeout 120 --access-logfile - --error-logfile -
