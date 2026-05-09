from __future__ import annotations

from pathlib import Path
from typing import Any

from .io import read_json, write_json
from .model import MarketplaceModel, Plugin, Workflow
from .projections import (
    render_athena_marketplace,
    render_claude_marketplace,
    render_codex_marketplace,
    render_plugin_claude_manifest,
    render_plugin_codex_manifest,
    render_workflow_json,
)
from .semver import bump_part


def write_per_plugin_manifests(model: MarketplaceModel) -> list[Path]:
    """Project each Plugin back to its two Per-plugin Manifests. Returns list of changed paths."""
    changed: list[Path] = []
    for plugin in model.plugins:
        for path, projection in (
            (plugin.claude_manifest_path, render_plugin_claude_manifest(plugin)),
            (plugin.codex_manifest_path, render_plugin_codex_manifest(plugin)),
        ):
            if _changed_on_disk(path, projection):
                write_json(path, projection)
                changed.append(path)
    return changed


def write_workflow_jsons(model: MarketplaceModel) -> list[Path]:
    changed: list[Path] = []
    for workflow in model.workflows:
        projection = render_workflow_json(workflow)
        if _changed_on_disk(workflow.workflow_json_path, projection):
            write_json(workflow.workflow_json_path, projection)
            changed.append(workflow.workflow_json_path)
    return changed


def write_registries(model: MarketplaceModel) -> list[Path]:
    """Write all three Marketplace Registries. Returns list of changed paths."""
    targets = [
        (model.repo_root / ".claude-plugin" / "marketplace.json", render_claude_marketplace(model)),
        (model.repo_root / ".agents" / "plugins" / "marketplace.json", render_codex_marketplace(model)),
        (model.repo_root / ".athena-workflow" / "marketplace.json", render_athena_marketplace(model)),
    ]
    changed: list[Path] = []
    for path, projection in targets:
        if _changed_on_disk(path, projection):
            write_json(path, projection)
            changed.append(path)
    return changed


def write_package_json_version(plugin: Plugin) -> Path | None:
    """If the plugin has a package.json, sync its version field. Returns path if changed."""
    pkg = plugin.package_json_path
    if not pkg.exists():
        return None
    data = read_json(pkg)
    if data.get("version") == plugin.version:
        return None
    data["version"] = plugin.version
    write_json(pkg, data)
    return pkg


def bump_plugin(model: MarketplaceModel, plugin_name: str, part: str = "patch") -> dict[str, Any]:
    """Bump a Plugin's version, cascade to dependent Workflow Plugin Pins, and bump those Workflows."""
    plugin = model.plugin(plugin_name)
    old_version = plugin.version
    new_version = bump_part(plugin.version, part)
    plugin.version = new_version
    cascaded: list[str] = []
    for workflow in model.workflows:
        pin_changed = False
        for pin in workflow.pins:
            if pin.plugin_name == plugin_name and pin.version != new_version:
                pin.version = new_version
                pin_changed = True
        if pin_changed:
            workflow.version = bump_part(workflow.version, "patch")
            cascaded.append(workflow.name)
    return {
        "plugin": plugin_name,
        "old_version": old_version,
        "new_version": new_version,
        "cascaded_workflows": cascaded,
    }


def bump_workflow(model: MarketplaceModel, workflow_name: str, part: str = "patch") -> dict[str, Any]:
    workflow = model.workflow(workflow_name)
    old_version = workflow.version
    workflow.version = bump_part(workflow.version, part)
    return {
        "workflow": workflow_name,
        "old_version": old_version,
        "new_version": workflow.version,
    }


def write_all(model: MarketplaceModel) -> list[Path]:
    """Write everything the model owns: per-plugin manifests, workflow.json files, three registries, package.jsons."""
    changed: list[Path] = []
    changed.extend(write_per_plugin_manifests(model))
    for plugin in model.plugins:
        pkg = write_package_json_version(plugin)
        if pkg is not None:
            changed.append(pkg)
    changed.extend(write_workflow_jsons(model))
    changed.extend(write_registries(model))
    return changed


def diff_registries(model: MarketplaceModel) -> dict[str, bool]:
    """Returns {path_str: needs_rewrite}. Useful for validation mode."""
    targets = [
        (model.repo_root / ".claude-plugin" / "marketplace.json", render_claude_marketplace(model)),
        (model.repo_root / ".agents" / "plugins" / "marketplace.json", render_codex_marketplace(model)),
        (model.repo_root / ".athena-workflow" / "marketplace.json", render_athena_marketplace(model)),
    ]
    return {
        str(path.relative_to(model.repo_root)): _changed_on_disk(path, projection)
        for path, projection in targets
    }


def _changed_on_disk(path: Path, projection: Any) -> bool:
    if not path.exists():
        return True
    return read_json(path) != projection
