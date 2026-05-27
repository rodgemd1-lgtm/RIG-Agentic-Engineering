"""Archon Bridge: Archon calls DeerFlow only at approved long-horizon nodes.

This module defines the YAML contract and validation logic for Archon workflow
nodes that delegate to DeerFlow. Archon retains full workflow ordering authority.
DeerFlow only supervises the work within the node's scope.

Forbidden:
    [ ] DeerFlow choosing next Archon node
    [ ] DeerFlow skipping Archon node
    [ ] DeerFlow editing workflow YAML
    [ ] DeerFlow marking run completed without verifier
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Optional

import yaml

logger = logging.getLogger(__name__)

# Allowed node types that can invoke DeerFlow
ALLOWED_NODE_TYPES = {"deerflow", "deerflow_resume"}

# Input files that can be passed to DeerFlow
ALLOWED_INPUT_FILES = {"spec.md", "plan.md", "DoneContract.yaml", "tasks.md", "intent.md"}


class DeerFlowNodeConfig:
    """Validated configuration for an Archon → DeerFlow bridge node."""

    def __init__(
        self,
        node_id: str,
        run_id: str,
        input_files: list[str],
        max_runtime_minutes: int = 240,
        max_subagents: int = 6,
        proof_required: bool = True,
        mission_id: str = "",
        model_name: str = "",
        subagent_enabled: bool = True,
    ) -> None:
        self.node_id = node_id
        self.run_id = run_id
        self.input_files = input_files
        self.max_runtime_minutes = max_runtime_minutes
        self.max_subagents = max_subagents
        self.proof_required = proof_required
        self.mission_id = mission_id
        self.model_name = model_name
        self.subagent_enabled = subagent_enabled

    def validate(self) -> list[str]:
        """
        Validate this node configuration.

        Returns:
            List of error messages (empty = valid)
        """
        errors = []

        if not self.run_id:
            errors.append("run_id is required for DeerFlow nodes")

        for f in self.input_files:
            if f not in ALLOWED_INPUT_FILES:
                errors.append(
                    f"Input file '{f}' not in allowed list: {sorted(ALLOWED_INPUT_FILES)}"
                )

        if self.max_runtime_minutes > 240:
            errors.append(
                f"max_runtime_minutes ({self.max_runtime_minutes}) exceeds limit (240)"
            )

        if self.max_subagents > 6:
            errors.append(
                f"max_subagents ({self.max_subagents}) exceeds limit (6)"
            )

        if self.proof_required and not self.run_id:
            errors.append("Proof required but no run_id specified")

        return errors

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for Archon workflow YAML."""
        result: dict[str, Any] = {
            "id": self.node_id,
            "type": "deerflow",
            "allowed": True,
            "run_id": self.run_id,
            "input_files": self.input_files,
            "max_runtime_minutes": self.max_runtime_minutes,
            "max_subagents": self.max_subagents,
            "proof_required": self.proof_required,
        }
        if self.mission_id:
            result["mission_id"] = self.mission_id
        if self.model_name:
            result["model_name"] = self.model_name
        return result

    @classmethod
    def from_yaml_node(cls, node: dict[str, Any]) -> "DeerFlowNodeConfig":
        """Parse a DeerFlow node from Archon workflow YAML."""
        return cls(
            node_id=node["id"],
            run_id=node.get("run_id", ""),
            input_files=node.get("input_files", []),
            max_runtime_minutes=node.get("max_runtime_minutes", 240),
            max_subagents=node.get("max_subagents", 6),
            proof_required=node.get("proof_required", True),
            mission_id=node.get("mission_id", ""),
            model_name=node.get("model_name", ""),
            subagent_enabled=node.get("subagent_enabled", True),
        )


def validate_archon_workflow(workflow_path: Path) -> list[str]:
    """
    Validate an Archon workflow YAML for safe DeerFlow bridge nodes.

    Checks:
    - All deerflow-type nodes have required fields
    - Input files are from the allowed list
    - Runtime/subagent limits are within bounds
    - No node attempts to modify workflow structure

    Returns:
        List of validation errors (empty = workflow is safe)
    """
    errors: list[str] = []

    if not workflow_path.exists():
        return [f"Workflow file not found: {workflow_path}"]

    with open(workflow_path) as f:
        workflow = yaml.safe_load(f)

    if not workflow:
        return ["Empty or invalid YAML"]

    nodes = workflow.get("nodes", workflow if isinstance(workflow, list) else [])

    for node in nodes:
        node_type = node.get("type", "")
        if node_type in ALLOWED_NODE_TYPES:
            config = DeerFlowNodeConfig.from_yaml_node(node)
            node_errors = config.validate()
            for err in node_errors:
                errors.append(f"Node '{node.get('id', '?')}': {err}")

            # Boundary check: nodes cannot modify workflow structure
            if node.get("modify_workflow", False):
                errors.append(
                    f"Node '{node.get('id', '?')}': DeerFlow nodes cannot modify workflows"
                )

            if node.get("skip_validation", False):
                errors.append(
                    f"Node '{node.get('id', '?')}': DeerFlow nodes cannot skip validation"
                )

    logger.info(
        f"Archon workflow validation: {len(errors)} errors in {workflow_path}"
    )
    return errors


def generate_sample_node() -> dict[str, Any]:
    """Generate a sample DeerFlow bridge node for Archon workflow YAML."""
    return {
        "id": "execute_long_horizon_mission",
        "type": "deerflow",
        "allowed": True,
        "run_id": "${run_id}",
        "mission_id": "${mission_id}",
        "input_files": [
            "spec.md",
            "plan.md",
            "DoneContract.yaml",
        ],
        "max_runtime_minutes": 240,
        "max_subagents": 6,
        "proof_required": True,
    }
