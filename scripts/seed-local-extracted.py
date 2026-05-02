#!/usr/bin/env python3
"""Seed skill.discovered + skill.extracted events from local plugins/<p>/skills/<s>/SKILL.md.

Useful for exercising the eval+report stages without GitHub API access. Each
plugin skill becomes one synthetic skill_id of the form
``athena/<plugin>#<skill_path>``. Existing events (matched by dedupe_key) are
left in place — the underlying SQLiteEventStore uses INSERT OR IGNORE.
"""
from __future__ import annotations

import sys
from datetime import UTC, datetime
from hashlib import sha256
from pathlib import Path
from uuid import uuid4

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from evals.config import load_settings  # noqa: E402
from evals.events.models import SkillDiscovered, SkillExtracted, dedupe_key  # noqa: E402
from evals.events.store import SQLiteEventStore  # noqa: E402
from evals.extraction.frontmatter import parse  # noqa: E402


def main() -> int:
    settings = load_settings()
    store = SQLiteEventStore(settings.db_path)
    run_id = uuid4()
    now = datetime.now(UTC)

    skills_root = REPO_ROOT / "plugins"
    discovered_new = 0
    extracted_new = 0

    for skill_md in sorted(skills_root.glob("*/skills/*/SKILL.md")):
        plugin = skill_md.parent.parent.parent.name
        skill_dir = skill_md.parent
        skill_name = skill_dir.name
        skill_path = f"skills/{skill_name}"
        skill_id = f"athena/{plugin}#{skill_path}"
        repo_url = f"file://{REPO_ROOT}/plugins/{plugin}"

        discovered = SkillDiscovered(
            event_id=uuid4(),
            occurred_at=now,
            run_id=run_id,
            skill_id=skill_id,
            dedupe_key=dedupe_key(skill_id, "discovery", "1", repo_url),
            source_registry="local",
            repo_url=repo_url,
            initial_metadata={
                "category": plugin,
                "publisher_type": "local",
                "skill_path": skill_path,
            },
        )
        if store.append(discovered):
            discovered_new += 1

        skill_md_bytes = skill_md.read_bytes()
        claude_yaml = skill_dir / "agents" / "claude.yaml"
        openai_yaml = skill_dir / "agents" / "openai.yaml"
        claude_bytes = claude_yaml.read_bytes() if claude_yaml.exists() else None
        openai_bytes = openai_yaml.read_bytes() if openai_yaml.exists() else None

        skill_md_sha = sha256(skill_md_bytes).hexdigest()
        claude_sha = sha256(claude_bytes).hexdigest() if claude_bytes else None
        openai_sha = sha256(openai_bytes).hexdigest() if openai_bytes else None
        content_hash = sha256(
            skill_md_bytes + (claude_bytes or b"") + (openai_bytes or b"")
        ).hexdigest()

        parsed = parse(skill_md_bytes.decode("utf-8"))

        extracted = SkillExtracted(
            event_id=uuid4(),
            occurred_at=now,
            run_id=run_id,
            skill_id=skill_id,
            dedupe_key=dedupe_key(skill_id, "extract", "1", content_hash),
            skill_md_sha=skill_md_sha,
            frontmatter=parsed.frontmatter,
            overlays={"claude": claude_sha, "openai": openai_sha},
            content_hash=content_hash,
        )
        if store.append(extracted):
            extracted_new += 1

    store.close()
    print(f"[OK] seeded local: discovered_new={discovered_new} extracted_new={extracted_new}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
