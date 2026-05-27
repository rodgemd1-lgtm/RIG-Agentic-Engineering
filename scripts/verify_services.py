#!/usr/bin/env python3
"""Verify service connectivity for optional RIGForge services.

Checks Postgres, Qdrant, Neo4j, Langfuse connectivity.
"""

from __future__ import annotations

import json
import socket
import sys
from pathlib import Path

import yaml


def check_port(host: str, port: int, timeout: float = 2.0) -> dict:
    """Check if a TCP port is reachable."""
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return {"status": "READY", "detail": f"{host}:{port} reachable"}
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        return {"status": "NOT_CONFIGURED", "detail": f"{host}:{port} unreachable: {e}", "fix": f"Start service on {host}:{port}"}


def main() -> None:
    repo_root = Path(__file__).parent.parent
    config_path = repo_root / "config" / "environment.yaml"

    if not config_path.exists():
        print(json.dumps({"error": f"Config not found: {config_path}"}), file=sys.stderr)
        sys.exit(1)

    config = yaml.safe_load(config_path.read_text())
    results = {}

    # Default service ports
    default_ports = {
        "postgres": ("localhost", 5432),
        "qdrant": ("localhost", 6333),
        "neo4j": ("localhost", 7687),
        "langfuse": ("localhost", 3000),
    }

    for name, spec in config.get("services", {}).items():
        host, port = default_ports.get(name, ("localhost", 0))
        if port:
            results[name] = check_port(host, port)
        else:
            results[name] = {"status": "UNKNOWN", "detail": "No port configured"}

    # Overall status
    has_ready = any(r["status"] == "READY" for r in results.values())
    has_blocked = any(r["status"] == "NOT_CONFIGURED" for r in results.values())

    if has_ready and not has_blocked:
        overall = "READY"
    elif has_ready:
        overall = "DEGRADED"
    else:
        overall = "NOT_CONFIGURED"

    report = {
        "timestamp": "2026-05-27T17:15:00Z",
        "overall_status": overall,
        "services": results,
        "next_safe_action": "Start required services" if has_blocked else "Services ready",
    }

    print(json.dumps(report, indent=2))
    sys.exit(0)


if __name__ == "__main__":
    main()
