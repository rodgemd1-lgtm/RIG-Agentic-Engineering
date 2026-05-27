"""Pydantic models for rigforge contracts and data structures."""

from __future__ import annotations

import enum
from datetime import datetime
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# ═══════════════════════════════════════════════════════════════
# Status Enums
# ═══════════════════════════════════════════════════════════════

class SystemStatus(str, enum.Enum):
    READY = "READY"
    DEGRADED = "DEGRADED"
    BLOCKED = "BLOCKED"


class CheckStatus(str, enum.Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"
    SKIP = "skip"


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


# ═══════════════════════════════════════════════════════════════
# Doctor Models
# ═══════════════════════════════════════════════════════════════

class DoctorCheck(BaseModel):
    name: str
    status: CheckStatus
    detail: str = ""
    fix: str = ""


class DoctorResult(BaseModel):
    status: SystemStatus
    checks: list[DoctorCheck] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    next_safe_action: str = ""
    timestamp: datetime = Field(default_factory=datetime.utcnow)

    def to_yaml(self) -> str:
        """Render as YAML-like output."""
        lines = [f"status: {self.status.value}", "checks:"]
        for c in self.checks:
            lines.append(f"  {c.name}: {c.status.value}")
        lines.append(f"blockers: [{', '.join(self.blockers) if self.blockers else ''}]")
        lines.append(f"next_safe_action: {self.next_safe_action}")
        return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
# RunEnvelope — Every build mission is wrapped in one
# ═══════════════════════════════════════════════════════════════

class RunEnvelope(BaseModel):
    run_id: str = Field(default_factory=lambda: f"run_{uuid4().hex[:12]}")
    studio: str
    idea: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "created"
    harness: str = "archon"
    generator: str = "pycode"
    evaluator: str = "kimi"
    verifier: str = "codex"
    metadata: dict[str, Any] = Field(default_factory=dict)


# ═══════════════════════════════════════════════════════════════
# DoneContract — Negotiated definition of done
# ═══════════════════════════════════════════════════════════════

class DoneContract(BaseModel):
    run_id: str
    studio: str
    definition_of_done: str
    acceptance_criteria: list[str] = Field(default_factory=list)
    non_goals: list[str] = Field(default_factory=list)
    risk_level: RiskLevel = RiskLevel.MEDIUM
    rollback_plan: str = ""
    approved: bool = False
    approved_by: str = ""
    approved_at: Optional[datetime] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════
# ProofPacket — Evidence that something happened correctly
# ═══════════════════════════════════════════════════════════════

class ProofPacket(BaseModel):
    packet_id: str = Field(default_factory=lambda: f"pp_{uuid4().hex[:12]}")
    run_id: str = ""
    phase: str
    command: str
    status: str  # pass | fail
    evidence: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════
# Retrofit Models
# ═══════════════════════════════════════════════════════════════

class RetrofitStep(BaseModel):
    step_number: int
    name: str
    status: str = "pending"  # pending | done | skipped | failed
    detail: str = ""


class RetrofitReport(BaseModel):
    studio: str
    dry_run: bool
    steps: list[RetrofitStep] = Field(default_factory=list)
    blockers: list[str] = Field(default_factory=list)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════
# Incident / Learn Models
# ═══════════════════════════════════════════════════════════════

class Incident(BaseModel):
    incident_id: str
    title: str
    description: str
    failing_input: str = ""
    expected_behavior: str = ""
    actual_behavior: str = ""
    risk_level: RiskLevel = RiskLevel.MEDIUM
    created_at: datetime = Field(default_factory=datetime.utcnow)


class RegressionTest(BaseModel):
    test_id: str = Field(default_factory=lambda: f"reg_{uuid4().hex[:8]}")
    incident_id: str
    name: str
    failing_input: str
    expected_output: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


# ═══════════════════════════════════════════════════════════════
# Skill Promotion Models
# ═══════════════════════════════════════════════════════════════

class SkillPromotion(BaseModel):
    pattern_id: str
    name: str
    description: str
    occurrences: int = 0
    status: str = "proposed"  # proposed | scripted | tested | packaged | active
    script_path: str = ""
    test_path: str = ""
    skill_md_path: str = ""
    created_at: datetime = Field(default_factory=datetime.utcnow)
