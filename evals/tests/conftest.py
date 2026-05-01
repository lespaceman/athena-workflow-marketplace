from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import pytest

from evals.events.models import (
    EvalCompleted,
    EvalRequested,
    SkillDiscovered,
    SkillExtracted,
    dedupe_key,
)
from evals.events.store import SQLiteEventStore


@pytest.fixture
def db_path(tmp_path: Path) -> Path:
    return tmp_path / "evals.db"


@pytest.fixture
def store(db_path: Path) -> SQLiteEventStore:
    return SQLiteEventStore(db_path)


@pytest.fixture
def run_id() -> str:
    return str(uuid4())


@pytest.fixture
def now() -> datetime:
    return datetime.now(UTC)


@pytest.fixture
def make_discovered(run_id, now):
    def _make(skill_id="acme/example#skills/x", repo_url="https://github.com/acme/example"):
        return SkillDiscovered(
            event_id=uuid4(),
            occurred_at=now,
            run_id=run_id,
            skill_id=skill_id,
            dedupe_key=dedupe_key(skill_id, "discovery", "1", repo_url),
            source_registry="seeds.yaml",
            repo_url=repo_url,
        )
    return _make


@pytest.fixture
def make_extracted(run_id, now):
    def _make(skill_id="acme/example#skills/x", content_hash="abc123"):
        return SkillExtracted(
            event_id=uuid4(),
            occurred_at=now,
            run_id=run_id,
            skill_id=skill_id,
            dedupe_key=dedupe_key(skill_id, "extract", "1", content_hash),
            skill_md_sha="sha1:" + content_hash,
            frontmatter={"name": "x", "description": "y"},
            overlays={"claude": None, "openai": None},
            content_hash=content_hash,
        )
    return _make


@pytest.fixture
def make_eval_requested(run_id, now):
    def _make(
        skill_id="acme/example#skills/x",
        evaluator="compliance-check",
        version="1.0.0",
        inputs_hash="h",
    ):
        return EvalRequested(
            event_id=uuid4(),
            occurred_at=now,
            run_id=run_id,
            skill_id=skill_id,
            dedupe_key=dedupe_key(skill_id, evaluator, version, inputs_hash),
            evaluator=evaluator,
            evaluator_version=version,
            phase=1,
            inputs_hash=inputs_hash,
        )
    return _make


@pytest.fixture
def make_eval_completed(run_id, now):
    def _make(
        skill_id="acme/example#skills/x",
        evaluator="compliance-check",
        version="1.0.0",
        score=85.0,
    ):
        return EvalCompleted(
            event_id=uuid4(),
            occurred_at=now,
            run_id=run_id,
            skill_id=skill_id,
            dedupe_key=dedupe_key(skill_id, evaluator, version, "result"),
            evaluator=evaluator,
            evaluator_version=version,
            score=score,
            sub_scores={"a": 80.0, "b": 90.0},
            findings=[],
        )
    return _make
