from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any
from uuid import UUID


@dataclass(frozen=True)
class EvalContext:
    skill_id: str
    skill_md: str
    frontmatter: dict[str, Any]
    overlays: dict[str, str | None]
    repo_metadata: dict[str, Any]
    run_id: UUID
    # CostTracker is not implemented yet (Phase 2 / LLM judge work).
    # Typed loosely so we can swap a concrete class in later without breaking callers.
    cost_tracker: object | None = None


@dataclass(frozen=True)
class EvalResult:
    score: float  # 0..100
    sub_scores: dict[str, float] = field(default_factory=dict)
    findings: list[str] = field(default_factory=list)
    cost_usd: float = 0.0


class Evaluator(ABC):
    name: str = ""
    version: str = ""
    phase: int = 0
    consumes: tuple[str, ...] = ("skill.extracted",)
    timeout_seconds: int = 60

    @abstractmethod
    async def evaluate(self, ctx: EvalContext) -> EvalResult: ...


EVALUATORS: dict[str, type[Evaluator]] = {}


def register(cls: type[Evaluator]) -> type[Evaluator]:
    """Decorator: register an ``Evaluator`` subclass in ``EVALUATORS`` by name."""
    if not getattr(cls, "name", ""):
        raise ValueError(f"{cls.__name__} is missing a non-empty class-level 'name'")
    if not getattr(cls, "version", ""):
        raise ValueError(f"{cls.__name__} is missing a non-empty class-level 'version'")
    if cls.name in EVALUATORS and EVALUATORS[cls.name] is not cls:
        raise ValueError(f"duplicate evaluator name: {cls.name!r}")
    EVALUATORS[cls.name] = cls
    return cls
