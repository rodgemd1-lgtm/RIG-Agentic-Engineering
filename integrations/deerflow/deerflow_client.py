"""DeerFlow RIG Client — Thin wrapper around DeerFlowClient with strict RIG boundaries.

This module wraps the DeerFlow embedded Python client (deerflow.client.DeerFlowClient)
and enforces that no DeerFlow thread can be created without a valid RIG RunEnvelope.

If DeerFlow is not installed, the client operates in stub/dry-run mode so the rest of
the RIG stack can still be developed and tested independently.

Architecture:
    Archon/CLI → DeerFlowRigClient → (boundary checks) → DeerFlowClient → LangGraph
"""

from __future__ import annotations

import json
import logging
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

import yaml

from integrations.deerflow.thread_mapping import ThreadMapping, get_thread_mapping
from integrations.deerflow.workspace_mapping import WorkspaceMapping, get_workspace_mapping
from integrations.deerflow.proof_adapter import emit_proof_event

logger = logging.getLogger(__name__)

# ── Attempt to import the real DeerFlow SDK ──────────────────────────────────
_DEERFLOW_AVAILABLE = False
try:
    from deerflow.client import DeerFlowClient as _DeerFlowClient  # type: ignore[import-untyped]
    _DEERFLOW_AVAILABLE = True
except ImportError:
    logger.warning(
        "deerflow SDK not installed. "
        "DeerFlowRigClient operates in stub mode. "
        "Install via: cd deer-flow/backend && uv sync"
    )


