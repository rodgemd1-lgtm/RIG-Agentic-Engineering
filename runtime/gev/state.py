"""GEV state machine and audit trail.

Workflow:
    SPEC → CONTRACT_NEGOTIATION → GENERATOR_BUILD → EVALUATOR_CRITIQUE → GENERATOR_REPAIR → VERIFIER_CHECK → PROOF_SEALED → APPROVAL
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class GEVPhase(str, Enum):
    SPEC = "spec"
    CONTRACT_NEGOTIATION = "contract_negotiation"
    GENERATOR_BUILD = "generator_build"
    EVALUATOR_CRITIQUE = "evaluator_critique"
    GENERATOR_REPAIR = "generator_repair"
    VERIFIER_CHECK = "verifier_check"
    PROOF_SEALED = "proof_sealed"
    APPROVAL = "approval"


# Valid phase transitions
VALID_TRANSITIONS: dict[GEVPhase, set[GEVPhase]] = {
    GEVPhase.SPEC: {GEVPhase.CONTRACT_NEGOTIATION},
    GEVPhase.CONTRACT_NEGOTIATION: {GEVPhase.GENERATOR_BUILD},
    GEVPhase.GENERATOR_BUILD: {GEVPhase.EVALUATOR_CRITIQUE},
    GEVPhase.EVALUATOR_CRITIQUE: {GEVPhase.GENERATOR_REPAIR, GEVPhase.VERIFIER_CHECK},
    GEVPhase.GENERATOR_REPAIR: {GEVPhase.EVALUATOR_CRITIQUE},
    GEVPhase.VERIFIER_CHECK: {GEVPhase.PROOF_SEALED, GEVPhase.GENERATOR_REPAIR},
    GEVPhase.PROOF_SEALED: {GEVPhase.APPROVAL},
    GEVPhase.APPROVAL: set(),
}


@dataclass
class GEVAuditEntry:
    timestamp: datetime
    phase: GEVPhase
    actor: str  # generator | evaluator | verifier | hermes | mike
    action: str
    detail: str = ""


@dataclass
class GEVState:
    """GEV loop state machine with append-only audit trail."""
    run_id: str
    studio: str
    current_phase: GEVPhase = GEVPhase.SPEC
    verdict: str = ""  # PASS | FAIL | BLOCKED
    audit: list[GEVAuditEntry] = field(default_factory=list)
    critiques: list[str] = field(default_factory=list)  # Evaluator challenges
    blocked_artifacts: list[str] = field(default_factory=list)  # Missing items

    def can_transition(self, new_phase: GEVPhase) -> bool:
        allowed = VALID_TRANSITIONS.get(self.current_phase, set())
        return new_phase in allowed

    def transition(self, new_phase: GEVPhase, actor: str, action: str, detail: str = "") -> None:
        if not self.can_transition(new_phase):
            raise RuntimeError(
                f"Forbidden GEV transition: {self.current_phase.value} → {new_phase.value}. "
                f"Allowed: {[p.value for p in VALID_TRANSITIONS.get(self.current_phase, set())]}"
            )
        self.current_phase = new_phase
        self.audit.append(GEVAuditEntry(
            timestamp=datetime.now(timezone.utc),
            phase=new_phase,
            actor=actor,
            action=action,
            detail=detail,
        ))

    def is_terminal(self) -> bool:
        return self.current_phase == GEVPhase.APPROVAL

    def add_critique(self, critique: str) -> None:
        self.critiques.append(critique)

    def block_artifact(self, name: str) -> None:
        self.blocked_artifacts.append(name)

    def set_verdict(self, verdict: str) -> None:
        self.verdict = verdict