"""Test RIGForge environment verification.

Verifies doctor, version, and service checks work correctly.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest
import yaml


REPO_ROOT = Path(__file__).parent.parent.parent


class TestEnvironmentConfig:
    def test_environment_yaml_exists(self) -> None:
        """config/environment.yaml must exist."""
        path = REPO_ROOT / "config" / "environment.yaml"
        assert path.is_file()

    def test_environment_has_required(self) -> None:
        """environment.yaml must define required tools."""
        path = REPO_ROOT / "config" / "environment.yaml"
        config = yaml.safe_load(path.read_text())
        assert "required" in config
        assert "python" in config["required"]
        assert "git" in config["required"]
        assert "uv" in config["required"]

    def test_environment_has_optional(self) -> None:
        """environment.yaml must define optional tools."""
        path = REPO_ROOT / "config" / "environment.yaml"
        config = yaml.safe_load(path.read_text())
        assert "optional" in config

    def test_environment_has_services(self) -> None:
        """environment.yaml must define services."""
        path = REPO_ROOT / "config" / "environment.yaml"
        config = yaml.safe_load(path.read_text())
        assert "services" in config


class TestRuntimeVersions:
    def test_runtime_versions_exists(self) -> None:
        """config/runtime_versions.yaml must exist."""
        path = REPO_ROOT / "config" / "runtime_versions.yaml"
        assert path.is_file()

    def test_runtime_versions_has_python(self) -> None:
        """runtime_versions.yaml must specify Python version."""
        path = REPO_ROOT / "config" / "runtime_versions.yaml"
        config = yaml.safe_load(path.read_text())
        assert "python" in config


class TestVerifyScripts:
    def test_verify_environment_script_exists(self) -> None:
        """scripts/verify_environment.py must exist."""
        path = REPO_ROOT / "scripts" / "verify_environment.py"
        assert path.is_file()

    def test_verify_versions_script_exists(self) -> None:
        """scripts/verify_versions.py must exist."""
        path = REPO_ROOT / "scripts" / "verify_versions.py"
        assert path.is_file()

    def test_verify_services_script_exists(self) -> None:
        """scripts/verify_services.py must exist."""
        path = REPO_ROOT / "scripts" / "verify_services.py"
        assert path.is_file()

    def test_write_proof_script_exists(self) -> None:
        """scripts/write_environment_proof.py must exist."""
        path = REPO_ROOT / "scripts" / "write_environment_proof.py"
        assert path.is_file()


class TestEnvironmentProof:
    def test_environment_proofpacket_exists(self) -> None:
        """proof/environment/environment_proofpacket.json must exist after proof generation."""
        path = REPO_ROOT / "proof" / "environment" / "environment_proofpacket.json"
        # May not exist yet — skip if not generated
        if not path.exists():
            pytest.skip("ProofPacket not yet generated — run scripts/write_environment_proof.py")
        
        data = json.loads(path.read_text())
        assert data["phase"] == "phase_2_environment_bootstrap"
        assert data["status"] in ("READY", "DEGRADED", "BLOCKED")
        assert "evidence" in data
        assert "doctor_report" in data["evidence"]
        assert "version_report" in data["evidence"]

    def test_doctor_report_structure(self) -> None:
        """doctor report must have expected structure."""
        path = REPO_ROOT / "proof" / "environment" / "doctor_report.json"
        if not path.exists():
            pytest.skip("Doctor report not yet generated")
        
        data = json.loads(path.read_text())
        assert "overall_status" in data
        assert "checks" in data
        assert "python" in data["checks"]
        assert data["checks"]["python"]["status"] == "READY"

    def test_required_tools_ready(self) -> None:
        """All required tools must be READY."""
        path = REPO_ROOT / "proof" / "environment" / "doctor_report.json"
        if not path.exists():
            pytest.skip("Doctor report not yet generated")
        
        data = json.loads(path.read_text())
        config = yaml.safe_load((REPO_ROOT / "config" / "environment.yaml").read_text())
        
        for tool in config.get("required", {}):
            if tool in data["checks"]:
                assert data["checks"][tool]["status"] == "READY", f"Required tool not ready: {tool}"

    def test_no_false_pass_for_missing(self) -> None:
        """Missing tools must not falsely report PASS."""
        path = REPO_ROOT / "proof" / "environment" / "doctor_report.json"
        if not path.exists():
            pytest.skip("Doctor report not yet generated")
        
        data = json.loads(path.read_text())
        for tool, check in data["checks"].items():
            status = check["status"]
            assert status in ("READY", "NOT_INSTALLED", "NOT_CONFIGURED", "UNKNOWN")
            # Never a fake pass for missing tools
            if "not found" in check.get("detail", "").lower():
                assert status != "READY", f"{tool} falsely marked READY"
