import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from marketplace import check_workflow_references, load


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def make_plugin(root: Path, name: str, skills: list[str]) -> None:
    plugin_dir = root / "plugins" / name
    write_json(
        plugin_dir / ".claude-plugin" / "plugin.json",
        {"name": name, "description": f"{name} plugin", "version": "1.0.0", "author": {"name": "T"}, "category": "testing"},
    )
    write_json(
        plugin_dir / ".codex-plugin" / "plugin.json",
        {
            "name": name,
            "version": "1.0.0",
            "description": f"{name} plugin",
            "category": "testing",
            "author": {"name": "T"},
            "skills": "./skills/",
            "interface": {"displayName": name},
        },
    )
    for skill in skills:
        skill_dir = plugin_dir / "skills" / f"{skill}-dir"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(f"---\nname: {skill}\ndescription: {skill}\n---\n# {skill}\n", encoding="utf-8")


def make_workflow(root: Path, pins: list[str], md: str) -> None:
    wf_dir = root / "workflows" / "flow"
    write_json(
        wf_dir / "workflow.json",
        {
            "name": "flow",
            "description": "flow",
            "version": "0.0.1",
            "promptTemplate": "{input}",
            "workflowFile": "workflow.md",
            "plugins": [{"ref": f"{p}@lespaceman/athena-workflow-marketplace", "version": "1.0.0"} for p in pins],
        },
    )
    (wf_dir / "workflow.md").write_text(md, encoding="utf-8")


class TestWorkflowReferences(unittest.TestCase):
    def _findings(self, pins, md):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_plugin(root, "alpha", ["a-skill"])
            make_plugin(root, "beta", ["b-skill"])
            make_plugin(root, "gamma", ["shared-skill"])
            make_plugin(root, "delta", ["shared-skill"])
            make_workflow(root, pins, md)
            model = load(root)
            return check_workflow_references(model, model.workflow("flow"))

    def test_clean_workflow_has_no_findings(self):
        self.assertEqual(self._findings(["alpha"], "Load `a-skill` first.\n"), [])

    def test_skill_from_unpinned_plugin_is_reported(self):
        findings = self._findings(["alpha"], "Load `a-skill` then `b-skill`.\n")
        self.assertEqual(len(findings), 1)
        self.assertIn("`b-skill`", findings[0])
        self.assertIn("beta", findings[0])

    def test_unreferenced_pin_is_reported(self):
        findings = self._findings(["alpha", "beta"], "Load `a-skill`.\n")
        self.assertEqual(len(findings), 1)
        self.assertIn("'beta'", findings[0])
        self.assertIn("b-skill", findings[0])

    def test_plugin_name_counts_as_a_reference(self):
        self.assertEqual(self._findings(["alpha", "beta"], "Load `a-skill`; `beta` provides MCP tools.\n"), [])

    def test_shared_skill_name_is_fine_when_any_owner_is_pinned(self):
        self.assertEqual(self._findings(["gamma"], "Load `shared-skill`.\n"), [])

    def test_non_skill_backticks_are_ignored(self):
        self.assertEqual(self._findings(["alpha"], "Never work on `main`; run `npx playwright test`; load `a-skill`.\n"), [])

    def test_fenced_code_blocks_are_not_scanned(self):
        md = "Load `a-skill`.\n\n```\nrun `b-skill` here\n```\n\n~~~text\n`b-skill`\n~~~\n"
        self.assertEqual(self._findings(["alpha"], md), [])

    def test_ignore_comment_exempts_a_deliberate_mention(self):
        md = "Load `a-skill`; hand off to `b-skill` later.\n<!-- marketplace-validate: ignore-skill b-skill -->\n"
        self.assertEqual(self._findings(["alpha"], md), [])

    def test_quoted_and_crlf_frontmatter_names_resolve(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_plugin(root, "alpha", [])
            skill_dir = root / "plugins" / "alpha" / "skills" / "weird"
            skill_dir.mkdir(parents=True)
            (skill_dir / "SKILL.md").write_bytes(b'\xef\xbb\xbf---\r\nname: "quoted-skill"\r\ndescription: x\r\n---\r\n# body\r\n')
            (root / "plugins" / "alpha" / "skills" / "README.md").write_text("not a skill\n", encoding="utf-8")
            (root / "plugins" / "alpha" / "skills" / "empty-dir").mkdir()
            make_workflow(root, ["alpha"], "Load `quoted-skill`.\n")
            model = load(root)
            self.assertEqual(check_workflow_references(model, model.workflow("flow")), [])

    def test_missing_workflow_file_is_reported(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_plugin(root, "alpha", ["a-skill"])
            make_workflow(root, ["alpha"], "x")
            (root / "workflows" / "flow" / "workflow.md").unlink()
            model = load(root)
            findings = check_workflow_references(model, model.workflow("flow"))
            self.assertEqual(len(findings), 1)
            self.assertIn("does not exist", findings[0])


if __name__ == "__main__":
    unittest.main()
