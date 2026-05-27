"""Tests for DeerFlow workspace mapping.

Verifies that DeerFlow workspace paths map correctly to RIG worktrees
and that output collection/hashing works.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from integrations.deerflow.workspace_mapping import WorkspaceMapping


@pytest.fixture
def ws(tmp_path: Path) -> WorkspaceMapping:
    return WorkspaceMapping(repo_root=tmp_path)


class TestWorkspaceResolve:
    def test_resolve_returns_all_paths(self, ws: WorkspaceMapping) -> None:
        """Resolve returns all 6 path entries."""
        paths = ws.resolve("run_abc123")
        expected_keys = {
            "inputs", "workspace", "outputs",
            "deerflow_workspace", "deerflow_uploads", "deerflow_outputs",
        }
        assert set(paths.keys()) == expected_keys

    def test_rig_inputs_path(self, ws: WorkspaceMapping, tmp_path: Path) -> None:
        """Inputs map to runs/<run_id>/inputs/."""
        paths = ws.resolve("run_xyz")
        assert paths["inputs"] == tmp_path / "runs" / "run_xyz" / "inputs"

    def test_rig_workspace_path(self, ws: WorkspaceMapping, tmp_path: Path) -> None:
        """Workspace maps to worktrees/<run_id>/."""
        paths = ws.resolve("run_xyz")
        assert paths["workspace"] == tmp_path / "worktrees" / "run_xyz"

    def test_rig_outputs_path(self, ws: WorkspaceMapping, tmp_path: Path) -> None:
        """Outputs map to runs/<run_id>/outputs/."""
        paths = ws.resolve("run_xyz")
        assert paths["outputs"] == tmp_path / "runs" / "run_xyz" / "outputs"

    def test_deerflow_upload_path(self, ws: WorkspaceMapping) -> None:
        """DeerFlow uploads path follows expected structure."""
        paths = ws.resolve("run_xyz")
        assert "uploads" in str(paths["deerflow_uploads"])

    def test_deerflow_output_path(self, ws: WorkspaceMapping) -> None:
        """DeerFlow outputs path follows expected structure."""
        paths = ws.resolve("run_xyz")
        assert "outputs" in str(paths["deerflow_outputs"])


class TestWorkspaceEnsure:
    def test_ensure_creates_directories(
        self, ws: WorkspaceMapping, tmp_path: Path
    ) -> None:
        """ensure_directories creates all RIG paths."""
        ws.ensure_directories("run_ensure")
        assert (tmp_path / "runs" / "run_ensure" / "inputs").is_dir()
        assert (tmp_path / "worktrees" / "run_ensure").is_dir()
        assert (tmp_path / "runs" / "run_ensure" / "outputs").is_dir()


class TestWorkspaceCopyTo:
    def test_copy_inputs_to_workspace(
        self, ws: WorkspaceMapping, tmp_path: Path
    ) -> None:
        """Input files can be copied to workspace."""
        inputs_dir = tmp_path / "runs" / "run_copy" / "inputs"
        inputs_dir.mkdir(parents=True)
        (inputs_dir / "spec.md").write_text("# Spec\n")
        (inputs_dir / "plan.md").write_text("# Plan\n")

        copied = ws.copy_to_workspace("run_copy", ["spec.md", "plan.md"])
        assert len(copied) == 2
        assert (tmp_path / "worktrees" / "run_copy" / "spec.md").exists()
        assert (tmp_path / "worktrees" / "run_copy" / "plan.md").exists()


class TestWorkspaceCopyFrom:
    def test_copy_outputs_from_workspace(
        self, ws: WorkspaceMapping, tmp_path: Path
    ) -> None:
        """Output files can be copied back from workspace."""
        ws_dir = tmp_path / "worktrees" / "run_out"
        ws_dir.mkdir(parents=True)
        (ws_dir / "build.py").write_text("# built\n")
        (ws_dir / "test_build.py").write_text("# tests\n")

        copied = ws.copy_from_workspace("run_out")
        assert len(copied) >= 2
        assert (tmp_path / "runs" / "run_out" / "outputs" / "build.py").exists()


class TestWorkspaceHashing:
    def test_hash_outputs(self, ws: WorkspaceMapping, tmp_path: Path) -> None:
        """Output files are hashed with SHA-256."""
        outputs_dir = tmp_path / "runs" / "run_hash" / "outputs"
        outputs_dir.mkdir(parents=True)
        (outputs_dir / "result.json").write_text('{"status": "pass"}')

        hashes = ws.hash_outputs("run_hash")
        assert "result.json" in hashes
        assert len(hashes["result.json"]) == 64  # SHA-256 hex

    def test_hash_empty_outputs(self, ws: WorkspaceMapping) -> None:
        """No outputs → empty hash dict."""
        hashes = ws.hash_outputs("run_empty")
        assert hashes == {}


class TestWorkspaceManifest:
    def test_generate_manifest(self, ws: WorkspaceMapping, tmp_path: Path) -> None:
        """Manifest includes paths, hashes, and metadata."""
        outputs_dir = tmp_path / "runs" / "run_manifest" / "outputs"
        outputs_dir.mkdir(parents=True)
        (outputs_dir / "artifact.py").write_text("# artifact\n")

        manifest = ws.generate_manifest("run_manifest")
        assert manifest["run_id"] == "run_manifest"
        assert manifest["output_count"] == 1
        assert "artifact.py" in manifest["output_files"]
        assert "paths" in manifest

    def test_workspace_maps_to_worktree(self, ws: WorkspaceMapping) -> None:
        """DeerFlow workspace maps to RIG worktree path (not run dir)."""
        paths = ws.resolve("run_abc123")
        # workspace should be under worktrees/, NOT runs/
        assert "worktrees" in str(paths["workspace"])
        assert "runs" not in str(paths["workspace"])
