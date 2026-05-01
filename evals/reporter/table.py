import logging
import sys

from evals.config import Settings

log = logging.getLogger(__name__)


def run_report(
    settings: Settings,
    *,
    output_format: str,
    write_all: bool,
    sort_by: str,
    filter_category: str | None,
    min_tier: str | None,
) -> int:
    del settings, output_format, write_all, sort_by, filter_category, min_tier
    print("[ERROR] report not implemented yet (next phase)", file=sys.stderr)
    return 2
