import asyncio
import base64
import logging
from typing import Any, cast

import httpx
from tenacity import (
    AsyncRetrying,
    RetryCallState,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from evals.github.models import (
    Contributor,
    RateLimitInfo,
    Release,
    Repo,
    Stargazer,
    User,
)
from evals.github.ratelimit import parse_rate_limit_headers, seconds_until

log = logging.getLogger(__name__)

_LOW_REMAINING_THRESHOLD = 50
_DEFAULT_TIMEOUT = httpx.Timeout(30.0, connect=10.0)


class GitHubClientError(RuntimeError):
    def __init__(self, status: int, message: str) -> None:
        super().__init__(f"GitHub HTTP {status}: {message}")
        self.status = status
        self.message = message


class _RetriableHTTPError(Exception):
    def __init__(self, response: httpx.Response, ratelimit: RateLimitInfo | None) -> None:
        super().__init__(f"retriable status={response.status_code}")
        self.response = response
        self.ratelimit = ratelimit


def _is_retriable_status(status: int) -> bool:
    return status == 429 or 500 <= status < 600


def _is_secondary_rate_limit(response: httpx.Response) -> bool:
    if response.status_code != 403:
        return False
    if response.headers.get("Retry-After"):
        return True
    body_lower = response.text.lower() if response.content else ""
    return "secondary rate limit" in body_lower or "abuse" in body_lower


class GitHubClient:
    def __init__(
        self,
        token: str | None = None,
        base_url: str = "https://api.github.com",
        user_agent: str = "athena-evals/0.1",
        *,
        transport: httpx.AsyncBaseTransport | None = None,
        sleep: Any = asyncio.sleep,
    ) -> None:
        if token is None:
            log.warning(
                "[WARN] GITHUB_TOKEN not set; anonymous requests are limited to 60/hour"
            )
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": user_agent,
        }
        if token:
            headers["Authorization"] = f"Bearer {token}"
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers=headers,
            http2=False,
            timeout=_DEFAULT_TIMEOUT,
            transport=transport,
        )
        self._sleep = sleep

    async def aclose(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> "GitHubClient":
        return self

    async def __aexit__(self, *_: object) -> None:
        await self.aclose()

    # ---- public API ----

    async def get_repo(self, owner: str, repo: str) -> Repo:
        data = await self._get_json(f"/repos/{owner}/{repo}")
        return _repo_from_payload(data)

    async def get_contents(
        self, owner: str, repo: str, path: str, ref: str | None = None
    ) -> bytes:
        params = {"ref": ref} if ref else None
        data = await self._get_json(
            f"/repos/{owner}/{repo}/contents/{path.lstrip('/')}", params=params
        )
        if not isinstance(data, dict):
            raise GitHubClientError(200, f"unexpected contents payload type for {path}")
        encoding = data.get("encoding")
        content = data.get("content")
        if encoding == "base64" and isinstance(content, str):
            return base64.b64decode(content)
        if isinstance(content, str):
            return content.encode("utf-8")
        raise GitHubClientError(200, f"contents response missing 'content' for {path}")

    async def list_releases(self, owner: str, repo: str) -> list[Release]:
        data = await self._get_json(f"/repos/{owner}/{repo}/releases", params={"per_page": 100})
        items = data if isinstance(data, list) else []
        return [Release.model_validate(_pick(item, Release)) for item in items]

    async def list_contributors(self, owner: str, repo: str) -> list[Contributor]:
        data = await self._get_json(
            f"/repos/{owner}/{repo}/contributors", params={"per_page": 100}
        )
        items = data if isinstance(data, list) else []
        return [Contributor.model_validate(_pick(item, Contributor)) for item in items]

    async def list_stargazers(self, owner: str, repo: str, sample: int) -> list[Stargazer]:
        # Deterministic: take the first `sample` stargazers in API order.
        per_page = min(max(sample, 1), 100)
        data = await self._get_json(
            f"/repos/{owner}/{repo}/stargazers", params={"per_page": per_page}
        )
        items = data if isinstance(data, list) else []
        result: list[Stargazer] = []
        for raw in items[:sample]:
            login = _stargazer_login(raw)
            if login is None:
                continue
            result.append(
                Stargazer(login=login, starred_at=_safe_datetime(raw.get("starred_at")))
            )
        return result

    async def get_user(self, login: str) -> User:
        data = await self._get_json(f"/users/{login}")
        return User.model_validate(_pick(data, User))

    async def graphql(
        self, query: str, variables: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {"query": query}
        if variables is not None:
            payload["variables"] = variables
        response = await self._request_with_retry("POST", "/graphql", json_body=payload)
        body = response.json()
        if not isinstance(body, dict):
            raise GitHubClientError(response.status_code, "graphql body not an object")
        return cast(dict[str, Any], body)

    # ---- internals ----

    async def _get_json(
        self, path: str, params: dict[str, Any] | None = None
    ) -> Any:
        response = await self._request_with_retry("GET", path, params=params)
        return response.json()

    async def _request_with_retry(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> httpx.Response:
        async for attempt in AsyncRetrying(
            stop=stop_after_attempt(5),
            wait=wait_exponential(multiplier=1.0, min=1.0, max=60.0),
            retry=retry_if_exception(_should_retry),
            reraise=True,
            before_sleep=_log_before_sleep,
        ):
            with attempt:
                response = await self._client.request(
                    method, path, params=params, json=json_body
                )
                ratelimit = parse_rate_limit_headers(response.headers)
                await self._maybe_sleep_for_quota(ratelimit)
                if response.status_code == 403 and _is_secondary_rate_limit(response):
                    raise _RetriableHTTPError(response, ratelimit)
                if _is_retriable_status(response.status_code):
                    raise _RetriableHTTPError(response, ratelimit)
                if response.status_code >= 400:
                    raise GitHubClientError(response.status_code, response.text)
                return response
        # Unreachable: AsyncRetrying re-raises on exhaustion.
        raise GitHubClientError(0, "retry loop exhausted without return")

    async def _maybe_sleep_for_quota(self, info: RateLimitInfo) -> None:
        if info.remaining < _LOW_REMAINING_THRESHOLD:
            wait = seconds_until(info.reset_at)
            if wait > 0:
                log.warning(
                    "[WARN] rate limit low: remaining=%d sleeping=%.1fs",
                    info.remaining,
                    wait,
                )
                await self._sleep(wait)


def _should_retry(exc: BaseException) -> bool:
    if isinstance(exc, _RetriableHTTPError):
        return True
    return isinstance(exc, httpx.TransportError | httpx.TimeoutException)


def _log_before_sleep(retry_state: RetryCallState) -> None:
    outcome = retry_state.outcome
    if outcome is None:
        return
    exc = outcome.exception()
    if isinstance(exc, _RetriableHTTPError):
        retry_after = exc.ratelimit.retry_after_seconds if exc.ratelimit else None
        log.warning(
            "[WARN] github retry attempt=%d status=%d retry_after=%s",
            retry_state.attempt_number,
            exc.response.status_code,
            retry_after,
        )


def _repo_from_payload(data: Any) -> Repo:
    if not isinstance(data, dict):
        raise GitHubClientError(200, "repo payload not an object")
    license_obj = data.get("license") or {}
    return Repo(
        full_name=str(data.get("full_name", "")),
        stargazers_count=int(data.get("stargazers_count", 0)),
        forks_count=int(data.get("forks_count", 0)),
        default_branch=str(data.get("default_branch", "main")),
        pushed_at=_safe_datetime(data.get("pushed_at")),
        license_spdx=(
            str(license_obj.get("spdx_id"))
            if isinstance(license_obj, dict) and license_obj.get("spdx_id")
            else None
        ),
        archived=bool(data.get("archived", False)),
        open_issues_count=int(data.get("open_issues_count", 0)),
    )


def _pick(data: Any, model: type[Any]) -> dict[str, Any]:
    if not isinstance(data, dict):
        return {}
    fields = set(model.model_fields.keys())
    return {k: v for k, v in data.items() if k in fields}


def _stargazer_login(raw: Any) -> str | None:
    if not isinstance(raw, dict):
        return None
    if "login" in raw and isinstance(raw["login"], str):
        return raw["login"]
    user = raw.get("user")
    if isinstance(user, dict) and isinstance(user.get("login"), str):
        return cast(str, user["login"])
    return None


def _safe_datetime(value: Any) -> Any:
    # Pydantic will coerce strings; pass-through. None and missing become None.
    return value if value else None
