from __future__ import annotations

import math
import re
from collections.abc import Iterable
from statistics import mean

from evals.evaluators.base import EvalContext, EvalResult, Evaluator, register

# Patterns kept tight enough to avoid scanning prose for noise. Findings only
# record offsets — never the matched text — so log sinks cannot leak secrets.
_AWS_KEY_RE = re.compile(r"AKIA[0-9A-Z]{16}")
_GITHUB_PAT_RE = re.compile(r"gh[pousr]_[A-Za-z0-9]{36,}")
_HIGH_ENTROPY_RE = re.compile(r"[a-zA-Z0-9_\-]{40,}")
_PASSWORD_RE = re.compile(r"password\s*[:=]", re.IGNORECASE)
_BEARER_RE = re.compile(r"bearer [A-Za-z0-9._\-]+", re.IGNORECASE)

# Shannon-entropy threshold tuned to flag real high-entropy tokens while letting
# long prose words and snake_case identifiers pass.
_ENTROPY_THRESHOLD = 4.5


@register
class SecurityScan(Evaluator):
    name = "security-scan"
    version = "1.0.0"
    phase = 1
    timeout_seconds = 5

    async def evaluate(self, ctx: EvalContext) -> EvalResult:
        findings: list[str] = []

        secret_hits = list(_find_secret_hits(ctx.skill_md))
        for label, offset in secret_hits:
            findings.append(f"possible secret ({label}) at offset {offset}")
        secret_free = 0.0 if secret_hits else 1.0

        license_present = _score_license(ctx, findings)

        sub_scores = {
            "secret_free": secret_free,
            "license_present": license_present,
        }
        score = mean(sub_scores.values()) * 100.0
        return EvalResult(score=score, sub_scores=sub_scores, findings=findings)


def _find_secret_hits(text: str) -> Iterable[tuple[str, int]]:
    for label, pattern in (
        ("aws-access-key", _AWS_KEY_RE),
        ("github-pat", _GITHUB_PAT_RE),
        ("password-assignment", _PASSWORD_RE),
        ("bearer-token", _BEARER_RE),
    ):
        for match in pattern.finditer(text):
            yield label, match.start()
    for match in _HIGH_ENTROPY_RE.finditer(text):
        token = match.group(0)
        if _shannon_entropy(token) >= _ENTROPY_THRESHOLD:
            yield "high-entropy-token", match.start()


def _shannon_entropy(token: str) -> float:
    if not token:
        return 0.0
    counts: dict[str, int] = {}
    for ch in token:
        counts[ch] = counts.get(ch, 0) + 1
    length = len(token)
    return -sum((c / length) * math.log2(c / length) for c in counts.values())


def _score_license(ctx: EvalContext, findings: list[str]) -> float:
    if ctx.frontmatter.get("license"):
        return 1.0
    repo_license = ctx.repo_metadata.get("license") if ctx.repo_metadata else None
    if repo_license:
        return 1.0
    overlay_mentions_license = any(
        isinstance(v, str) and "license" in v.lower() for v in ctx.overlays.values()
    )
    if overlay_mentions_license:
        return 1.0
    findings.append("no license declared in frontmatter, overlays, or repo metadata")
    return 0.0
