#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
evals_venv="${repo_root}/evals/.venv"

if [ ! -x "${evals_venv}/bin/python" ]; then
  echo "[evals] virtualenv missing; bootstrap with:" >&2
  echo "  python3.12 -m venv evals/.venv && evals/.venv/bin/pip install -e 'evals[dev]'" >&2
  exit 1
fi

PYTHONPATH="${repo_root}${PYTHONPATH:+:${PYTHONPATH}}" \
  "${evals_venv}/bin/python" -m evals "$@"
