#!/usr/bin/env python3
"""
Generate agents/claude.yaml for a skill directory.

Usage:
    generate-claude-yaml.py <skill_dir> [--frontmatter key=value]
"""

import argparse
import re
import sys
from pathlib import Path

ALLOWED_KEYS = {
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


def quote_yaml(value: str) -> str:
    escaped = value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'


def parse_overrides(raw_items):
    frontmatter = {}
    for item in raw_items:
        if "=" not in item:
            raise ValueError(f"Invalid frontmatter override '{item}'. Use key=value.")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key not in ALLOWED_KEYS:
            allowed = ", ".join(sorted(ALLOWED_KEYS))
            raise ValueError(f"Unknown Claude frontmatter key '{key}'. Allowed: {allowed}")
        frontmatter[key] = value
    return frontmatter


def scalar_yaml(value: str) -> str:
    lower = value.lower()
    if lower == "true":
        return "true"
    if lower == "false":
        return "false"
    return quote_yaml(value)


def write_claude_yaml(skill_dir: Path, overrides):
    agents_dir = skill_dir / "agents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    lines = ["frontmatter:"]
    for key, value in overrides.items():
        lines.append(f"  {key}: {scalar_yaml(value)}")

    output = agents_dir / "claude.yaml"
    output.write_text("\n".join(lines) + "\n")
    print("[OK] Created agents/claude.yaml")
    return output


def main():
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
    if not skill_dir.exists() or not skill_dir.is_dir():
        print(f"[ERROR] Skill directory not found: {skill_dir}")
        sys.exit(1)
    if not (skill_dir / "SKILL.md").exists():
        print(f"[ERROR] SKILL.md not found in {skill_dir}")
        sys.exit(1)

    try:
        overrides = parse_overrides(args.frontmatter)
    except ValueError as exc:
        print(f"[ERROR] {exc}")
        sys.exit(1)

    write_claude_yaml(skill_dir, overrides)


if __name__ == "__main__":
    main()
