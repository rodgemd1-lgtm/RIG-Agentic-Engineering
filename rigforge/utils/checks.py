"""System check utilities for rigforge doctor."""

from __future__ import annotations

import shutil
import subprocess
from dataclasses import dataclass


@dataclass
class CheckResult:
    name: str
    passed: bool
    detail: str = ""
    fix: str = ""


def check_command(name: str, command: str, fix: str = "") -> CheckResult:
    """Check if a CLI command is available."""
    path = shutil.which(command)
    if path:
        return CheckResult(name=name, passed=True, detail=f"found at {path}")
    return CheckResult(name=name, passed=False, detail=f"{command} not found", fix=fix)


def check_python_module(name: str, import_name: str, fix: str = "") -> CheckResult:
    """Check if a Python module is importable."""
    try:
        __import__(import_name)
        return CheckResult(name=name, passed=True, detail=f"{name} importable")
    except ImportError:
        return CheckResult(name=name, passed=False, detail=f"{name} not installed", fix=fix)


def check_python_version(minimum: str = "3.11") -> CheckResult:
    """Check Python version meets minimum."""
    import sys
    version = f"{sys.version_info.major}.{sys.version_info.minor}"
    major, minor = map(int, minimum.split("."))
    if sys.version_info.major > major or (sys.version_info.major == major and sys.version_info.minor >= minor):
        return CheckResult(name="python", passed=True, detail=f"Python {version}")
    return CheckResult(name="python", passed=False, detail=f"Python {version} < {minimum}", fix="Upgrade Python")


def check_docker_running() -> CheckResult:
    """Check if Docker daemon is running."""
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return CheckResult(name="docker", passed=True, detail="Docker running")
        return CheckResult(name="docker", passed=False, detail="Docker not running", fix="Start Docker Desktop")
    except FileNotFoundError:
        return CheckResult(name="docker", passed=False, detail="docker not found", fix="Install Docker")
    except subprocess.TimeoutExpired:
        return CheckResult(name="docker", passed=False, detail="Docker timed out", fix="Check Docker status")


def check_git_repo() -> CheckResult:
    """Check if current directory is a git repo."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return CheckResult(name="git", passed=True, detail="git repo detected")
        return CheckResult(name="git", passed=False, detail="not a git repo", fix="Run git init")
    except FileNotFoundError:
        return CheckResult(name="git", passed=False, detail="git not found", fix="Install git")
    except subprocess.TimeoutExpired:
        return CheckResult(name="git", passed=False, detail="git timed out", fix="Check git installation")
