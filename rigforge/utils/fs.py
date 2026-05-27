"""Filesystem utilities for rigforge."""

from __future__ import annotations

import os
from pathlib import Path


def ensure_dir(path: Path) -> Path:
    """Create directory if it doesn't exist, return the path."""
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_if_missing(path: Path, content: str) -> bool:
    """Write file only if it doesn't exist. Returns True if written."""
    if path.exists():
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return True


def file_exists(path: Path) -> bool:
    return path.is_file()


def dir_exists(path: Path) -> bool:
    return path.is_dir()


def find_repo_root(marker: str = ".git") -> Path | None:
    """Walk up from cwd looking for repo root."""
    current = Path.cwd()
    for parent in [current] + list(current.parents):
        if (parent / marker).exists():
            return parent
    return None


def studio_dir(repo_root: Path, studio: str) -> Path:
    return repo_root / "studios" / studio


def runs_dir(repo_root: Path) -> Path:
    return repo_root / "runs"


def run_dir(repo_root: Path, run_id: str) -> Path:
    return runs_dir(repo_root) / run_id
