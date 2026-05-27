"""Tests for rigforge learn command."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner
import yaml

from rigforge.cli import app

runner = CliRunner()


def test_learn_creates_regression_yaml(tmp_repo: Path) -> None:
    """rigforge learn creates a regression test yaml file."""
    result = runner.invoke(
        app,
        [
            "learn", "incident_test_001",
            "--failing-input", "soul_id bypass",
            "--expected-output", "BLOCKED",
            "--repo", str(tmp_repo),
        ],
    )
    assert result.exit_code == 0

    evals_dir = tmp_repo / "rig-runtime" / "evals"
    regression_files = list(evals_dir.glob("reg_*.yaml"))
    assert len(regression_files) == 1

    content = yaml.safe_load(regression_files[0].read_text())
    assert content["incident_id"] == "incident_test_001"
    assert content["failing_input"] == "soul_id bypass"


def test_learn_blocks_without_failing_input(tmp_repo: Path) -> None:
    """rigforge learn refuses without --failing-input."""
    result = runner.invoke(
        app,
        ["learn", "incident_test_002", "--repo", str(tmp_repo)],
    )
    assert result.exit_code != 0
    assert "failing input" in result.output.lower() or "failing-input" in result.output


def test_learn_updates_baseline(tmp_repo: Path) -> None:
    """rigforge learn updates the eval baseline."""
    runner.invoke(
        app,
        [
            "learn", "incident_baseline_test",
            "--failing-input", "test input",
            "--repo", str(tmp_repo),
        ],
    )

    baseline_path = tmp_repo / "rig-runtime" / "evals" / "baseline.yaml"
    assert baseline_path.exists()

    baseline = yaml.safe_load(baseline_path.read_text())
    assert baseline is not None
    assert "tests" in baseline
    assert len(baseline["tests"]) >= 1


def test_learn_emits_proof_packet(tmp_repo: Path) -> None:
    """rigforge learn emits a ProofPacket."""
    runner.invoke(
        app,
        [
            "learn", "incident_pp_test",
            "--failing-input", "test",
            "--repo", str(tmp_repo),
        ],
    )

    proof_dir = tmp_repo / "rig-runtime" / "proof"
    packets = list(proof_dir.glob("pp_*.json"))
    assert len(packets) > 0


def test_learn_updates_evidence_graph(tmp_repo: Path) -> None:
    """rigforge learn updates the evidence graph."""
    runner.invoke(
        app,
        [
            "learn", "incident_graph_test",
            "--failing-input", "test",
            "--repo", str(tmp_repo),
        ],
    )

    graph_path = tmp_repo / "rig-runtime" / "evals" / "evidence_graph.yaml"
    assert graph_path.exists()

    graph = yaml.safe_load(graph_path.read_text())
    assert "nodes" in graph
    assert "edges" in graph
    assert len(graph["nodes"]) >= 1
