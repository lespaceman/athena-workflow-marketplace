from evals.extraction.frontmatter import PORTABLE_FORBIDDEN_KEYS, parse

GOOD = """---
name: define-regression-scope
description: >
  Use to define impact-based regression scope for a release. Triggers include "regression
  scope for...". This skill owns regression intent; it does NOT own live exploration.
---

# Define Regression Scope

Body content.
"""

MISSING_DESCRIPTION = """---
name: thing
---
body
"""

CLAUDE_ONLY_KEY = """---
name: thing
description: x
argument-hint: "<arg>"
---
body
"""

NO_FRONTMATTER = "just markdown body"


def test_parses_good_skill_md():
    parsed = parse(GOOD)
    assert parsed.is_valid
    assert parsed.frontmatter["name"] == "define-regression-scope"
    assert "Body content." in parsed.body


def test_flags_missing_required_keys():
    parsed = parse(MISSING_DESCRIPTION)
    assert not parsed.is_valid
    assert any("description" in f for f in parsed.findings)


def test_warns_on_claude_only_keys():
    parsed = parse(CLAUDE_ONLY_KEY)
    assert any("Claude-only key" in f for f in parsed.findings)
    assert "argument-hint" in PORTABLE_FORBIDDEN_KEYS


def test_handles_missing_frontmatter():
    parsed = parse(NO_FRONTMATTER)
    assert not parsed.is_valid
    assert "missing or invalid frontmatter" in parsed.findings[0]
