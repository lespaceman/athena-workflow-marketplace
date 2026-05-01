import pytest

from evals.scoring.composite import bucket_scores, reliability_score, tier


def test_bucket_scores_average_present_evaluators():
    scores = {
        "repo-health": 80.0,
        "release-cadence": 60.0,
        "compliance-check": 100.0,
        "security-scan": 50.0,
    }
    buckets = bucket_scores(scores)
    assert buckets["health"] == 70.0
    assert buckets["compliance"] == 100.0
    assert buckets["security"] == 50.0
    assert buckets["provenance"] == 0.0


def test_reliability_score_uses_default_weights():
    scores = {
        "repo-health": 100.0,
        "release-cadence": 100.0,
        "follower-authenticity": 100.0,
        "contributor-authenticity": 100.0,
        "compliance-check": 100.0,
        "cross-runtime": 100.0,
        "live-validator": 100.0,
        "report-quality": 100.0,
        "security-scan": 100.0,
    }
    assert reliability_score(scores) == pytest.approx(100.0)


def test_reliability_score_zero_when_empty():
    assert reliability_score({}) == 0.0


@pytest.mark.parametrize(
    ("score", "expected"),
    [(95.0, "S"), (90.0, "S"), (85.0, "A"), (75.0, "B"), (65.0, "C"), (50.0, "D"), (0.0, "D")],
)
def test_tier_thresholds(score, expected):
    assert tier(score) == expected
