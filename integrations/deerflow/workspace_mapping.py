"""Workspace mapping: DeerFlow workspace paths <-> RIG worktree paths.

DeerFlow paths:
    /mnt/user-data/uploads   → runs/<run_id>/inputs/
    /mnt/user-data/workspace → worktrees/<run_id>/
    /mnt/user-data/outputs   → runs/<run_id>/outputs/

All final outputs must be copied to runs/<run_id>/outputs/ and hashed into ProofPacket.
"""

from __future__ import annotations

import hashlib
import json
import logging
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)


class WorkspaceMapping:
    """Maps between DeerFlow thread workspace paths and RIG run directories."""

    def __init__(self, repo_root: Path = Path(".")) -> None:
        self.repo_root = repo_root.resolve()

    def resolve(self, run_id: str) -> dict[str, Path]:
        """
        Resolve all workspace paths for a given run ID.

        Returns:
            Dict with keys:
                inputs, workspace, outputs, deerflow_workspace, deerflow_uploads, deerflow_outputs
        """
        run_dir = self.repo_root / "runs" / run_id
        worktree_dir = self.repo_root / "worktrees" / run_id

        paths = {
            # RIG canonical paths
            "inputs": run_dir / "inputs",
            "workspace": worktree_dir,
            "outputs": run_dir / "outputs",

            # DeerFlow thread workspace (inside DeerFlow's filesystem)
            "deerflow_workspace": Path(f"deerflow/.deer-flow/threads/{run_id}/user-data/workspace"),
            "deerflow_uploads": Path(f"deerflow/.deer-flow/threads/{run_id}/user-data/uploads"),
            "deerflow_outputs": Path(f"deerflow/.deer-flow/threads/{run_id}/user-data/outputs"),
        }

        return paths

    def ensure_directories(self, run_id: str) -> dict[str, Path]:
        """Create all necessary directories for a run."""
        paths = self.resolve(run_id)
        for key, path in paths.items():
            path.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Workspace dir ensured: {path}")
        return paths

    def copy_to_workspace(
        self,
        run_id: str,
        files: list[str],
        source_dir: Optional[Path] = None,
    ) -> list[Path]:
        """
        Copy input files from RIG run_dir/inputs/ into DeerFlow workspace.

        Args:
            run_id: The run ID
            files: List of filenames to copy
            source_dir: Override source directory (default: runs/<run_id>/inputs/)

        Returns:
            List of destination paths in the workspace
        """
        paths = self.resolve(run_id)
        src = source_dir or paths["inputs"]
        dst = paths["workspace"]
        dst.mkdir(parents=True, exist_ok=True)

        copied = []
        for filename in files:
            src_file = src / filename
            dst_file = dst / filename
            if src_file.exists():
                shutil.copy2(src_file, dst_file)
                copied.append(dst_file)
                logger.info(f"Copied to workspace: {src_file} → {dst_file}")
            else:
                logger.warning(f"Input file not found: {src_file}")

        return copied

    def copy_from_workspace(
        self,
        run_id: str,
        files: Optional[list[str]] = None,
    ) -> list[Path]:
        """
        Copy outputs from DeerFlow workspace back to RIG runs/<run_id>/outputs/.

        If files is None, copies everything from workspace/outputs/.

        Returns:
            List of copied file paths in runs/<run_id>/outputs/
        """
        paths = self.resolve(run_id)
        ws_outputs = paths["outputs"]
        rig_outputs = paths["outputs"]
        rig_outputs.mkdir(parents=True, exist_ok=True)

        if files is None:
            # Copy all files from workspace outputs
            ws_src = paths["workspace"]
            if ws_src.exists():
                copied = []
                for f in ws_src.rglob("*"):
                    if f.is_file():
                        rel = f.relative_to(ws_src)
                        dst_file = rig_outputs / rel
                        dst_file.parent.mkdir(parents=True, exist_ok=True)
                        shutil.copy2(f, dst_file)
                        copied.append(dst_file)
                logger.info(f"Copied {len(copied)} files from workspace to outputs")
                return copied
            return []

        copied = []
        ws_src_base = paths["workspace"]
        for filename in files:
            src = ws_src_base / filename
            dst = rig_outputs / filename
            if src.exists():
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied.append(dst)
                logger.info(f"Output collected: {src} → {dst}")
            else:
                logger.warning(f"Output file not found in workspace: {src}")

        return copied

    def hash_outputs(self, run_id: str) -> dict[str, str]:
        """
        Hash all files in runs/<run_id>/outputs/ for ProofPacket evidence.

        Returns:
            Dict mapping relative file paths to SHA-256 hex digests
        """
        paths = self.resolve(run_id)
        outputs_dir = paths["outputs"]

        if not outputs_dir.exists():
            return {}

        hashes = {}
        for f in sorted(outputs_dir.rglob("*")):
            if f.is_file():
                rel = str(f.relative_to(outputs_dir))
                sha256 = hashlib.sha256(f.read_bytes()).hexdigest()
                hashes[rel] = sha256

        logger.info(f"Hashed {len(hashes)} output files for run {run_id}")
        return hashes

    def generate_manifest(self, run_id: str) -> dict[str, Any]:
        """
        Generate a complete workspace manifest for ProofPacket evidence.

        Includes file listing + hashes of all outputs.
        """
        paths = self.resolve(run_id)
        hashes = self.hash_outputs(run_id)

        manifest = {
            "run_id": run_id,
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "paths": {k: str(v) for k, v in paths.items()},
            "output_files": hashes,
            "output_count": len(hashes),
        }

        return manifest


def get_workspace_mapping(repo_root: Path = Path(".")) -> WorkspaceMapping:
    """Get a WorkspaceMapping instance."""
    return WorkspaceMapping(repo_root)
