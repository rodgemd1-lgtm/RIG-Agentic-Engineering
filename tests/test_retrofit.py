"""Tests for rigforge retrofit command."""

from __future__ import annotations

from pathlib import Path

from typer.testing import CliRunner

from rigforge.cli import app

runner = CliRunner()


def test_retrofit_dry_run_no_modify(tmp_repo: Path) -> None:
    """rigforge retrofit --dry-run does not modify files."""
    studio_path = tmp_repo / "studios" / "teststudio"
    studio_path.mkdir(parents=True)

    result = runner.invoke(app, ["retrofit", "teststudio", "--dry-run", "--repo", str(tmp_repo)])
    # Dry-run should succeed (exit 0) since studio exists
    assert result.exit_code == 0

    # No retrofit files should be created
    assert not (studio_path / "RunEnvelope.json").exists()
    assert not (studio_path / "DoneContract.yaml").exists()
    assert not (studio_path / "tool_allowlist.yaml").exists()


def test_retrofit_apply_creates_files(tmp_repo: Path) -> None:
    """rigforge retrofit --apply creates retrofit files."""
    studio_path = tmp_repo / "studios" / "teststudio"
    studio_path.mkdir(parents=True)

    result = runner.invoke(app, ["retrofit", "teststudio", "--apply", "--repo", str(tmp_repo)])
    assert result.exit_code == 0

    assert (studio_path / "RunEnvelope.json").exists()
    assert (studio_path / "DoneContract.yaml").exists()
    assert (studio_path / "tool_allowlist.yaml").exists()
    assert (studio_path / "gev_loop.yaml").exists()
    assert (studio_path / "proof_policy.yaml").exists()


def test_retrofit_verify_after_apply(tmp_repo: Path) -> None:
    """rigforge retrofit --verify passes after --apply."""
    studio_path = tmp_repo / "studios" / "teststudio"
    studio_path.mkdir(parents=True)

    runner.invoke(app, ["retrofit", "teststudio", "--apply", "--repo", str(tmp_repo)])
    result = runner.invoke(app, ["retrofit", "teststudio", "--verify", "--repo", str(tmp_repo)])
    assert result.exit_code == 0


def test_retrofit_missing_studio_fails(tmp_repo: Path) -> None:
    """Retrofit on non-existent studio should fail."""
    result = runner.invoke(app, ["retrofit", "nonexistent", "--dry-run", "--repo", str(tmp_repo)])
    assert result.exit_code != 0
