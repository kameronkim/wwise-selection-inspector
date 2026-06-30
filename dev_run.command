#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"

PYTHON_BIN="${PYTHON:-python3}"
if [ ! -d ".venv" ]; then
  "$PYTHON_BIN" -m venv .venv
fi

.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
exec .venv/bin/python main.py
