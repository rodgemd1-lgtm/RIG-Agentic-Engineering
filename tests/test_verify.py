"""Tests for rigforge verify command."""

from __future__ import annotations

import json
from pathlib import Path

from typer.testing import CliRunner
import yaml

from rigforge.cli import app

runner = CliRunner()


def test_verify_catches_missing_proof_packet(tmp_repo: Path) -> None:
    """rigforge verify catches missing ProofPacket."""
    rd = tmp_repo / "runs" / "run_nopp"
    rd.mkdir(parents=True)
    (rd / "spec.md").write_text("# Spec")
    (rd / "DoneContract.yaml").write_text(yaml.dump({
        "run_id": "run_nopp",
        "studio": "test",
        "definition_of_done": "test",
        "risk_level": "LOW",
    }))

    result = runner.invoke(
        app,
        ["verify", "teststudio", "--run-id", "run_nopp", "--repo", str(tmp_repo)],
    )
    assert result.exit_code != 0
    assert "ProofPacket" in result.output


def test_verify_passes_with_proof_packet(tmp_repo: Path) -> None:
    """rigforge verify passes when ProofPackets exist and pass."""
    rd = tmp_repo / "runs" / "run_withpp"
    rd.mkdir(parents=True)

    (rd / "spec.md").write_text("# Spec")
    (rd / "DoneContract.yaml").write_text(yaml.dump({
        "run_id": "run_withpp",
        "studio": "test",
        "definition_of_done": "test",
        "risk_level": "LOW",
    }))

    proof_dir = rd / "proof"
    proof_dir.mkdir()
    pp = {
        "packet_id": "pp_test_001",
        "phase": "build",
        "command": "rigforge build teststudio",
        "status": "pass",
        "evidence": {},
    }
    (proof_dir / "pp_test_001.json").write_text(json.dumps(pp))

    reg_dir = rd / "evals"
    reg_dir.mkdir()
    (reg_dir / "reg_test.yaml").write_text("test: regression\n")

    result = runner.invoke(
        app,
        ["verify", "teststudio", "--run-id", "run_withpp", "--repo", str(tmp_repo)],
    )
    assert result.exit_code == 0


def test_verify_requires_run_id(tmp_repo: Path) -> None:
    """rigforge verify requires --run-id."""
    result = runner.invoke(
        app,
        ["verify", "teststudio", "--repo", str(tmp_repo)],
    )
    assert result.exit_code != 0
    assert "--run-id" in result.output
