from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Literal

from .io import read_json
from .model import MarketplaceModel, Plugin, Workflow


Runtime = Literal["athena", "claude", "codex"]


class CompileError(ValueError):
    pass


@dataclass
class CompiledPlugin:
    name: str
    version: str
    ref: str
    plugin_root: str
    skills_root: str | None
    overlay_manifest: str | None
    mcp_servers: dict[str, Any] = field(default_factory=dict)

    def as_dict(self) -> dict[str, Any]:
        out: dict[str, Any] = {
            "name": self.name,
            "version": self.version,
            "ref": self.ref,
            "pluginRoot": self.plugin_root,
        }
        if self.skills_root is not None:
            out["skillsRoot"] = self.skills_root
        if self.overlay_manifest is not None:
            out["overlayManifest"] = self.overlay_manifest
        if self.mcp_servers:
            out["mcpServers"] = self.mcp_servers
        return out


@dataclass
class CompiledWorkflowPlan:
    runtime: Runtime
    workflow_name: str
    workflow_version: str
    workflow_file: str | None
    prompt_template: str
    loop: dict[str, Any]
    plugins: list[CompiledPlugin]
    validation_findings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict[str, Any]:
        return {
            "runtime": self.runtime,
            "workflow": {
                "name": self.workflow_name,
                "version": self.workflow_version,
                "workflowFile": self.workflow_file,
                "promptTemplate": self.prompt_template,
                "loop": self.loop,
            },
            "plugins": [p.as_dict() for p in self.plugins],
            "validationFindings": list(self.validation_findings),
        }


def compile_workflow(model: MarketplaceModel, workflow_name: str, runtime: Runtime) -> CompiledWorkflowPlan:
    """Resolve a Workflow plus its Plugin Pins into a runtime-owned plan.

    This is the seam RFC 0002 calls the Compiled Workflow Plan: callers ask for a
    Workflow by name and Runtime, while plugin roots, overlay manifests, skill roots,
    MCP config, and pin validation stay behind this module.
    """
    if runtime not in ("athena", "claude", "codex"):
        raise CompileError(f"unknown Runtime: {runtime!r}")

    workflow = model.workflow(workflow_name)
    findings: list[str] = []
    compiled_plugins: list[CompiledPlugin] = []

    for pin in workflow.pins:
        try:
            plugin = model.plugin(pin.plugin_name)
        except KeyError as exc:
            raise CompileError(
                f"workflow {workflow.name!r} pins unknown Plugin {pin.plugin_name!r}"
            ) from exc
        if pin.version != plugin.version:
            findings.append(
                f"Plugin Pin {pin.plugin_name!r} is pinned at {pin.version}, current Plugin version is {plugin.version}"
            )
        compiled_plugins.append(_compile_plugin(model, plugin, pin.ref, pin.version, runtime))

    return CompiledWorkflowPlan(
        runtime=runtime,
        workflow_name=workflow.name,
        workflow_version=workflow.version,
        workflow_file=_workflow_file(model, workflow),
        prompt_template=workflow.raw.get("promptTemplate", "{input}"),
        loop=dict(workflow.raw.get("loop", {})),
        plugins=compiled_plugins,
        validation_findings=findings,
    )


def _compile_plugin(
    model: MarketplaceModel,
    plugin: Plugin,
    ref: str,
    pinned_version: str,
    runtime: Runtime,
) -> CompiledPlugin:
    assert plugin.path is not None
    plugin_root = _relative_contained(model.repo_root, plugin.path)
    skills_root = _skills_root(model, plugin, runtime)
    overlay_manifest = _overlay_manifest(model, plugin, runtime)
    return CompiledPlugin(
        name=plugin.name,
        version=pinned_version,
        ref=ref,
        plugin_root=plugin_root,
        skills_root=skills_root,
        overlay_manifest=overlay_manifest,
        mcp_servers=_mcp_servers(model, plugin),
    )


def _workflow_file(model: MarketplaceModel, workflow: Workflow) -> str | None:
    filename = workflow.raw.get("workflowFile")
    if not filename:
        return None
    assert workflow.path is not None
    return _relative_contained(model.repo_root, workflow.path / filename)


def _skills_root(model: MarketplaceModel, plugin: Plugin, runtime: Runtime) -> str | None:
    assert plugin.path is not None
    if runtime == "codex":
        return _relative_contained(model.repo_root, plugin.path / plugin.skills_path)
    return _relative_contained(model.repo_root, plugin.path / "skills")


def _overlay_manifest(model: MarketplaceModel, plugin: Plugin, runtime: Runtime) -> str | None:
    if runtime == "codex":
        return _relative_contained(model.repo_root, plugin.codex_manifest_path)
    if runtime == "claude":
        return _relative_contained(model.repo_root, plugin.claude_manifest_path)
    return None


def _mcp_servers(model: MarketplaceModel, plugin: Plugin) -> dict[str, Any]:
    if plugin.mcp_servers is None:
        return {}
    if isinstance(plugin.mcp_servers, dict):
        return dict(plugin.mcp_servers)
    if isinstance(plugin.mcp_servers, str):
        assert plugin.path is not None
        mcp_path = plugin.path / plugin.mcp_servers
        _relative_contained(model.repo_root, mcp_path)
        data = read_json(mcp_path)
        servers = data.get("mcpServers", data)
        if not isinstance(servers, dict):
            raise CompileError(f"Plugin {plugin.name!r} MCP config must be an object")
        return servers
    raise CompileError(f"Plugin {plugin.name!r} has unsupported MCP config shape")


def _relative_contained(repo_root: Path, path: Path) -> str:
    resolved_root = repo_root.resolve()
    resolved_path = path.resolve()
    try:
        rel = resolved_path.relative_to(resolved_root)
    except ValueError as exc:
        raise CompileError(f"resolved path escapes repo root: {path}") from exc
    return f"./{rel.as_posix()}"
