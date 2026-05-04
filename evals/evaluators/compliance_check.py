from __future__ import annotations

from statistics import mean

from evals.evaluators.base import EvalContext, EvalResult, Evaluator, register
from evals.extraction.frontmatter import PORTABLE_FORBIDDEN_KEYS, parse


@register
class ComplianceCheck(Evaluator):
    name = "compliance-check"
    version = "1.0.0"
    phase = 1
    timeout_seconds = 10

    async def evaluate(self, ctx: EvalContext) -> EvalResult:
        parsed = parse(ctx.skill_md)
        findings: list[str] = list(parsed.findings)

        # frontmatter_schema: 1.0 if no ERROR findings, else 0.0.
        has_errors = any(f.startswith("ERROR:") for f in parsed.findings)
        frontmatter_schema = 0.0 if has_errors else 1.0

        # portable_keys: penalize each Claude-only key in the portable SKILL.md.
        violations = sorted(set(parsed.frontmatter) & PORTABLE_FORBIDDEN_KEYS)
        total_forbidden = len(PORTABLE_FORBIDDEN_KEYS)
        portable_keys = (
            1.0 if not violations else max(0.0, 1.0 - (len(violations) / total_forbidden))
        )
        if violations:
            findings.append(f"portable SKILL.md contains Claude-only keys: {', '.join(violations)}")

        # overlays_present: fraction of {claude, openai} overlays present.
        present = sum(1 for k in ("claude", "openai") if ctx.overlays.get(k))
        overlays_present = present / 2.0
        if present < 2:
            findings.append(f"overlays present: {present}/2 (claude/openai)")

        # description_quality: heuristic over length + trigger language + scope statement.
        description = parsed.frontmatter.get("description")
        description_quality = _score_description(
            description if isinstance(description, str) else None,
            findings,
        )

        sub_scores = {
            "frontmatter_schema": frontmatter_schema,
            "portable_keys": portable_keys,
            "overlays_present": overlays_present,
            "description_quality": description_quality,
        }
        score = mean(sub_scores.values()) * 100.0
        return EvalResult(score=score, sub_scores=sub_scores, findings=findings)


def _score_description(description: str | None, findings: list[str]) -> float:
    if not description:
        findings.append("description missing or empty")
        return 0.0
    text = description.lower()
    checks = (
        len(description) >= 100,
        ("trigger" in text) or ("use to" in text),
        ("does not" in text) or ("scope" in text),
    )
    passed = sum(1 for ok in checks if ok)
    if passed < len(checks):
        findings.append(
            f"description heuristic {passed}/{len(checks)}: "
            "want >=100 chars, trigger language, scope statement"
        )
    return passed / len(checks)
