#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."
uv sync --frozen --no-dev
uv run --frozen --no-dev python scripts/preparar_ecg.py
