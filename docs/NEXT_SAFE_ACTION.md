# Next Safe Action

## Current Phase
Phase 4: Control Plane — **PASS**

## Next Phase
Phase 5: GEV Loop + DoneContract

## What to Do

1. Create `contracts/v1/done_contract.py` — DoneContract Pydantic model
2. Create `contracts/v1/verifier_package.py` — What verifier receives
3. Create `contracts/v1/required_artifact.py` — Artifact requirements
4. Create `contracts/v1/acceptance_criterion.py` — Pass/fail criteria
5. Create `contracts/v1/forbidden_action.py` — Actions generator must not take
6. Create `runtime/gev/generator_runner.py`, `evaluator_runner.py`, `verifier_runner.py`
7. Wire `rigforge specify <studio>`, `rigforge build <studio>`, `rigforge verify <studio>`
8. Create `tests/gev/`
9. Seal GEV ProofPacket

## Core Law

```text
No DoneContract, no code.
No acceptance criteria, no mission.
No required artifacts, no verifier package.
No verifier package, no PASS.
```

## Verifier Isolation

Verifier receives ONLY:
- spec.md
- DoneContract.yaml
- Final file tree
- Test commands
- ProofPacket paths
- Hash manifest

Verifier must NOT receive:
- Generator chat history
- Evaluator chat history
- Intermediate drafts