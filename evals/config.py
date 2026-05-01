import os
from dataclasses import dataclass, field
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EVALS_ROOT = Path(__file__).resolve().parent
DATA_DIR = EVALS_ROOT / "data"
RUNS_DIR = EVALS_ROOT / "runs"
DEFAULT_DB_PATH = DATA_DIR / "evals.db"


@dataclass(frozen=True)
class Settings:
    github_token: str | None
    anthropic_api_key: str | None
    judge_model: str
    cost_cap_usd: float
    db_path: Path = DEFAULT_DB_PATH
    data_dir: Path = DATA_DIR
    runs_dir: Path = RUNS_DIR
    extra: dict[str, str] = field(default_factory=dict)


def load_settings(
    judge_model: str = "claude-opus-4-7",
    cost_cap_usd: float = 5.00,
    db_path: Path | None = None,
) -> Settings:
    return Settings(
        github_token=os.environ.get("GITHUB_TOKEN"),
        anthropic_api_key=os.environ.get("ANTHROPIC_API_KEY"),
        judge_model=os.environ.get("EVALS_JUDGE_MODEL", judge_model),
        cost_cap_usd=float(os.environ.get("EVALS_COST_CAP_USD", cost_cap_usd)),
        db_path=db_path or DEFAULT_DB_PATH,
    )
