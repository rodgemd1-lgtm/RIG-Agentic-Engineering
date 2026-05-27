# Build Card 5 — GEV Loop: Generator, Evaluator, Verifier, DoneContract

**Status:** ⚪ Pending  
**Phase:** 5 of 7  
**Owner:** PyCode / Generator  
**Critique:** Claude Code / Evaluator  
**Verifier:** Codex CLI (stateless)  
**Gate:** G04 — GEV Loop Ready
**Unblocked by:** Phase 4 ProofPacket sealed

## Goal

Create the "two coding agents going against each other plus verifier" system correctly. Do not make two coding agents randomly fight. Use structured DoneContract negotiation, Generator build, Evaluator critique, Verifier stateless check.

## Agent Roles

| Role | Agent | Job |
|---|---|---|
| Coordinator / Governor | **Codex or Hermes** | Reads manifest, enforces phase order |
| Generator | **PyCode / PiCode** | Writes code, tests, files |
| Evaluator | **Claude Code, Gemini, or Kimi** | Critiques scope, tests, edge cases, risk |
| Verifier | **Codex CLI** | Stateless final check from files/tests/proof only |

## Workflow

```
Spec
↓
DoneContract negotiation
↓
Generator builds (only after contract sealed)
↓
Evaluator critiques
↓
Generator repairs (if evaluator blocks)
↓
Verifier checks statelessly
↓
ProofPacket sealed
↓
Approval if needed
```

## Required Cards

1. **BUILD CARD** — RIG DoneContract Schema for Generator-Evaluator-Verifier Builds
2. **BUILD CARD** — RIG Role-Specific AGENTS.md Files
3. **BUILD CARD** — RIG Universal Studio Hardening Layer
4. **BUILD CARD** — RIG Agentic Engineering Failure Runbook and Incident Response

## What the Agent Builds

```
contracts/v1/
├── done_contract.py          # DoneContract Pydantic model
├── verifier_package.py       # What verifier receives
├── required_artifact.py      # Artifact requirements
├── acceptance_criterion.py   # Pass/fail criteria
└── forbidden_action.py       # Actions generator must not take

runtime/gev/
├── generator_runner.py       # Generator execution harness
├── evaluator_runner.py       # Evaluator execution harness
├── verifier_runner.py      # Verifier execution harness
├── done_contract_negotiator.py  # Contract negotiation logic
└── verifier_package_builder.py  # Package assembly

agents/
├── generator/AGENTS.md
├── evaluator/AGENTS.md
├── verifier/AGENTS.md
└── hermes/AGENTS.md

tests/gev/
├── __init__.py
├── test_done_contract_required.py
├── test_generator_cannot_build_without_contract.py
├── test_evaluator_must_challenge.py
├── test_verifier_cannot_see_chat_history.py
└── test_missing_proof_blocks_pass.py
```

## Core Law

```
DoneContract required before code.
Generator builds only after sealed contract.
Evaluator must challenge weak tests, missing artifacts, rollback gaps, proof gaps.
Verifier package excludes generator/evaluator chat history.
Verifier can only use files, tests, schemas, hashes, ProofPackets.
Missing ProofPacket returns BLOCKED, not PASS.
```

## Required Commands

```bash
rigforge specify <studio>    # Create DoneContract
rigforge plan <studio>       # Plan build steps
rigforge build <studio>      # GEV build execution
rigforge verify <studio>     # Stateless verification
```

## DoneContract Schema

```python
class DoneContract(BaseModel):
    run_id: str
    studio: str
    idea: str
    # Must-haves
    required_artifacts: list[RequiredArtifact]
    # Must-pass
    acceptance_criteria: list[AcceptanceCriterion]
    # Must-never
    forbidden_actions: list[ForbiddenAction]
    # Verifier package
    verifier_package: VerifierPackage
    # Signatures
    generator_signature: Optional[str]
    evaluator_signature: Optional[str]
    approved: bool = False
    approved_by: Optional[str]
    approval_timestamp: Optional[datetime]

class RequiredArtifact(BaseModel):
    name: str
    path: str
    description: str
    required: bool = True
    test_command: Optional[str]  # If artifact must be testable

class AcceptanceCriterion(BaseModel):
    id: str
    description: str
    test_command: Optional[str]
    manual_check: bool = False

class ForbiddenAction(BaseModel):
    action: str
    reason: str
    consequence: str = "BLOCKED"

class VerifierPackage(BaseModel):
    spec_path: str
    done_contract_path: str
    file_tree_snapshot: list[str]
    test_commands: list[str]
    proof_packet_paths: list[str]
    hash_manifest: dict[str, str]
    # Explicitly excluded:
    # - generator chat history
    # - evaluator chat history
    # - intermediate drafts
```

## Evaluator Rules

The Evaluator MUST challenge:
- Missing required artifacts
- Weak or missing tests
- No rollback path defined
- Missing proof for external-facing features
- Forbidden actions not clearly blocked
- Ambiguous acceptance criteria

The Evaluator MUST NOT:
- Edit code directly
- Auto-approve anything
- Trust the Generator's self-assessment

## Verifier Rules

The Verifier receives ONLY:
- `spec.md`
- `DoneContract.yaml`
- Final file tree
- Test commands
- ProofPacket paths
- Hash manifest

The Verifier MUST NOT receive:
- Generator chat history
- Evaluator chat history
- Intermediate drafts
- Self-assessments from other agents

The Verifier returns:
- `PASS` — all criteria met, all artifacts present, all tests pass
- `FAIL` — criteria not met or artifacts missing
- `BLOCKED` — missing ProofPacket or incomplete evidence

## Exit Criteria

```text
[ ] DoneContract schema exists and validates
[ ] Generator cannot write code before contract is sealed
[ ] Evaluator must challenge weak tests, missing artifacts, rollback gaps
[ ] Verifier package excludes generator/evaluator chat history
[ ] Verifier can only use files, tests, schemas, hashes, ProofPackets
[ ] Missing ProofPacket returns BLOCKED, not PASS
[ ] GEV smoke mission passes
[ ] Build Card 6 is unblocked
```

## Proof Required

```json
{
  "phase": "gev",
  "run_id": "gev_loop_YYYYMMDD_HHMMSS",
  "status": "pass",
  "evidence": {
    "done_contract_schema_valid": true,
    "contract_required_before_build": true,
    "evaluator_challenges_present": true,
    "verifier_isolated": true,
    "missing_proof_blocks": true,
    "smoke_mission_passed": true,
    "test_count": "≥5",
    "test_status": "pass"
  }
}
```

## Next Phase

Phase 6 is unblocked when GEV smoke mission passes with verifier PASS.
