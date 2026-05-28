"""Ownership validator — ensures every registry entry has an owner."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from runtime.control_plane.registry_loader import RegistryLoader


@dataclass
class OwnershipError:
    registry: str
    entry_id: str
    message: str


@dataclass
class OwnershipResult:
    valid: bool
    errors: list[OwnershipError] = field(default_factory=list)
    total_entries: int = 0
    entries_with_owner: int = 0


KNOWN_OWNERS = {"mike", "hermes", "codex", "pycode", "evaluator", "verifier", "generator", "cockpit"}


class OwnershipValidator:
    """Validate that every registry entry has an owner field."""

    def __init__(self, repo_root: str = ".") -> None:
        self.loader = RegistryLoader(repo_root)

    def validate_entry(
        self, registry: str, entry: dict[str, Any]
    ) -> OwnershipError | None:
        """Check one entry for owner field."""
        entry_id = entry.get("id", "<unknown>")
        if "owner" not in entry or not entry["owner"]:
            return OwnershipError(
                registry=registry,
                entry_id=entry_id,
                message=f"{registry}/{entry_id} has no owner",
            )
        return None

    def validate_all(self) -> OwnershipResult:
        """Validate all registry entries have owners."""
        result = OwnershipResult(valid=True)
        registries = [
            ("service", self.loader.load_service()),
            ("api", self.loader.load_api()),
            ("mcp", self.loader.load_mcp()),
            ("tool", self.loader.load_tool()),
            ("model", self.loader.load_model()),
            ("node", self.loader.load_node()),
            ("app", self.loader.load_app()),
            ("workflow", self.loader.load_workflow()),
            ("proof", self.loader.load_proof()),
            ("approval", self.loader.load_approval()),
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
                    result.entries_with_owner += 1
        return result