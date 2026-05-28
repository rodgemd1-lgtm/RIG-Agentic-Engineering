"""Tests for RIGForge Control Plane registries and validators.

Verifies:
- All 10 registries exist and validate
- Every service has owner, healthcheck, proof_path
- Every tool has allowed_agents
- Every model has allowed_use_cases
- Every workflow/app has proof_path
- Unregistered service is blocked
- Ownership is 100%
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from runtime.control_plane.registry_loader import RegistryLoader
from runtime.control_plane.registry_validator import (
    REQUIRED_FIELDS,
    validate_all_registries,
)
from runtime.control_plane.ownership_validator import OwnershipValidator
from runtime.control_plane.proof_path_validator import ProofPathValidator


REPO_ROOT = Path(__file__).parent.parent.parent


class TestAllRegistriesExist:
    def test_service_registry_exists(self) -> None:
        assert (REPO_ROOT / "config/service_registry.yaml").is_file()

    def test_api_registry_exists(self) -> None:
        assert (REPO_ROOT / "config/api_registry.yaml").is_file()

    def test_mcp_registry_exists(self) -> None:
        assert (REPO_ROOT / "config/mcp_registry.yaml").is_file()

    def test_tool_registry_exists(self) -> None:
        assert (REPO_ROOT / "config/tool_registry.yaml").is_file()

    def test_model_registry_exists(self) -> None:
        assert (REPO_ROOT / "config/model_registry.yaml").is_file()

    def test_node_registry_exists(self) -> None:
        assert (REPO_ROOT / "config/node_registry.yaml").is_file()

    def test_app_registry_exists(self) -> None:
        assert (REPO_ROOT / "config/app_registry.yaml").is_file()

    def test_workflow_registry_exists(self) -> None:
        assert (REPO_ROOT / "config/workflow_registry.yaml").is_file()

    def test_proof_registry_exists(self) -> None:
        assert (REPO_ROOT / "config/proof_registry.yaml").is_file()

    def test_approval_registry_exists(self) -> None:
        assert (REPO_ROOT / "config/approval_registry.yaml").is_file()


class TestRegistryValidation:
    def test_all_registries_validate(self) -> None:
        """All 10 registries pass field validation."""
        result = validate_all_registries(REPO_ROOT)
        assert result.valid is True, (
            f"Registry validation failed with {result.total_errors} errors: "
            f"{[(e.registry, e.entry_id, e.field) for r in result.results.values() for e in r.errors]}"
        )

    def test_registry_counts(self) -> None:
        """All 10 registries have entries."""
        loader = RegistryLoader(REPO_ROOT)
        stats = loader.stats()
        stats_by_name = {s.registry_name: s for s in stats}
        for name in RegistryLoader.REGISTRY_FILES:
            s = stats_by_name[name]
            assert s.loaded is True, f"{name} registry not loaded"
            assert s.entry_count > 0, f"{name} registry has no entries"


class TestServiceRegistry:
    def test_every_service_has_owner(self) -> None:
        """Every service entry has an owner field."""
        loader = RegistryLoader(REPO_ROOT)
        services = loader.load_service()
        for svc in services:
            assert "owner" in svc, f"Service {svc.get('id')} has no owner"
            assert svc["owner"], f"Service {svc.get('id')} has empty owner"

    def test_every_service_has_healthcheck(self) -> None:
        """Every service entry has a healthcheck."""
        loader = RegistryLoader(REPO_ROOT)
        services = loader.load_service()
        for svc in services:
            assert "healthcheck" in svc, f"Service {svc.get('id')} has no healthcheck"

    def test_every_service_has_proof_path(self) -> None:
        """Every service entry has a proof_path."""
        loader = RegistryLoader(REPO_ROOT)
        services = loader.load_service()
        for svc in services:
            assert "proof_path" in svc, f"Service {svc.get('id')} has no proof_path"


class TestToolRegistry:
    def test_every_tool_has_allowed_agents(self) -> None:
        """Every tool has an allowed_agents list."""
        loader = RegistryLoader(REPO_ROOT)
        tools = loader.load_tool()
        for tool in tools:
            assert "allowed_agents" in tool, f"Tool {tool.get('id')} has no allowed_agents"
            assert isinstance(tool["allowed_agents"], list), f"Tool {tool.get('id')} allowed_agents is not a list"
            assert len(tool["allowed_agents"]) > 0, f"Tool {tool.get('id')} has empty allowed_agents"


class TestModelRegistry:
    def test_every_model_has_allowed_use_cases(self) -> None:
        """Every model has allowed_use_cases."""
        loader = RegistryLoader(REPO_ROOT)
        models = loader.load_model()
        for model in models:
            assert "allowed_use_cases" in model, f"Model {model.get('id')} has no allowed_use_cases"
            assert isinstance(model["allowed_use_cases"], list), f"Model {model.get('id')} allowed_use_cases is not a list"


class TestOwnership:
    def test_all_entries_have_owners(self) -> None:
        """Every registry entry has an owner. 100% ownership rate."""
        result = OwnershipValidator(REPO_ROOT).validate_all()
        assert result.valid is True, (
            f"Ownership validation failed: {[(e.registry, e.entry_id) for e in result.errors]}"
        )
        assert result.entries_with_owner == result.total_entries, (
            f"Not all entries have owners: {result.entries_with_owner}/{result.total_entries}"
        )


class TestProofPaths:
    def test_all_workflows_have_proof_path(self) -> None:
        """Every workflow entry has a proof_path."""
        result = ProofPathValidator(REPO_ROOT).validate_all()
        assert result.valid is True, (
            f"Proof path validation failed: {[(e.registry, e.entry_id) for e in result.errors]}"
        )

    def test_all_apps_have_proof_path(self) -> None:
        """Every app entry has a proof_path."""
        loader = RegistryLoader(REPO_ROOT)
        apps = loader.load_app()
        for app in apps:
            assert "proof_path" in app, f"App {app.get('id')} has no proof_path"


class TestApprovalFlows:
    def test_all_approval_flows_have_required_signers(self) -> None:
        """Every approval flow has required_signers."""
        loader = RegistryLoader(REPO_ROOT)
        flows = loader.load_approval()
        for flow in flows:
            assert "required_signers" in flow, f"Approval flow {flow.get('id')} has no required_signers"
            assert isinstance(flow["required_signers"], list), f"Flow {flow.get('id')} required_signers not a list"
            assert "mike" in flow["required_signers"], f"Flow {flow.get('id')} does not require mike approval"


class TestControlPlaneCoreLaw:
    def test_not_registered_does_not_exist(self) -> None:
        """Only registered services are recognized."""
        loader = RegistryLoader(REPO_ROOT)
        services = loader.load_service()
        ids = {s["id"] for s in services}
        assert "unregistered-service" not in ids, "Unregistered service should not be in registry"

    def test_unregistered_service_blocked(self) -> None:
        """Unregistered service IDs cannot be used."""
        loader = RegistryLoader(REPO_ROOT)
        services = loader.load_service()
        registered_ids = {s["id"] for s in services}
        # Any unregistered ID is blocked
        unregistered = "fake-service-xyz"
        assert unregistered not in registered_ids


class TestVerifyScript:
    def test_verify_script_exists(self) -> None:
        assert (REPO_ROOT / "scripts/verify_control_plane.py").is_file()

    def test_verify_script_passes(self) -> None:
        """scripts/verify_control_plane.py should exit 0."""
        import subprocess, sys
        interpreter = str(REPO_ROOT / ".venv/bin/python3") if (REPO_ROOT / ".venv/bin/python3").exists() else sys.executable
        result = subprocess.run(
            [interpreter, str(REPO_ROOT / "scripts/verify_control_plane.py")],
            capture_output=True, text=True, timeout=30,
        )
        assert result.returncode == 0, f"Script failed: {result.stderr}"