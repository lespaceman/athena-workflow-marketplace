"""CLI: python3 -m suite_validators <playwright|robot|intent>"""
from __future__ import annotations

import sys

from . import SUITES
from .common import run_assertions


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if not args or args[0] not in SUITES:
        print(f"usage: python3 -m suite_validators <{('|').join(sorted(SUITES))}>", file=sys.stderr)
        return 2
    name = args[0]
    return run_assertions(name, SUITES[name])


if __name__ == "__main__":
    sys.exit(main())
