"""Markdown renderer: tier-grouped report with collapsible details per skill."""

from __future__ import annotations

from typing import TYPE_CHECKING

from evals.scoring.weights import TIER_THRESHOLDS

if TYPE_CHECKING:
    from evals.reporter.table import ReportRow


_TIER_ORDER: tuple[str, ...] = tuple(name for name, _ in TIER_THRESHOLDS)


def render_markdown(rows: list[ReportRow]) -> str:
    """Render rows as a Markdown reliability report.

    Layout:

    * ``# Skill Reliability Report`` heading.
    * One ``## Tier <X>`` section per tier (S, A, B, C, D), in that order,
      omitting tiers with no rows.
    * Each skill becomes a ``<details>`` block whose ``<summary>`` shows the
      ``skill_id`` and composite ``score``; the body lists bucket sub-scores
      and findings.
    """
    parts: list[str] = ["# Skill Reliability Report", ""]
    by_tier: dict[str, list[ReportRow]] = {tier: [] for tier in _TIER_ORDER}
    for row in rows:
        # Unknown tiers (e.g. from a future schema) are bucketed into a fresh
        # list so they still appear in the report.
        by_tier.setdefault(row.tier, []).append(row)

    for tier, tier_rows in by_tier.items():
        if not tier_rows:
            continue
        parts.append(f"## Tier {tier}")
        parts.append("")
        for row in tier_rows:
            parts.extend(_render_skill(row))
            parts.append("")
    return "\n".join(parts).rstrip() + "\n"


def _render_skill(row: ReportRow) -> list[str]:
    summary = f"<summary><strong>{row.skill_id}</strong> &mdash; score {row.score:.1f}</summary>"
    lines: list[str] = ["<details>", summary, ""]
    lines.append(f"- Repo: {row.repo_url}")
    lines.append(f"- Category: {row.category}")
    lines.append("- Bucket scores:")
    for bucket in ("health", "provenance", "compliance", "security"):
        value = row.bucket_scores.get(bucket, 0.0)
        lines.append(f"  - {bucket}: {value:.1f}")
    if row.findings:
        lines.append("- Findings:")
        for finding in row.findings:
            lines.append(f"  - {finding}")
    else:
        lines.append("- Findings: none")
    lines.append("")
    lines.append("</details>")
    return lines
