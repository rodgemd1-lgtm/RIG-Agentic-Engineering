#!/usr/bin/env python3
"""Seal the environment ProofPacket by combining doctor, version, and service reports.

Writes:
- proof/environment/doctor_report.json
- proof/environment/version_report.json
- proof/environment/environment_proofpacket.json
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone


def run_script(name: str) -> dict:
    """Run a verification script and capture JSON output."""
    repo_root = Path(__file__).parent.parent
    script_path = repo_root / "scripts" / name
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return json.loads(result.stdout) if result.returncode in (0, 1) else {"error": result.stderr}
    except Exception as e:
        return {"error": str(e)}


def main() -> None:
    repo_root = Path(__file__).parent.parent
    proof_dir = repo_root / "proof" / "environment"
    proof_dir.mkdir(parents=True, exist_ok=True)

    # Run all verification scripts
    doctor = run_script("verify_environment.py")
    versions = run_script("verify_versions.py")
    services = run_script("verify_services.py")

    # Write individual reports
    (proof_dir / "doctor_report.json").write_text(json.dumps(doctor, indent=2))
    (proof_dir / "version_report.json").write_text(json.dumps(versions, indent=2))
    (proof_dir / "services_report.json").write_text(json.dumps(services, indent=2))

    # Determine overall environment status
    statuses = [
        doctor.get("overall_status", "UNKNOWN"),
        versions.get("overall_status", "UNKNOWN"),
        services.get("overall_status", "UNKNOWN"),
    ]

    if "BLOCKED" in statuses:
        overall = "BLOCKED"
    elif "DEGRADED" in statuses:
        overall = "DEGRADED"
    elif "NOT_CONFIGURED" in statuses:
        overall = "DEGRADED"
    else:
        overall = "READY"

    # Build proof packet
    proofpacket = {
        "phase": "phase_2_environment_bootstrap",
        "status": overall,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "run_id": f"env_bootstrap_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}",
        "evidence": {
            "doctor_report": doctor,
            "version_report": versions,
            "services_report": services,
        },
        "blockers": doctor.get("blockers", []),
        "next_safe_action": (
            "Install missing critical tools" if overall == "BLOCKED"
            else "Environment ready — proceed to Phase 3: Runtime Kernel"
            if overall == "READY"
            else "Fix optional service issues or proceed with DEGRADED flag"
        ),
        "proof_summary": (
            f"Environment status: {overall}. "
            f"Doctor: {doctor.get('overall_status')}. "
            f"Versions: {versions.get('overall_status')}. "
            f"Services: {services.get('overall_status')}."
        ),
    }

    (proof_dir / "environment_proofpacket.json").write_text(json.dumps(proofpacket, indent=2))

    print(json.dumps(proofpacket, indent=2))
    # DEGRADED is acceptable — optional tools/services missing but core ready
    sys.exit(0 if overall in ("READY", "DEGRADED") else 1)


if __name__ == "__main__":
    main()
