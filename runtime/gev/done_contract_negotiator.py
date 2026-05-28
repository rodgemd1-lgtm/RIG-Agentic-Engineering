"""DoneContract negotiator — formal contract negotiation between Generator and Evaluator."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from contractsv1.done_contract import ContractStatus, DoneContract


@dataclass
class NegotiationResult:
    """Result of a negotiation round."""
    contract: DoneContract
    challenges: list[str]
    blocked: bool
    sealed: bool


class DoneContractNegotiator:
    """Formal DoneContract negotiation.

    Rules:
    - Contract starts in DRAFT
    - Evaluator must challenge: missing artifacts, weak tests, no rollback, proof gaps
    - Generator revises based on challenges
    - Contract is SEALED only when Evaluator passes it
    - Generator cannot build before SEALED
    """

    def __init__(self, repo_root: Path | str = ".") -> None:
        self.repo_root = Path(repo_root)

    def create_draft(
        self,
        run_id: str,
        studio: str,
        idea: str,
        required_artifacts: list[dict],
        acceptance_criteria: list[dict],
        forbidden_actions: list[dict],
    ) -> DoneContract:
        """Create initial draft contract."""
        return DoneContract(
            run_id=run_id,
            studio=studio,
            idea=idea,
            required_artifacts=required_artifacts,
            acceptance_criteria=acceptance_criteria,
            forbidden_actions=forbidden_actions,
            status=ContractStatus.DRAFT,
        )

    def negotiate(
        self, contract: DoneContract, evaluator_challenges: list[str]
    ) -> NegotiationResult:
        """One round of negotiation: evaluator challenges, contract may be updated."""
        if contract.status == ContractStatus.SEALED:
            return NegotiationResult(
                contract=contract,
                challenges=[],
                blocked=False,
                sealed=True,
            )

        challenges = [c for c in evaluator_challenges if c.strip()]

        if challenges:
            # Evaluator found issues — keep in negotiation
            updated = contract.model_copy(deep=True)
            updated.status = ContractStatus.NEGOTIATING
            return NegotiationResult(
                contract=updated,
                challenges=challenges,
                blocked=True,
                sealed=False,
            )

        # No challenges — Evaluator approves, seal the contract
        sealed = contract.model_copy(deep=True)
        sealed.status = ContractStatus.SEALED
        return NegotiationResult(
            contract=sealed,
            challenges=[],
            blocked=False,
            sealed=True,
        )

    def can_build(self, contract: DoneContract) -> tuple[bool, str]:
        """Check if Generator may build. Returns (can_build, reason)."""
        if contract.status == ContractStatus.SEALED:
            return True, "Contract sealed"
        if contract.status == ContractStatus.DRAFT:
            return False, "Contract not yet negotiated"
        if contract.status == ContractStatus.NEGOTIATING:
            return False, "Contract in negotiation"
        if contract.status == ContractStatus.BROKEN:
            return False, "Contract broken"
        return False, f"Unknown contract status: {contract.status}"

    def save(self, contract: DoneContract) -> None:
        """Save contract to YAML."""
        import yaml
        path = self.repo_root / "runs" / contract.run_id / "DoneContract.yaml"
        path.parent.mkdir(parents=True, exist_ok=True)
        data = contract.model_dump(mode="json")
        with open(path, "w", encoding="utf-8") as f:
            yaml.dump(data, f, default_flow_style=False)

    def load(self, run_id: str) -> DoneContract | None:
        """Load contract from YAML."""
        import yaml
        path = self.repo_root / "runs" / run_id / "DoneContract.yaml"
        if not path.exists():
            return None
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        return DoneContract(**data) if data else None