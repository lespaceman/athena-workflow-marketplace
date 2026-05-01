import re
from dataclasses import dataclass

import yaml

FRONTMATTER_RE = re.compile(r"^---\n(.*?)\n---", re.DOTALL)

PORTABLE_FORBIDDEN_KEYS: frozenset[str] = frozenset({
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
})

REQUIRED_KEYS: frozenset[str] = frozenset({"name", "description"})


@dataclass(frozen=True)
class ParsedFrontmatter:
    frontmatter: dict[str, object]
    body: str
    findings: list[str]

    @property
    def is_valid(self) -> bool:
        return not any(f.startswith("ERROR:") for f in self.findings)


def parse(skill_md_text: str) -> ParsedFrontmatter:
    findings: list[str] = []
    match = FRONTMATTER_RE.match(skill_md_text)
    if not match:
        return ParsedFrontmatter({}, skill_md_text, ["ERROR: missing or invalid frontmatter"])

    try:
        loaded = yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError as exc:
        return ParsedFrontmatter({}, skill_md_text, [f"ERROR: yaml parse failed: {exc}"])

    if not isinstance(loaded, dict):
        return ParsedFrontmatter({}, skill_md_text, ["ERROR: frontmatter is not a mapping"])

    body = skill_md_text[match.end():].lstrip("\n")

    missing = REQUIRED_KEYS - loaded.keys()
    for key in sorted(missing):
        findings.append(f"ERROR: required key missing: {key}")

    portable_violations = sorted(set(loaded) & PORTABLE_FORBIDDEN_KEYS)
    for key in portable_violations:
        findings.append(f"WARN: portable SKILL.md contains Claude-only key: {key}")

    allowed_tools = loaded.get("allowed-tools")
    if allowed_tools is not None and not isinstance(allowed_tools, str):
        findings.append("ERROR: allowed-tools must be a space-delimited string for portable mode")

    if isinstance(allowed_tools, str) and "*" in allowed_tools:
        findings.append("WARN: allowed-tools contains wildcard; should enumerate explicit tools")

    return ParsedFrontmatter(loaded, body, findings)
