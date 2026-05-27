"""Tests for Archon-DeerFlow bridge boundaries.

Verifies that:
- DeerFlow cannot modify Archon workflow YAML
- DeerFlow cannot bypass Archon flow control
- Archon validates DeerFlow nodes properly
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from integrations.deerflow.archon_bridge import (
    DeerFlowNodeConfig,
    validate_archon_workflow,
    ALLOWED_INPUT_FILES,
)


class TestDeerFlowNodeConfig:
    def test_valid_node(self) -> None:
        """A well-formed DeerFlow node config validates cleanly."""
        config = DeerFlowNodeConfig(
            node_id="execute_long_horizon_mission",
            run_id="run_abc123",
            input_files=["spec.md", "plan.md", "DoneContract.yaml"],
            max_runtime_minutes=240,
            max_subagents=6,
        )
        errors = config.validate()
        assert errors == []

    def test_empty_run_id_raises(self) -> None:
        """Empty run_id is rejected."""
        config = DeerFlowNodeConfig(
            node_id="test_node",
            run_id="",
            input_files=["spec.md"],
        )
        errors = config.validate()
        assert any("run_id" in e for e in errors)

    def test_disallowed_input_file_raises(self) -> None:
        """Input file not in allowed list is rejected."""
        config = DeerFlowNodeConfig(
            node_id="test_node",
            run_id="run_123",
            input_files=["/etc/passwd"],
        )
        errors = config.validate()
        assert any("not in allowed list" in e for e in errors)

    def test_excessive_runtime_raises(self) -> None:
        """Runtime > 240 minutes is rejected."""
        config = DeerFlowNodeConfig(
            node_id="test_node",
            run_id="run_123",
            input_files=["spec.md"],
            max_runtime_minutes=300,
        )
        errors = config.validate()
        assert any("max_runtime_minutes" in e for e in errors)

    def test_excessive_subagents_raises(self) -> None:
        """Subagents > 6 is rejected."""
        config = DeerFlowNodeConfig(
            node_id="test_node",
            run_id="run_123",
            input_files=["spec.md"],
            max_subagents=8,
        )
        errors = config.validate()
        assert any("max_subagents" in e for e in errors)

    def test_serialization(self) -> None:
        """Node config serializes to dict correctly."""
        config = DeerFlowNodeConfig(
            node_id="mission_node",
            run_id="run_abc",
            input_files=["spec.md", "plan.md"],
            mission_id="soul-id-regression",
        )
        d = config.to_dict()
        assert d["id"] == "mission_node"
        assert d["type"] == "deerflow"
        assert d["allowed"] is True
        assert "spec.md" in d["input_files"]


class TestArchonWorkflowValidation:
    def test_valid_workflow(self, tmp_path: Path) -> None:
        """A valid Archon workflow with DeerFlow nodes passes validation."""
        workflow = {
            "nodes": [
                {
                    "id": "execute_long_horizon_mission",
                    "type": "deerflow",
                    "allowed": True,
                    "run_id": "${run_id}",
                    "input_files": ["spec.md", "plan.md", "DoneContract.yaml"],
                    "max_runtime_minutes": 240,
                    "max_subagents": 6,
                    "proof_required": True,
                }
            ]
        }
        wf_path = tmp_path / "workflow.yaml"
        wf_path.write_text(yaml.dump(workflow))

        errors = validate_archon_workflow(wf_path)
        assert errors == []

    def test_modify_workflow_forbidden(self, tmp_path: Path) -> None:
        """DeerFlow node that tries to modify workflow structure is caught."""
        workflow = {
            "nodes": [
                {
                    "id": "bad_node",
                    "type": "deerflow",
                    "run_id": "run_123",
                    "modify_workflow": True,
                }
            ]
        }
        wf_path = tmp_path / "workflow.yaml"
        wf_path.write_text(yaml.dump(workflow))

        errors = validate_archon_workflow(wf_path)
        assert any("cannot modify workflows" in e for e in errors)

    def test_skip_validation_forbidden(self, tmp_path: Path) -> None:
        """DeerFlow node that tries to skip validation is caught."""
        workflow = {
            "nodes": [
                {
                    "id": "bad_node",
                    "type": "deerflow",
                    "run_id": "run_123",
                    "skip_validation": True,
                }
            ]
        }
        wf_path = tmp_path / "workflow.yaml"
        wf_path.write_text(yaml.dump(workflow))

        errors = validate_archon_workflow(wf_path)
        assert any("cannot skip validation" in e for e in errors)

    def test_missing_run_id(self, tmp_path: Path) -> None:
        """DeerFlow node without run_id is caught."""
        workflow = {
            "nodes": [
                {
                    "id": "bad_node",
                    "type": "deerflow",
                }
            ]
        }
        wf_path = tmp_path / "workflow.yaml"
        wf_path.write_text(yaml.dump(workflow))

        errors = validate_archon_workflow(wf_path)
        assert any("run_id" in e.lower() for e in errors)

    def test_nonexistent_file(self, tmp_path: Path) -> None:
        """Missing workflow file is reported."""
        errors = validate_archon_workflow(tmp_path / "nonexistent.yaml")
        assert any("not found" in e for e in errors)

    def test_empty_yaml(self, tmp_path: Path) -> None:
        """Empty YAML is reported."""
        wf_path = tmp_path / "empty.yaml"
        wf_path.write_text("")
        errors = validate_archon_workflow(wf_path)
        assert any("Empty" in e for e in errors)


class TestDeerFlowCannotBypassArchon:
    """DeerFlow cannot modify Archon workflow structure."""

    def test_deerflow_cannot_add_nodes(self, tmp_path: Path) -> None:
        """DeerFlow node with add_nodes flag is forbidden."""
        workflow = {
            "nodes": [
                {
                    "id": "infiltrator",
                    "type": "deerflow",
                    "run_id": "run_123",
                    "modify_workflow": True,
                }
            ]
        }
        wf_path = tmp_path / "bad_workflow.yaml"
        wf_path.write_text(yaml.dump(workflow))

        errors = validate_archon_workflow(wf_path)
        assert len(errors) > 0

    def test_deerflow_cannot_skip_nodes(self, tmp_path: Path) -> None:
        """skip_validation flag is caught."""
        workflow = {
            "nodes": [
                {
                    "id": "skipper",
                    "type": "deerflow",
                    "run_id": "run_123",
                    "skip_validation": True,
                }
            ]
        }
        wf_path = tmp_path / "skip_workflow.yaml"
        wf_path.write_text(yaml.dump(workflow))

        errors = validate_archon_workflow(wf_path)
        assert any("skip" in e.lower() for e in errors)

    def test_allowed_input_files_list(self) -> None:
        """Allowed input files are exactly the expected set."""
        expected = {"spec.md", "plan.md", "DoneContract.yaml", "tasks.md", "intent.md"}
        assert ALLOWED_INPUT_FILES == expected
