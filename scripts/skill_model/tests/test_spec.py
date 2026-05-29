from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from skill_model import (
    CLAUDE_OVERLAY_KEYS,
    find_misplaced_skills,
    load,
    write_claude_overlay,
)


def make_skill(root: Path, name: str = "ex", *, skill_md: str | None = None,
               claude_yaml: str | None = None, openai_yaml: str | None = None) -> Path:
    skill_dir = root / "plugins" / "p" / "skills" / name
    skill_dir.mkdir(parents=True, exist_ok=True)
    (skill_dir / "SKILL.md").write_text(
        skill_md
        if skill_md is not None
        else "---\nname: ex\ndescription: example\n---\n\n# Body\n"
    )
    if claude_yaml is not None:
        (skill_dir / "agents").mkdir(exist_ok=True)
        (skill_dir / "agents" / "claude.yaml").write_text(claude_yaml)
    if openai_yaml is not None:
        (skill_dir / "agents").mkdir(exist_ok=True)
        (skill_dir / "agents" / "openai.yaml").write_text(openai_yaml)
    return skill_dir


class TestLoadAndValidate(unittest.TestCase):
    def test_minimal_skill_validates(self):
        with TemporaryDirectory() as tmp:
            sd = make_skill(Path(tmp))
            problems = load(sd).validate()
            self.assertEqual(problems, [])

    def test_portable_frontmatter_with_claude_only_key_fails(self):
        with TemporaryDirectory() as tmp:
            sd = make_skill(
                Path(tmp),
                skill_md="---\nname: ex\ndescription: example\nargument-hint: <thing>\n---\n",
            )
            problems = load(sd).validate()
            self.assertTrue(any("argument-hint" in p for p in problems))

    def test_claude_overlay_with_unknown_key_fails(self):
        with TemporaryDirectory() as tmp:
            sd = make_skill(
                Path(tmp),
                claude_yaml="frontmatter:\n  argument-hint: \"<thing>\"\n  what-is-this: yes\n",
            )
            problems = load(sd).validate()
            self.assertTrue(any("what-is-this" in p for p in problems))

    def test_openai_overlay_missing_interface_fields_fails(self):
        with TemporaryDirectory() as tmp:
            sd = make_skill(
                Path(tmp),
                openai_yaml=(
                    "interface:\n"
                    "  display_name: \"Ex\"\n"
                ),
            )
            problems = load(sd).validate()
            self.assertTrue(any("short_description" in p and "default_prompt" in p for p in problems))

    def test_allowed_tools_must_be_string(self):
        with TemporaryDirectory() as tmp:
            sd = make_skill(
                Path(tmp),
                skill_md="---\nname: ex\ndescription: example\nallowed-tools:\n  - Read\n---\n",
            )
            problems = load(sd).validate()
            self.assertTrue(any("allowed-tools" in p for p in problems))


class TestWriteClaudeOverlay(unittest.TestCase):
    def test_write_overlay_emits_valid_file(self):
        with TemporaryDirectory() as tmp:
            sd = make_skill(Path(tmp))
            path = write_claude_overlay(sd, {"argument-hint": "<x>", "user-invocable": True})
            self.assertTrue(path.exists())
            content = path.read_text()
            self.assertIn("argument-hint", content)
            self.assertIn("user-invocable: true", content)
            problems = load(sd).validate()
            self.assertEqual(problems, [])

    def test_write_overlay_rejects_unknown_keys(self):
        with TemporaryDirectory() as tmp:
            sd = make_skill(Path(tmp))
            with self.assertRaises(ValueError):
                write_claude_overlay(sd, {"description": "no, that's portable"})


class TestKeyTable(unittest.TestCase):
    def test_canonical_keys_match_legacy_lists(self):
        # Sanity: this is the single source of truth replacing two duplicated sets.
        self.assertIn("argument-hint", CLAUDE_OVERLAY_KEYS)
        self.assertIn("user-invocable", CLAUDE_OVERLAY_KEYS)
        self.assertIn("hooks", CLAUDE_OVERLAY_KEYS)
        self.assertNotIn("name", CLAUDE_OVERLAY_KEYS)
        self.assertNotIn("description", CLAUDE_OVERLAY_KEYS)


class TestSkillLayout(unittest.TestCase):
    def test_flat_skill_is_not_flagged(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, "explore")
            self.assertEqual(find_misplaced_skills(root), [])

    def test_category_nested_skill_is_flagged(self):
        # Athena's plugin loader and this repo's skill discovery both expect
        # skills exactly one level under skills/. A category folder hides them.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            nested = root / "plugins" / "p" / "skills" / "engineering" / "tdd"
            nested.mkdir(parents=True)
            skill_md = nested / "SKILL.md"
            skill_md.write_text("---\nname: tdd\ndescription: x\n---\n\n# Body\n")

            self.assertEqual(find_misplaced_skills(root), [skill_md.resolve()])

    def test_vendored_upstream_skills_are_not_flagged(self):
        # tanstack-start vendors upstream skill bundles under skills/upstream/.
        # Those are bundled reference material, not top-level skills, so the
        # layout gate must leave them alone.
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            vendored = (
                root / "plugins" / "tanstack-start" / "skills" / "upstream"
                / "@tanstack" / "router-core" / "skills" / "router-core"
            )
            vendored.mkdir(parents=True)
            (vendored / "SKILL.md").write_text(
                "---\nname: router-core\ndescription: x\n---\n\n# Body\n"
            )

            self.assertEqual(find_misplaced_skills(root), [])


if __name__ == "__main__":
    unittest.main()
