import base64
from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

import httpx
import pytest
import respx

from evals.config import Settings
from evals.events.models import SkillDiscovered, SkillExtracted, dedupe_key
from evals.events.store import SQLiteEventStore
from evals.extraction.extractor import run_extract

SKILL_MD = (Path(__file__).parent / "fixtures" / "skills" / "good.md").read_text()


def _b64(text: str) -> str:
    return base64.b64encode(text.encode("utf-8")).decode("ascii")


def _contents_payload(text: str, path: str) -> dict[str, object]:
    return {
        "name": Path(path).name,
        "path": path,
        "type": "file",
        "encoding": "base64",
        "content": _b64(text),
    }


def _future_reset() -> str:
    return str(int(datetime.now(UTC).timestamp()) + 3600)


def _seed_discovered(store: SQLiteEventStore, skill_id: str, repo_url: str, skill_path: str):
    event = SkillDiscovered(
        event_id=uuid4(),
        occurred_at=datetime.now(UTC),
        run_id=uuid4(),
        skill_id=skill_id,
        dedupe_key=dedupe_key(skill_id, "discovery", "1", repo_url),
        source_registry="seeds.yaml",
        repo_url=repo_url,
        initial_metadata={
            "category": "java-spring-boot",
            "publisher_type": "individual",
            "skill_path": skill_path,
        },
    )
    store.append(event)


@pytest.fixture
def settings(db_path: Path) -> Settings:
    return Settings(
        github_token=None,
        anthropic_api_key=None,
        judge_model="test",
        cost_cap_usd=0.0,
        db_path=db_path,
    )


def test_run_extract_emits_skill_extracted(settings, capsys):
    skill_id = "acme/example#skills/foo"
    store = SQLiteEventStore(settings.db_path)
    try:
        _seed_discovered(
            store,
            skill_id=skill_id,
            repo_url="https://github.com/acme/example",
            skill_path="skills/foo",
        )
    finally:
        store.close()

    headers = {
        "X-RateLimit-Remaining": "4999",
        "X-RateLimit-Reset": _future_reset(),
    }
    with respx.mock(base_url="https://api.github.com") as mock:
        mock.get("/repos/acme/example/contents/skills/foo/SKILL.md").mock(
            return_value=httpx.Response(
                200,
                json=_contents_payload(SKILL_MD, "skills/foo/SKILL.md"),
                headers=headers,
            )
        )
        mock.get("/repos/acme/example/contents/skills/foo/agents/claude.yaml").mock(
            return_value=httpx.Response(
                404, json={"message": "Not Found"}, headers=headers
            )
        )
        mock.get("/repos/acme/example/contents/skills/foo/agents/openai.yaml").mock(
            return_value=httpx.Response(
                404, json={"message": "Not Found"}, headers=headers
            )
        )
        rc = run_extract(settings)
    assert rc == 0
    out = capsys.readouterr().out
    assert "[OK] extracted: new=1 duplicate=0 failed=0" in out

    store = SQLiteEventStore(settings.db_path)
    try:
        extracted = [
            e for e in store.read_for_skill(skill_id) if isinstance(e, SkillExtracted)
        ]
    finally:
        store.close()

    assert len(extracted) == 1
    ev = extracted[0]
    assert ev.frontmatter["name"] == "define-regression-scope"
    assert "description" in ev.frontmatter
    assert ev.overlays == {"claude": None, "openai": None}
    assert len(ev.content_hash) == 64
    assert len(ev.skill_md_sha) == 64


def test_run_extract_is_idempotent(settings, capsys):
    skill_id = "acme/example#skills/foo"
    store = SQLiteEventStore(settings.db_path)
    try:
        _seed_discovered(
            store,
            skill_id=skill_id,
            repo_url="https://github.com/acme/example",
            skill_path="skills/foo",
        )
    finally:
        store.close()

    headers = {
        "X-RateLimit-Remaining": "4999",
        "X-RateLimit-Reset": _future_reset(),
    }
    with respx.mock(base_url="https://api.github.com") as mock:
        mock.get("/repos/acme/example/contents/skills/foo/SKILL.md").mock(
            return_value=httpx.Response(
                200,
                json=_contents_payload(SKILL_MD, "skills/foo/SKILL.md"),
                headers=headers,
            )
        )
        mock.get("/repos/acme/example/contents/skills/foo/agents/claude.yaml").mock(
            return_value=httpx.Response(
                404, json={"message": "Not Found"}, headers=headers
            )
        )
        mock.get("/repos/acme/example/contents/skills/foo/agents/openai.yaml").mock(
            return_value=httpx.Response(
                404, json={"message": "Not Found"}, headers=headers
            )
        )
        assert run_extract(settings) == 0
        capsys.readouterr()
        assert run_extract(settings) == 0
        out = capsys.readouterr().out

    assert "new=0 duplicate=1 failed=0" in out

    store = SQLiteEventStore(settings.db_path)
    try:
        extracted = [
            e for e in store.read_for_skill(skill_id) if isinstance(e, SkillExtracted)
        ]
    finally:
        store.close()
    assert len(extracted) == 1


def test_run_extract_with_overlays_includes_shas(settings, capsys):
    skill_id = "acme/example#skills/foo"
    store = SQLiteEventStore(settings.db_path)
    try:
        _seed_discovered(
            store,
            skill_id=skill_id,
            repo_url="https://github.com/acme/example",
            skill_path="skills/foo",
        )
    finally:
        store.close()

    headers = {
        "X-RateLimit-Remaining": "4999",
        "X-RateLimit-Reset": _future_reset(),
    }
    claude_yaml = "argument-hint: <release>\nuser-invocable: true\n"
    openai_yaml = "display_name: Foo\nshort_description: bar\n"
    with respx.mock(base_url="https://api.github.com") as mock:
        mock.get("/repos/acme/example/contents/skills/foo/SKILL.md").mock(
            return_value=httpx.Response(
                200,
                json=_contents_payload(SKILL_MD, "skills/foo/SKILL.md"),
                headers=headers,
            )
        )
        mock.get("/repos/acme/example/contents/skills/foo/agents/claude.yaml").mock(
            return_value=httpx.Response(
                200,
                json=_contents_payload(claude_yaml, "skills/foo/agents/claude.yaml"),
                headers=headers,
            )
        )
        mock.get("/repos/acme/example/contents/skills/foo/agents/openai.yaml").mock(
            return_value=httpx.Response(
                200,
                json=_contents_payload(openai_yaml, "skills/foo/agents/openai.yaml"),
                headers=headers,
            )
        )
        rc = run_extract(settings)

    assert rc == 0
    capsys.readouterr()

    store = SQLiteEventStore(settings.db_path)
    try:
        extracted = [
            e for e in store.read_for_skill(skill_id) if isinstance(e, SkillExtracted)
        ]
    finally:
        store.close()
    assert len(extracted) == 1
    ev = extracted[0]
    assert ev.overlays["claude"] is not None
    assert ev.overlays["openai"] is not None
    assert len(ev.overlays["claude"]) == 64
