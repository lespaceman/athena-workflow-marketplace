import logging
import sys

from evals.config import Settings

log = logging.getLogger(__name__)


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
    del settings, phase, evaluator, judge_model, cost_cap_usd, force, strict
    print("[ERROR] eval dispatcher not implemented yet (phase 1+ pending)", file=sys.stderr)
    return 2
