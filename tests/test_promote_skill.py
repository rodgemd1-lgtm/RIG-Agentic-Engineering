"""Tests for rigforge promote-skill command."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner
import yaml

from rigforge.cli import app

runner = CliRunner()


def test_promote_skill_creates_proposal(tmp_repo: Path) -> None:
    """rigforge promote-skill creates a promotion proposal, not an active skill."""
    result = runner.invoke(
        app,
        ["promote-skill", "test_pattern_001", "--repo", str(tmp_repo)],
    )
    assert result.exit_code == 0

    proposal_path = tmp_repo / "rig-runtime" / "skills" / "test_pattern_001" / "promotion_proposal.yaml"
    assert proposal_path.exists()

    proposal = yaml.safe_load(proposal_path.read_text())
    assert proposal["pattern_id"] == "test_pattern_001"
    assert proposal["status"] == "proposed"


def test_promote_skill_creates_skill_stub(tmp_repo: Path) -> None:
    """rigforge promote-skill creates a SKILL.md stub."""
    runner.invoke(
        app,
        ["promote-skill", "test_pattern_002", "--repo", str(tmp_repo)],
    )

    skill_md_path = tmp_repo / "rig-runtime" / "skills" / "test_pattern_002" / "SKILL.md"
    assert skill_md_path.exists()

    content = skill_md_path.read_text()
    assert "PROPOSED" in content
    assert "Not yet active" in content


def test_promote_skill_not_active(tmp_repo: Path) -> None:
    """Promoted skill should be proposed, never active."""
    runner.invoke(
        app,
        ["promote-skill", "test_pattern_003", "--repo", str(tmp_repo)],
    )

    proposal_path = tmp_repo / "rig-runtime" / "skills" / "test_pattern_003" / "promotion_proposal.yaml"
    proposal = yaml.safe_load(proposal_path.read_text())
    assert proposal["status"] != "active"
