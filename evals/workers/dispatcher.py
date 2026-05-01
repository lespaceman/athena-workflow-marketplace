from __future__ import annotations

import asyncio
import logging
import time
from collections.abc import Iterable
from datetime import UTC, datetime
from hashlib import sha256
from uuid import UUID, uuid4

from evals.config import Settings
from evals.evaluators import EVALUATORS
from evals.evaluators.base import EvalContext, EvalResult, Evaluator
from evals.events.models import (
    EvalCompleted,
    EvalFailed,
    EvalRequested,
    EvalStarted,
    SkillExtracted,
    dedupe_key,
)
from evals.events.store import EventStore, SQLiteEventStore
from evals.workers.pool import BoundedRunner

log = logging.getLogger(__name__)

DEFAULT_PHASE = 1
WORKER_ID = "local-1"
MAX_CONCURRENCY = 8


def run_eval(
    settings: Settings,
    *,
    phase: int | None,
    evaluator: str | None,
    judge_model: str,
    cost_cap_usd: float,
    force: bool,
    strict: bool,
) -> int:
    # judge_model and cost_cap_usd are accepted for CLI parity; Phase 1 evaluators
    # are deterministic and do not consume them yet.
    del judge_model, cost_cap_usd

    store = SQLiteEventStore(settings.db_path)
    try:
        return asyncio.run(
            _run_async(
                store=store,
                phase=phase,
                evaluator_name=evaluator,
                force=force,
                strict=strict,
            )
        )
    finally:
        store.close()


async def _run_async(
    *,
    store: EventStore,
    phase: int | None,
    evaluator_name: str | None,
    force: bool,
    strict: bool,
) -> int:
    run_id = uuid4()
    selected = _select_evaluators(phase=phase, evaluator_name=evaluator_name)
    if strict and evaluator_name and evaluator_name not in EVALUATORS:
        log.error("[ERR] requested evaluator %s is not registered", evaluator_name)
        return 1
    if not selected:
        log.warning("[WARN] no evaluators matched (phase=%s evaluator=%s)", phase, evaluator_name)

    skills = list(_latest_extracted_per_skill(store))
    instances: list[Evaluator] = [cls() for cls in selected]

    tasks = _build_tasks(skills=skills, evaluators=instances, force=force, store=store)
    runner = BoundedRunner(max_concurrency=MAX_CONCURRENCY)
    outcomes = await runner.run(
        lambda task: _execute_task(task, run_id=run_id, store=store), list(tasks)
    )

    completed = sum(1 for o in outcomes if o == "completed")
    failed = sum(1 for o in outcomes if o == "failed")
    skipped = sum(1 for o in outcomes if o == "skipped")
    resolved_phase = phase if phase is not None else DEFAULT_PHASE
    log.info(
        "[OK] phase=%d evaluators=%d skills=%d completed=%d failed=%d skipped=%d",
        resolved_phase,
        len(instances),
        len(skills),
        completed,
        failed,
        skipped,
    )
    return 0


def _select_evaluators(
    *, phase: int | None, evaluator_name: str | None
) -> list[type[Evaluator]]:
    if evaluator_name:
        cls = EVALUATORS.get(evaluator_name)
        return [cls] if cls is not None else []
    target_phase = phase if phase is not None else DEFAULT_PHASE
    return [cls for cls in EVALUATORS.values() if cls.phase == target_phase]


def _latest_extracted_per_skill(store: EventStore) -> Iterable[SkillExtracted]:
    latest: dict[str, SkillExtracted] = {}
    for _seq, event in store.read_since(cursor=0, types=["skill.extracted"]):
        if isinstance(event, SkillExtracted):
            latest[event.skill_id] = event
    return latest.values()


class _Task:
    __slots__ = ("skill", "evaluator", "inputs_hash", "ddk")

    def __init__(
        self,
        skill: SkillExtracted,
        evaluator: Evaluator,
        inputs_hash: str,
        ddk: str,
    ) -> None:
        self.skill = skill
        self.evaluator = evaluator
        self.inputs_hash = inputs_hash
        self.ddk = ddk


def _build_tasks(
    *,
    skills: list[SkillExtracted],
    evaluators: list[Evaluator],
    force: bool,
    store: EventStore,
) -> list[_Task]:
    tasks: list[_Task] = []
    for skill in skills:
        for evaluator in evaluators:
            inputs_hash = _inputs_hash(skill.content_hash, evaluator.name)
            ddk = dedupe_key(skill.skill_id, evaluator.name, evaluator.version, inputs_hash)
            if not force and store.has_dedupe_key(ddk):
                log.debug(
                    "[SKIP] %s/%s already evaluated (dedupe hit)",
                    skill.skill_id,
                    evaluator.name,
                )
                continue
            tasks.append(_Task(skill, evaluator, inputs_hash, ddk))
    return tasks


