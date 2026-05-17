import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from marketplace import (
    ConsistencyError,
    bump_plugin,
    bump_workflow,
    load,
    write_all,
)


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def make_repo(root: Path) -> None:
    """Build a minimal but valid repo layout with one plugin and one workflow."""
    plugin_dir = root / "plugins" / "alpha"
    write_json(
        plugin_dir / ".claude-plugin" / "plugin.json",
        {
            "name": "alpha",
            "description": "first plugin",
            "version": "0.1.0",
            "author": {"name": "Athenaflow"},
            "keywords": ["alpha"],
            "category": "testing",
        },
    )
    write_json(
        plugin_dir / ".codex-plugin" / "plugin.json",
        {
            "name": "alpha",
            "version": "0.1.0",
            "description": "first plugin",
            "category": "testing",
            "author": {"name": "Athenaflow"},
            "skills": "./skills/",
            "interface": {
                "displayName": "Alpha",
                "shortDescription": "first plugin",
                "developerName": "Athenaflow",
                "category": "Testing",
            },
        },
    )
    workflow_dir = root / "workflows" / "alpha-flow"
    write_json(
        workflow_dir / "workflow.json",
        {
            "name": "alpha-flow",
            "description": "uses alpha",
            "version": "0.0.1",
            "promptTemplate": "{input}",
            "plugins": [
                {"ref": "alpha@lespaceman/athena-workflow-marketplace", "version": "0.1.0"},
            ],
        },
    )


class TestLoaderConsistency(unittest.TestCase):
    def test_load_succeeds_when_per_plugin_manifests_agree(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            model = load(root)
            self.assertEqual(len(model.plugins), 1)
            self.assertEqual(model.plugins[0].version, "0.1.0")
            self.assertEqual(len(model.workflows), 1)

    def test_load_errors_on_description_drift(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            # Introduce drift
            cx = root / "plugins" / "alpha" / ".codex-plugin" / "plugin.json"
            data = json.loads(cx.read_text())
            data["description"] = "different description"
            cx.write_text(json.dumps(data, indent=2) + "\n")
            with self.assertRaises(ConsistencyError) as cm:
                load(root)
            self.assertIn("description", str(cm.exception))

    def test_load_errors_on_version_drift(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            cx = root / "plugins" / "alpha" / ".codex-plugin" / "plugin.json"
            data = json.loads(cx.read_text())
            data["version"] = "9.9.9"
            cx.write_text(json.dumps(data, indent=2) + "\n")
            with self.assertRaises(ConsistencyError):
                load(root)

    def test_load_errors_on_category_drift(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            cx = root / "plugins" / "alpha" / ".codex-plugin" / "plugin.json"
            data = json.loads(cx.read_text())
            data["category"] = "developer-tools"
            cx.write_text(json.dumps(data, indent=2) + "\n")
            with self.assertRaises(ConsistencyError) as cm:
                load(root)
            self.assertIn("category", str(cm.exception))

    def test_load_errors_on_string_plugin_pin(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            workflow = root / "workflows" / "alpha-flow" / "workflow.json"
            data = json.loads(workflow.read_text())
            data["plugins"] = ["alpha@lespaceman/athena-workflow-marketplace"]
            workflow.write_text(json.dumps(data, indent=2) + "\n")
            with self.assertRaises(ConsistencyError) as cm:
                load(root)
            self.assertIn("Plugin Pin objects", str(cm.exception))

    def test_load_errors_when_prompt_template_does_not_accept_input(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            workflow = root / "workflows" / "alpha-flow" / "workflow.json"
            data = json.loads(workflow.read_text())
            data["promptTemplate"] = "static prompt"
            workflow.write_text(json.dumps(data, indent=2) + "\n")
            with self.assertRaises(ConsistencyError) as cm:
                load(root)
            self.assertIn("{input}", str(cm.exception))


class TestBumpAndCascade(unittest.TestCase):
    def test_bump_plugin_cascades_to_workflow_pin(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            model = load(root)
            result = bump_plugin(model, "alpha", "patch")
            self.assertEqual(result["new_version"], "0.1.1")
            self.assertEqual(result["cascaded_workflows"], ["alpha-flow"])
            # Workflow version also bumped (patch)
            self.assertEqual(model.workflow("alpha-flow").version, "0.0.2")
            # Pin updated
            self.assertEqual(model.workflow("alpha-flow").pins[0].version, "0.1.1")

    def test_bump_workflow_does_not_touch_plugins(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            model = load(root)
            original_plugin_version = model.plugin("alpha").version
            bump_workflow(model, "alpha-flow", "minor")
            self.assertEqual(model.plugin("alpha").version, original_plugin_version)
            self.assertEqual(model.workflow("alpha-flow").version, "0.1.0")


class TestWriteAll(unittest.TestCase):
    def test_write_all_round_trips(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            model = load(root)
            bump_plugin(model, "alpha", "minor")
            write_all(model)
            reloaded = load(root)
            self.assertEqual(reloaded.plugin("alpha").version, "0.2.0")
            self.assertEqual(reloaded.workflow("alpha-flow").pins[0].version, "0.2.0")
            self.assertEqual(reloaded.workflow("alpha-flow").version, "0.0.2")

    def test_write_all_writes_three_registries(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_repo(root)
            model = load(root)
            write_all(model)
            self.assertTrue((root / ".claude-plugin" / "marketplace.json").exists())
            self.assertTrue((root / ".agents" / "plugins" / "marketplace.json").exists())
            self.assertTrue((root / ".athena-workflow" / "marketplace.json").exists())


if __name__ == "__main__":
    unittest.main()
