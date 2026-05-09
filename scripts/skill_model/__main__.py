"""CLI: python3 -m skill_model <command> [args...]"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .spec import CLAUDE_OVERLAY_KEYS, discover_skills, load, write_claude_overlay


def _parse_overrides(items: list[str]) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in items:
        if "=" not in item:
            raise ValueError(f"invalid override {item!r} (use key=value)")
        key, value = item.split("=", 1)
        key = key.strip()
        value = value.strip()
        if key not in CLAUDE_OVERLAY_KEYS:
            allowed = ", ".join(sorted(CLAUDE_OVERLAY_KEYS))
            raise ValueError(f"unknown Claude overlay key {key!r} (allowed: {allowed})")
        out[key] = value
    return out


def cmd_validate(args: argparse.Namespace) -> int:
    skill_dirs = [Path(p) for p in args.skill_dirs] if args.skill_dirs else discover_skills(args.repo_root)
    problems: list[str] = []
    for skill_dir in skill_dirs:
        spec = load(skill_dir)
        problems.extend(spec.validate())
    if problems:
        for p in problems:
            print(p)
        return 1
    print(f"OK: {len(skill_dirs)} skills validate cleanly.")
    return 0


def cmd_write_claude_overlay(args: argparse.Namespace) -> int:
    try:
        overrides = _parse_overrides(args.frontmatter)
    except ValueError as e:
        print(f"[ERROR] {e}")
        return 1
    path = write_claude_overlay(args.skill_dir, overrides)
    print(f"[OK] wrote {path}")
    return 0


def cmd_list_keys(args: argparse.Namespace) -> int:
    for k in sorted(CLAUDE_OVERLAY_KEYS):
        print(k)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="skill_model", description="SkillSpec tooling")
    parser.add_argument("--repo-root", default=".")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_v = sub.add_parser("validate", help="validate one or more skills (or all skills if none given)")
    p_v.add_argument("skill_dirs", nargs="*")
    p_v.set_defaults(func=cmd_validate)

    p_w = sub.add_parser("write-claude-overlay", help="write agents/claude.yaml for a skill")
    p_w.add_argument("skill_dir")
    p_w.add_argument("--frontmatter", action="append", default=[], help="key=value (repeatable)")
    p_w.set_defaults(func=cmd_write_claude_overlay)

    p_k = sub.add_parser("list-keys", help="print the canonical Claude overlay key list")
    p_k.set_defaults(func=cmd_list_keys)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
