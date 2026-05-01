from datetime import UTC, datetime
from pathlib import Path
from uuid import uuid4

from evals.config import Settings
from evals.events.models import SkillDiscovered, dedupe_key
from evals.events.store import SQLiteEventStore
from evals.seeds.loader import load_seeds


def run_discover(settings: Settings, seeds_path: Path | None = None) -> int:
    store = SQLiteEventStore(settings.db_path)
    try:
        run_id = uuid4()
        candidates = load_seeds(seeds_path)
        new_count = 0
        duplicate_count = 0
        now = datetime.now(UTC)
        for candidate in candidates:
            event = SkillDiscovered(
                event_id=uuid4(),
                occurred_at=now,
                run_id=run_id,
                skill_id=candidate.skill_id,
                dedupe_key=dedupe_key(
                    candidate.skill_id, "discovery", "1", candidate.repo_url
                ),
                source_registry=candidate.source_registry,
                repo_url=candidate.repo_url,
                initial_metadata={
                    "category": candidate.category,
                    "publisher_type": candidate.publisher_type,
                    "skill_path": candidate.skill_path,
                },
            )
            if store.append(event):
                new_count += 1
            else:
                duplicate_count += 1
        total = new_count + duplicate_count
        print(
            f"[OK] discovered: new={new_count} duplicate={duplicate_count} total={total}"
        )
        return 0
    finally:
        store.close()
