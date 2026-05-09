#!/usr/bin/env bash
# Repo-specific skill compatibility checks.
#
# Delegates to the SkillSpec module (scripts/skill_model). The single canonical
# table of Claude-overlay frontmatter keys lives in scripts/skill_model/spec.py;
# this script no longer duplicates it.
set -euo pipefail
exec "$(cd "$(dirname "$0")" && pwd)/skill-model-cli" validate "$@"
