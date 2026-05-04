from __future__ import annotations

import asyncio
from uuid import uuid4

from evals.evaluators.base import EvalContext
from evals.evaluators.security_scan import SecurityScan
from evals.extraction.frontmatter import parse

CLEAN_SKILL_MD = """---
name: clean-skill
description: A safe skill with explicit scope. Use to do things; does NOT touch the network.
license: MIT
---

# Clean

Plain prose without secrets.
"""

# Embedded fake AWS access key — pattern only, not a real credential.
LEAKY_SKILL_MD = """---
name: leaky-skill
description: example
license: MIT
---

# Leaky

Do not commit AKIAIOSFODNN7EXAMPLE to source.
"""

NO_LICENSE_MD = """---
name: no-license
description: example
---

# No license

Plain body.
"""


def _ctx(
    skill_md: str,
    *,
    overlays: dict[str, str | None] | None = None,
    repo_metadata: dict[str, object] | None = None,
) -> EvalContext:
    return EvalContext(
        skill_id="acme/example#skills/x",
        skill_md=skill_md,
        frontmatter=dict(parse(skill_md).frontmatter),
        overlays=overlays or {"claude": None, "openai": None},
        repo_metadata=repo_metadata or {},
        run_id=uuid4(),
    )


def _run(ev, ctx):
    return asyncio.run(ev.evaluate(ctx))


def test_clean_skill_scores_full():
    result = _run(SecurityScan(), _ctx(CLEAN_SKILL_MD))
    assert result.sub_scores["secret_free"] == 1.0
    assert result.sub_scores["license_present"] == 1.0
    assert "allowed_tools_scoped" not in result.sub_scores
    assert "safe_tool_set" not in result.sub_scores
    assert result.score == 100.0


def test_embedded_secret_zeroes_secret_free():
    result = _run(SecurityScan(), _ctx(LEAKY_SKILL_MD))
    assert result.sub_scores["secret_free"] == 0.0
    # Findings reference offset, never the matched literal.
    assert any("offset" in f for f in result.findings)
    assert not any("AKIAIOSFODNN7EXAMPLE" in f for f in result.findings)


def test_missing_license_penalized():
    result = _run(SecurityScan(), _ctx(NO_LICENSE_MD))
    assert result.sub_scores["license_present"] == 0.0


def test_repo_metadata_satisfies_license():
    result = _run(SecurityScan(), _ctx(NO_LICENSE_MD, repo_metadata={"license": "MIT"}))
    assert result.sub_scores["license_present"] == 1.0
