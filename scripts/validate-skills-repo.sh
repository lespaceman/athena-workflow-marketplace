#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "$0")/.." && pwd)"
pythonpath="${repo_root}/.codex-tools/pyyaml"

PYTHONPATH="${pythonpath}${PYTHONPATH:+:${PYTHONPATH}}" python3 - "$repo_root" "$@" <<'PY'
import re
import sys
from pathlib import Path

import yaml

repo_root = Path(sys.argv[1])
if len(sys.argv) > 2:
    skill_dirs = [Path(p) for p in sys.argv[2:]]
else:
    skill_dirs = sorted((repo_root / "plugins").glob("*/skills/*"))
problems = []

portable_forbidden = {
    "argument-hint",
    "user-invocable",
    "disable-model-invocation",
    "context",
    "agent",
    "hooks",
    "paths",
    "model",
    "effort",
    "shell",
}

allowed_claude_overlay_keys = portable_forbidden

for skill_dir in skill_dirs:
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        continue

    content = skill_md.read_text()
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        problems.append(f"{skill_md}: missing or invalid frontmatter")
        continue

    frontmatter = yaml.safe_load(match.group(1)) or {}
    bad = sorted(set(frontmatter) & portable_forbidden)
    if bad:
        problems.append(f"{skill_md}: portable SKILL.md contains Claude-only keys: {', '.join(bad)}")

    allowed_tools = frontmatter.get("allowed-tools")
    if allowed_tools is not None and not isinstance(allowed_tools, str):
        problems.append(f"{skill_md}: allowed-tools must be a space-delimited string for portable mode")

    claude_overlay = skill_dir / "agents" / "claude.yaml"
    if claude_overlay.exists():
        data = yaml.safe_load(claude_overlay.read_text()) or {}
        frontmatter_overlay = data.get("frontmatter")
        if not isinstance(frontmatter_overlay, dict):
            problems.append(f"{claude_overlay}: missing frontmatter mapping")
        else:
            extra = sorted(set(frontmatter_overlay) - allowed_claude_overlay_keys)
            if extra:
                problems.append(f"{claude_overlay}: unsupported Claude overlay keys: {', '.join(extra)}")

if problems:
    for problem in problems:
        print(problem)
    sys.exit(1)

print("Repo skill compatibility checks passed.")
PY
