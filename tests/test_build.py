"""Tests for rigforge build command."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner
import yaml

from rigforge.cli import app

runner = CliRunner()


def _create_run_with_contract(repo: Path, run_id: str, approved: bool = False) -> Path:
    """Helper: create a run directory with DoneContract and RunEnvelope."""
    rd = repo / "runs" / run_id
    rd.mkdir(parents=True)
    (rd / "proof").mkdir()

    envelope = {
        "run_id": run_id,
        "studio": "teststudio",
        "idea": "test",
        "status": "created",
    }
    (rd / "RunEnvelope.json").write_text(json.dumps(envelope))

    contract = {
        "run_id": run_id,
        "studio": "teststudio",
        "definition_of_done": "test",
        "acceptance_criteria": [],
        "non_goals": [],
        "risk_level": "MEDIUM",
        "rollback_plan": "",
        "approved": approved,
        "approved_by": "test" if approved else "",
    }
    (rd / "DoneContract.yaml").write_text(yaml.dump(contract))

    (rd / "tool_allowlist.yaml").write_text("allowed_tools: []\n")
    (rd / "approval_packet.json").write_text('{}')

    return rd


def test_build_refuses_missing_done_contract(tmp_repo: Path) -> None:
    """rigforge build refuses missing DoneContract."""
    result = runner.invoke(
        app,
        ["build", "teststudio", "--run-id", "run_missing", "--repo", str(tmp_repo)],
    )
    assert result.exit_code != 0
    assert "DoneContract" in result.output


def test_build_refuses_unapproved_contract(tmp_repo: Path) -> None:
    """rigforge build refuses when DoneContract is not approved."""
    _create_run_with_contract(tmp_repo, "run_unapproved", approved=False)

    result = runner.invoke(
        app,
        ["build", "teststudio", "--run-id", "run_unapproved", "--repo", str(tmp_repo)],
    )
    assert result.exit_code != 0
    assert "not approved" in result.output


def test_build_succeeds_with_approved_contract(tmp_repo: Path) -> None:
    """rigforge build proceeds with approved DoneContract."""
    _create_run_with_contract(tmp_repo, "run_approved", approved=True)

    result = runner.invoke(
        app,
        ["build", "teststudio", "--run-id", "run_approved", "--repo", str(tmp_repo)],
    )
    assert result.exit_code == 0

    # Verify ProofPacket was emitted
    proof_files = list((tmp_repo / "runs" / "run_approved" / "proof").glob("pp_*.json"))
    assert len(proof_files) > 0


def test_build_refuses_invalid_harness(tmp_repo: Path) -> None:
    """rigforge build refuses invalid harness."""
    _create_run_with_contract(tmp_repo, "run_harness", approved=True)

    result = runner.invoke(
        app,
        ["build", "teststudio", "--run-id", "run_harness", "--harness", "invalid", "--repo", str(tmp_repo)],
    )
    assert result.exit_code != 0
    assert "Invalid harness" in result.output


def test_build_emits_proof_packet(tmp_repo: Path) -> None:
    """rigforge build emits a ProofPacket on success."""
    _create_run_with_contract(tmp_repo, "run_pp", approved=True)

    runner.invoke(
        app,
        ["build", "teststudio", "--run-id", "run_pp", "--repo", str(tmp_repo)],
    )

    proof_dir = tmp_repo / "runs" / "run_pp" / "proof"
    packets = list(proof_dir.glob("pp_*.json"))
    assert len(packets) == 1

    pp_data = json.loads(packets[0].read_text())
    assert pp_data["status"] == "pass"
    assert pp_data["phase"] == "build"
