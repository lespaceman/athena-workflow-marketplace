"""Reliability report renderer.

This module is the entrypoint dispatched by ``cli.py`` for the ``report``
subcommand. It builds :class:`ReportRow` records from the SQLite projections
and event log, applies sort/filter flags, and renders them as a rich
``rich.Table``, JSONL, and/or Markdown.

The row builder (:func:`build_rows`) is a pure function so it can be exercised
directly in tests without going through the rich/CLI layer.
"""

from __future__ import annotations

import json
import logging
import sqlite3
from collections.abc import Callable
from contextlib import closing
from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from typing import TYPE_CHECKING, Any
from uuid import UUID, uuid4

from rich.console import Console
from rich.table import Table

from evals.events.models import ReportGenerated, SkillDiscovered
from evals.events.store import EventStore, SQLiteEventStore
from evals.reporter.jsonl import write_jsonl
from evals.reporter.markdown import render_markdown
from evals.scoring.composite import bucket_scores, reliability_score, tier
from evals.scoring.weights import TIER_THRESHOLDS

if TYPE_CHECKING:
    from evals.config import Settings


log = logging.getLogger(__name__)

_BUCKET_COLUMNS: tuple[str, ...] = ("health", "provenance", "compliance", "security")
_TIER_RANK: dict[str, int] = {name: i for i, (name, _) in enumerate(TIER_THRESHOLDS)}
_TIER_STYLE: dict[str, str] = {
    "S": "bold green",
    "A": "green",
    "B": "yellow",
    "C": "orange3",
    "D": "red",
}


@dataclass(frozen=True, slots=True)
class ReportRow:
    """One row of the reliability report.

    Mirrors what the rich/jsonl/markdown renderers consume. Built once per
    skill from the projections and event log; downstream code never mutates
    it.
    """

    skill_id: str
    repo_url: str
    category: str
    tier: str
    score: float
    bucket_scores: dict[str, float] = field(default_factory=dict)
    evaluator_scores: dict[str, float] = field(default_factory=dict)
    findings: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class ReportFilters:
    sort_by: str = "score"
    filter_category: str | None = None
    min_tier: str | None = None


def build_rows(
    store: EventStore,
    conn: sqlite3.Connection,
    filters: ReportFilters,
) -> list[ReportRow]:
    """Build report rows from projections plus the event log.

    Pure function: no I/O beyond the supplied ``store`` and ``conn``.
    """
    skills = _load_skills(conn)
    evals_by_skill = _load_evals(conn)

    rows: list[ReportRow] = []
    for skill_id, repo_url in skills:
        evaluator_scores, findings = evals_by_skill.get(skill_id, ({}, []))
        category = _category_for_skill(store, skill_id)
        buckets = bucket_scores(evaluator_scores)
        score = reliability_score(evaluator_scores)
        rows.append(
            ReportRow(
                skill_id=skill_id,
                repo_url=repo_url,
                category=category,
                tier=tier(score),
                score=score,
                bucket_scores=buckets,
                evaluator_scores=dict(evaluator_scores),
                findings=list(findings),
            )
        )

    rows = _filter_rows(rows, filters)
    rows.sort(key=_sort_key(filters.sort_by), reverse=_sort_descending(filters.sort_by))
    return rows


