import json
import sqlite3
from collections.abc import Iterable, Iterator
from contextlib import closing
from pathlib import Path
from typing import Protocol

from evals.events.models import Event, event_from_payload

MIGRATION_FILE = Path(__file__).parent / "migrations" / "0001_init.sql"


class EventStore(Protocol):
    def append(self, event: Event) -> bool: ...
    def read_since(
        self,
        cursor: int | None = None,
        types: Iterable[str] | None = None,
    ) -> Iterator[tuple[int, Event]]: ...
    def read_for_skill(self, skill_id: str) -> Iterator[Event]: ...
    def has_dedupe_key(self, key: str) -> bool: ...


class SQLiteEventStore:
    def __init__(self, path: Path | str) -> None:
        self._path = Path(path)
        self._path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self._path, isolation_level=None)
        self._conn.row_factory = sqlite3.Row
        self._migrate()

    def _migrate(self) -> None:
        ddl = MIGRATION_FILE.read_text()
        with closing(self._conn.cursor()) as cur:
            cur.executescript(ddl)

    def append(self, event: Event) -> bool:
        payload = event.model_dump(mode="json")
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                """
                INSERT OR IGNORE INTO events
                  (event_id, event_type, occurred_at, run_id, skill_id,
                   schema_version, dedupe_key, payload)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(event.event_id),
                    event.event_type,
                    event.occurred_at.isoformat(),
                    str(event.run_id),
                    event.skill_id,
                    event.schema_version,
                    event.dedupe_key,
                    json.dumps(payload),
                ),
            )
            return cur.rowcount > 0

    def read_since(
        self,
        cursor: int | None = None,
        types: Iterable[str] | None = None,
    ) -> Iterator[tuple[int, Event]]:
        sql = "SELECT seq, event_type, payload FROM events WHERE seq > ?"
        params: list[object] = [cursor or 0]
        type_list = list(types) if types is not None else None
        if type_list:
            placeholders = ",".join("?" for _ in type_list)
            sql += f" AND event_type IN ({placeholders})"
            params.extend(type_list)
        sql += " ORDER BY seq ASC"
        with closing(self._conn.cursor()) as cur:
            cur.execute(sql, params)
            for row in cur.fetchall():
                yield row["seq"], event_from_payload(row["event_type"], json.loads(row["payload"]))

    def read_for_skill(self, skill_id: str) -> Iterator[Event]:
        with closing(self._conn.cursor()) as cur:
            cur.execute(
                "SELECT event_type, payload FROM events WHERE skill_id = ? ORDER BY seq ASC",
                (skill_id,),
            )
            for row in cur.fetchall():
                yield event_from_payload(row["event_type"], json.loads(row["payload"]))

    def has_dedupe_key(self, key: str) -> bool:
        with closing(self._conn.cursor()) as cur:
            cur.execute("SELECT 1 FROM events WHERE dedupe_key = ? LIMIT 1", (key,))
            return cur.fetchone() is not None

    def close(self) -> None:
        self._conn.close()
