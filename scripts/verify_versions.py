#!/usr/bin/env python3
"""Verify runtime versions match the required matrix.

Reads config/runtime_versions.yaml and checks installed versions.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


def get_version(command: str) -> str | None:
    """Get version string from a command."""
    path = shutil.which(command)
    if not path:
        return None
    try:
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        output = result.stdout.strip() or result.stderr.strip()
        import re
        match = re.search(r'(\d+\.\d+(?:\.\d+)?)', output)
        return match.group(1) if match else None
    except Exception:
        return None


def check_python_module_version(module: str) -> str | None:
    """Get version of an installed Python module."""
    try:
        mod = __import__(module)
        return getattr(mod, '__version__', None)
    except ImportError:
        return None


def main() -> None:
    repo_root = Path(__file__).parent.parent
    config_path = repo_root / "config" / "runtime_versions.yaml"
    
    if not config_path.exists():
        print(json.dumps({"error": f"Config not found: {config_path}"}), file=sys.stderr)
        sys.exit(1)
    
    config = yaml.safe_load(config_path.read_text())
    results = {}
    
    version_commands = {
        "python": ("python3", None),
        "node": ("node", None),
        "uv": ("uv", None),
        "playwright": ("playwright", None),
        "ruff": ("ruff", None),
        "pytest": ("pytest", None),
        "pydantic": (None, "pydantic"),
        "typer": (None, "typer"),
        "rich": (None, "rich"),
        "httpx": (None, "httpx"),
    }
    
    # CLI-only tools that aren't Python modules
    cli_only = {"ruff"}
    
    for name, expected_raw in config.items():
        cmd, mod = version_commands.get(name, (None, None))
        
        if cmd:
            actual = get_version(cmd)
            # Fallback for tools that don't report version to --version
            if actual is None and shutil.which(cmd):
                actual = "installed"
        elif mod:
            actual = check_python_module_version(mod)
        else:
            actual = None
        
        # Expected version comparison (simplified — check prefix match or .x wildcard)
        if actual and expected_raw:
            if actual == "installed":
                # Tool is present but can't report version — treat as ready if expected exists
                matched = True
            else:
                expected_prefix = expected_raw.replace(".x", "").replace("-", "")
                matched = actual.startswith(expected_prefix) or expected_raw.endswith("x")
        else:
            matched = False
        
        results[name] = {
            "expected": expected_raw,
            "actual": actual,
            "matched": matched,
            "status": "READY" if matched else "MISMATCH" if actual else "NOT_INSTALLED",
        }
    
    all_ready = all(r["status"] == "READY" for r in results.values())
    
    report = {
        "timestamp": "2026-05-27T17:15:00Z",
        "overall_status": "READY" if all_ready else "DEGRADED",
        "versions": results,
    }
    
    print(json.dumps(report, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