def _inputs_hash(content_hash: str, evaluator_name: str) -> str:
    return sha256(f"{content_hash}|{evaluator_name}".encode()).hexdigest()


async def _execute_task(task: _Task, *, run_id: UUID, store: EventStore) -> str:
    skill = task.skill
    evaluator = task.evaluator

    requested = EvalRequested(
        event_id=uuid4(),
        occurred_at=datetime.now(UTC),
        run_id=run_id,
        skill_id=skill.skill_id,
        dedupe_key=task.ddk,
        evaluator=evaluator.name,
        evaluator_version=evaluator.version,
        phase=evaluator.phase,
        inputs_hash=task.inputs_hash,
    )
    store.append(requested)

    started_ddk = sha256(
        f"started|{skill.skill_id}|{evaluator.name}@{evaluator.version}|{run_id}".encode()
    ).hexdigest()
    started = EvalStarted(
        event_id=uuid4(),
        occurred_at=datetime.now(UTC),
        run_id=run_id,
        skill_id=skill.skill_id,
        dedupe_key=started_ddk,
        evaluator=evaluator.name,
        evaluator_version=evaluator.version,
        worker_id=WORKER_ID,
    )
    store.append(started)

    ctx = EvalContext(
        skill_id=skill.skill_id,
        skill_md=_reconstruct_skill_md(skill),
        frontmatter=dict(skill.frontmatter),
        overlays=dict(skill.overlays),
        repo_metadata={},
        run_id=run_id,
        cost_tracker=None,
    )

    start = time.perf_counter()
    try:
        result = await asyncio.wait_for(
            evaluator.evaluate(ctx), timeout=evaluator.timeout_seconds
        )
    except TimeoutError:
        _emit_failed(
            store=store,
            run_id=run_id,
            skill_id=skill.skill_id,
            evaluator=evaluator,
            error_class="Timeout",
            error_message=f"evaluator exceeded {evaluator.timeout_seconds}s",
            retriable=True,
        )
        return "failed"
    except Exception as exc:
        _emit_failed(
            store=store,
            run_id=run_id,
            skill_id=skill.skill_id,
            evaluator=evaluator,
            error_class=exc.__class__.__name__,
            error_message=str(exc),
            retriable=False,
        )
        return "failed"

    duration_ms = int((time.perf_counter() - start) * 1000)
    _emit_completed(
        store=store,
        run_id=run_id,
        skill_id=skill.skill_id,
        evaluator=evaluator,
        result=result,
        duration_ms=duration_ms,
    )
    return "completed"


def _reconstruct_skill_md(skill: SkillExtracted) -> str:
    # SkillExtracted does not carry the raw body; for Phase 1 evaluators that
    # only need the frontmatter, a reconstructed YAML header is sufficient.
    # Extraction-side improvements can later persist the full body.
    import yaml

    header = yaml.safe_dump(skill.frontmatter, sort_keys=False).strip()
    return f"---\n{header}\n---\n"


def _emit_failed(
    *,
    store: EventStore,
    run_id: UUID,
    skill_id: str,
    evaluator: Evaluator,
    error_class: str,
    error_message: str,
    retriable: bool,
) -> None:
    failed_ddk = sha256(
        f"failed|{skill_id}|{evaluator.name}@{evaluator.version}|{run_id}".encode()
    ).hexdigest()
    store.append(
        EvalFailed(
            event_id=uuid4(),
            occurred_at=datetime.now(UTC),
            run_id=run_id,
            skill_id=skill_id,
            dedupe_key=failed_ddk,
            evaluator=evaluator.name,
            error_class=error_class,
            error_message=error_message,
            retriable=retriable,
        )
    )


def _emit_completed(
    *,
    store: EventStore,
    run_id: UUID,
    skill_id: str,
    evaluator: Evaluator,
    result: EvalResult,
    duration_ms: int,
) -> None:
    completed_ddk = sha256(
        f"completed|{skill_id}|{evaluator.name}@{evaluator.version}|{run_id}".encode()
    ).hexdigest()
    store.append(
        EvalCompleted(
            event_id=uuid4(),
            occurred_at=datetime.now(UTC),
            run_id=run_id,
            skill_id=skill_id,
            dedupe_key=completed_ddk,
            evaluator=evaluator.name,
            evaluator_version=evaluator.version,
            score=result.score,
            sub_scores=result.sub_scores,
            findings=result.findings,
            cost_usd=result.cost_usd,
            duration_ms=duration_ms,
        )
    )
