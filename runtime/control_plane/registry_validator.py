"""Registry validator — enforces required fields per registry type."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from runtime.control_plane.registry_loader import RegistryLoader, load_all_registries


@dataclass
class ValidationError:
    """A single validation failure."""
    registry: str
    entry_id: str
    field: str
    message: str


@dataclass
class ValidationResult:
    """Result of validating one registry."""
    registry: str
    valid: bool
    errors: list[ValidationError] = field(default_factory=list)
    entry_count: int = 0


@dataclass
class FullValidationResult:
    """Result of validating all registries."""
    valid: bool
    results: dict[str, ValidationResult] = field(default_factory=dict)
    total_errors: int = 0


REQUIRED_FIELDS = {
    "service": ["id", "name", "owner"],
    "api": ["id", "name", "owner", "endpoint", "method"],
    "mcp": ["id", "name", "owner"],
    "tool": ["id", "name", "owner", "allowed_agents"],
    "model": ["id", "name", "owner", "allowed_use_cases"],
    "node": ["id", "name", "owner"],
    "app": ["id", "name", "owner"],
    "workflow": ["id", "name", "owner", "path", "proof_path"],
    "proof": ["id", "name", "owner", "path"],
    "approval": ["id", "name", "owner", "required_signers"],
}

SERVICE_REQUIRED_FIELDS = ["owner", "healthcheck", "proof_path"]
TOOL_REQUIRED_FIELDS = ["allowed_agents"]
MODEL_REQUIRED_FIELDS = ["allowed_use_cases"]


class RegistryValidator:
    """Validate that all registry entries have required fields."""

    def __init__(self, repo_root: Path | str = ".") -> None:
        self.loader = RegistryLoader(repo_root)

    def _validate_entry(
        self, registry_name: str, entry: dict[str, Any], required: list[str]
    ) -> list[ValidationError]:
        """Validate a single entry against required fields."""
        errors = []
        entry_id = entry.get("id", "<unknown>")
        for field_name in required:
            if field_name not in entry or entry[field_name] is None:
                errors.append(ValidationError(
                    registry=registry_name,
                    entry_id=entry_id,
                    field=field_name,
                    message=f"Missing required field '{field_name}' in {registry_name}/{entry_id}",
                ))
        return errors

    def validate_service(self) -> ValidationResult:
        """Validate service registry entries."""
        entries = self.loader.load_service()
        result = ValidationResult(registry="service", valid=True, entry_count=len(entries))
        for entry in entries:
            errors = self._validate_entry("service", entry, REQUIRED_FIELDS["service"])
            # Services must also have healthcheck and proof_path
            errors += self._validate_entry("service", entry, SERVICE_REQUIRED_FIELDS)
            result.errors.extend(errors)
            result.valid = result.valid and len(errors) == 0
        return result

    def validate_api(self) -> ValidationResult:
        """Validate API registry entries."""
        entries = self.loader.load_api()
        result = ValidationResult(registry="api", valid=True, entry_count=len(entries))
        for entry in entries:
            errors = self._validate_entry("api", entry, REQUIRED_FIELDS["api"])
            result.errors.extend(errors)
        result.valid = len(result.errors) == 0
        return result

    def validate_mcp(self) -> ValidationResult:
        """Validate MCP server registry entries."""
        entries = self.loader.load_mcp()
        result = ValidationResult(registry="mcp", valid=True, entry_count=len(entries))
        for entry in entries:
            errors = self._validate_entry("mcp", entry, REQUIRED_FIELDS["mcp"])
            result.errors.extend(errors)
        result.valid = len(result.errors) == 0
        return result

    def validate_tool(self) -> ValidationResult:
        """Validate tool registry entries."""
        entries = self.loader.load_tool()
        result = ValidationResult(registry="tool", valid=True, entry_count=len(entries))
        for entry in entries:
            errors = self._validate_entry("tool", entry, REQUIRED_FIELDS["tool"])
            errors += self._validate_entry("tool", entry, TOOL_REQUIRED_FIELDS)
            result.errors.extend(errors)
        result.valid = len(result.errors) == 0
        return result

    def validate_model(self) -> ValidationResult:
        """Validate model registry entries."""
        entries = self.loader.load_model()
        result = ValidationResult(registry="model", valid=True, entry_count=len(entries))
        for entry in entries:
            errors = self._validate_entry("model", entry, REQUIRED_FIELDS["model"])
            errors += self._validate_entry("model", entry, MODEL_REQUIRED_FIELDS)
            result.errors.extend(errors)
        result.valid = len(result.errors) == 0
        return result

    def validate_node(self) -> ValidationResult:
        """Validate node registry entries."""
        entries = self.loader.load_node()
        result = ValidationResult(registry="node", valid=True, entry_count=len(entries))
        for entry in entries:
            errors = self._validate_entry("node", entry, REQUIRED_FIELDS["node"])
            result.errors.extend(errors)
        result.valid = len(result.errors) == 0
        return result

    def validate_app(self) -> ValidationResult:
        """Validate app registry entries."""
        entries = self.loader.load_app()
        result = ValidationResult(registry="app", valid=True, entry_count=len(entries))
        for entry in entries:
            errors = self._validate_entry("app", entry, REQUIRED_FIELDS["app"])
            result.errors.extend(errors)
        result.valid = len(result.errors) == 0
        return result

    def validate_workflow(self) -> ValidationResult:
        """Validate workflow registry entries."""
        entries = self.loader.load_workflow()
        result = ValidationResult(registry="workflow", valid=True, entry_count=len(entries))
        for entry in entries:
            errors = self._validate_entry("workflow", entry, REQUIRED_FIELDS["workflow"])
            result.errors.extend(errors)
        result.valid = len(result.errors) == 0
        return result

    def validate_proof(self) -> ValidationResult:
        """Validate proof path registry entries."""
        entries = self.loader.load_proof()
        result = ValidationResult(registry="proof", valid=True, entry_count=len(entries))
        for entry in entries:
            errors = self._validate_entry("proof", entry, REQUIRED_FIELDS["proof"])
            result.errors.extend(errors)
        result.valid = len(result.errors) == 0
        return result

    def validate_approval(self) -> ValidationResult:
        """Validate approval flow registry entries."""
        entries = self.loader.load_approval()
        result = ValidationResult(registry="approval", valid=True, entry_count=len(entries))
        for entry in entries:
            errors = self._validate_entry("approval", entry, REQUIRED_FIELDS["approval"])
            result.errors.extend(errors)
        result.valid = len(result.errors) == 0
        return result

    def validate_all(self) -> FullValidationResult:
        """Validate all registries and return combined result."""
        results = {
            "service": self.validate_service(),
            "api": self.validate_api(),
            "mcp": self.validate_mcp(),
            "tool": self.validate_tool(),
            "model": self.validate_model(),
            "node": self.validate_node(),
            "app": self.validate_app(),
            "workflow": self.validate_workflow(),
            "proof": self.validate_proof(),
            "approval": self.validate_approval(),
        }
        total_errors = sum(len(r.errors) for r in results.values())
        return FullValidationResult(
            valid=total_errors == 0,
            results=results,
            total_errors=total_errors,
        )


def validate_all_registries(repo_root: Path | str = ".") -> FullValidationResult:
    """Convenience: validate all registries."""
    return RegistryValidator(repo_root).validate_all()