#!/usr/bin/env python3
"""Verify Aider installation and RIGForge policy compliance."""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def check_aider() -> tuple[bool, str]:
    """Check if aider is installed and get its path."""
    path = shutil.which("aider")
    if path:
        return True, path
    local = Path.home() / ".local/bin/aider"
    if local.exists():
        return True, str(local)
    return False, "not found"


def check_version() -> tuple[bool, str]:
    """Get Aider version string."""
    path = shutil.which("aider") or str(Path.home() / ".local/bin/aider")
    try:
        result = subprocess.run(
            [path, "--version"],
            capture_output=True, text=True, timeout=10,
        )
        version = result.stdout.strip() or result.stderr.strip()
        return bool(version), version
    except Exception as e:
        return False, str(e)


def check_policy(repo_root: Path) -> tuple[bool, str]:
    p = repo_root / "docs/tools/AIDER_GENERATOR_POLICY.md"
    return p.exists(), str(p)


def check_local_setup(repo_root: Path) -> tuple[bool, str]:
    p = repo_root / "docs/tools/AIDER_LOCAL_SETUP.md"
    return p.exists(), str(p)


def check_usage(repo_root: Path) -> tuple[bool, str]:
    p = repo_root / "docs/tools/AIDER_USAGE_FOR_GTM_STUDIO.md"
    return p.exists(), str(p)


def check_registry(repo_root: Path) -> tuple[bool, str]:
    pending = repo_root / "docs/pending_registry_entries/aider_generator_tool.yaml"
    live = repo_root / "config/tool_registry.yaml"
    found = []
    if pending.exists():
        found.append("pending")
    if live.exists():
        found.append("live/tool_registry.yaml")
    ok = len(found) > 0
    return ok, ", ".join(found) if found else "not found"


def check_gitignore(repo_root: Path) -> tuple[bool, str]:
    gi = repo_root / ".gitignore"
    if not gi.exists():
        return False, ".gitignore not found"
    content = gi.read_text()
    missing = []
    for item in (".env", ".aider"):
        if item not in content:
            missing.append(item)
    if missing:
        return False, f"missing: {', '.join(missing)}"
    return True, "clean"


def main() -> None:
    repo_root = Path(__file__).parent.parent

    checks = {
        "aider_installed": check_aider(),
        "aider_version": check_version(),
        "policy_doc": check_policy(repo_root),
        "local_setup_doc": check_local_setup(repo_root),
        "usage_doc": check_usage(repo_root),
        "registry_entry": check_registry(repo_root),
        "gitignore_safety": check_gitignore(repo_root),
    }

    blockers = [k for k, v in checks.items() if not v[0]]
    passed = len(checks) - len(blockers)

    report = {
        "tool": "aider",
        "role": "bounded_code_generator",
        "version": checks["aider_version"][1],
        "install_path": checks["aider_installed"][1],
        "checks": {k: {"status": "pass" if v[0] else "fail", "detail": v[1]} for k, v in checks.items()},
        "passed": passed,
        "total": len(checks),
        "status": "AVAILABLE" if not blockers else "BLOCKED",
        "blockers": blockers,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "next_safe_action": (
            "GTM Studio retrofit inventory"
            if not blockers
            else f"Fix: {', '.join(blockers)}"
        ),
    }

    print(json.dumps(report, indent=2))
    sys.exit(0 if not blockers else 1)


if __name__ == "__main__":
    main()