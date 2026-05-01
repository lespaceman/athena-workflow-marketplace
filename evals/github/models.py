from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class _GHBase(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")


class Repo(_GHBase):
    full_name: str
    stargazers_count: int = 0
    forks_count: int = 0
    default_branch: str = "main"
    pushed_at: datetime | None = None
    license_spdx: str | None = None
    archived: bool = False
    open_issues_count: int = 0


class User(_GHBase):
    login: str
    created_at: datetime | None = None
    followers: int = 0
    following: int = 0
    public_repos: int = 0


class Stargazer(_GHBase):
    # GitHub returns either a bare User or {starred_at, user} when the
    # custom Accept header is sent. We normalize to login + optional starred_at.
    login: str
    starred_at: datetime | None = None


class Contributor(_GHBase):
    login: str
    contributions: int = 0


class Release(_GHBase):
    tag_name: str
    name: str | None = None
    published_at: datetime | None = None
    draft: bool = False
    prerelease: bool = False


class RateLimitInfo(_GHBase):
    remaining: int
    reset_at: datetime
    is_secondary: bool = False
    retry_after_seconds: float | None = Field(default=None)
