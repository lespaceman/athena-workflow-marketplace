from __future__ import annotations

from pathlib import Path

from .io import read_json
from .model import MarketplaceModel, Plugin, PluginPin, Workflow


SHARED_FIELDS = ("name", "version", "description")


class ConsistencyError(ValueError):
    pass


def load(repo_root: Path | str = ".") -> MarketplaceModel:
    repo = Path(repo_root).resolve()
    plugins = _load_plugins(repo)
    workflows = _load_workflows(repo)
    plugins = _apply_existing_order(plugins, repo / ".claude-plugin" / "marketplace.json", "plugins")
    workflows = _apply_existing_order(workflows, repo / ".athena-workflow" / "marketplace.json", "workflows")
    return MarketplaceModel(repo_root=repo, plugins=plugins, workflows=workflows)


def _apply_existing_order(items, registry_path: Path, key: str):
    """Sort items by their order in an existing registry, with unknowns appended alphabetically."""
    if not registry_path.exists():
        return items
    try:
        existing = read_json(registry_path).get(key, [])
        order = {entry["name"]: i for i, entry in enumerate(existing) if "name" in entry}
    except (KeyError, TypeError):
        return items
    return sorted(items, key=lambda x: (order.get(x.name, len(order)), x.name))


def _load_plugins(repo: Path) -> list[Plugin]:
    plugins_dir = repo / "plugins"
    plugins: list[Plugin] = []
    for path in sorted(plugins_dir.iterdir()):
        if not path.is_dir():
            continue
        claude_manifest_path = path / ".claude-plugin" / "plugin.json"
        codex_manifest_path = path / ".codex-plugin" / "plugin.json"
        if not claude_manifest_path.exists() or not codex_manifest_path.exists():
            raise ConsistencyError(
                f"plugin {path.name!r} missing per-plugin manifest "
                f"(expected both {claude_manifest_path} and {codex_manifest_path})"
            )
        claude = read_json(claude_manifest_path)
        codex = read_json(codex_manifest_path)
        _check_shared_fields(path.name, claude, codex)
        plugin = Plugin(
            name=claude["name"],
            version=claude["version"],
            description=claude["description"],
            category=claude["category"],
            author=claude.get("author", {}),
            keywords=list(claude.get("keywords", [])),
            repository=claude.get("repository"),
            license=claude.get("license"),
            homepage=claude.get("homepage"),
            contributors=claude.get("contributors"),
            marketplace_description=claude.get("marketplaceDescription"),
            skills_path=codex.get("skills", "./skills/"),
            mcp_servers=codex.get("mcpServers"),
            interface=dict(codex.get("interface", {})),
            path=path,
        )
        plugins.append(plugin)
    return plugins


def _check_shared_fields(plugin_name: str, claude: dict, codex: dict) -> None:
    mismatches = []
    for field in SHARED_FIELDS:
        if claude.get(field) != codex.get(field):
            mismatches.append(
                f"  {field}:\n"
                f"    .claude-plugin: {claude.get(field)!r}\n"
                f"    .codex-plugin:  {codex.get(field)!r}"
            )
    if mismatches:
        raise ConsistencyError(
            f"plugin {plugin_name!r} has Shared Field disagreement between Per-plugin Manifests:\n"
            + "\n".join(mismatches)
        )


def _load_workflows(repo: Path) -> list[Workflow]:
    workflows_dir = repo / "workflows"
    workflows: list[Workflow] = []
    for path in sorted(workflows_dir.iterdir()):
        if not path.is_dir():
            continue
        wj = path / "workflow.json"
        if not wj.exists():
            raise ConsistencyError(f"workflow {path.name!r} missing workflow.json")
        data = read_json(wj)
        pins = [PluginPin.from_ref(p["ref"], p["version"]) for p in data.get("plugins", [])]
        workflows.append(
            Workflow(
                name=data["name"],
                version=data.get("version", "0.0.0"),
                description=data.get("description", ""),
                marketplace_description=data.get("marketplaceDescription"),
                raw=data,
                pins=pins,
                path=path,
            )
        )
    return workflows
