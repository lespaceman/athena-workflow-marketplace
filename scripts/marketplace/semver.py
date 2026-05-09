from __future__ import annotations


def bump_part(version: str, part: str) -> str:
    if part not in ("major", "minor", "patch"):
        raise ValueError(f"unknown bump part: {part!r}")
    pieces = version.split(".")
    if len(pieces) != 3 or not all(p.isdigit() for p in pieces):
        raise ValueError(f"unsupported semver: {version!r}")
    major, minor, patch = (int(p) for p in pieces)
    if part == "major":
        return f"{major + 1}.0.0"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    return f"{major}.{minor}.{patch + 1}"
