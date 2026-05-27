"""SkillSpec — load, validate, and project a skill across SKILL.md, agents/claude.yaml, and agents/openai.yaml.

The single canonical table of Claude-overlay frontmatter keys lives here. SKILL.md frontmatter
must NOT contain these (they belong in agents/claude.yaml); agents/claude.yaml frontmatter MUST
contain only these.
"""
from __future__ import annotations

import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# Resolve the repo's bundled PyYAML location so this module imports cleanly without
# requiring users to install anything globally.
_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_PYYAML_PATH = _REPO_ROOT / ".codex-tools" / "pyyaml"
if str(_PYYAML_PATH) not in sys.path:
    sys.path.insert(0, str(_PYYAML_PATH))

import yaml  # noqa: E402


# === Single source of truth for the SKILL.md ↔ claude.yaml split. ===
CLAUDE_OVERLAY_KEYS = frozenset(
    {
        "argument-hint",
        "user-invocable",
        "context",
        "agent",
        "hooks",
        "paths",
        "model",
        "effort",
        "shell",
    }
)

# Keys banned outright across every skill in this repo. All skills must remain
# model-invocable, so disable-model-invocation may not appear in SKILL.md or
# agents/claude.yaml.
BANNED_FRONTMATTER_KEYS = frozenset({"disable-model-invocation"})


# Required interface fields in agents/openai.yaml.
OPENAI_REQUIRED_INTERFACE_FIELDS = ("display_name", "short_description", "default_prompt")


_FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)


@dataclass
class SkillSpec:
    path: Path
    portable_frontmatter: dict[str, Any] = field(default_factory=dict)
    claude_overlay: dict[str, Any] | None = None
    openai_overlay: dict[str, Any] | None = None

    @property
    def name(self) -> str:
        return self.portable_frontmatter.get("name", self.path.name)

    @property
    def skill_md_path(self) -> Path:
        return self.path / "SKILL.md"

    @property
    def claude_yaml_path(self) -> Path:
        return self.path / "agents" / "claude.yaml"

    @property
    def openai_yaml_path(self) -> Path:
        return self.path / "agents" / "openai.yaml"

    def render_claude_overlay(self, frontmatter: dict[str, Any]) -> str:
        """Render an agents/claude.yaml document body for a given frontmatter override dict.

        Validates that all keys are Claude-overlay keys before rendering. Empty dicts
        are allowed and produce a valid (but minimal) overlay file.
        """
        unknown = sorted(set(frontmatter) - CLAUDE_OVERLAY_KEYS)
        if unknown:
            allowed = ", ".join(sorted(CLAUDE_OVERLAY_KEYS))
            raise ValueError(
                f"unknown Claude overlay keys: {', '.join(unknown)} (allowed: {allowed})"
            )
        lines = ["frontmatter:"]
        for key, value in frontmatter.items():
            lines.append(f"  {key}: {_scalar_yaml(value)}")
        return "\n".join(lines) + "\n"

    def validate(self) -> list[str]:
        """Return a list of validation problem messages. Empty list = valid."""
        problems: list[str] = []
        if not self.skill_md_path.exists():
            problems.append(f"{self.skill_md_path}: SKILL.md missing")
            return problems
        if not self.portable_frontmatter:
            problems.append(f"{self.skill_md_path}: missing or invalid frontmatter")
        else:
            banned = sorted(set(self.portable_frontmatter) & BANNED_FRONTMATTER_KEYS)
            if banned:
                problems.append(
                    f"{self.skill_md_path}: banned frontmatter keys: {', '.join(banned)} "
                    f"(all skills must remain model-invocable)"
                )
            bad = sorted(set(self.portable_frontmatter) & CLAUDE_OVERLAY_KEYS)
            if bad:
                problems.append(
                    f"{self.skill_md_path}: portable SKILL.md contains Claude-only keys: {', '.join(bad)}"
                )
            allowed_tools = self.portable_frontmatter.get("allowed-tools")
            if allowed_tools is not None and not isinstance(allowed_tools, str):
                problems.append(
                    f"{self.skill_md_path}: allowed-tools must be a space-delimited string for portable mode"
                )
        if self.claude_yaml_path.exists():
            if self.claude_overlay is None:
                problems.append(f"{self.claude_yaml_path}: failed to parse YAML")
            else:
                fm = self.claude_overlay.get("frontmatter")
                if not isinstance(fm, dict):
                    problems.append(f"{self.claude_yaml_path}: missing frontmatter mapping")
                else:
                    banned = sorted(set(fm) & BANNED_FRONTMATTER_KEYS)
                    if banned:
                        problems.append(
                            f"{self.claude_yaml_path}: banned frontmatter keys: {', '.join(banned)} "
                            f"(all skills must remain model-invocable)"
                        )
                    extra = sorted(set(fm) - CLAUDE_OVERLAY_KEYS - BANNED_FRONTMATTER_KEYS)
                    if extra:
                        problems.append(
                            f"{self.claude_yaml_path}: unsupported Claude overlay keys: {', '.join(extra)}"
                        )
        if self.openai_yaml_path.exists():
            if self.openai_overlay is None:
                problems.append(f"{self.openai_yaml_path}: failed to parse YAML")
            else:
                interface = self.openai_overlay.get("interface")
                if not isinstance(interface, dict):
                    problems.append(f"{self.openai_yaml_path}: missing interface mapping")
                else:
                    missing = [f for f in OPENAI_REQUIRED_INTERFACE_FIELDS if f not in interface]
                    if missing:
                        problems.append(
                            f"{self.openai_yaml_path}: interface missing required fields: {', '.join(missing)}"
                        )
        return problems


def load(skill_path: Path | str) -> SkillSpec:
    path = Path(skill_path).resolve()
    spec = SkillSpec(path=path)
    if spec.skill_md_path.exists():
        match = _FRONTMATTER_RE.match(spec.skill_md_path.read_text())
        if match:
            try:
                parsed = yaml.safe_load(match.group(1)) or {}
                if isinstance(parsed, dict):
                    spec.portable_frontmatter = parsed
            except yaml.YAMLError:
                pass
    if spec.claude_yaml_path.exists():
        try:
            spec.claude_overlay = yaml.safe_load(spec.claude_yaml_path.read_text()) or {}
        except yaml.YAMLError:
            spec.claude_overlay = None
    if spec.openai_yaml_path.exists():
        try:
            spec.openai_overlay = yaml.safe_load(spec.openai_yaml_path.read_text()) or {}
        except yaml.YAMLError:
            spec.openai_overlay = None
    return spec


def discover_skills(repo_root: Path | str = ".") -> list[Path]:
    """Find every SKILL.md under plugins/*/skills/* and return the containing directories."""
    repo = Path(repo_root).resolve()
    return sorted(p.parent for p in (repo / "plugins").glob("*/skills/*/SKILL.md"))


def write_claude_overlay(skill_path: Path | str, frontmatter: dict[str, Any]) -> Path:
    spec = load(skill_path)
    body = spec.render_claude_overlay(frontmatter)
    spec.claude_yaml_path.parent.mkdir(parents=True, exist_ok=True)
    spec.claude_yaml_path.write_text(body)
    return spec.claude_yaml_path


def _scalar_yaml(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return str(value)
    s = str(value)
    lower = s.lower()
    if lower == "true":
        return "true"
    if lower == "false":
        return "false"
    escaped = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")
    return f'"{escaped}"'
