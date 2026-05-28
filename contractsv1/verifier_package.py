"""GEV contracts: required_artifact, acceptance_criterion, forbidden_action."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RequiredArtifact(BaseModel):
    """A file or artifact that must be produced for the mission."""
    name: str
    path: str
    description: str = ""
    required: bool = True
    test_command: str = ""  # If artifact must pass a test


class AcceptanceCriterion(BaseModel):
    """A criterion the final output must satisfy."""
    id: str
    description: str
    test_command: str = ""
    manual_check: bool = False


class ForbiddenAction(BaseModel):
    """An action the generator must not take."""
    action: str
    reason: str
    consequence: str = "BLOCKED"


class VerifierPackage(BaseModel):
    """What the stateless verifier receives.

    Core law: Verifier must NOT receive:
    - Generator chat history
    - Evaluator chat history
    - Intermediate drafts
    - Self-assessments
    """
    run_id: str
    studio: str
    spec_path: str
    done_contract_path: str
    file_tree_snapshot: list[str] = Field(default_factory=list)
    test_commands: list[str] = Field(default_factory=list)
    proof_packet_paths: list[str] = Field(default_factory=list)
    hash_manifest: dict[str, str] = Field(default_factory=dict)
    # Explicitly excluded (set to empty — these must NEVER be included):
    generator_chat_history: list[str] = Field(default_factory=list)
    evaluator_chat_history: list[str] = Field(default_factory=list)
    intermediate_drafts: list[str] = Field(default_factory=list)
    self_assessments: list[str] = Field(default_factory=list)

    def is_clean(self) -> bool:
        """VerifierPackage is clean (contains only allowed artifacts)."""
        return (
            len(self.generator_chat_history) == 0
            and len(self.evaluator_chat_history) == 0
            and len(self.intermediate_drafts) == 0
        )