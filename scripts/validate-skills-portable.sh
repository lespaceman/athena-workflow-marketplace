#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"

validator=""
if command -v agentskills >/dev/null 2>&1; then
  validator="$(command -v agentskills)"
elif command -v skills-ref >/dev/null 2>&1; then
  validator="$(command -v skills-ref)"
elif [ -x "${repo_root}/.venv/bin/agentskills" ]; then
  validator="${repo_root}/.venv/bin/agentskills"
elif [ -x "${repo_root}/.venv/bin/skills-ref" ]; then
  validator="${repo_root}/.venv/bin/skills-ref"
else
  echo "Official skill validator not found." >&2
  echo "Install the agentskills/skills-ref CLI into the repo venv or put it on PATH." >&2
  exit 1
fi

if [ "$#" -gt 0 ]; then
  skill_dirs=("$@")
else
  while IFS= read -r skill_md; do
    skill_dirs+=("$(dirname "$skill_md")")
  done < <(find "${repo_root}/plugins" -name SKILL.md | sort)
fi

for skill_dir in "${skill_dirs[@]}"; do
  echo "== ${skill_dir} =="
  "${validator}" validate "${skill_dir}"
done
