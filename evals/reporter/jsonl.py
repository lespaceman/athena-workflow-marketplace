"""JSONL renderer: one JSON object per skill row."""

from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from evals.reporter.table import ReportRow


def write_jsonl(rows: list[ReportRow], path: Path) -> None:
    """Write each row as a JSON object on its own line.

    The dataclass is converted to a plain dict via :func:`dataclasses.asdict`
    so nested dicts/lists round-trip cleanly through ``json``.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(asdict(row), sort_keys=True))
            fh.write("\n")
