#!/usr/bin/env python3
"""
Generate agents/claude.yaml for a skill directory.

Delegates to skill_model.write_claude_overlay; the canonical Claude-overlay key list
lives in scripts/skill_model/spec.py. Keep this entry point so existing call sites
(init-compatible-skill.py, docs in CLAUDE.md) continue to work.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from skill_model import write_claude_overlay
from skill_model.spec import CLAUDE_OVERLAY_KEYS


def parse_overrides(items: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"Invalid frontmatter override '{item}'. Use key=value.")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key not in CLAUDE_OVERLAY_KEYS:
            allowed = ", ".join(sorted(CLAUDE_OVERLAY_KEYS))
            raise ValueError(f"Unknown Claude frontmatter key '{key}'. Allowed: {allowed}")
        out[key] = value
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description="Create agents/claude.yaml for a skill directory.")
    parser.add_argument("skill_dir", help="Path to the skill directory")
    parser.add_argument(
        "--frontmatter",
        action="append",
        default=[],
        help="Claude-specific frontmatter override in key=value format (repeatable)",
    )
    args = parser.parse_args()

    skill_dir = Path(args.skill_dir).resolve()
    if not skill_dir.is_dir():
        print(f"[ERROR] Skill directory not found: {skill_dir}")
        return 1
    if not (skill_dir / "SKILL.md").exists():
        print(f"[ERROR] SKILL.md not found in {skill_dir}")
        return 1

    try:
        overrides = parse_overrides(args.frontmatter)
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        return 1

    out_path = write_claude_overlay(skill_dir, overrides)
    print(f"[OK] Created {out_path.relative_to(Path.cwd()) if out_path.is_relative_to(Path.cwd()) else out_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
