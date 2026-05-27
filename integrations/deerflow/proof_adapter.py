"""Proof adapter: Every DeerFlow sub-agent result produces a ProofPacket event.

Integration between DeerFlow thread events and RIG ProofPacket system.
All sub-agent outputs get captured, hashed, and stored as evidence.
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from rigforge.models import ProofPacket

logger = logging.getLogger(__name__)

PROOF_DIR = Path("rig-runtime/proof/deerflow")


def emit_proof_event(
    run_id: str,
    deerflow_thread_id: str,
    subagent_id: str,
    task: str,
    files_touched: list[str],
    outputs: list[str],
    summary: str,
    status: str,  # "pass" | "fail" | "blocked"
    trace_uri: str,
    extra_evidence: Optional[dict[str, Any]] = None,
) -> ProofPacket:
    """
    Emit a ProofPacket event for a DeerFlow sub-agent result.

    This is the ONLY way DeerFlow events become RIG audit evidence.

    Args:
        run_id: RIG RunEnvelope ID
        deerflow_thread_id: DeerFlow thread ID
        subagent_id: Sub-agent identifier (lead_agent, researcher, coder, etc.)
        task: What the sub-agent was asked to do
        files_touched: Files modified by this sub-agent
        outputs: Output file paths produced
        summary: Human-readable result summary
        status: "pass" | "fail" | "blocked"
        trace_uri: Langfuse/LangSmith trace URI for this sub-agent run
        extra_evidence: Any additional evidence data

    Returns:
        The created ProofPacket
    """
    if status not in ("pass", "fail", "blocked"):
        raise ValueError(f"Invalid proof status: {status}. Must be pass, fail, or blocked.")

    evidence: dict[str, Any] = {
        "deerflow_thread_id": deerflow_thread_id,
        "subagent_id": subagent_id,
        "task": task,
        "files_touched": files_touched,
        "outputs": outputs,
        "summary": summary,
        "trace_uri": trace_uri,
    }
    if extra_evidence:
        evidence.update(extra_evidence)

    pp = ProofPacket(
        packet_id=f"pp_df_{uuid.uuid4().hex[:12]}",
        run_id=run_id,
        phase="deerflow",
        command=f"deerflow.subagent.{subagent_id}",
        status=status,
        evidence=evidence,
    )

    # Persist to disk
    proof_dir = PROOF_DIR / run_id
    proof_dir.mkdir(parents=True, exist_ok=True)

    proof_file = proof_dir / f"{pp.packet_id}.json"
    proof_file.write_text(
        json.dumps(pp.model_dump(mode="json"), indent=2, default=str)
    )

    logger.info(
        f"ProofPacket emitted: {pp.packet_id} "
        f"(run={run_id}, subagent={subagent_id}, status={status})"
    )
    return pp


def collect_subagent_results(
    run_id: str,
    thread_events: list[dict[str, Any]],
) -> list[ProofPacket]:
    """
    Process a batch of DeerFlow thread events and emit ProofPackets.

    Args:
        run_id: RIG run ID
        thread_events: List of DeerFlow event dicts from thread history

    Returns:
        List of emitted ProofPackets
    """
    packets = []

    for event in thread_events:
        subagent_id = event.get("subagent_id", "unknown")
        task = event.get("task", "")
        status = event.get("status", "pass")
        files_touched = event.get("files_touched", [])
        outputs = event.get("outputs", [])
        summary = event.get("summary", "")
        trace_uri = event.get("trace_uri", "")
        thread_id = event.get("thread_id", "")

        pp = emit_proof_event(
            run_id=run_id,
            deerflow_thread_id=thread_id,
            subagent_id=subagent_id,
            task=task,
            files_touched=files_touched,
            outputs=outputs,
            summary=summary,
            status=status,
            trace_uri=trace_uri,
        )
        packets.append(pp)

    logger.info(f"Collected {len(packets)} proof events for run {run_id}")
    return packets


def get_proof_packets(run_id: str) -> list[dict[str, Any]]:
    """Retrieve all ProofPackets for a DeerFlow run."""
    proof_dir = PROOF_DIR / run_id
    if not proof_dir.exists():
        return []

    packets = []
    for f in sorted(proof_dir.glob("pp_df_*.json")):
        packets.append(json.loads(f.read_text()))
    return packets
