#!/usr/bin/env python3
"""scripts/start_deerflow_run.py — Start a DeerFlow long-horizon run for a RIG mission.

Usage:
    python scripts/start_deerflow_run.py --mission soul-id-regression
    python scripts/start_deerflow_run.py --mission soul-id-regression --run-id run_abc123
    python scripts/start_deerflow_run.py --mission soul-id-regression --dry-run
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
import uuid
from pathlib import Path

REPO_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(REPO_ROOT))

from integrations.deerflow.deerflow_client import DeerFlowRigClient
from integrations.deerflow.thread_mapping import get_thread_mapping, reset_default_store


def create_run_envelope(run_id: str, mission: str, studio: str = "app") -> Path:
    """Create a minimal RunEnvelope + DoneContract for the mission."""
    run_dir = REPO_ROOT / "runs" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    envelope = {
        "run_id": run_id,
        "studio": studio,
        "idea": mission,
        "status": "deerflow_supervised",
        "harness": "deerflow",
    }
    (run_dir / "RunEnvelope.json").write_text(json.dumps(envelope, indent=2))

    import yaml
    contract = {
        "run_id": run_id,
        "studio": studio,
        "definition_of_done": mission,
        "acceptance_criteria": [],
        "non_goals": [],
        "risk_level": "MEDIUM",
        "rollback_plan": "Revert worktree",
        "approved": True,
        "approved_by": "smoke_test",
    }
    (run_dir / "DoneContract.yaml").write_text(yaml.dump(contract))

    return run_dir


async def main() -> None:
    parser = argparse.ArgumentParser(description="Start a DeerFlow long-horizon run")
    parser.add_argument("--mission", required=True, help="Mission identifier")
    parser.add_argument("--run-id", default="", help="Run ID (auto-generated if empty)")
    parser.add_argument("--studio", default="app", help="Studio name")
    parser.add_argument("--dry-run", action="store_true", help="Validate without calling DeerFlow")
    args = parser.parse_args()

    run_id = args.run_id or f"run_{uuid.uuid4().hex[:12]}"
    print(f"\n🦌 DeerFlow RIG Smoke Test")
    print(f"   mission: {args.mission}")
    print(f"   run_id:  {run_id}")
    print(f"   studio:  {args.studio}")
    print()

    # Step 1: Create RunEnvelope
    run_dir = create_run_envelope(run_id, args.mission, args.studio)
    print(f"✓ RunEnvelope created: {run_dir / 'RunEnvelope.json'}")

    if args.dry_run:
        print("\n[DRY RUN] Would start DeerFlow thread for this mission.")
        print(f"  Mapping store: {get_thread_mapping().store_path}")
        return

    # Step 2: Initialize DeerFlow client
    config_path = REPO_ROOT / "config" / "deerflow_rig.yaml"
    client = DeerFlowRigClient(config_path=str(config_path))
    print(f"✓ DeerFlowRigClient initialized (stub={client.is_stub})")

    # Step 3: Start long-horizon run
    mission_message = f"Execute RIG mission: {args.mission}. Follow the spec, plan, and DoneContract in the run directory."

    try:
        result = await client.run_long_horizon(
            run_id=run_id,
            message=mission_message,
            mission_id=args.mission,
            input_files=["spec.md", "plan.md", "DoneContract.yaml"],
        )
    except Exception as e:
        print(f"✗ DeerFlow run failed: {e}")
        sys.exit(1)

    # Step 4: Output results
    print(f"\n✓ DeerFlow run started")
    print(f"  thread_id: {result.get('thread_id', 'N/A')}")
    print(f"  status:    {result.get('status', 'N/A')}")

    mapping_record = result.get("mapping_record", {})
    if mapping_record:
        print(f"  mapping:   run={mapping_record.get('rig_run_id')} ↔ thread={mapping_record.get('deerflow_thread_id')}")

    print(f"\nNext steps:")
    print(f"  python scripts/verify_deerflow_mapping.py --run-id {run_id}")
    print(f"  python scripts/verify_deerflow_proof.py --run-id {run_id}")


if __name__ == "__main__":
    asyncio.run(main())
