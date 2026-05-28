#!/usr/bin/env python3
"""Verify the Control Plane: all registries validate, ownership is complete, proof paths exist."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

from runtime.control_plane.registry_validator import validate_all_registries
from runtime.control_plane.ownership_validator import OwnershipValidator
from runtime.control_plane.proof_path_validator import ProofPathValidator
from runtime.control_plane.registry_loader import RegistryLoader


def main() -> None:
    repo_root = Path(__file__).parent.parent
    results = {}

    # 1. Registry field validation
    reg_result = validate_all_registries(repo_root)
    results["registry_validation"] = {
        "valid": reg_result.valid,
        "total_errors": reg_result.total_errors,
        "errors": [
            {"registry": e.registry, "entry": e.entry_id, "field": e.field, "msg": e.message}
            for r in reg_result.results.values()
            for e in r.errors
        ],
        "summary": {
            name: {"valid": r.valid, "count": r.entry_count, "errors": len(r.errors)}
            for name, r in reg_result.results.items()
        },
    }

    # 2. Ownership validation
    own_result = OwnershipValidator(repo_root).validate_all()
    results["ownership_validation"] = {
        "valid": own_result.valid,
        "total_entries": own_result.total_entries,
        "entries_with_owner": own_result.entries_with_owner,
        "ownership_rate": (
            f"{own_result.entries_with_owner}/{own_result.total_entries}"
            if own_result.total_entries > 0 else "N/A"
        ),
        "errors": [
            {"registry": e.registry, "entry": e.entry_id, "msg": e.message}
            for e in own_result.errors
        ],
    }

    # 3. Proof path validation
    proof_result = ProofPathValidator(repo_root).validate_all()
    results["proof_path_validation"] = {
        "valid": proof_result.valid,
        "total_entries": proof_result.total_entries,
        "entries_with_proof_path": proof_result.entries_with_proof_path,
        "errors": [
            {"registry": e.registry, "entry": e.entry_id, "msg": e.message}
            for e in proof_result.errors
        ],
    }

    # 4. Registry stats
    loader = RegistryLoader(repo_root)
    stats = loader.stats()
    results["registry_stats"] = [
        {"name": s.registry_name, "entries": s.entry_count, "loaded": s.loaded}
        for s in stats
    ]

    # Overall status
    overall = (
        reg_result.valid
        and own_result.valid
        and proof_result.valid
    )
    results["overall_status"] = "PASS" if overall else "FAIL"
    results["timestamp"] = datetime.now(timezone.utc).isoformat()

    print(json.dumps(results, indent=2))
    sys.exit(0 if overall else 1)


if __name__ == "__main__":
    main()