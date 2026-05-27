"""Shared fixtures for rigforge tests."""

from __future__ import annotations

import tempfile
from pathlib import Path

import pytest


@pytest.fixture
def tmp_repo(tmp_path: Path) -> Path:
    """Create a temporary git-initialized repo."""
    import subprocess
    subprocess.run(
        ["git", "init", "-q"],
        cwd=tmp_path,
        capture_output=True,
        check=True,
    )
    return tmp_path
