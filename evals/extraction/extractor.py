import asyncio
import sys
from collections.abc import Iterable
from datetime import UTC, datetime
from hashlib import sha256
from urllib.parse import urlparse
from uuid import UUID, uuid4

from evals.config import Settings
from evals.events.models import SkillDiscovered, SkillExtracted, dedupe_key
from evals.events.store import SQLiteEventStore
from evals.extraction.frontmatter import parse
from evals.github.client import GitHubClient, GitHubClientError

_CONCURRENCY = 8


def run_extract(settings: Settings, skill_id: str | None = None) -> int:
    return asyncio.run(_run_extract_async(settings, skill_id))


async def _run_extract_async(settings: Settings, skill_id: str | None) -> int:
    store = SQLiteEventStore(settings.db_path)
    client = GitHubClient(token=settings.github_token)
    try:
        candidates = list(_collect_candidates(store, skill_id))
        if not candidates:
            print("[OK] extracted: new=0 duplicate=0 failed=0")
            return 0

        run_id = uuid4()
        sem = asyncio.Semaphore(_CONCURRENCY)
        results = await asyncio.gather(
            *(
                _extract_one(store, client, sem, run_id, cand)
                for cand in candidates
            ),
            return_exceptions=False,
        )
        new_count = sum(1 for r in results if r == "new")
        duplicate_count = sum(1 for r in results if r == "duplicate")
        failed_count = sum(1 for r in results if r == "failed")
        print(
            f"[OK] extracted: new={new_count} duplicate={duplicate_count} "
            f"failed={failed_count}"
        )
        return 0
    finally:
        await client.aclose()
        store.close()


def _collect_candidates(
    store: SQLiteEventStore, skill_id: str | None
) -> Iterable[SkillDiscovered]:
    seen: set[str] = set()
    if skill_id is not None:
        events = store.read_for_skill(skill_id)
    else:
        events = (event for _, event in store.read_since(cursor=0, types=["skill.discovered"]))
    for event in events:
        if not isinstance(event, SkillDiscovered):
            continue
        if event.skill_id in seen:
            continue
        seen.add(event.skill_id)
        yield event


async def _extract_one(
    store: SQLiteEventStore,
    client: GitHubClient,
    sem: asyncio.Semaphore,
    run_id: UUID,
    candidate: SkillDiscovered,
) -> str:
    async with sem:
        try:
            owner, repo = _parse_repo_url(candidate.repo_url)
        except ValueError as exc:
            print(
                f"[ERROR] extract {candidate.skill_id}: {exc}",
                file=sys.stderr,
            )
            return "failed"

        skill_path = str(candidate.initial_metadata.get("skill_path") or "").strip("/")
        if not skill_path:
            print(
                f"[ERROR] extract {candidate.skill_id}: missing skill_path metadata",
                file=sys.stderr,
            )
            return "failed"

        try:
            skill_md_bytes = await client.get_contents(
                owner, repo, f"{skill_path}/SKILL.md"
            )
        except GitHubClientError as exc:
            print(
                f"[ERROR] extract {candidate.skill_id}: SKILL.md fetch failed: {exc}",
                file=sys.stderr,
            )
            return "failed"

        claude_bytes, openai_bytes = await asyncio.gather(
            _try_get_optional(client, owner, repo, f"{skill_path}/agents/claude.yaml"),
            _try_get_optional(client, owner, repo, f"{skill_path}/agents/openai.yaml"),
        )

        skill_md_text = skill_md_bytes.decode("utf-8")

        skill_md_sha = sha256(skill_md_bytes).hexdigest()
        claude_sha = sha256(claude_bytes).hexdigest() if claude_bytes else None
        openai_sha = sha256(openai_bytes).hexdigest() if openai_bytes else None
        content_hash = sha256(
            skill_md_bytes + (claude_bytes or b"") + (openai_bytes or b"")
        ).hexdigest()

        key = dedupe_key(candidate.skill_id, "extract", "1", content_hash)
        if store.has_dedupe_key(key):
            return "duplicate"

        parsed = parse(skill_md_text)
        event = SkillExtracted(
            event_id=uuid4(),
            occurred_at=datetime.now(UTC),
            run_id=run_id,
            skill_id=candidate.skill_id,
            dedupe_key=key,
            skill_md_sha=skill_md_sha,
            frontmatter=parsed.frontmatter,
            overlays={"claude": claude_sha, "openai": openai_sha},
            content_hash=content_hash,
        )
        appended = store.append(event)
        return "new" if appended else "duplicate"


async def _try_get_optional(
    client: GitHubClient, owner: str, repo: str, path: str
) -> bytes | None:
    try:
        return await client.get_contents(owner, repo, path)
    except GitHubClientError as exc:
        if exc.status == 404:
            return None
        raise


def _parse_repo_url(repo_url: str) -> tuple[str, str]:
    parsed = urlparse(repo_url)
    parts = [p for p in parsed.path.split("/") if p]
    if len(parts) < 2:
        raise ValueError(f"cannot parse owner/repo from {repo_url!r}")
    owner, repo = parts[0], parts[1]
    if repo.endswith(".git"):
        repo = repo[:-4]
    return owner, repo
