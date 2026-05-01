from datetime import UTC, datetime, timedelta

from evals.github.ratelimit import parse_rate_limit_headers, seconds_until


def test_parse_rate_limit_headers_basic():
    reset_epoch = int(datetime(2026, 5, 1, 12, 0, 0, tzinfo=UTC).timestamp())
    info = parse_rate_limit_headers(
        {"X-RateLimit-Remaining": "42", "X-RateLimit-Reset": str(reset_epoch)}
    )
    assert info.remaining == 42
    assert info.reset_at == datetime(2026, 5, 1, 12, 0, 0, tzinfo=UTC)
    assert info.is_secondary is False
    assert info.retry_after_seconds is None


def test_parse_rate_limit_headers_lowercase_keys():
    reset_epoch = int(datetime(2026, 5, 1, 12, 0, 0, tzinfo=UTC).timestamp())
    info = parse_rate_limit_headers(
        {"x-ratelimit-remaining": "5", "x-ratelimit-reset": str(reset_epoch)}
    )
    assert info.remaining == 5


def test_parse_rate_limit_headers_secondary_when_retry_after_with_quota():
    info = parse_rate_limit_headers(
        {"X-RateLimit-Remaining": "1000", "Retry-After": "10"}
    )
    assert info.is_secondary is True
    assert info.retry_after_seconds == 10.0


def test_parse_rate_limit_headers_not_secondary_when_quota_exhausted():
    info = parse_rate_limit_headers(
        {"X-RateLimit-Remaining": "0", "Retry-After": "60"}
    )
    assert info.is_secondary is False
    assert info.retry_after_seconds == 60.0


def test_parse_rate_limit_headers_handles_missing_values():
    info = parse_rate_limit_headers({})
    assert info.remaining == 10_000
    assert info.is_secondary is False


def test_parse_rate_limit_headers_handles_invalid_values():
    info = parse_rate_limit_headers(
        {"X-RateLimit-Remaining": "not-a-number", "Retry-After": "abc"}
    )
    assert info.remaining == 10_000
    assert info.retry_after_seconds is None


def test_seconds_until_future_returns_positive():
    now = datetime(2026, 5, 1, 12, 0, 0, tzinfo=UTC)
    reset = now + timedelta(seconds=30)
    assert seconds_until(reset, now=now) == 30.0


def test_seconds_until_past_returns_zero():
    now = datetime(2026, 5, 1, 12, 0, 0, tzinfo=UTC)
    reset = now - timedelta(seconds=10)
    assert seconds_until(reset, now=now) == 0.0
