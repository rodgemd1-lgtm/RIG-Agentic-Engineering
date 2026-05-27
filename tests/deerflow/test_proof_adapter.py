"""Tests for DeerFlow proof adapter.

Verifies that every DeerFlow sub-agent result produces a ProofPacket event
and that the evidence is properly structured.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest

from integrations.deerflow.proof_adapter import (
    emit_proof_event,
    collect_subagent_results,
    get_proof_packets,
)


@pytest.fixture(autouse=True)
def _cleanup_proof_dirs(tmp_path: Path):
    """Redirect proof output to tmp_path for test isolation."""
    with patch("integrations.deerflow.proof_adapter.PROOF_DIR", tmp_path / "proof"):
        yield


class TestEmitProofEvent:
    def test_emits_valid_proof_packet(self, tmp_path: Path) -> None:
        """emit_proof_event creates a valid ProofPacket."""
        pp = emit_proof_event(
            run_id="run_abc123",
            deerflow_thread_id="df_thread_xyz",
            subagent_id="lead_agent",
            task="thread_created",
            files_touched=["spec.md"],
            outputs=[],
            summary="Thread created successfully",
            status="pass",
            trace_uri="http://localhost:2026/api/langgraph/threads/df_thread_xyz",
        )
        assert pp.run_id == "run_abc123"
        assert pp.status == "pass"
        assert pp.phase == "deerflow"
        assert pp.evidence["deerflow_thread_id"] == "df_thread_xyz"
        assert pp.evidence["subagent_id"] == "lead_agent"

    def test_persists_to_disk(self, tmp_path: Path) -> None:
        """ProofPacket is written to disk."""
        pp = emit_proof_event(
            run_id="run_disk",
            deerflow_thread_id="df_disk",
            subagent_id="researcher",
            task="research",
            files_touched=[],
            outputs=["findings.md"],
            summary="Research complete",
            status="pass",
            trace_uri="http://localhost:2026/trace/123",
        )
        proof_dir = tmp_path / "proof" / "run_disk"
        assert proof_dir.exists()

        files = list(proof_dir.glob("pp_df_*.json"))
        assert len(files) == 1

        data = json.loads(files[0].read_text())
        assert data["packet_id"] == pp.packet_id
        assert data["status"] == "pass"

    def test_invalid_status_raises(self) -> None:
        """Invalid status raises ValueError."""
        with pytest.raises(ValueError, match="Invalid proof status"):
            emit_proof_event(
                run_id="run_123",
                deerflow_thread_id="df_123",
                subagent_id="agent",
                task="test",
                files_touched=[],
                outputs=[],
                summary="test",
                status="invalid",
                trace_uri="http://localhost:2026",
            )

    def test_fail_status(self, tmp_path: Path) -> None:
        """Failed sub-agent produces fail ProofPacket."""
        pp = emit_proof_event(
            run_id="run_fail",
            deerflow_thread_id="df_fail",
            subagent_id="coder",
            task="implement_feature",
            files_touched=["feature.py"],
            outputs=[],
            summary="Build failed: syntax error",
            status="fail",
            trace_uri="http://localhost:2026/trace/fail",
        )
        assert pp.status == "fail"

    def test_blocked_status(self, tmp_path: Path) -> None:
        """Blocked sub-agent produces blocked ProofPacket."""
        pp = emit_proof_event(
            run_id="run_blocked",
            deerflow_thread_id="df_blocked",
            subagent_id="deployer",
            task="deploy",
            files_touched=[],
            outputs=[],
            summary="Blocked: approval required",
            status="blocked",
            trace_uri="http://localhost:2026/trace/blocked",
        )
        assert pp.status == "blocked"

    def test_extra_evidence(self, tmp_path: Path) -> None:
        """Extra evidence is merged into the packet."""
        pp = emit_proof_event(
            run_id="run_extra",
            deerflow_thread_id="df_extra",
            subagent_id="agent",
            task="test",
            files_touched=[],
            outputs=[],
            summary="test",
            status="pass",
            trace_uri="http://localhost:2026",
            extra_evidence={"cost_usd": 0.05, "tokens_used": 1500},
        )
        assert pp.evidence["cost_usd"] == 0.05
        assert pp.evidence["tokens_used"] == 1500


class TestCollectSubagentResults:
    def test_collects_multiple_events(self, tmp_path: Path) -> None:
        """Multiple sub-agent events produce multiple ProofPackets."""
        events = [
            {
                "subagent_id": "researcher",
                "task": "research",
                "status": "pass",
                "files_touched": ["research.md"],
                "outputs": ["findings.md"],
                "summary": "Research done",
                "trace_uri": "http://localhost:2026/trace/1",
                "thread_id": "df_thread_1",
            },
            {
                "subagent_id": "coder",
                "task": "implement",
                "status": "pass",
                "files_touched": ["app.py"],
                "outputs": ["app.py"],
                "summary": "Code written",
                "trace_uri": "http://localhost:2026/trace/2",
                "thread_id": "df_thread_1",
            },
        ]
        packets = collect_subagent_results("run_batch", events)
        assert len(packets) == 2
        assert packets[0].evidence["subagent_id"] == "researcher"
        assert packets[1].evidence["subagent_id"] == "coder"


class TestGetProofPackets:
    def test_get_packets_for_run(self, tmp_path: Path) -> None:
        """Can retrieve all ProofPackets for a run."""
        emit_proof_event(
            run_id="run_retrieve",
            deerflow_thread_id="df_ret",
            subagent_id="agent1",
            task="task1",
            files_touched=[],
            outputs=[],
            summary="done",
            status="pass",
            trace_uri="http://localhost:2026",
        )
        emit_proof_event(
            run_id="run_retrieve",
            deerflow_thread_id="df_ret",
            subagent_id="agent2",
            task="task2",
            files_touched=[],
            outputs=[],
            summary="done",
            status="pass",
            trace_uri="http://localhost:2026",
        )

        packets = get_proof_packets("run_retrieve")
        assert len(packets) == 2

    def test_get_packets_empty(self, tmp_path: Path) -> None:
        """No packets for unknown run."""
        packets = get_proof_packets("run_nonexistent")
        assert packets == []
