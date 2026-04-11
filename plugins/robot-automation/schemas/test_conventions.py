"""Tests for conventions.yaml schema validation.

Run from the marketplace repo root:
    python -m pytest plugins/robot-automation/schemas/test_conventions.py -v
"""
import pathlib

import pytest

from validate_conventions import ConventionsError, validate_file

FIXTURES = pathlib.Path(__file__).parent / "fixtures"


def test_valid_minimal_fixture_passes():
    validate_file(FIXTURES / "valid-minimal.yaml")


def test_valid_full_fixture_passes():
    validate_file(FIXTURES / "valid-full.yaml")


def test_wrong_version_is_rejected():
    with pytest.raises(ConventionsError, match="version"):
        validate_file(FIXTURES / "invalid-version.yaml")


def test_missing_required_field_is_rejected():
    with pytest.raises(ConventionsError, match="required"):
        validate_file(FIXTURES / "invalid-missing-field.yaml")


def test_unknown_field_is_rejected(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text(
        (FIXTURES / "valid-minimal.yaml").read_text(encoding="utf-8")
        + "\nunknown_field: 42\n",
        encoding="utf-8",
    )
    with pytest.raises(ConventionsError, match="unknown_field|additionalProperties"):
        validate_file(bad)
