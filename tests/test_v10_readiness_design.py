"""Tests for the V10 readiness design artifact."""

from __future__ import annotations

import json
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).parent.parent


def test_v10_design_doc_exists_and_covers_required_outputs() -> None:
    """The design doc should define the required V10 planning outputs."""
    path = REPO_ROOT / "docs" / "V10_READINESS_DESIGN.md"
    assert path.is_file()

    content = path.read_text()
    required_sections = [
        "V10 Product Promise",
        "CLI Surface",
        "First deterministic local smoke command",
        "MCP Surface",
        "Agent Workflow Animation",
        "Quality Animation",
        "Weekly Improvement Animation",
        "Blockers and Gaps",
        "Proof Paths and Test Commands",
        "It does **not** claim final PASS",
    ]
    for section in required_sections:
        assert section in content


def test_v10_design_proof_artifact_is_not_a_final_pass() -> None:
    """The proof artifact should explicitly stay in design-only state."""
    path = REPO_ROOT / "proof" / "v10" / "v10_readiness_design.json"
    assert path.is_file()

    data = json.loads(path.read_text())
    assert data["status"] == "DESIGN_ONLY"
    assert data["not_final_pass"] is True
    assert data["smoke_command"] == "rigforge doctor --json"
    assert "docs/V10_READINESS_DESIGN.md" in data["proof_paths"]
    assert "python3 -m pytest tests/test_v10_readiness_design.py -q" in data["test_commands"]


def test_v10_proof_path_registered() -> None:
    """The proof registry should expose the V10 design proof path."""
    path = REPO_ROOT / "config" / "proof_registry.yaml"
    data = yaml.safe_load(path.read_text())
    paths = {entry["path"] for entry in data["proof_paths"]}
    assert "proof/v10/" in paths
