import json
import logging
import sqlite3
from contextlib import closing

from evals.config import Settings
from evals.events.models import (
    EvalCompleted,
    EvalFailed,
    EvalRequested,
    EvalStarted,
    SkillDiscovered,
    SkillExtracted,
)
from evals.events.store import SQLiteEventStore

log = logging.getLogger(__name__)


def rebuild_projections(settings: Settings, full: bool = False) -> int:
    store = SQLiteEventStore(settings.db_path)
    conn = sqlite3.connect(settings.db_path, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        if full:
            with closing(conn.cursor()) as cur:
                cur.execute("DELETE FROM skills_current")
                cur.execute("DELETE FROM evals_current")

        skills_count = 0
        evals_count = 0
        for seq, event in store.read_since(cursor=0):
            if isinstance(event, SkillDiscovered):
                _upsert_skill_discovered(conn, seq, event)
                skills_count += 1
            elif isinstance(event, SkillExtracted):
                _upsert_skill_extracted(conn, seq, event)
            elif isinstance(event, EvalRequested):
                _upsert_eval_status(
                    conn, event.skill_id, event.evaluator, event.evaluator_version, "requested"
                )
                evals_count += 1
            elif isinstance(event, EvalStarted):
                _upsert_eval_status(
                    conn, event.skill_id, event.evaluator, event.evaluator_version, "started"
                )
            elif isinstance(event, EvalCompleted):
                _upsert_eval_completed(conn, event)
            elif isinstance(event, EvalFailed):
                _upsert_eval_status(conn, event.skill_id, event.evaluator, "*", "failed")

        log.info("[OK] projections rebuilt: skills=%d evals=%d", skills_count, evals_count)
        return 0
    finally:
        conn.close()
        store.close()


def _upsert_skill_discovered(conn: sqlite3.Connection, seq: int, event: SkillDiscovered) -> None:
    with closing(conn.cursor()) as cur:
        cur.execute(
            """
            INSERT INTO skills_current (skill_id, repo_url, last_seq)
            VALUES (?, ?, ?)
            ON CONFLICT(skill_id) DO UPDATE SET
              repo_url = excluded.repo_url,
              last_seq = excluded.last_seq
            """,
            (event.skill_id, event.repo_url, seq),
        )


def _upsert_skill_extracted(conn: sqlite3.Connection, seq: int, event: SkillExtracted) -> None:
    with closing(conn.cursor()) as cur:
        cur.execute(
            """
            INSERT INTO skills_current
              (skill_id, repo_url, last_extracted_at, content_hash, frontmatter, last_seq)
            VALUES (?, '', ?, ?, ?, ?)
            ON CONFLICT(skill_id) DO UPDATE SET
              last_extracted_at = excluded.last_extracted_at,
              content_hash      = excluded.content_hash,
              frontmatter       = excluded.frontmatter,
              last_seq          = excluded.last_seq
            """,
            (
                event.skill_id,
                event.occurred_at.isoformat(),
                event.content_hash,
                json.dumps(event.frontmatter),
                seq,
            ),
        )


def _upsert_eval_status(
    conn: sqlite3.Connection,
    skill_id: str,
    evaluator: str,
    version: str,
    status: str,
) -> None:
    with closing(conn.cursor()) as cur:
        cur.execute(
            """
            INSERT INTO evals_current (skill_id, evaluator, evaluator_version, status)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(skill_id, evaluator, evaluator_version) DO UPDATE SET
              status = excluded.status
            """,
            (skill_id, evaluator, version, status),
        )


def _upsert_eval_completed(conn: sqlite3.Connection, event: EvalCompleted) -> None:
    with closing(conn.cursor()) as cur:
        cur.execute(
            """
            INSERT INTO evals_current
              (skill_id, evaluator, evaluator_version, score, sub_scores, findings,
               status, completed_at, cost_usd)
            VALUES (?, ?, ?, ?, ?, ?, 'completed', ?, ?)
            ON CONFLICT(skill_id, evaluator, evaluator_version) DO UPDATE SET
              score        = excluded.score,
              sub_scores   = excluded.sub_scores,
              findings     = excluded.findings,
              status       = 'completed',
              completed_at = excluded.completed_at,
              cost_usd     = excluded.cost_usd
            """,
            (
                event.skill_id,
                event.evaluator,
                event.evaluator_version,
                event.score,
                json.dumps(event.sub_scores),
                json.dumps(event.findings),
                event.occurred_at.isoformat(),
                event.cost_usd,
            ),
        )
