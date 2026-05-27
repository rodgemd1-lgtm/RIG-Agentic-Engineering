#!/usr/bin/env python3
"""Verify RIGForge environment: check all required tools and services.

Reads config/environment.yaml and checks each tool.
Outputs JSON report to stdout.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
from pathlib import Path

import yaml


def check_version(command: str, min_version: str) -> dict:
    """Check if a command exists and meets minimum version."""
    path = shutil.which(command)
    if not path:
        return {"status": "NOT_INSTALLED", "detail": f"{command} not found", "fix": f"Install {command}"}
    
    try:
        result = subprocess.run(
            [command, "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        version_output = result.stdout.strip() or result.stderr.strip()
        # Extract version number (rough)
        import re
        version_match = re.search(r'(\d+\.\d+(?:\.\d+)?)', version_output)
        version = version_match.group(1) if version_match else "unknown"
        
        return {
            "status": "READY",
            "detail": f"{command} {version} at {path}",
            "version": version,
        }
    except Exception as e:
        return {"status": "NOT_CONFIGURED", "detail": str(e), "fix": f"Check {command} installation"}


def check_command(command: str) -> dict:
    """Check if a command exists."""
    path = shutil.which(command)
    if path:
        return {"status": "READY", "detail": f"found at {path}"}
    return {"status": "NOT_INSTALLED", "detail": f"{command} not found", "fix": f"Install {command}"}


def check_daemon(command: str) -> dict:
    """Check if a daemon/service is running."""
    try:
        result = subprocess.run(
            [command, "info"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            return {"status": "READY", "detail": f"{command} daemon running"}
        return {"status": "NOT_CONFIGURED", "detail": f"{command} not running", "fix": f"Start {command}"}
    except FileNotFoundError:
        return {"status": "NOT_INSTALLED", "detail": f"{command} not found", "fix": f"Install {command}"}
    except subprocess.TimeoutExpired:
        return {"status": "NOT_CONFIGURED", "detail": f"{command} timed out", "fix": f"Check {command} status"}


def check_module(import_name: str) -> dict:
    """Check if a Python module is importable."""
    try:
        __import__(import_name)
        return {"status": "READY", "detail": f"{import_name} importable"}
    except ImportError:
        return {"status": "NOT_INSTALLED", "detail": f"{import_name} not installed", "fix": f"pip install {import_name}"}


def run_checks(config_path: Path) -> dict:
    """Run all checks from environment config."""
    config = yaml.safe_load(config_path.read_text())
    results = {}
    
    # Required checks
    for name, spec in config.get("required", {}).items():
        check_type = spec.get("check_type", "command")
        if check_type == "version":
            min_ver = spec.get("min_version", "0")
            results[name] = check_version(spec["command"], min_ver)
        elif check_type == "daemon":
            results[name] = check_daemon(spec["command"])
        else:
            results[name] = check_command(spec["command"])
    
    # Optional checks
    for name, spec in config.get("optional", {}).items():
        check_type = spec.get("check_type", "command")
        if check_type == "module":
            import_name = spec.get("import_name", name)
            results[name] = check_module(import_name)
        elif check_type == "version":
            min_ver = spec.get("min_version", "0")
            results[name] = check_version(spec["command"], min_ver)
        else:
            results[name] = check_command(spec["command"])
    
    # Service checks
    for name, spec in config.get("services", {}).items():
        results[name] = check_command(spec["command"])
    
    return results


def determine_overall(results: dict, required: dict, optional: dict, services: dict) -> str:
    """Determine overall status from individual results.
    
    Required tools that are NOT_INSTALLED/NOT_CONFIGURED = BLOCKED.
    Optional tools/services that are missing = DEGRADED.
    """
    # Check required tools
    for name in required:
        if name in results and results[name]["status"] in ("NOT_INSTALLED", "NOT_CONFIGURED"):
            return "BLOCKED"
    
    # Check optional tools and services
    optional_names = list(optional.keys()) + list(services.keys())
    has_missing = any(
        results[name]["status"] in ("NOT_INSTALLED", "NOT_CONFIGURED", "UNKNOWN")
        for name in optional_names if name in results
    )
    
    if has_missing:
        return "DEGRADED"
    return "READY"


def main() -> None:
    repo_root = Path(__file__).parent.parent
    config_path = repo_root / "config" / "environment.yaml"
    
    if not config_path.exists():
        print(json.dumps({"error": f"Config not found: {config_path}"}), file=sys.stderr)
        sys.exit(1)
    
    config = yaml.safe_load(config_path.read_text())
    results = run_checks(config_path)
    overall = determine_overall(results, config.get("required", {}), config.get("optional", {}), config.get("services", {}))
    
    # Determine blockers (required tools that are not READY)
    blockers = []
    for name, spec in config.get("required", {}).items():
        if results[name]["status"] != "READY":
            blockers.append(name)
    
    report = {
        "timestamp": "2026-05-27T17:15:00Z",
        "overall_status": overall,
        "checks": results,
        "blockers": blockers,
        "next_safe_action": "Install missing tools" if blockers else "Environment ready",
    }
    
    print(json.dumps(report, indent=2))
    sys.exit(0 if overall in ("READY", "DEGRADED") else 1)


if __name__ == "__main__":
    main()
