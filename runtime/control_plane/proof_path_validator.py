"""Proof path validator — ensures every workflow/app has a proof path."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from runtime.control_plane.registry_loader import RegistryLoader


@dataclass
class ProofPathError:
    registry: str
    entry_id: str
    message: str


@dataclass
class ProofPathResult:
    valid: bool
    errors: list[ProofPathError] = field(default_factory=list)
    total_entries: int = 0
    entries_with_proof_path: int = 0


class ProofPathValidator:
    """Validate that workflows and apps have proof_path."""

    ENTRIES_REQUIRING_PROOF = {"workflow", "app", "service"}

    def __init__(self, repo_root: str = ".") -> None:
        self.repo_root = Path(repo_root)
        self.loader = RegistryLoader(repo_root)

    def validate_entry(
        self, registry: str, entry: dict[str, Any]
    ) -> ProofPathError | None:
        """Check one entry for proof_path field."""
        if registry not in self.ENTRIES_REQUIRING_PROOF:
            return None
        entry_id = entry.get("id", "<unknown>")
        if "proof_path" not in entry or not entry["proof_path"]:
            return ProofPathError(
                registry=registry,
                entry_id=entry_id,
                message=f"{registry}/{entry_id} has no proof_path — cannot participate in RIG workflow",
            )
        return None

    def validate_all(self) -> ProofPathResult:
        """Validate all entries requiring proof_path."""
        result = ProofPathResult(valid=True)
        registries = [
            ("service", self.loader.load_service()),
            ("app", self.loader.load_app()),
            ("workflow", self.loader.load_workflow()),
        ]
        for name, entries in registries:
            if not isinstance(entries, list):
                continue
            for entry in entries:
                result.total_entries += 1
                err = self.validate_entry(name, entry)
                if err:
                    result.errors.append(err)
                    result.valid = False
                else:
                    result.entries_with_proof_path += 1
        return result