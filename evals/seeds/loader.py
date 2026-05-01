from dataclasses import dataclass
from pathlib import Path

import yaml

DEFAULT_SEEDS = Path(__file__).parent / "registries.yaml"


@dataclass(frozen=True)
class DiscoveryCandidate:
    skill_id: str
    repo_url: str
    skill_path: str
    category: str
    publisher_type: str
    source_registry: str


def load_seeds(path: Path | None = None) -> list[DiscoveryCandidate]:
    src = path or DEFAULT_SEEDS
    raw = yaml.safe_load(src.read_text()) or {}
    skills = raw.get("skills") or []
    return [
        DiscoveryCandidate(
            skill_id=item["skill_id"],
            repo_url=item["repo_url"],
            skill_path=item["skill_path"],
            category=item.get("category", "uncategorized"),
            publisher_type=item.get("publisher_type", "community"),
            source_registry=item.get("source_registry", "seeds.yaml"),
        )
        for item in skills
    ]
