from collections.abc import Mapping

from evals.scoring.weights import BUCKET_EVALUATORS, DEFAULT_WEIGHTS, TIER_THRESHOLDS


def _avg(*values: float | None) -> float:
    present = [v for v in values if v is not None]
    if not present:
        return 0.0
    return sum(present) / len(present)


def bucket_scores(eval_scores: Mapping[str, float | None]) -> dict[str, float]:
    return {
        bucket: _avg(*(eval_scores.get(name) for name in evaluators))
        for bucket, evaluators in BUCKET_EVALUATORS.items()
    }


def reliability_score(
    eval_scores: Mapping[str, float | None],
    weights: Mapping[str, float] = DEFAULT_WEIGHTS,
) -> float:
    buckets = bucket_scores(eval_scores)
    return sum(buckets[name] * weight for name, weight in weights.items())


def tier(score: float) -> str:
    for name, threshold in TIER_THRESHOLDS:
        if score >= threshold:
            return name
    return "D"
