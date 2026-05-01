from __future__ import annotations

import dataclasses
from uuid import uuid4

import pytest

from evals.evaluators.base import (
    EVALUATORS,
    EvalContext,
    EvalResult,
    Evaluator,
    register,
)


@pytest.fixture(autouse=True)
def _restore_registry():
    snapshot = dict(EVALUATORS)
    yield
    EVALUATORS.clear()
    EVALUATORS.update(snapshot)


def test_register_populates_evaluators():
    @register
    class MyEvaluator(Evaluator):
        name = "test-register-populates"
        version = "1.0.0"
        phase = 1

        async def evaluate(self, ctx: EvalContext) -> EvalResult:  # pragma: no cover
            return EvalResult(score=0.0)

    assert EVALUATORS["test-register-populates"] is MyEvaluator


def test_register_rejects_duplicate_names():
    @register
    class FirstWinner(Evaluator):
        name = "duplicate-name-test"
        version = "1.0.0"

        async def evaluate(self, ctx: EvalContext) -> EvalResult:  # pragma: no cover
            return EvalResult(score=0.0)

    with pytest.raises(ValueError, match="duplicate evaluator name"):
        @register
        class SecondLoser(Evaluator):
            name = "duplicate-name-test"
            version = "1.0.0"

            async def evaluate(self, ctx: EvalContext) -> EvalResult:  # pragma: no cover
                return EvalResult(score=0.0)

    assert EVALUATORS["duplicate-name-test"] is FirstWinner


def test_register_requires_name_and_version():
    with pytest.raises(ValueError, match="missing a non-empty class-level 'name'"):
        @register
        class NoName(Evaluator):
            version = "1.0.0"

            async def evaluate(self, ctx: EvalContext) -> EvalResult:  # pragma: no cover
                return EvalResult(score=0.0)

    with pytest.raises(ValueError, match="missing a non-empty class-level 'version'"):
        @register
        class NoVersion(Evaluator):
            name = "no-version"

            async def evaluate(self, ctx: EvalContext) -> EvalResult:  # pragma: no cover
                return EvalResult(score=0.0)


def test_eval_result_is_frozen():
    result = EvalResult(score=42.0)
    assert dataclasses.is_dataclass(result)
    with pytest.raises(dataclasses.FrozenInstanceError):
        result.score = 99.0  # type: ignore[misc]


def test_eval_context_is_frozen():
    ctx = EvalContext(
        skill_id="a/b#s",
        skill_md="---\nname: x\n---\n",
        frontmatter={"name": "x"},
        overlays={"claude": None, "openai": None},
        repo_metadata={},
        run_id=uuid4(),
    )
    assert dataclasses.is_dataclass(ctx)
    with pytest.raises(dataclasses.FrozenInstanceError):
        ctx.skill_id = "other"  # type: ignore[misc]
