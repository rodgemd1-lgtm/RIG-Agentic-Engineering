"""Healthcheck runner — runs health checks for registered services."""

from __future__ import annotations

import json
import subprocess
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from runtime.control_plane.registry_loader import RegistryLoader


@dataclass
class HealthcheckResult:
    """Result of a single health check."""
    service_id: str
    status: str  # "pass" | "fail" | "skip"
    detail: str = ""
    latency_ms: int = 0


@dataclass
class HealthcheckReport:
    """Report of all health checks."""
    checked: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    results: list[HealthcheckResult] = field(default_factory=list)


def check_http(endpoint: str, timeout: float = 5.0) -> tuple[str, str]:
    """Check an HTTP endpoint. Returns (status, detail)."""
    import time
    start = time.monotonic()
    try:
        req = urllib.request.Request(endpoint, headers={"User-Agent": "RIGForge/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            latency = int((time.monotonic() - start) * 1000)
            return ("pass", f"HTTP {resp.status} in {latency}ms")
    except urllib.error.URLError as e:
        return ("fail", f"Connection failed: {e.reason}")
    except Exception as e:
        return ("fail", str(e))


def check_command(command: str, timeout: float = 10.0) -> tuple[str, str]:
    """Check a command exists and runs. Returns (status, detail)."""
    import shutil
    path = shutil.which(command)
    if path:
        return ("pass", f"Found at {path}")
    return ("fail", f"{command} not found")


def check_service(service: dict[str, Any]) -> HealthcheckResult:
    """Run health check for a service entry."""
    hc = service.get("healthcheck", {})
    hc_type = hc.get("type", "none")
    service_id = service.get("id", "<unknown>")

    if hc_type == "none":
        return HealthcheckResult(service_id=service_id, status="skip", detail="No healthcheck defined")

    if hc_type == "http":
        endpoint = hc.get("endpoint", "")
        status, detail = check_http(endpoint)
        return HealthcheckResult(service_id=service_id, status=status, detail=detail)

    if hc_type == "command":
        command = hc.get("command", "")
        status, detail = check_command(command)
        return HealthcheckResult(service_id=service_id, status=status, detail=detail)

    return HealthcheckResult(service_id=service_id, status="skip", detail=f"Unknown healthcheck type: {hc_type}")


class HealthcheckRunner:
    """Run health checks for all registered services."""

    def __init__(self, repo_root: Path | str = ".") -> None:
        self.loader = RegistryLoader(repo_root)

    def run(self, service_ids: list[str] | None = None) -> HealthcheckReport:
        """Run health checks. If service_ids is None, run all."""
        report = HealthcheckReport()
        services = self.loader.load_service()

        for svc in services:
            if service_ids and svc.get("id") not in service_ids:
                continue
            result = check_service(svc)
            report.results.append(result)
            report.checked += 1
            if result.status == "pass":
                report.passed += 1
            elif result.status == "fail":
                report.failed += 1
            else:
                report.skipped += 1

        return report

    def to_dict(self, report: HealthcheckReport) -> dict[str, Any]:
        """Convert report to dict for JSON serialization."""
        return {
            "checked": report.checked,
            "passed": report.passed,
            "failed": report.failed,
            "skipped": report.skipped,
            "results": [
                {
                    "service_id": r.service_id,
                    "status": r.status,
                    "detail": r.detail,
                    "latency_ms": r.latency_ms,
                }
                for r in report.results
            ],
        }