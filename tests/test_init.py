"""Tests for rigforge init command."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

from typer.testing import CliRunner

from rigforge.cli import app

runner = CliRunner()


def test_init_creates_folder_structure(tmp_repo: Path) -> None:
    """rigforge init creates the required folder structure."""
    result = runner.invoke(app, ["init", "--repo", str(tmp_repo)])
    assert result.exit_code == 0

    assert (tmp_repo / "rig-runtime").is_dir()
    assert (tmp_repo / "rig-runtime" / "config").is_dir()
    assert (tmp_repo / "rig-runtime" / "contracts").is_dir()
    assert (tmp_repo / "rig-runtime" / "workflows").is_dir()
    assert (tmp_repo / "rig-runtime" / "agents").is_dir()
    assert (tmp_repo / "rig-runtime" / "studios").is_dir()
    assert (tmp_repo / "rig-runtime" / "scripts").is_dir()
    assert (tmp_repo / "rig-runtime" / "tests").is_dir()
    assert (tmp_repo / "rig-runtime" / "evals").is_dir()
    assert (tmp_repo / "rig-runtime" / "proof").is_dir()
    assert (tmp_repo / "rig-runtime" / "docs").is_dir()
    assert (tmp_repo / "rig-runtime" / "runs").is_dir()


def test_init_creates_config_file(tmp_repo: Path) -> None:
    """rigforge init creates rig.yaml config file."""
    result = runner.invoke(app, ["init", "--repo", str(tmp_repo)])
    assert result.exit_code == 0

    rig_yaml = tmp_repo / "rig-runtime" / "config" / "rig.yaml"
    assert rig_yaml.is_file()
    content = rig_yaml.read_text()
    assert "version:" in content


def test_init_idempotent(tmp_repo: Path) -> None:
    """Running init twice should not fail."""
    runner.invoke(app, ["init", "--repo", str(tmp_repo)])
    result = runner.invoke(app, ["init", "--repo", str(tmp_repo)])
    assert result.exit_code == 0


def test_init_invalid_path() -> None:
    """Init with non-existent path should fail."""
    result = runner.invoke(app, ["init", "--repo", "/nonexistent/path/xyz"])
    assert result.exit_code != 0
