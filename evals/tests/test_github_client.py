import json
from datetime import UTC, datetime
from pathlib import Path

import httpx
import pytest
import respx

from evals.github.client import GitHubClient, GitHubClientError

FIXTURES = Path(__file__).parent / "fixtures" / "github"


def _load_fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def _future_reset_epoch(seconds_ahead: int = 3600) -> int:
    return int(datetime.now(UTC).timestamp()) + seconds_ahead


@pytest.mark.asyncio
async def test_get_repo_returns_parsed_repo_model():
    payload = _load_fixture("repo_active.json")
    with respx.mock(base_url="https://api.github.com") as mock:
        mock.get("/repos/acme/example").mock(
            return_value=httpx.Response(
                200,
                json=payload,
                headers={
                    "X-RateLimit-Remaining": "4999",
                    "X-RateLimit-Reset": str(_future_reset_epoch()),
                },
            )
        )
        client = GitHubClient(token="fake-token")
        try:
            repo = await client.get_repo("acme", "example")
        finally:
            await client.aclose()

    assert repo.full_name == "acme/example"
    assert repo.stargazers_count == 4321
    assert repo.forks_count == 123
    assert repo.default_branch == "main"
    assert repo.archived is False
    assert repo.license_spdx == "MIT"


@pytest.mark.asyncio
async def test_404_raises_github_client_error():
    payload = _load_fixture("repo_404.json")
    with respx.mock(base_url="https://api.github.com") as mock:
        mock.get("/repos/acme/missing").mock(
            return_value=httpx.Response(
                404,
                json=payload,
                headers={
                    "X-RateLimit-Remaining": "4999",
                    "X-RateLimit-Reset": str(_future_reset_epoch()),
                },
            )
        )
        client = GitHubClient(token="fake-token")
        try:
            with pytest.raises(GitHubClientError) as exc_info:
                await client.get_repo("acme", "missing")
        finally:
            await client.aclose()
    assert exc_info.value.status == 404


@pytest.mark.asyncio
async def test_429_retries_until_success():
    payload = _load_fixture("repo_active.json")
    headers = {
        "X-RateLimit-Remaining": "4999",
        "X-RateLimit-Reset": str(_future_reset_epoch()),
    }
    with respx.mock(base_url="https://api.github.com") as mock:
        route = mock.get("/repos/acme/example").mock(
            side_effect=[
                httpx.Response(
                    429, json={"message": "rate limited"},
                    headers={**headers, "Retry-After": "1"},
                ),
                httpx.Response(200, json=payload, headers=headers),
            ]
        )
        sleeps: list[float] = []

        async def fake_sleep(seconds: float) -> None:
            sleeps.append(seconds)

        client = GitHubClient(token="fake-token", sleep=fake_sleep)
        try:
            repo = await client.get_repo("acme", "example")
        finally:
            await client.aclose()

    assert repo.full_name == "acme/example"
    assert route.call_count == 2


@pytest.mark.asyncio
async def test_low_remaining_triggers_sleep():
    payload = _load_fixture("repo_active.json")
    reset_epoch = int(datetime.now(UTC).timestamp()) + 30
    headers = {
        "X-RateLimit-Remaining": "0",
        "X-RateLimit-Reset": str(reset_epoch),
    }
    with respx.mock(base_url="https://api.github.com") as mock:
        mock.get("/repos/acme/example").mock(
            return_value=httpx.Response(200, json=payload, headers=headers)
        )
        sleeps: list[float] = []

        async def fake_sleep(seconds: float) -> None:
            sleeps.append(seconds)

        client = GitHubClient(token="fake-token", sleep=fake_sleep)
        try:
            await client.get_repo("acme", "example")
        finally:
            await client.aclose()

    assert sleeps, "expected at least one sleep when remaining=0"
    assert sleeps[0] > 0


@pytest.mark.asyncio
async def test_secondary_rate_limit_403_is_retried():
    payload = _load_fixture("repo_active.json")
    headers = {
        "X-RateLimit-Remaining": "4999",
        "X-RateLimit-Reset": str(_future_reset_epoch()),
    }
    with respx.mock(base_url="https://api.github.com") as mock:
        route = mock.get("/repos/acme/example").mock(
            side_effect=[
                httpx.Response(
                    403,
                    json={"message": "You have exceeded a secondary rate limit"},
                    headers={**headers, "Retry-After": "1"},
                ),
                httpx.Response(200, json=payload, headers=headers),
            ]
        )
        sleeps: list[float] = []

        async def fake_sleep(seconds: float) -> None:
            sleeps.append(seconds)

        client = GitHubClient(token="fake-token", sleep=fake_sleep)
        try:
            repo = await client.get_repo("acme", "example")
        finally:
            await client.aclose()

    assert repo.full_name == "acme/example"
    assert route.call_count == 2


@pytest.mark.asyncio
async def test_regular_403_without_secondary_signal_raises():
    headers = {
        "X-RateLimit-Remaining": "4999",
        "X-RateLimit-Reset": str(_future_reset_epoch()),
    }
    with respx.mock(base_url="https://api.github.com") as mock:
        mock.get("/repos/acme/private").mock(
            return_value=httpx.Response(
                403,
                json={"message": "Forbidden"},
                headers=headers,
            )
        )
        client = GitHubClient(token="fake-token")
        try:
            with pytest.raises(GitHubClientError) as exc_info:
                await client.get_repo("acme", "private")
        finally:
            await client.aclose()
    assert exc_info.value.status == 403
