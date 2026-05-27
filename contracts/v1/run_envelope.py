"""RunEnvelope Pydantic model for RIG Runtime Kernel.

Every build mission is wrapped in a RunEnvelope.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


class RunEnvelope(BaseModel):
    """Mission context and identity for every RIG build.
    
    Core law: No RunEnvelope, no run.
    """
    run_id: str = Field(default_factory=lambda: f"run_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{hex(hash(datetime.now()))[2:8]}")
    studio: str  # "app", "agent", "api", "web"
    idea: str = ""  # One-line description
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "draft"  # "draft" | "building" | "needs_approval" | "completed" | "failed"
    harness: str = "archon"  # "local" | "deerflow" | "archon"
    harness_args: dict[str, Any] = Field(default_factory=dict)
    tool_registry_path: str = ""  # Path to tool contract registry
    generator: str = "pycode"
    evaluator: str = "kimi"
    verifier: str = "codex"
    metadata: dict[str, Any] = Field(default_factory=dict)


class Mission(BaseModel):
    """A RIG mission definition."""
    mission_id: str
    run_id: str
    description: str
    phase: str = "draft"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class WorkflowState(BaseModel):
    """Current workflow state for a run."""
    run_id: str
    current_phase: str = "draft"
    phases_completed: list[str] = Field(default_factory=list)
    current_gate: str = "G00"
