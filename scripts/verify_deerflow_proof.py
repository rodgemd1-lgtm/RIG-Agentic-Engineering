#!/usr/bin/env python3
"""scripts/verify_deerflow_proof.py — Verify ProofPacket emission for a DeerFlow run.

Usage:
    python scripts/verify_deerflow_proof.py --run-id run_abc123
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from integrations.deerflow.proof_adapter import get_proof_packets


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify DeerFlow proof packets")
    parser.add_argument("--run-id", required=True, help="Run ID to verify")
    args = parser.parse_args()

    run_id = args.run_id
    print(f"\n🔍 Verify DeerFlow ProofPackets: {run_id}\n")
    exit_code = 0

    # Check 1: ProofPackets exist
    packets = get_proof_packets(run_id)
    if packets:
        print(f"  ✓ Found {len(packets)} ProofPacket(s):")
        for pp in packets:
            print(f"    - {pp.get('packet_id')}: status={pp.get('status')}, phase={pp.get('phase')}")
            evidence = pp.get("evidence", {})
            if evidence.get("subagent_id"):
                print(f"      subagent={evidence['subagent_id']}, task={evidence.get('task', '?')}")
            if evidence.get("trace_uri"):
                print(f"      trace={evidence['trace_uri']}")
    else:
        print(f"  ✗ No ProofPackets found for run {run_id}")
        exit_code = 1

    # Check 2: All required fields present
    required_fields = {"packet_id", "run_id", "phase", "command", "status", "evidence"}
    for pp in packets:
        missing = required_fields - set(pp.keys())
        if missing:
            print(f"  ✗ Packet {pp.get('packet_id')} missing fields: {missing}")
            exit_code = 1

    # Check 3: Evidence links to thread
    for pp in packets:
        evidence = pp.get("evidence", {})
        thread_id = evidence.get("deerflow_thread_id")
        if thread_id:
            print(f"  ✓ Packet {pp['packet_id']} linked to thread {thread_id}")
        else:
            print(f"  ⚠ Packet {pp['packet_id']} has no thread linkage")

    # Check 4: Output hashes if workspace exists
    ws_mapping = REPO_ROOT / "runs" / run_id / "outputs"
    if ws_mapping.exists():
        from integrations.deerflow.workspace_mapping import WorkspaceMapping
        ws = WorkspaceMapping(REPO_ROOT)
        hashes = ws.hash_outputs(run_id)
        if hashes:
            print(f"  ✓ Output hashes: {len(hashes)} file(s)")
            for fname, fhash in list(hashes.items())[:5]:
                print(f"    {fname}: {fhash[:16]}...")
        else:
            print(f"  ○ No output files to hash")

    print()
    if exit_code == 0:
        print(f"✅ All proof checks passed for {run_id}")
    else:
        print(f"❌ Proof verification failed for {run_id}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
