from __future__ import annotations

import asyncio
from uuid import uuid4

import pytest

from evals.evaluators.base import EvalContext
from evals.evaluators.compliance_check import ComplianceCheck
from evals.extraction.frontmatter import parse

GOOD_SKILL_MD = """---
name: define-regression-scope
description: >
  Use to define impact-based regression scope for a release. Triggers include
  "regression scope for X" and "what regressions to run". This skill owns
  regression intent and produces the charter; it does NOT own live exploration
  or playwright execution. Scope: charter creation only.
license: MIT
---

# Define Regression Scope

Body content.
"""

MISSING_DESCRIPTION_MD = """---
name: thing
---

body
"""

CLAUDE_ONLY_KEY_MD = """---
name: thing
description: a short description
argument-hint: "<arg>"
---

body
"""


def _ctx(skill_md: str, *, overlays: dict[str, str | None] | None = None) -> EvalContext:
    parsed = parse(skill_md)
    return EvalContext(
        skill_id="acme/example#skills/x",
        skill_md=skill_md,
        frontmatter=dict(parsed.frontmatter),
        overlays=overlays or {"claude": "yaml-content", "openai": "yaml-content"},
        repo_metadata={},
        run_id=uuid4(),
    )


def _run(ev, ctx):
    return asyncio.run(ev.evaluate(ctx))


def test_good_skill_scores_high():
    result = _run(ComplianceCheck(), _ctx(GOOD_SKILL_MD))
    assert result.sub_scores["frontmatter_schema"] == 1.0
    assert result.sub_scores["portable_keys"] == 1.0
    assert result.sub_scores["overlays_present"] == 1.0
    assert result.sub_scores["description_quality"] == 1.0
    assert "allowed_tools_form" not in result.sub_scores
    assert result.score == pytest.approx(100.0)


def test_missing_description_drops_schema_and_quality():
    result = _run(ComplianceCheck(), _ctx(MISSING_DESCRIPTION_MD))
    assert result.sub_scores["frontmatter_schema"] == 0.0
    assert result.sub_scores["description_quality"] == 0.0
    assert any("description" in f for f in result.findings)


def test_claude_only_keys_lowers_portable_keys():
    result = _run(ComplianceCheck(), _ctx(CLAUDE_ONLY_KEY_MD))
    assert result.sub_scores["portable_keys"] < 1.0
    assert any("Claude-only" in f for f in result.findings)


def test_missing_overlays_lowers_overlays_present():
    ctx = _ctx(GOOD_SKILL_MD, overlays={"claude": None, "openai": None})
    result = _run(ComplianceCheck(), ctx)
    assert result.sub_scores["overlays_present"] == 0.0
