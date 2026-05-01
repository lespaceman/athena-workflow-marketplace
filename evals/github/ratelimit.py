from collections.abc import Mapping
from datetime import UTC, datetime

from evals.github.models import RateLimitInfo


def parse_rate_limit_headers(headers: Mapping[str, str]) -> RateLimitInfo:
    """Extract rate-limit info from response headers.

    Falls back to safe defaults: remaining=infinite-ish, reset=now, no secondary.
    """
    remaining_raw = headers.get("X-RateLimit-Remaining") or headers.get("x-ratelimit-remaining")
    reset_raw = headers.get("X-RateLimit-Reset") or headers.get("x-ratelimit-reset")
    retry_after_raw = headers.get("Retry-After") or headers.get("retry-after")

    remaining = _to_int(remaining_raw, default=10_000)
    reset_epoch = _to_int(reset_raw, default=int(datetime.now(UTC).timestamp()))
    retry_after = _to_float(retry_after_raw)

    # Secondary rate limit signals: GitHub sets either a documentation URL
    # in the body or a Retry-After header without exhausting the primary
    # quota. Retry-After is the structurally reliable header.
    is_secondary = retry_after is not None and remaining > 0

    return RateLimitInfo(
        remaining=remaining,
        reset_at=datetime.fromtimestamp(reset_epoch, tz=UTC),
        is_secondary=is_secondary,
        retry_after_seconds=retry_after,
    )


def seconds_until(reset_at: datetime, *, now: datetime | None = None) -> float:
    current = now or datetime.now(UTC)
    delta = (reset_at - current).total_seconds()
    return max(delta, 0.0)


def _to_int(value: str | None, *, default: int) -> int:
    if value is None:
        return default
    try:
        return int(value)
    except ValueError:
        return default


def _to_float(value: str | None) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None
