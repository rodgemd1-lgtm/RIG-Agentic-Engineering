# Aider Generator Tool Policy

## Tool Identity

**Name:** Aider (`aider-chat`)  
**Version:** 0.86.2  
**Role:** Bounded code generator (Generator tool)  
**RIGForge Phase:** Phase 5+ (GEV Loop)  
**Owner:** mike

## Prime Rule

Aider is a **coding tool**. It is not the orchestrator, evaluator, or verifier. It cannot self-approve, bypass DoneContract, or perform external side effects.

## Role Constraints

| Allowed | Forbidden |
|---|---|
| Read files in allowed_files list | Self-verify |
| Edit files in allowed_files list | Approve own work |
| Run local test commands | Modify frozen doctrine |
| Write to proof/ output dirs | Modify production without approval |
| Emit ProofPacket drafts | Perform external side effects |
| Ask clarifying questions | Read verifier private notes |

## Required Inputs Before Aider Executes

1. `spec.md` — must exist
2. `DoneContract.yaml` — must be SEALED
3. `allowed_files` list — scope of writable files
4. `forbidden_files` list — never touched
5. `required_tests` list — tests Aider must run
6. `proof_requirements` — what ProofPacket must contain

## Required Outputs From Aider

1. `files_changed_summary` — list of modified files
2. `tests_run` — commands executed
3. `test_results` — pass/fail for each
4. `proof_draft` — ProofPacket draft

## Downstream Gates

Aider output must pass:
1. Evaluator review (LOOP_BACK / PASS_TO_VERIFIER / BLOCK)
2. Stateless Verifier (PASS / FAIL / BLOCKED)
3. ProofPacket seal

Aider alone cannot approve anything.

## Usage in GEV Loop

```
DoneContract (sealed)
    ↓
Aider implements allowed files only
    ↓
Evaluator critiques
    ↓
Aider fixes if LOOP_BACK
    ↓
Verifier stateless check
    ↓
ProofPacket
    ↓
Approval (if needed)
```

## Verifier Isolation

Aider MUST NOT see:
- Verifier's private notes
- Evaluator's critique before it's shared
- Generator's internal reasoning

## Example Aider Invocation

```bash
aider --read-only-files spec.md \
       --allowed-edit-files src/*.py \
       --forbidden-edit-files contracts/v1/*.py \
       --test-commands "pytest tests/" \
       --proof-output proof/...
```