import logging
import sys
from pathlib import Path

from evals.config import Settings

log = logging.getLogger(__name__)


def run_discover(settings: Settings, seeds_path: Path | None = None) -> int:
    del settings, seeds_path
    print("[ERROR] discover not implemented yet (phase 0 module pending)", file=sys.stderr)
    return 2
