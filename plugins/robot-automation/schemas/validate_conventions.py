"""Validator for conventions.yaml against conventions.schema.json.

Usage:
    python validate_conventions.py <path/to/conventions.yaml>
"""
from __future__ import annotations

import json
import pathlib
import sys

import jsonschema
import yaml

SCHEMA_PATH = pathlib.Path(__file__).parent / "conventions.schema.json"


class ConventionsError(RuntimeError):
    """Raised when conventions.yaml fails schema validation."""


def _load_schema() -> dict:
    with SCHEMA_PATH.open(encoding="utf-8") as fh:
        return json.load(fh)


def validate_file(path: pathlib.Path | str) -> dict:
    """Load and validate a conventions.yaml file."""
    path = pathlib.Path(path)
    with path.open(encoding="utf-8") as fh:
        doc = yaml.safe_load(fh)
    try:
        jsonschema.validate(doc, _load_schema())
    except jsonschema.ValidationError as exc:
        raise ConventionsError(f"{path}: {exc.message}") from exc
    return doc


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: validate_conventions.py <path>", file=sys.stderr)
        return 2
    try:
        validate_file(argv[1])
    except ConventionsError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
