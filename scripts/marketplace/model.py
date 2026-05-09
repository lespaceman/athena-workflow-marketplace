from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


REPO_OWNER_REF = "lespaceman/athena-workflow-marketplace"

CLAUDE_MARKETPLACE_TOP = {
    "name": "athena-workflow-marketplace",
    "owner": {"name": "Athenaflow"},
    "metadata": {
        "description": "Claude Code plugins for browser automation, layered E2E testing, and developer tooling",
        "version": "1.0.0",
        "pluginRoot": "./plugins",
    },
}

CODEX_MARKETPLACE_TOP = {
    "name": "athena-workflow-marketplace",
    "interface": {"displayName": "Athena Plugin Marketplace"},
}

ATHENA_MARKETPLACE_TOP = {
    "name": "athena-workflow-marketplace",
    "owner": {"name": "Athenaflow"},
    "metadata": {
        "description": "A marketplace of AI-powered browser automation workflows for Athena",
        "workflowRoot": "./workflows",
    },
}


@dataclass
class Plugin:
    name: str
    version: str
    description: str
    category: str
    author: dict[str, Any]
    keywords: list[str] = field(default_factory=list)
    repository: str | None = None
    license: str | None = None
    homepage: str | None = None
    contributors: list[Any] | None = None
    marketplace_description: str | None = None
    skills_path: str = "./skills/"
    mcp_servers: dict[str, Any] | None = None
    interface: dict[str, Any] = field(default_factory=dict)
    path: Path | None = None

    @property
    def display_marketplace_description(self) -> str:
        return self.marketplace_description if self.marketplace_description else self.description

    @property
    def claude_manifest_path(self) -> Path:
        assert self.path is not None
        return self.path / ".claude-plugin" / "plugin.json"

    @property
    def codex_manifest_path(self) -> Path:
        assert self.path is not None
        return self.path / ".codex-plugin" / "plugin.json"

    @property
    def package_json_path(self) -> Path:
        assert self.path is not None
        return self.path / "package.json"


@dataclass
class PluginPin:
    plugin_name: str
    version: str

    @classmethod
    def from_ref(cls, ref: str, version: str) -> "PluginPin":
        plugin_name = ref.split("@", 1)[0] if "@" in ref else ref
        return cls(plugin_name=plugin_name, version=version)

    @property
    def ref(self) -> str:
        return f"{self.plugin_name}@{REPO_OWNER_REF}"


@dataclass
class Workflow:
    name: str
    version: str
    description: str
    marketplace_description: str | None = None
    raw: dict[str, Any] = field(default_factory=dict)
    pins: list[PluginPin] = field(default_factory=list)
    path: Path | None = None

    @property
    def display_marketplace_description(self) -> str:
        return self.marketplace_description if self.marketplace_description else self.description

    @property
    def workflow_json_path(self) -> Path:
        assert self.path is not None
        return self.path / "workflow.json"


@dataclass
class MarketplaceModel:
    repo_root: Path
    plugins: list[Plugin] = field(default_factory=list)
    workflows: list[Workflow] = field(default_factory=list)

    def plugin(self, name: str) -> Plugin:
        for p in self.plugins:
            if p.name == name:
                return p
        raise KeyError(f"plugin not found: {name}")

    def workflow(self, name: str) -> Workflow:
        for w in self.workflows:
            if w.name == name:
                return w
        raise KeyError(f"workflow not found: {name}")

    def workflows_pinning(self, plugin_name: str) -> list[Workflow]:
        return [w for w in self.workflows if any(p.plugin_name == plugin_name for p in w.pins)]
