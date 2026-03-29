#!/usr/bin/env bash
set -euo pipefail

if [ "$#" -lt 1 ]; then
  echo "Usage: $0 <skill_directory> [<skill_directory> ...]" >&2
  exit 1
fi

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
validator="/Users/nadeem/.codex/skills/.system/skill-creator/scripts/quick_validate.py"
pythonpath="${repo_root}/.codex-tools/pyyaml"

for skill_dir in "$@"; do
  echo "== ${skill_dir} =="
  PYTHONPATH="${pythonpath}${PYTHONPATH:+:${PYTHONPATH}}" python3 "${validator}" "${skill_dir}"
done
