#!/usr/bin/env python3
"""
Initialize a repo-compatible skill scaffold.

Creates:
- spec-clean SKILL.md
- agents/openai.yaml
- agents/claude.yaml

Wraps the upstream skill-creator init_skill.py for the base scaffold, then adds
the Claude overlay used by this repo.
"""

import argparse
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
UPSTREAM_INIT = Path("/Users/nadeem/.codex/skills/.system/skill-creator/scripts/init_skill.py")
CLAUDE_GEN = REPO_ROOT / "scripts" / "generate-claude-yaml.py"


def run(cmd):
    result = subprocess.run(cmd)
    if result.returncode != 0:
        sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="Create a new skill scaffold compatible with Claude and Codex.")
    parser.add_argument("skill_name", help="Skill name (hyphen-case)")
    parser.add_argument("--path", required=True, help="Parent directory where the skill folder will be created")
    parser.add_argument("--resources", default="", help="Comma-separated resources: scripts,references,assets")
    parser.add_argument("--examples", action="store_true", help="Include example resource files")
    parser.add_argument(
        "--interface",
        action="append",
        default=[],
        help="OpenAI UI interface override in key=value format (repeatable)",
    )
    parser.add_argument("--argument-hint", help="Claude argument hint for slash-menu autocomplete")
    parser.add_argument(
        "--user-invocable",
        choices=("true", "false"),
        default="true",
        help="Whether the skill should appear in the Claude slash menu",
    )
    parser.add_argument(
        "--claude",
        action="append",
        default=[],
        help="Additional Claude frontmatter override in key=value format (repeatable)",
    )
    args = parser.parse_args()

    if not UPSTREAM_INIT.exists():
        print(f"[ERROR] Upstream init script not found: {UPSTREAM_INIT}")
        sys.exit(1)

    init_cmd = [sys.executable, str(UPSTREAM_INIT), args.skill_name, "--path", args.path]
    if args.resources:
        init_cmd.extend(["--resources", args.resources])
    if args.examples:
        init_cmd.append("--examples")
    for item in args.interface:
        init_cmd.extend(["--interface", item])

    run(init_cmd)

    skill_dir = Path(args.path).resolve() / args.skill_name
    claude_overrides = [f"user-invocable={args.user_invocable}"]
    if args.argument_hint:
        claude_overrides.append(f"argument-hint={args.argument_hint}")
    claude_overrides.extend(args.claude)

    claude_cmd = [sys.executable, str(CLAUDE_GEN), str(skill_dir)]
    for item in claude_overrides:
        claude_cmd.extend(["--frontmatter", item])
    run(claude_cmd)

    print("\n[OK] Repo-compatible skill scaffold created.")
    print(f"   Skill: {skill_dir}")
    print("   Portable core: SKILL.md")
    print("   Claude overlay: agents/claude.yaml")
    print("   OpenAI UI metadata: agents/openai.yaml")


if __name__ == "__main__":
    main()
