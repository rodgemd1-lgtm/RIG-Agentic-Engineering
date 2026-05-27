"""Tests for rigforge approve command."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner
import yaml

from rigforge.cli import app

runner = CliRunner()


def _create_run_with_approvable_artifacts(repo: Path, run_id: str) -> Path:
    """Create a run with DoneContract, ProofPacket, and approval_packet."""
    rd = repo / "runs" / run_id
    rd.mkdir(parents=True)

    (rd / "DoneContract.yaml").write_text(yaml.dump({
        "run_id": run_id,
        "studio": "test",
        "definition_of_done": "test",
        "acceptance_criteria": [],
        "non_goals": [],
        "risk_level": "LOW",
        "rollback_plan": "",
        "approved": False,
        "approved_by": "",
    }))

    proof_dir = rd / "proof"
    proof_dir.mkdir()
    pp = {
        "packet_id": "pp_test_approve",
        "run_id": run_id,
        "phase": "build",
        "command": "rigforge build test",
        "status": "pass",
        "evidence": {},
    }
    (proof_dir / "pp_test_approve.json").write_text(json.dumps(pp))

    (rd / "approval_packet.json").write_text(json.dumps({
        "run_id": run_id,
        "status": "ready_for_approval",
    }))

    return rd


def test_approve_refuses_no_approval_packet(tmp_repo: Path) -> None:
    """rigforge approve refuses when no approval packet exists."""
    rd = tmp_repo / "runs" / "run_no_packet"
    rd.mkdir(parents=True)
    (rd / "DoneContract.yaml").write_text(yaml.dump({
        "run_id": "run_no_packet",
        "studio": "test",
        "approved": False,
        "risk_level": "LOW",
    }))
    proof_dir = rd / "proof"
    proof_dir.mkdir()
    (proof_dir / "pp_001.json").write_text(json.dumps({"status": "pass"}))

    result = runner.invoke(
        app,
        ["approve", "run_no_packet", "--repo", str(tmp_repo)],
    )
    assert result.exit_code != 0
    assert "approval packet" in result.output


def test_approve_refuses_no_proof_packet(tmp_repo: Path) -> None:
    """rigforge approve refuses when no ProofPacket exists."""
    rd = tmp_repo / "runs" / "run_no_pp"
    rd.mkdir(parents=True)
    (rd / "DoneContract.yaml").write_text(yaml.dump({
        "run_id": "run_no_pp",
        "studio": "test",
        "approved": False,
        "risk_level": "LOW",
    }))
    (rd / "approval_packet.json").write_text("{}")

    result = runner.invoke(
        app,
        ["approve", "run_no_pp", "--repo", str(tmp_repo)],
    )
    assert result.exit_code != 0
    assert "ProofPacket" in result.output


def test_approve_refuses_unsigned(tmp_repo: Path) -> None:
    """rigforge approve refuses auto-approval (no --by, no --signature)."""
    _create_run_with_approvable_artifacts(tmp_repo, "run_unsigned")

    result = runner.invoke(
        app,
        ["approve", "run_unsigned", "--repo", str(tmp_repo)],
    )
    assert result.exit_code != 0
    assert "auto-approval" in result.output


def test_approve_records_approval(tmp_repo: Path) -> None:
    """rigforge approve records approval with --by and --signature."""
    _create_run_with_approvable_artifacts(tmp_repo, "run_signed")

    result = runner.invoke(
        app,
        ["approve", "run_signed", "--by", "mike", "--signature", "test_sig", "--repo", str(tmp_repo)],
    )
    assert result.exit_code == 0

    # Verify DoneContract updated
    contract_path = tmp_repo / "runs" / "run_signed" / "DoneContract.yaml"
    contract = yaml.safe_load(contract_path.read_text())
    assert contract["approved"] is True
    assert contract["approved_by"] == "mike"

    # Verify ProofPacket emitted
    proof_files = list((tmp_repo / "runs" / "run_signed" / "proof").glob("pp_*.json"))
    assert len(proof_files) >= 2  # original + approval
