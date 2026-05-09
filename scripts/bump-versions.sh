#!/usr/bin/env bash
# Bump plugin and workflow versions, cascade Plugin Pins, and rewrite all three Marketplace Registries.
#
# Usage:
#   ./scripts/bump-versions.sh                    # autodetect changed plugins/workflows from git diff
#   ./scripts/bump-versions.sh <plugin-or-workflow> [<more>...]
#   BUMP=minor ./scripts/bump-versions.sh         # bump minor instead of patch
#
# All logic lives in scripts/marketplace/. This wrapper preserves the documented entry point.
set -euo pipefail
repo_root="$(cd "$(dirname "$0")/.." && pwd)"
part="${BUMP:-patch}"
PYTHONPATH="${repo_root}/scripts" exec python3 -m marketplace --repo-root "${repo_root}" bump --part "${part}" "$@"
