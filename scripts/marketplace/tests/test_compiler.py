import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from marketplace import CompileError, compile_workflow, load


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def make_repo(root: Path) -> None:
    plugin_dir = root / "plugins" / "browser"
    write_json(
        plugin_dir / ".claude-plugin" / "plugin.json",
        {
            "name": "browser",
            "description": "browser plugin",
            "version": "1.0.0",
            "author": {"name": "Athenaflow"},
            "keywords": ["browser"],
            "category": "browser-automation",
        },
    )
    write_json(
        plugin_dir / ".codex-plugin" / "plugin.json",
        {
            "name": "browser",
            "version": "1.0.0",
            "description": "browser plugin",
            "category": "browser-automation",
            "author": {"name": "Athenaflow"},
            "skills": "./skills/",
            "mcpServers": "./.mcp.json",
            "interface": {"displayName": "Browser"},
        },
    )
    write_json(
        plugin_dir / ".mcp.json",
        {
            "mcpServers": {
                "browser": {
                    "command": "npx",
                    "args": ["-y", "agent-web-interface@latest"],
                }
            }
        },
    )
    (plugin_dir / "skills" / "browse").mkdir(parents=True)

    workflow_dir = root / "workflows" / "browser-flow"
    write_json(
        workflow_dir / "workflow.json",
        {
            "name": "browser-flow",
            "description": "uses browser",
            "version": "0.0.1",
            "promptTemplate": "Do this: {input}",
            "workflowFile": "workflow.md",
            "loop": {"enabled": True, "maxIterations": 3},
            "plugins": [
                {"ref": "browser@lespaceman/athena-workflow-marketplace", "version": "1.0.0"},
            ],
        },
    )
    (workflow_dir / "workflow.md").write_text("# Browser Flow\n")


class TestCompileWorkflow(unittest.TestCase):
    def test_compile_codex_plan_resolves_overlay_skills_and_mcp(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            plan = compile_workflow(load(root), "browser-flow", "codex")

            self.assertEqual(plan.runtime, "codex")
            self.assertEqual(plan.workflow_name, "browser-flow")
            self.assertEqual(plan.workflow_file, "./workflows/browser-flow/workflow.md")
            self.assertEqual(plan.prompt_template, "Do this: {input}")
            self.assertEqual(plan.loop["maxIterations"], 3)

            plugin = plan.plugins[0]
            self.assertEqual(plugin.plugin_root, "./plugins/browser")
            self.assertEqual(plugin.skills_root, "./plugins/browser/skills")
            self.assertEqual(plugin.overlay_manifest, "./plugins/browser/.codex-plugin/plugin.json")
            self.assertEqual(plugin.mcp_servers["browser"]["command"], "npx")
            self.assertEqual(plan.validation_findings, [])

    def test_compile_claude_plan_uses_claude_overlay(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            plan = compile_workflow(load(root), "browser-flow", "claude")
            self.assertEqual(
                plan.plugins[0].overlay_manifest,
                "./plugins/browser/.claude-plugin/plugin.json",
            )

    def test_compile_reports_pin_version_drift(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            workflow = root / "workflows" / "browser-flow" / "workflow.json"
            data = json.loads(workflow.read_text())
            data["plugins"][0]["version"] = "0.9.0"
            workflow.write_text(json.dumps(data, indent=2) + "\n")

            plan = compile_workflow(load(root), "browser-flow", "athena")
            self.assertIn("pinned at 0.9.0", plan.validation_findings[0])

    def test_compile_errors_on_unknown_plugin_pin(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            workflow = root / "workflows" / "browser-flow" / "workflow.json"
            data = json.loads(workflow.read_text())
            data["plugins"][0]["ref"] = "missing@lespaceman/athena-workflow-marketplace"
            workflow.write_text(json.dumps(data, indent=2) + "\n")

            with self.assertRaises(CompileError):
                compile_workflow(load(root), "browser-flow", "athena")

    def test_compile_rejects_mcp_path_escaping_repo(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            manifest = root / "plugins" / "browser" / ".codex-plugin" / "plugin.json"
            data = json.loads(manifest.read_text())
            data["mcpServers"] = "../../../outside.json"
            manifest.write_text(json.dumps(data, indent=2) + "\n")

            with self.assertRaises(CompileError):
                compile_workflow(load(root), "browser-flow", "codex")


if __name__ == "__main__":
    unittest.main()