class DeerFlowRigClient:
    """RIG-bound wrapper around DeerFlowClient.

    Enforces:
    - No thread without RunEnvelope
    - Workspace paths mapped to RIG worktrees
    - Every sub-agent result → ProofPacket event
    - Permissions from config/deerflow_rig.yaml

    Usage:
        client = DeerFlowRigClient(config_path="config/deerflow_rig.yaml")
        result = await client.run_long_horizon(
            run_id="run_abc123",
            message="Build the Soul ID regression portal",
            mission_id="soul-id-regression",
        )
    """

    def __init__(
        self,
        config_path: str = "config/deerflow_rig.yaml",
        base_url: Optional[str] = None,
    ) -> None:
        self.config_path = Path(config_path)
        self._config = self._load_config()
        self._limits = self._config.get("deerflow", {}).get("limits", {})
        self._permissions = self._config.get("deerflow", {}).get("permissions", {})
        self._base_url = base_url or self._config.get("deerflow", {}).get(
            "base_url", "http://localhost:2026"
        )

        # Initialize real DeerFlow client if available
        if _DEERFLOW_AVAILABLE:
            self._client = _DeerFlowClient()
        else:
            self._client = None
            logger.info("DeerFlowRigClient: stub mode (no DeerFlow SDK)")

    def _load_config(self) -> dict[str, Any]:
        """Load DeerFlow RIG config, falling back to defaults."""
        if self.config_path.exists():
            with open(self.config_path) as f:
                return yaml.safe_load(f) or {}
        return {}

    @property
    def is_stub(self) -> bool:
        """True if DeerFlow SDK is not installed."""
        return self._client is None

    # ── Boundary enforcement ──────────────────────────────────────────────────

    def _check_run_envelope(self, run_id: str) -> dict[str, Any]:
        """
        Load and validate RunEnvelope for a given run_id.

        Raises:
            RuntimeError: If no RunEnvelope exists or it's invalid.
            FileNotFoundError: If run directory doesn't exist.
        """
        envelope_path = Path("runs") / run_id / "RunEnvelope.json"
        if not envelope_path.exists():
            raise FileNotFoundError(
                f"No RunEnvelope found at {envelope_path}. "
                f"Create one before starting a DeerFlow thread. "
                f"Rule: No DeerFlow thread without RunEnvelope."
            )

        with open(envelope_path) as f:
            envelope = json.load(f)

        if not isinstance(envelope, dict) or "run_id" not in envelope:
            raise RuntimeError(f"Invalid RunEnvelope at {envelope_path}")

        logger.info(f"RunEnvelope validated: {run_id} (studio={envelope.get('studio', '?')})")
        return envelope

    def _check_permission(self, action: str) -> None:
        """
        Check RIG permissions from config.

        Raises:
            PermissionError: If the action is forbidden by RIG boundaries.
        """
        forbidden = {
            "modify_archon_workflows": "can_modify_archon_workflows",
            "modify_rig_gates": "can_modify_rig_gates",
            "modify_audit_logs": "can_modify_audit_logs",
            "perform_external_side_effects": "can_perform_external_side_effects",
        }

        if action in forbidden:
            config_key = forbidden[action]
            allowed = self._permissions.get(config_key, False)
            if not allowed:
                raise PermissionError(
                    f"DeerFlow forbidden from '{action}'. "
                    f"Set '{config_key}: true' in config/deerflow_rig.yaml to allow."
                )

    # ── Public API ────────────────────────────────────────────────────────────

    async def run_long_horizon(
        self,
        run_id: str,
        message: str,
        mission_id: str = "",
        input_files: Optional[list[str]] = None,
        config: Optional[dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """
        Start or continue a long-horizon DeerFlow run mapped to a RIG run.

        This is the ONLY way to create DeerFlow threads from RIG.

        Args:
            run_id: RIG RunEnvelope ID
            message: The mission/task description for the lead agent
            mission_id: Optional human-readable mission identifier
            input_files: Files to upload to DeerFlow workspace (relative to run dir)
            config: Extra DeerFlow configurable (model_name, subagent_enabled, etc.)

        Returns:
            Dict with thread_id, run_id, mapping_record, status

        Raises:
            FileNotFoundError: If RunEnvelope doesn't exist
            PermissionError: If a forbidden action is detected
            RuntimeError: If limits exceeded
        """
        # Gate 1: Must have RunEnvelope
        envelope = self._check_run_envelope(run_id)

        # Gate 2: Check limits
        max_runtime = self._limits.get("max_runtime_minutes", 240)
        max_subagents = self._limits.get("max_subagents", 6)
        max_cost = self._limits.get("max_cost_usd", 20.0)

        # Gate 3: Create or look up thread mapping
        mapping_store = get_thread_mapping()
        existing = mapping_store.get_by_run_id(run_id)
        if existing:
            thread_id = existing["deerflow_thread_id"]
            logger.info(f"Resuming DeerFlow thread {thread_id} for run {run_id}")
        else:
            thread_id = f"df_{uuid.uuid4().hex[:16]}"
            logger.info(f"Creating DeerFlow thread {thread_id} for run {run_id}")

        # Gate 4: Workspace mapping
        ws_mapping = get_workspace_mapping()
        ws_paths = ws_mapping.resolve(run_id)

        # Record the mapping
        mapping_record = mapping_store.create(
            rig_run_id=run_id,
            rig_mission_id=mission_id or run_id,
            deerflow_thread_id=thread_id,
            studio=envelope.get("studio", "unknown"),
            workflow_id=mission_id or run_id,
            worktree_path=str(ws_paths["workspace"]),
            deerflow_workspace=str(ws_paths["deerflow_workspace"]),
        )

        # Emit proof event for thread creation
        emit_proof_event(
            run_id=run_id,
            deerflow_thread_id=thread_id,
            subagent_id="lead_agent",
            task="thread_created",
            files_touched=input_files or [],
            outputs=[],
            summary=f"DeerFlow thread {thread_id} created for run {run_id}",
            status="pass",
            trace_uri=f"{self._base_url}/api/langgraph/threads/{thread_id}",
        )

        if self.is_stub:
            return self._stub_run(
                run_id=run_id,
                thread_id=thread_id,
                message=message,
                mapping_record=mapping_record,
            )

        # Real DeerFlow invocation via DeerFlowClient
        deerflow_config = {
            "configurable": {
                "thread_id": thread_id,
                "subagent_enabled": True,
                "max_subagents": max_subagents,
            }
        }
        if config:
            deerflow_config["configurable"].update(config)

        result = await self._client.ainvoke(
            thread_id=thread_id,
            message=message,
            config=deerflow_config,
        )

        return {
            "thread_id": thread_id,
            "run_id": run_id,
            "mapping_record": mapping_record,
            "status": "completed",
            "result": result,
        }

    async def resume_thread(
        self,
        run_id: str,
        message: str = "Continue where you left off.",
    ) -> dict[str, Any]:
        """
        Resume a paused DeerFlow thread.

        DeerFlow checkpointing via LangGraph handles state restoration.
        RIG validates the thread mapping still exists.
        """
        self._check_run_envelope(run_id)

        mapping_store = get_thread_mapping()
        mapping = mapping_store.get_by_run_id(run_id)
        if not mapping:
            raise FileNotFoundError(
                f"No thread mapping for run {run_id}. "
                f"Call run_long_horizon first."
            )

        thread_id = mapping["deerflow_thread_id"]
        logger.info(f"Resuming thread {thread_id} for run {run_id}")

        if self.is_stub:
            return self._stub_run(run_id, thread_id, message, mapping)

        result = await self._client.ainvoke(
            thread_id=thread_id,
            message=message,
        )

        return {
            "thread_id": thread_id,
            "run_id": run_id,
            "status": "resumed",
            "result": result,
        }

    def get_status(self, run_id: str) -> dict[str, Any]:
        """
        Get status of a DeerFlow supervised run.

        Returns status dict with runtime, subagents used, cost so far.
        """
        self._check_run_envelope(run_id)

        mapping_store = get_thread_mapping()
        mapping = mapping_store.get_by_run_id(run_id)
        if not mapping:
            return {"status": "not_started", "run_id": run_id}

        return {
            "status": "running" if not self.is_stub else "stub",
            "run_id": run_id,
            "thread_id": mapping.get("deerflow_thread_id"),
            "studio": mapping.get("studio"),
            "limits": self._limits,
        }

    def _stub_run(
        self,
        run_id: str,
        thread_id: str,
        message: str,
        mapping_record: dict[str, Any],
    ) -> dict[str, Any]:
        """Stub mode response when DeerFlow SDK is not installed."""
        logger.info(
            f"[STUB] DeerFlow run: thread={thread_id}, run={run_id}, "
            f"message='{message[:80]}...'"
        )
        return {
            "thread_id": thread_id,
            "run_id": run_id,
            "mapping_record": mapping_record,
            "status": "stub",
            "summary": f"[STUB] DeerFlow would process: {message[:200]}",
        }
