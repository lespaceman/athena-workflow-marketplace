from __future__ import annotations

from copy import deepcopy
from typing import Any

from .model import (
    ATHENA_MARKETPLACE_TOP,
    CLAUDE_MARKETPLACE_TOP,
    CODEX_MARKETPLACE_TOP,
    MarketplaceModel,
    Plugin,
    Workflow,
)


def render_plugin_claude_manifest(plugin: Plugin) -> dict[str, Any]:
    out: dict[str, Any] = {
        "name": plugin.name,
        "description": plugin.description,
        "version": plugin.version,
    }
    if plugin.author:
        out["author"] = deepcopy(plugin.author)
    if plugin.contributors is not None:
        out["contributors"] = deepcopy(plugin.contributors)
    if plugin.homepage is not None:
        out["homepage"] = plugin.homepage
    if plugin.keywords:
        out["keywords"] = list(plugin.keywords)
    if plugin.category:
        out["category"] = plugin.category
    if plugin.license is not None:
        out["license"] = plugin.license
    if plugin.marketplace_description is not None:
        out["marketplaceDescription"] = plugin.marketplace_description
    if plugin.repository is not None:
        out["repository"] = plugin.repository
    return out


def render_plugin_codex_manifest(plugin: Plugin) -> dict[str, Any]:
    out: dict[str, Any] = {
        "name": plugin.name,
        "version": plugin.version,
        "description": plugin.description,
    }
    if plugin.author:
        out["author"] = deepcopy(plugin.author)
    if plugin.contributors is not None:
        out["contributors"] = deepcopy(plugin.contributors)
    out["skills"] = plugin.skills_path
    if plugin.interface:
        out["interface"] = deepcopy(plugin.interface)
    if plugin.mcp_servers is not None:
        out["mcpServers"] = deepcopy(plugin.mcp_servers)
    return out


_MARKETPLACE_OWNER_NAME = "Athenaflow"
_SELF_REPOSITORIES = frozenset(
    {
        "https://github.com/AthenaFlow/workflow-marketplace",
        "https://github.com/lespaceman/athena-workflow-marketplace",
    }
)


def render_claude_marketplace_entry(plugin: Plugin) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "name": plugin.name,
        "source": f"./plugins/{plugin.name}",
        "description": plugin.display_marketplace_description,
        "version": plugin.version,
    }
    # Include author only when it differs from the marketplace owner — keeps third-party
    # attribution intact while suppressing redundant Athenaflow noise.
    if plugin.author and plugin.author.get("name") != _MARKETPLACE_OWNER_NAME:
        entry["author"] = deepcopy(plugin.author)
    if plugin.keywords:
        entry["keywords"] = list(plugin.keywords)
    if plugin.category:
        entry["category"] = plugin.category
    # Forward repository only when it points outside this marketplace; self-pointers
    # are implicit in the marketplace's own owner metadata.
    if plugin.repository is not None and plugin.repository not in _SELF_REPOSITORIES:
        entry["repository"] = plugin.repository
    if plugin.license is not None:
        entry["license"] = plugin.license
    return entry


def render_codex_marketplace_entry(plugin: Plugin) -> dict[str, Any]:
    return {
        "name": plugin.name,
        "description": plugin.display_marketplace_description,
        "version": plugin.version,
        "source": {
            "source": "local",
            "path": f"./plugins/{plugin.name}",
        },
        "policy": {
            "installation": "AVAILABLE",
            "authentication": "ON_INSTALL",
        },
        "category": plugin.category,
    }


def render_athena_marketplace_entry(workflow: Workflow) -> dict[str, Any]:
    return {
        "name": workflow.name,
        "source": f"./workflows/{workflow.name}/workflow.json",
        "description": workflow.display_marketplace_description,
        "version": workflow.version,
    }


def render_claude_marketplace(model: MarketplaceModel) -> dict[str, Any]:
    out = deepcopy(CLAUDE_MARKETPLACE_TOP)
    out["plugins"] = [render_claude_marketplace_entry(p) for p in model.plugins]
    return out


def render_codex_marketplace(model: MarketplaceModel) -> dict[str, Any]:
    out = deepcopy(CODEX_MARKETPLACE_TOP)
    out["plugins"] = [render_codex_marketplace_entry(p) for p in model.plugins]
    return out


def render_athena_marketplace(model: MarketplaceModel) -> dict[str, Any]:
    out = deepcopy(ATHENA_MARKETPLACE_TOP)
    out["workflows"] = [render_athena_marketplace_entry(w) for w in model.workflows]
    return out


def render_workflow_json(workflow: Workflow) -> dict[str, Any]:
    """Project a Workflow back to its workflow.json shape, preserving extra fields."""
    out = deepcopy(workflow.raw)
    out["name"] = workflow.name
    out["description"] = workflow.description
    out["version"] = workflow.version
    if workflow.pins:
        out["plugins"] = [{"ref": p.ref, "version": p.version} for p in workflow.pins]
    elif "plugins" in out and not out["plugins"]:
        out["plugins"] = []
    return out
