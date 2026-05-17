"""CLI entry point: python3 -m marketplace <command> [args...]"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

from .compiler import CompileError, compile_workflow
from .loader import ConsistencyError, load
from .writer import (
    bump_plugin,
    bump_workflow,
    diff_registries,
    write_all,
    write_per_plugin_manifests,
    write_registries,
    write_workflow_jsons,
)


def _repo_root_from_args(args: argparse.Namespace) -> Path:
    return Path(args.repo_root).resolve()


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        model = load(_repo_root_from_args(args))
    except (ConsistencyError, CompileError) as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    diffs = diff_registries(model)
    drift = [p for p, changed in diffs.items() if changed]
    if drift:
        print("Marketplace Registries are not in sync with canonical sources:")
        for p in drift:
            print(f"  - {p}")
        print("\nRun: python3 -m marketplace write-registries")
        return 1
    plan_findings = _compile_all_workflows(model)
    if plan_findings:
        print("Compiled Workflow Plan validation failed:")
        for finding in plan_findings:
            print(f"  - {finding}")
        return 1
    print(f"OK: {len(model.plugins)} plugins, {len(model.workflows)} workflows; all three registries in sync.")
    return 0


def cmd_write_registries(args: argparse.Namespace) -> int:
    model = load(_repo_root_from_args(args))
    changed = write_registries(model)
    if changed:
        for p in changed:
            print(f"wrote {p.relative_to(model.repo_root)}")
    else:
        print("registries already in sync")
    return 0


def cmd_write_all(args: argparse.Namespace) -> int:
    model = load(_repo_root_from_args(args))
    changed = write_all(model)
    if changed:
        for p in changed:
            print(f"wrote {p.relative_to(model.repo_root)}")
    else:
        print("everything already in sync")
    return 0


def cmd_bump(args: argparse.Namespace) -> int:
    repo_root = _repo_root_from_args(args)
    model = load(repo_root)
    targets = list(args.targets) if args.targets else _autodetect_targets(model, repo_root)
    if not targets and not args.targets:
        print("no plugin or workflow changes detected")
        return 0
    plugin_names = {p.name for p in model.plugins}
    workflow_names = {w.name for w in model.workflows}
    bumped_plugins: list[dict] = []
    bumped_workflows: list[dict] = []
    pin_touched_workflows: set[str] = set()
    for target in targets:
        if target in plugin_names:
            result = bump_plugin(model, target, args.part)
            bumped_plugins.append(result)
            pin_touched_workflows.update(result["cascaded_workflows"])
        elif target in workflow_names:
            bumped_workflows.append(bump_workflow(model, target, args.part))
        else:
            print(f"warning: {target!r} is neither a plugin nor a workflow", file=sys.stderr)
    # Auto-detected workflow changes also bump (matching legacy behavior).
    if not args.targets:
        for wf_name in _autodetect_workflow_changes(repo_root):
            if wf_name in workflow_names and wf_name not in pin_touched_workflows and wf_name not in {b["workflow"] for b in bumped_workflows}:
                bumped_workflows.append(bump_workflow(model, wf_name, args.part))
    changed = write_all(model)
    for r in bumped_plugins:
        print(f"plugin {r['plugin']}: {r['old_version']} -> {r['new_version']}")
        for w in r["cascaded_workflows"]:
            print(f"  cascaded pin to workflow {w}")
    for r in bumped_workflows:
        print(f"workflow {r['workflow']}: {r['old_version']} -> {r['new_version']}")
    print(f"\nwrote {len(changed)} files")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    model = load(_repo_root_from_args(args))
    payload = {
        "plugins": [
            {"name": p.name, "version": p.version, "description": p.description, "category": p.category}
            for p in model.plugins
        ],
        "workflows": [
            {
                "name": w.name,
                "version": w.version,
                "pins": [{"plugin": pin.plugin_name, "version": pin.version} for pin in w.pins],
            }
            for w in model.workflows
        ],
    }
    print(json.dumps(payload, indent=2))
    return 0


def cmd_compile(args: argparse.Namespace) -> int:
    model = load(_repo_root_from_args(args))
    try:
        plan = compile_workflow(model, args.workflow, args.runtime)
    except (CompileError, KeyError) as e:
        print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print(json.dumps(plan.as_dict(), indent=2))
    return 0


def _compile_all_workflows(model) -> list[str]:
    findings: list[str] = []
    for workflow in model.workflows:
        for runtime in ("athena", "claude", "codex"):
            try:
                plan = compile_workflow(model, workflow.name, runtime)
            except CompileError as e:
                findings.append(f"{workflow.name} ({runtime}): {e}")
                continue
            for finding in plan.validation_findings:
                findings.append(f"{workflow.name} ({runtime}): {finding}")
    return findings


def _autodetect_targets(model, repo_root: Path) -> list[str]:
    """Walk git diff for changed plugins (mirrors legacy bump-versions.sh behaviour)."""
    plugins_changed: list[str] = []
    seen: set[str] = set()
    for path in _changed_files(repo_root):
        if path.startswith("plugins/"):
            name = path.split("/", 2)[1]
            if name not in seen and any(p.name == name for p in model.plugins):
                seen.add(name)
                plugins_changed.append(name)
    return plugins_changed


def _autodetect_workflow_changes(repo_root: Path) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for path in _changed_files(repo_root):
        if path.startswith("workflows/"):
            parts = path.split("/", 2)
            if len(parts) >= 2 and parts[1] and parts[1] not in seen:
                seen.add(parts[1])
                out.append(parts[1])
    return out


def _changed_files(repo_root: Path) -> list[str]:
    for cmd in (["git", "diff", "--name-only", "HEAD~1", "HEAD"], ["git", "diff", "--name-only", "HEAD"]):
        try:
            out = subprocess.run(cmd, cwd=repo_root, capture_output=True, text=True, check=True).stdout
            return [line for line in out.splitlines() if line]
        except subprocess.CalledProcessError:
            continue
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="marketplace", description="Cross-runtime plugin marketplace tooling")
    parser.add_argument("--repo-root", default=".", help="repo root (default: current directory)")
    sub = parser.add_subparsers(dest="cmd", required=True)

    p_validate = sub.add_parser("validate", help="check that all three Marketplace Registries are projections of the canonical model")
    p_validate.set_defaults(func=cmd_validate)

    p_wr = sub.add_parser("write-registries", help="rewrite the three Marketplace Registries from the canonical model")
    p_wr.set_defaults(func=cmd_write_registries)

    p_wa = sub.add_parser("write-all", help="rewrite per-plugin manifests, workflow.jsons, and the three registries")
    p_wa.set_defaults(func=cmd_write_all)

    p_bump = sub.add_parser("bump", help="bump version(s) and cascade Plugin Pins")
    p_bump.add_argument("targets", nargs="*", help="plugin or workflow name(s); empty = autodetect from git diff")
    p_bump.add_argument("--part", choices=["major", "minor", "patch"], default="patch")
    p_bump.set_defaults(func=cmd_bump)

    p_show = sub.add_parser("show", help="dump the canonical model as JSON")
    p_show.set_defaults(func=cmd_show)

    p_compile = sub.add_parser("compile-workflow", help="resolve a Workflow and its Plugin Pins into a runtime-owned plan")
    p_compile.add_argument("workflow", help="Workflow name")
    p_compile.add_argument("--runtime", choices=["athena", "claude", "codex"], default="athena")
    p_compile.set_defaults(func=cmd_compile)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