def run_report(
    settings: Settings,
    *,
    output_format: str,
    write_all: bool,
    sort_by: str,
    filter_category: str | None,
    min_tier: str | None,
) -> int:
    """Render the reliability report and emit a ``report.generated`` event."""
    store = SQLiteEventStore(settings.db_path)
    conn = sqlite3.connect(settings.db_path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        filters = ReportFilters(
            sort_by=sort_by, filter_category=filter_category, min_tier=min_tier
        )
        rows = build_rows(store, conn, filters)

        run_id = uuid4()
        run_dir = settings.runs_dir / str(run_id)
        formats = _formats_to_emit(output_format, write_all)
        output_paths = _emit(rows, formats, run_dir)

        summary = _composite_summary(rows)
        store.append(_make_report_event(run_id, rows, output_paths, summary))

        log.info(
            "[OK] report rendered: skills=%d S=%d A=%d B=%d C=%d D=%d",
            len(rows),
            summary.get("S", 0),
            summary.get("A", 0),
            summary.get("B", 0),
            summary.get("C", 0),
            summary.get("D", 0),
        )
        return 0
    finally:
        conn.close()
        store.close()


def _formats_to_emit(output_format: str, write_all: bool) -> tuple[str, ...]:
    if write_all:
        return ("rich", "jsonl", "md")
    return (output_format,)


def _emit(rows: list[ReportRow], formats: tuple[str, ...], run_dir: Path) -> list[str]:
    paths: list[str] = []
    for fmt in formats:
        if fmt == "rich":
            _render_rich(rows)
        elif fmt == "jsonl":
            target = run_dir / "report.jsonl"
            write_jsonl(rows, target)
            paths.append(str(target))
        elif fmt == "md":
            target = run_dir / "report.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render_markdown(rows), encoding="utf-8")
            paths.append(str(target))
        else:
            raise ValueError(f"Unknown output_format: {fmt}")
    return paths


def _render_rich(rows: list[ReportRow]) -> None:
    table = Table(title="Skill Reliability Report")
    table.add_column("Skill", overflow="fold")
    table.add_column("Tier", justify="center")
    table.add_column("Score", justify="right")
    for bucket in _BUCKET_COLUMNS:
        table.add_column(bucket.title(), justify="right")
    table.add_column("Findings", overflow="fold")

    for row in rows:
        style = _TIER_STYLE.get(row.tier, "")
        bucket_cells = [f"{row.bucket_scores.get(b, 0.0):.1f}" for b in _BUCKET_COLUMNS]
        findings_cell = "; ".join(row.findings) if row.findings else "-"
        table.add_row(
            row.skill_id,
            f"[{style}]{row.tier}[/{style}]" if style else row.tier,
            f"{row.score:.1f}",
            *bucket_cells,
            findings_cell,
        )

    Console().print(table)


def _composite_summary(rows: list[ReportRow]) -> dict[str, int]:
    summary: dict[str, int] = {name: 0 for name, _ in TIER_THRESHOLDS}
    for row in rows:
        summary[row.tier] = summary.get(row.tier, 0) + 1
    return summary


def _make_report_event(
    run_id: UUID,
    rows: list[ReportRow],
    output_paths: list[str],
    summary: dict[str, int],
) -> ReportGenerated:
    now = datetime.now(UTC)
    dedupe_input = f"{run_id}|report|{','.join(sorted(output_paths))}"
    return ReportGenerated(
        event_id=uuid4(),
        occurred_at=now,
        run_id=run_id,
        skill_id="*",
        dedupe_key=sha256(dedupe_input.encode()).hexdigest(),
        output_paths=list(output_paths),
        skills_count=len(rows),
        composite_summary=summary,
    )


def _load_skills(conn: sqlite3.Connection) -> list[tuple[str, str]]:
    with closing(conn.cursor()) as cur:
        cur.execute("SELECT skill_id, repo_url FROM skills_current ORDER BY skill_id")
        return [(row["skill_id"], row["repo_url"]) for row in cur.fetchall()]


def _load_evals(
    conn: sqlite3.Connection,
) -> dict[str, tuple[dict[str, float], list[str]]]:
    """Aggregate completed evaluator scores and findings keyed by ``skill_id``."""
    out: dict[str, tuple[dict[str, float], list[str]]] = {}
    with closing(conn.cursor()) as cur:
        cur.execute(
            """
            SELECT skill_id, evaluator, score, findings
            FROM evals_current
            WHERE status = 'completed'
            ORDER BY skill_id, evaluator
            """
        )
        for row in cur.fetchall():
            scores, findings = out.setdefault(row["skill_id"], ({}, []))
            if row["score"] is not None:
                scores[row["evaluator"]] = float(row["score"])
            findings.extend(_decode_findings(row["findings"]))
    return out


def _decode_findings(raw: str | None) -> list[str]:
    if not raw:
        return []
    try:
        decoded = json.loads(raw)
    except json.JSONDecodeError:
        return []
    if not isinstance(decoded, list):
        return []
    return [str(item) for item in decoded]


def _category_for_skill(store: EventStore, skill_id: str) -> str:
    """Latest ``initial_metadata.category`` from the skill's discovery events."""
    category = "uncategorized"
    for event in store.read_for_skill(skill_id):
        if isinstance(event, SkillDiscovered):
            value = event.initial_metadata.get("category")
            if value:
                category = value
    return category


def _filter_rows(rows: list[ReportRow], filters: ReportFilters) -> list[ReportRow]:
    out = rows
    if filters.filter_category is not None:
        out = [r for r in out if r.category == filters.filter_category]
    if filters.min_tier is not None:
        threshold = _TIER_RANK.get(filters.min_tier)
        if threshold is None:
            raise ValueError(f"Unknown tier: {filters.min_tier}")
        out = [r for r in out if _TIER_RANK.get(r.tier, len(_TIER_RANK)) <= threshold]
    return out


def _sort_descending(sort_by: str) -> bool:
    # Numeric sorts (score, bucket cells) read more naturally descending;
    # alphabetic sorts (skill, tier name) read ascending.
    return sort_by not in {"skill", "tier"}


def _sort_key(sort_by: str) -> Callable[[ReportRow], Any]:
    if sort_by == "skill":
        return lambda r: r.skill_id
    if sort_by == "tier":
        return lambda r: _TIER_RANK.get(r.tier, len(_TIER_RANK))
    if sort_by in _BUCKET_COLUMNS:
        return lambda r: r.bucket_scores.get(sort_by, 0.0)
    # Default (including "score" or any unknown key) sorts by score for
    # deterministic output.
    return lambda r: r.score
