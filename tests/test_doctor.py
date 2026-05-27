"""Tests for rigforge doctor command."""

from __future__ import annotations

from rigforge.commands.doctor import run_doctor
from rigforge.models import SystemStatus


def test_doctor_returns_valid_status() -> None:
    """rigforge doctor returns READY, DEGRADED, or BLOCKED."""
    result = run_doctor()
    assert result.status in (SystemStatus.READY, SystemStatus.DEGRADED, SystemStatus.BLOCKED)


def test_doctor_has_checks() -> None:
    """rigforge doctor returns at least one check."""
    result = run_doctor()
    assert len(result.checks) > 0


def test_doctor_python_passes() -> None:
    """Python check should pass on the test runner."""
    result = run_doctor()
    python_check = next((c for c in result.checks if c.name == "python"), None)
    assert python_check is not None
    assert python_check.status.value == "pass"


def test_doctor_has_next_safe_action() -> None:
    """Doctor result always includes a next_safe_action."""
    result = run_doctor()
    assert result.next_safe_action != ""


def test_doctor_blockers_consistent() -> None:
    """BLOCKED status means at least one blocker."""
    result = run_doctor()
    if result.status == SystemStatus.BLOCKED:
        assert len(result.blockers) > 0
