import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from evals.config import Settings
from evals.events.models import (
    EvalCompleted,
    ReportGenerated,
    SkillDiscovered,
    dedupe_key,
)
from evals.events.projections import rebuild_projections
from evals.events.store import SQLiteEventStore
from evals.reporter.jsonl import write_jsonl
from evals.reporter.markdown import render_markdown
from evals.reporter.table import (
    ReportFilters,
    ReportRow,
    build_rows,
    run_report,
)

SKILL_HIGH = "acme/example#skills/highly-rated"
SKILL_LOW = "other/sample#skills/just-okay"
REPO_HIGH = "https://github.com/acme/example"
REPO_LOW = "https://github.com/other/sample"


def _settings(db_path: Path, runs_dir: Path) -> Settings:
    return Settings(
        github_token=None,
        anthropic_api_key=None,
        judge_model="test-model",
        cost_cap_usd=0.0,
        db_path=db_path,
        data_dir=db_path.parent,
        runs_dir=runs_dir,
    )


def _seed_skill(
    store: SQLiteEventStore,
    *,
    skill_id: str,
    repo_url: str,
    category: str,
) -> None:
    run_id = uuid4()
    store.append(
        SkillDiscovered(
            event_id=uuid4(),
            occurred_at=datetime.now(UTC),
            run_id=run_id,
            skill_id=skill_id,
            dedupe_key=dedupe_key(skill_id, "discovery", "1", repo_url),
            source_registry="seeds.yaml",
            repo_url=repo_url,
            initial_metadata={"category": category},
        )
    )


def _seed_eval(
    store: SQLiteEventStore,
    *,
    skill_id: str,
    evaluator: str,
    score: float,
    findings: list[str] | None = None,
) -> None:
    store.append(
        EvalCompleted(
            event_id=uuid4(),
            occurred_at=datetime.now(UTC),
            run_id=uuid4(),
            skill_id=skill_id,
            dedupe_key=dedupe_key(skill_id, evaluator, "1.0.0", f"r-{evaluator}"),
            evaluator=evaluator,
            evaluator_version="1.0.0",
            score=score,
            sub_scores={},
            findings=findings or [],
        )
    )


@pytest.fixture
def populated_db(tmp_path: Path) -> Path:
    db_path = tmp_path / "evals.db"
    store = SQLiteEventStore(db_path)
    try:
        _seed_skill(
            store,
            skill_id=SKILL_HIGH,
            repo_url=REPO_HIGH,
            category="testing",
        )
        # All buckets at 100 -> tier S.
        for evaluator in (
            "repo-health",
            "release-cadence",
            "follower-authenticity",
            "contributor-authenticity",
            "compliance-check",
            "cross-runtime",
            "live-validator",
            "report-quality",
            "security-scan",
        ):
            _seed_eval(
                store,
                skill_id=SKILL_HIGH,
                evaluator=evaluator,
                score=100.0,
                findings=["all-good"] if evaluator == "compliance-check" else None,
            )

        _seed_skill(
            store,
            skill_id=SKILL_LOW,
            repo_url=REPO_LOW,
            category="docs",
        )
        # Mixed scores -> tier C.
        _seed_eval(store, skill_id=SKILL_LOW, evaluator="repo-health", score=60.0)
        _seed_eval(store, skill_id=SKILL_LOW, evaluator="release-cadence", score=60.0)
        _seed_eval(
            store,
            skill_id=SKILL_LOW,
            evaluator="compliance-check",
            score=70.0,
            findings=["frontmatter-incomplete"],
        )
        _seed_eval(store, skill_id=SKILL_LOW, evaluator="security-scan", score=50.0)
    finally:
        store.close()

    settings = _settings(db_path, tmp_path / "runs")
    rebuild_projections(settings, full=True)
    return db_path


