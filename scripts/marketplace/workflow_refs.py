"""Cross-check a Workflow's workflowFile against its Plugin Pins.

Two rules (RFC 0001, "Workflow File Conventions"):

1. Every backticked name in the workflow file that is a Skill shipped by any Plugin in
   this repository must belong to a pinned Plugin. A dangling reference would make the
   workflow's own "missing Skill -> Stop" rule fire on every run.
2. Every pinned Plugin must be referenced at least once, by its own name or by one of
   its Skills. An unreferenced pin costs context on every turn and never routes.
3. In a Plugins table (a Markdown row whose first cell is a backticked Plugin name),
   every backticked name in the remaining cells must be a Skill that Plugin ships. This
   is the one place a name that exists nowhere (a typo, a removed Skill) can be caught.

Limits: outside a Plugins table, rule 1 only knows Skills that exist somewhere in this
repository, so a nonexistent name in running prose is invisible. Fenced code blocks are not
scanned. A workflow file can exempt a deliberate mention of an unpinned Skill with an
HTML comment: ``<!-- marketplace-validate: ignore-skill <name> -->``.
"""
from __future__ import annotations

import re
from pathlib import Path

from .model import MarketplaceModel, Plugin, Workflow

_BACKTICKED = re.compile(r"`([A-Za-z0-9][A-Za-z0-9_-]*)`")
_FENCE = re.compile(r"^[ \t]*(`{3,}|~{3,}).*?^[ \t]*\1[ \t]*$", re.S | re.M)
_FRONTMATTER = re.compile("\\A\ufeff?---[ \\t]*\\r?\\n(.*?)\\r?\\n---[ \\t]*(?:\\r?\\n|\\Z)", re.S)
_NAME_FIELD = re.compile(r"^name:[ \t]*(.+?)[ \t]*$", re.M)
_IGNORE = re.compile(r"<!--\s*marketplace-validate:\s*ignore-skill\s+([A-Za-z0-9][A-Za-z0-9_-]*)\s*-->")
_TABLE_ROW = re.compile(r"^\|\s*`([A-Za-z0-9][A-Za-z0-9_-]*)`\s*\|(.*)\|\s*$", re.M)


def _skill_roots(plugin: Plugin) -> list[Path]:
    """Both places a runtime may load skills from: the Codex `skills` path and `./skills`."""
    assert plugin.path is not None
    roots: list[Path] = []
    for rel in (plugin.skills_path, "./skills/"):
        root = (plugin.path / rel).resolve()
        if root.is_dir() and root not in roots:
            roots.append(root)
    return roots


def plugin_skill_names(plugin: Plugin) -> list[str]:
    """Skill names shipped by a Plugin, from each ``skills/<dir>/SKILL.md`` frontmatter.

    Falls back to the directory name when the frontmatter cannot be parsed, which is what
    the runtimes themselves do.
    """
    names: list[str] = []
    for root in _skill_roots(plugin):
        for entry in sorted(root.iterdir()):
            skill_md = entry / "SKILL.md"
            if not entry.is_dir() or not skill_md.is_file():
                continue
            text = skill_md.read_text(encoding="utf-8")
            fm = _FRONTMATTER.match(text)
            name_match = _NAME_FIELD.search(fm.group(1)) if fm else None
            name = name_match.group(1).strip("\"'") if name_match else entry.name
            if name not in names:
                names.append(name)
    return names


def skill_owners(model: MarketplaceModel) -> dict[str, set[str]]:
    """Map each Skill name to the set of Plugins that ship it (execution layers share names)."""
    owners: dict[str, set[str]] = {}
    for plugin in model.plugins:
        for skill in plugin_skill_names(plugin):
            owners.setdefault(skill, set()).add(plugin.name)
    return owners


def workflow_file_path(workflow: Workflow) -> Path | None:
    filename = workflow.raw.get("workflowFile")
    if not filename or workflow.path is None:
        return None
    return workflow.path / filename


def referenced_names(markdown: str) -> tuple[set[str], set[str]]:
    """Backticked names outside fenced code blocks, plus explicitly ignored skill names."""
    ignored = set(_IGNORE.findall(markdown))
    prose = _FENCE.sub("", markdown)
    return set(_BACKTICKED.findall(prose)), ignored


def plugin_table_rows(markdown: str) -> list[tuple[str, list[str]]]:
    """(first-cell name, backticked names in the other cells) for every table row."""
    prose = _FENCE.sub("", markdown)
    return [(head, _BACKTICKED.findall(rest)) for head, rest in _TABLE_ROW.findall(prose)]


def check_workflow_references(
    model: MarketplaceModel,
    workflow: Workflow,
    owners: dict[str, set[str]] | None = None,
) -> list[str]:
    """Return human-readable findings; an empty list means the workflow file is consistent."""
    md_path = workflow_file_path(workflow)
    if md_path is None:
        return []
    if not md_path.is_file():
        return [f"{workflow.name}: workflowFile {md_path.name!r} does not exist"]

    markdown = md_path.read_text(encoding="utf-8")
    tokens, ignored = referenced_names(markdown)
    if owners is None:
        owners = skill_owners(model)
    pinned = {pin.plugin_name for pin in workflow.pins}
    known = {p.name for p in model.plugins}
    findings: list[str] = []

    for head, names in plugin_table_rows(markdown):
        if head not in known:
            continue
        shipped = set(plugin_skill_names(model.plugin(head)))
        for name in names:
            if name not in shipped and name != head:
                findings.append(
                    f"{workflow.name}: {md_path.name} lists `{name}` under plugin {head!r}, "
                    f"which ships no such skill ({', '.join(sorted(shipped)) or 'none'})"
                )

    for token in sorted(tokens - ignored):
        token_owners = owners.get(token)
        if token_owners and not (token_owners & pinned):
            findings.append(
                f"{workflow.name}: {md_path.name} names skill `{token}` but its plugin "
                f"({', '.join(sorted(token_owners))}) is not pinned in workflow.json"
            )

    for plugin_name in sorted(pinned):
        if plugin_name not in known:
            continue  # the compiler already reports unknown pins
        skills = plugin_skill_names(model.plugin(plugin_name))
        if plugin_name in tokens or any(skill in tokens for skill in skills):
            continue
        findings.append(
            f"{workflow.name}: pins plugin {plugin_name!r} but {md_path.name} never names it "
            f"or any of its skills ({', '.join(skills) or 'none shipped'})"
        )
    return findings


def check_all_workflow_references(model: MarketplaceModel) -> list[str]:
    owners = skill_owners(model)
    findings: list[str] = []
    for workflow in model.workflows:
        findings.extend(check_workflow_references(model, workflow, owners))
    return findings
