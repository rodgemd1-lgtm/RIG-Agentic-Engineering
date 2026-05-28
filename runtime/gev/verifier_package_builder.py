"""Verifier package builder — assembles what the stateless verifier receives.

Core law: Verifier must NOT receive Generator or Evaluator chat history.
Core law: No verifier package, no PASS.
"""

from __future__ import annotations

import hashlib
import subprocess
from dataclasses import dataclass
from pathlib import Path

from contractsv1.verifier_package import VerifierPackage
from contractsv1.done_contract import DoneContract


@dataclass
class BuildResult:
    """Result of building the verifier package."""
    package: VerifierPackage
    clean: bool  # True if no forbidden items included
    file_hashes: dict[str, str]


class VerifierPackageBuilder:
    """Assemble the VerifierPackage for stateless judgment.

    Verifier receives ONLY:
    - spec.md
    - DoneContract.yaml
    - Final file tree snapshot
    - Test commands
    - ProofPacket paths
    - Hash manifest

    Verifier must NOT receive:
    - Generator chat history
    - Evaluator chat history
    - Intermediate drafts
    - Self-assessments
    """

    FORBIDDEN_KEYS = [
        "generator_chat_history",
        "evaluator_chat_history",
        "intermediate_drafts",
        "self_assessments",
    ]

    def __init__(self, repo_root: Path | str = ".") -> None:
        self.repo_root = Path(repo_root)

    def hash_file(self, path: Path) -> str:
        """Compute SHA-256 hash of a file."""
        if not path.exists():
            return "NOT_FOUND"
        sha = hashlib.sha256()
        sha.update(path.read_bytes())
        return sha.hexdigest()

    def get_file_tree(self, root: Path, relative_to: Path | None = None) -> list[str]:
        """Get list of all files under root, as relative paths."""
        rel = relative_to or root
        files = []
        if not root.is_dir():
            return files
        for p in sorted(root.rglob("*")):
            if p.is_file() and not any(part.startswith(".") for part in p.parts):
                try:
                    files.append(str(p.relative_to(rel)))
                except ValueError:
                    files.append(str(p))
        return files

    def build(
        self,
        run_id: str,
        studio: str,
        spec_path: str,
        done_contract_path: str,
        workspace_root: Path,
        proof_paths: list[str],
        test_commands: list[str],
    ) -> BuildResult:
        """Build the complete VerifierPackage."""
        file_tree = self.get_file_tree(workspace_root)
        hashes = {str(p): self.hash_file(workspace_root / p) for p in file_tree}

        package = VerifierPackage(
            run_id=run_id,
            studio=studio,
            spec_path=spec_path,
            done_contract_path=done_contract_path,
            file_tree_snapshot=file_tree,
            test_commands=test_commands,
            proof_packet_paths=proof_paths,
            hash_manifest=hashes,
        )

        clean = package.is_clean()

        return BuildResult(
            package=package,
            clean=clean,
            file_hashes=hashes,
        )

    def verify_against_package(
        self, package: VerifierPackage, workspace_root: Path
    ) -> tuple[bool, list[str]]:
        """Verify actual files match the package hash manifest."""
        mismatches = []
        for rel_path, expected_hash in package.hash_manifest.items():
            actual_hash = self.hash_file(workspace_root / rel_path)
            if actual_hash != expected_hash:
                mismatches.append(f"{rel_path}: expected {expected_hash}, got {actual_hash}")
        return len(mismatches) == 0, mismatches