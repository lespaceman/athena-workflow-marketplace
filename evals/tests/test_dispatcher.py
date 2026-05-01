from __future__ import annotations

from datetime import UTC, datetime
from uuid import uuid4

import pytest

from evals.config import Settings
from evals.events.models import (
    EvalCompleted,
    EvalRequested,
    EvalStarted,
    SkillDiscovered,
    SkillExtracted,
    dedupe_key,
)
from evals.events.store import SQLiteEventStore
from evals.workers.dispatcher import run_eval

PHASE1_EVALUATORS = {"compliance-check", "security-scan"}


@pytest.fixture
def settings(tmp_path) -> Settings:
    return Settings(
        github_token=None,
        anthropic_api_key=None,
        judge_model="claude-opus-4-7",
        cost_cap_usd=5.0,
        db_path=tmp_path / "evals.db",
    )


def _seed(settings: Settings, skill_id: str = "acme/example#skills/x") -> None:
    store = SQLiteEventStore(settings.db_path)
    try:
        run_id = uuid4()
        now = datetime.now(UTC)
        repo_url = "https://github.com/acme/example"
        store.append(
            SkillDiscovered(
                event_id=uuid4(),
                occurred_at=now,
                run_id=run_id,
                skill_id=skill_id,
                dedupe_key=dedupe_key(skill_id, "discovery", "1", repo_url),
                source_registry="seeds.yaml",
                repo_url=repo_url,
            )
        )
        content_hash = "deadbeef"
        store.append(
            SkillExtracted(
                event_id=uuid4(),
                occurred_at=now,
                run_id=run_id,
                skill_id=skill_id,
                dedupe_key=dedupe_key(skill_id, "extract", "1", content_hash),
                skill_md_sha=f"sha1:{content_hash}",
                frontmatter={
                    "name": "x",
                    "description": (
                        "Use to do a thing. Triggers include 'do the thing'. "
                        "This skill does NOT do other things; scope is narrow."
                    ),
                    "allowed-tools": "Read Write",
                    "license": "MIT",
                },
                overlays={"claude": "yaml-content", "openai": "yaml-content"},
                content_hash=content_hash,
            )
        )
    finally:
        store.close()


def _events_by_type(settings: Settings) -> dict[str, list]:
    store = SQLiteEventStore(settings.db_path)
    try:
        bucket: dict[str, list] = {}
        for _seq, event in store.read_since(cursor=0):
            bucket.setdefault(event.event_type, []).append(event)
        return bucket
    finally:
        store.close()


def test_dispatcher_runs_phase1_evaluators_for_each_skill(settings):
    _seed(settings)

    rc = run_eval(
        settings,
        phase=1,
        evaluator=None,
        judge_model="x",
        cost_cap_usd=0.0,
        force=False,
        strict=False,
    )
    assert rc == 0

    by_type = _events_by_type(settings)
    requested_evaluators = {ev.evaluator for ev in by_type.get("eval.requested", [])}
    started_evaluators = {ev.evaluator for ev in by_type.get("eval.started", [])}
    completed_evaluators = {ev.evaluator for ev in by_type.get("eval.completed", [])}

    assert PHASE1_EVALUATORS.issubset(requested_evaluators)
    assert PHASE1_EVALUATORS.issubset(started_evaluators)
    assert PHASE1_EVALUATORS.issubset(completed_evaluators)

    for ev in by_type["eval.completed"]:
        assert isinstance(ev, EvalCompleted)
        assert 0.0 <= ev.score <= 100.0


def test_dispatcher_dedupes_on_rerun_without_force(settings):
    _seed(settings)
    run_eval(
        settings,
        phase=1,
        evaluator=None,
        judge_model="x",
        cost_cap_usd=0.0,
        force=False,
        strict=False,
    )
    before = _events_by_type(settings)

    run_eval(
        settings,
        phase=1,
        evaluator=None,
        judge_model="x",
        cost_cap_usd=0.0,
        force=False,
        strict=False,
    )
    after = _events_by_type(settings)

    for kind in ("eval.requested", "eval.started", "eval.completed"):
        assert len(after.get(kind, [])) == len(before.get(kind, [])), (
            f"{kind} should not grow on rerun without --force"
        )


def test_dispatcher_force_rerun_emits_new_completed(settings):
    _seed(settings)
    run_eval(
        settings,
        phase=1,
        evaluator=None,
        judge_model="x",
        cost_cap_usd=0.0,
        force=False,
        strict=False,
    )
    before = _events_by_type(settings)

    run_eval(
        settings,
        phase=1,
        evaluator=None,
        judge_model="x",
        cost_cap_usd=0.0,
        force=True,
        strict=False,
    )
    after = _events_by_type(settings)

    # With --force, dispatcher emits a fresh requested+started+completed per task.
    assert len(after["eval.completed"]) > len(before["eval.completed"])


def test_dispatcher_filter_to_single_evaluator(settings):
    _seed(settings)
    rc = run_eval(
        settings,
        phase=None,
        evaluator="compliance-check",
        judge_model="x",
        cost_cap_usd=0.0,
        force=False,
        strict=False,
    )
    assert rc == 0
    by_type = _events_by_type(settings)
    requested_evaluators = {ev.evaluator for ev in by_type.get("eval.requested", [])}
    assert requested_evaluators == {"compliance-check"}


def test_dispatcher_strict_unknown_evaluator(settings):
    _seed(settings)
    rc = run_eval(
        settings,
        phase=None,
        evaluator="not-a-real-evaluator",
        judge_model="x",
        cost_cap_usd=0.0,
        force=False,
        strict=True,
    )
    assert rc == 1


def test_event_payload_shapes(settings):
    _seed(settings)
    run_eval(
        settings,
        phase=1,
        evaluator="compliance-check",
        judge_model="x",
        cost_cap_usd=0.0,
        force=False,
        strict=False,
    )
    by_type = _events_by_type(settings)
    assert all(isinstance(ev, EvalRequested) for ev in by_type["eval.requested"])
    assert all(isinstance(ev, EvalStarted) for ev in by_type["eval.started"])
    assert all(isinstance(ev, EvalCompleted) for ev in by_type["eval.completed"])