def test_build_rows_produces_expected_categories_and_tiers(populated_db: Path) -> None:
    store = SQLiteEventStore(populated_db)
    conn = sqlite3.connect(populated_db, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        rows = build_rows(store, conn, ReportFilters())
    finally:
        conn.close()
        store.close()

    by_id = {r.skill_id: r for r in rows}
    assert set(by_id) == {SKILL_HIGH, SKILL_LOW}

    high = by_id[SKILL_HIGH]
    assert high.category == "testing"
    assert high.tier == "S"
    assert high.score == pytest.approx(100.0)
    assert high.bucket_scores["health"] == pytest.approx(100.0)
    assert "all-good" in high.findings

    low = by_id[SKILL_LOW]
    assert low.category == "docs"
    assert low.tier in {"C", "D"}
    assert low.bucket_scores["security"] == pytest.approx(50.0)


def test_build_rows_filters_by_min_tier_and_category(populated_db: Path) -> None:
    store = SQLiteEventStore(populated_db)
    conn = sqlite3.connect(populated_db, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        only_s = build_rows(store, conn, ReportFilters(min_tier="A"))
        only_docs = build_rows(store, conn, ReportFilters(filter_category="docs"))
    finally:
        conn.close()
        store.close()

    assert [r.skill_id for r in only_s] == [SKILL_HIGH]
    assert [r.skill_id for r in only_docs] == [SKILL_LOW]


def test_build_rows_sorts_descending_by_score_by_default(populated_db: Path) -> None:
    store = SQLiteEventStore(populated_db)
    conn = sqlite3.connect(populated_db, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        rows = build_rows(store, conn, ReportFilters())
    finally:
        conn.close()
        store.close()

    assert [r.skill_id for r in rows] == [SKILL_HIGH, SKILL_LOW]


def test_render_markdown_groups_by_tier_and_emits_details(populated_db: Path) -> None:
    store = SQLiteEventStore(populated_db)
    conn = sqlite3.connect(populated_db, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        rows = build_rows(store, conn, ReportFilters())
    finally:
        conn.close()
        store.close()

    md = render_markdown(rows)
    assert md.startswith("# Skill Reliability Report")
    # One <details> block per skill.
    assert md.count("<details>") == len(rows)
    assert md.count("</details>") == len(rows)
    # The S tier heading is present for the high-scoring skill.
    assert "## Tier S" in md
    assert SKILL_HIGH in md
    assert SKILL_LOW in md


def test_write_jsonl_round_trips(tmp_path: Path) -> None:
    rows = [
        ReportRow(
            skill_id="x/y#z",
            repo_url="https://github.com/x/y",
            category="testing",
            tier="S",
            score=99.0,
            bucket_scores={"health": 100.0},
            evaluator_scores={"repo-health": 100.0},
            findings=["clean"],
        ),
        ReportRow(
            skill_id="a/b#c",
            repo_url="https://github.com/a/b",
            category="docs",
            tier="C",
            score=62.0,
            bucket_scores={"health": 60.0},
            evaluator_scores={"repo-health": 60.0},
            findings=[],
        ),
    ]
    target = tmp_path / "out.jsonl"
    write_jsonl(rows, target)

    decoded = [json.loads(line) for line in target.read_text().splitlines() if line]
    assert len(decoded) == 2
    assert decoded[0]["skill_id"] == "x/y#z"
    assert decoded[0]["bucket_scores"] == {"health": 100.0}
    assert decoded[1]["tier"] == "C"
    assert decoded[1]["findings"] == []


def test_run_report_rich_emits_event_and_returns_zero(
    populated_db: Path, tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    settings = _settings(populated_db, tmp_path / "runs")
    rc = run_report(
        settings,
        output_format="rich",
        write_all=False,
        sort_by="score",
        filter_category=None,
        min_tier=None,
    )
    assert rc == 0
    # rich.Console writes to stdout by default; just assert non-empty.
    captured = capsys.readouterr()
    assert captured.out.strip() != ""

    store = SQLiteEventStore(populated_db)
    try:
        events = [
            event
            for _, event in store.read_since(cursor=0, types=["report.generated"])
        ]
    finally:
        store.close()
    assert events, "expected at least one report.generated event"
    assert isinstance(events[-1], ReportGenerated)
    assert events[-1].skills_count == 2
    assert events[-1].composite_summary.get("S") == 1


def test_run_report_write_all_creates_three_outputs(
    populated_db: Path, tmp_path: Path
) -> None:
    runs_dir = tmp_path / "runs"
    settings = _settings(populated_db, runs_dir)
    rc = run_report(
        settings,
        output_format="rich",
        write_all=True,
        sort_by="score",
        filter_category=None,
        min_tier=None,
    )
    assert rc == 0

    children = list(runs_dir.iterdir())
    assert len(children) == 1
    run_dir = children[0]
    assert (run_dir / "report.jsonl").exists()
    assert (run_dir / "report.md").exists()
