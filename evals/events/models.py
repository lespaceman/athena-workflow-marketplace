from datetime import datetime
from hashlib import sha256
from typing import Annotated, Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class _EventBase(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    event_id: UUID
    occurred_at: datetime
    run_id: UUID
    skill_id: str
    schema_version: int = 1
    dedupe_key: str


class SkillDiscovered(_EventBase):
    event_type: Literal["skill.discovered"] = "skill.discovered"
    source_registry: str
    repo_url: str
    initial_metadata: dict[str, str] = Field(default_factory=dict)


class SkillExtracted(_EventBase):
    event_type: Literal["skill.extracted"] = "skill.extracted"
    skill_md_sha: str
    frontmatter: dict[str, object]
    overlays: dict[str, str | None]
    content_hash: str


class EvalRequested(_EventBase):
    event_type: Literal["eval.requested"] = "eval.requested"
    evaluator: str
    evaluator_version: str
    phase: int
    inputs_hash: str


class EvalStarted(_EventBase):
    event_type: Literal["eval.started"] = "eval.started"
    evaluator: str
    evaluator_version: str
    worker_id: str


class EvalProgress(_EventBase):
    event_type: Literal["eval.progress"] = "eval.progress"
    evaluator: str
    pct: float
    note: str | None = None


class EvalCompleted(_EventBase):
    event_type: Literal["eval.completed"] = "eval.completed"
    evaluator: str
    evaluator_version: str
    score: float
    sub_scores: dict[str, float] = Field(default_factory=dict)
    findings: list[str] = Field(default_factory=list)
    cost_usd: float = 0.0
    duration_ms: int = 0


class EvalFailed(_EventBase):
    event_type: Literal["eval.failed"] = "eval.failed"
    evaluator: str
    error_class: str
    error_message: str
    retriable: bool = False


class ReportGenerated(_EventBase):
    event_type: Literal["report.generated"] = "report.generated"
    output_paths: list[str] = Field(default_factory=list)
    skills_count: int = 0
    composite_summary: dict[str, int] = Field(default_factory=dict)


Event = Annotated[
    (
        SkillDiscovered
        | SkillExtracted
        | EvalRequested
        | EvalStarted
        | EvalProgress
        | EvalCompleted
        | EvalFailed
        | ReportGenerated
    ),
    Field(discriminator="event_type"),
]


_TYPE_MAP: dict[str, type[BaseModel]] = {
    "skill.discovered": SkillDiscovered,
    "skill.extracted": SkillExtracted,
    "eval.requested": EvalRequested,
    "eval.started": EvalStarted,
    "eval.progress": EvalProgress,
    "eval.completed": EvalCompleted,
    "eval.failed": EvalFailed,
    "report.generated": ReportGenerated,
}


def event_from_payload(event_type: str, payload: dict[str, object]) -> Event:
    cls = _TYPE_MAP.get(event_type)
    if cls is None:
        raise ValueError(f"Unknown event_type: {event_type}")
    return cls.model_validate(payload)  # type: ignore[return-value]


def dedupe_key(skill_id: str, evaluator: str, version: str, inputs_hash: str) -> str:
    return sha256(f"{skill_id}|{evaluator}@{version}|{inputs_hash}".encode()).hexdigest()
