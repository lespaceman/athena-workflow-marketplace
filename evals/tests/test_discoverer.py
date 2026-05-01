from pathlib import Path

import pytest

from evals.config import Settings
from evals.events.models import SkillDiscovered
from evals.events.store import SQLiteEventStore
from evals.extraction.discoverer import run_discover

SEEDS_YAML = """\
skills:
  - skill_id: acme/example#skills/foo
    repo_url: https://github.com/acme/example
    skill_path: skills/foo
    category: react
    publisher_type: community
    source_registry: test-registry
  - skill_id: acme/example#skills/bar
    repo_url: https://github.com/acme/example
    skill_path: skills/bar
    category: java-spring-boot
    publisher_type: official
    source_registry: test-registry
"""


@pytest.fixture
def seeds_path(tmp_path: Path) -> Path:
    p = tmp_path / "seeds.yaml"
    p.write_text(SEEDS_YAML)
    return p


@pytest.fixture
def settings(db_path: Path) -> Settings:
    return Settings(
        github_token=None,
        anthropic_api_key=None,
        judge_model="test",
        cost_cap_usd=0.0,
        db_path=db_path,
    )


def test_run_discover_creates_events_for_each_seed(settings, seeds_path, capsys):
    rc = run_discover(settings, seeds_path=seeds_path)
    assert rc == 0
    out = capsys.readouterr().out
    assert "[OK] discovered: new=2 duplicate=0 total=2" in out

    store = SQLiteEventStore(settings.db_path)
    try:
        events = [
            event for _, event in store.read_since(cursor=0, types=["skill.discovered"])
        ]
    finally:
        store.close()

    assert len(events) == 2
    assert all(isinstance(e, SkillDiscovered) for e in events)
    skill_ids = {e.skill_id for e in events}
    assert skill_ids == {"acme/example#skills/foo", "acme/example#skills/bar"}
    foo = next(e for e in events if e.skill_id == "acme/example#skills/foo")
    assert foo.source_registry == "test-registry"
    assert foo.repo_url == "https://github.com/acme/example"
    assert foo.initial_metadata["category"] == "react"
    assert foo.initial_metadata["skill_path"] == "skills/foo"
    assert foo.initial_metadata["publisher_type"] == "community"


def test_run_discover_is_idempotent(settings, seeds_path, capsys):
    assert run_discover(settings, seeds_path=seeds_path) == 0
    capsys.readouterr()
    assert run_discover(settings, seeds_path=seeds_path) == 0
    out = capsys.readouterr().out
    assert "new=0 duplicate=2 total=2" in out

    store = SQLiteEventStore(settings.db_path)
    try:
        events = list(store.read_since(cursor=0, types=["skill.discovered"]))
    finally:
        store.close()
    assert len(events) == 2
