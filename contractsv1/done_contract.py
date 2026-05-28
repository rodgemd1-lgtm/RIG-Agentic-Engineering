"""DoneContract — binding contract between Generator, Evaluator, and Verifier.

Core law: No DoneContract, no code.
No acceptance criteria, no mission.
No required artifacts, no verifier package.
No verifier package, no PASS.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ContractStatus(str, Enum):
    DRAFT = "draft"
    NEGOTIATING = "negotiating"
    SEALED = "sealed"
    BROKEN = "broken"
    FULFILLED = "fulfilled"


class DoneContract(BaseModel):
    """Binding contract for a GEV build mission.

    Generator cannot build before this is SEALED.
    Evaluator must challenge all weak spots before approving.
    Verifier can only receive the VerifierPackage — never chat history.
    """
    run_id: str
    studio: str
    idea: str = ""

    # Must-haves
    required_artifacts: list[dict] = Field(default_factory=list)
    # Must-pass
    acceptance_criteria: list[dict] = Field(default_factory=list)
    # Must-never
    forbidden_actions: list[dict] = Field(default_factory=list)

    # Meta
    generator_signature: str = ""
    evaluator_signature: str = ""
    approved: bool = False
    approved_by: str = ""
    approved_at: datetime | None = None
    status: ContractStatus = ContractStatus.DRAFT
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def is_sealed(self) -> bool:
        return self.status == ContractStatus.SEALED

    def is_blocked(self) -> bool:
        return self.status in (ContractStatus.BROKEN, ContractStatus.DRAFT)

    def can_build(self) -> bool:
        """Generator may build only after contract is sealed."""
        return self.is_sealed() and not self.is_blocked()

    def summary(self) -> str:
        artifacts = [a.get("name") for a in self.required_artifacts]
        criteria = [c.get("description") for c in self.acceptance_criteria]
        forbidden = [f.get("action") for f in self.forbidden_actions]
        return (
            f"DoneContract({self.run_id})[{self.status.value}]: "
            f"{len(artifacts)} artifacts, {len(criteria)} criteria, "
            f"{len(forbidden)} forbidden"
        )