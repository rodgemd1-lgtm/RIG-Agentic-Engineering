#!/usr/bin/env python3
"""scripts/verify_deerflow_mapping.py — Verify DeerFlow thread mapping for a run.

Usage:
    python scripts/verify_deerflow_mapping.py --run-id run_abc123
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from integrations.deerflow.thread_mapping import get_thread_mapping
from integrations.deerflow.workspace_mapping import WorkspaceMapping


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify DeerFlow thread mapping")
    parser.add_argument("--run-id", required=True, help="Run ID to verify")
    args = parser.parse_args()

    run_id = args.run_id
    print(f"\n🔍 Verify DeerFlow Mapping: {run_id}\n")
    exit_code = 0

    # Check 1: RunEnvelope exists
    envelope_path = REPO_ROOT / "runs" / run_id / "RunEnvelope.json"
    if envelope_path.exists():
        envelope = json.loads(envelope_path.read_text())
        print(f"  ✓ RunEnvelope exists: studio={envelope.get('studio', '?')}")
    else:
        print(f"  ✗ RunEnvelope missing: {envelope_path}")
        exit_code = 1

    # Check 2: Thread mapping exists
    mapping_store = get_thread_mapping()
    mapping = mapping_store.get_by_run_id(run_id)
    if mapping:
        print(f"  ✓ Thread mapping exists: thread={mapping['deerflow_thread_id']}")
        print(f"    studio={mapping.get('studio')}, workflow={mapping.get('workflow_id')}")
        print(f"    created_at={mapping.get('created_at')}")
    else:
        print(f"  ✗ No thread mapping found for run {run_id}")
        exit_code = 1

    # Check 3: Workspace paths resolve
    ws = WorkspaceMapping(REPO_ROOT)
    paths = ws.resolve(run_id)
    print(f"  ✓ Workspace paths resolved:")
    for key, path in paths.items():
        exists = "✓" if path.exists() else "○"
        print(f"    {exists} {key}: {path}")

    # Check 4: Bidirectional lookup works
    if mapping:
        reverse = mapping_store.get_by_thread_id(mapping["deerflow_thread_id"])
        if reverse and reverse.get("rig_run_id") == run_id:
            print(f"  ✓ Bidirectional lookup: thread → run = {run_id}")
        else:
            print(f"  ✗ Bidirectional lookup failed")
            exit_code = 1

    print()
    if exit_code == 0:
        print(f"✅ All mapping checks passed for {run_id}")
    else:
        print(f"❌ Mapping verification failed for {run_id}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
