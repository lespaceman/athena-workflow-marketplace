import logging
import sys

from evals.config import Settings

log = logging.getLogger(__name__)


def run_extract(settings: Settings, skill_id: str | None = None) -> int:
    del settings, skill_id
    print("[ERROR] extract not implemented yet (phase 0.5 module pending)", file=sys.stderr)
    return 2
