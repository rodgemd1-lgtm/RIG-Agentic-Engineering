# Aider Usage for GTM Studio Retrofit

## Context

Aider is the bounded generator tool for GTM Studio retrofit under RIGForge Phase 5 (GEV Loop).

## Allowed Scope

Aider may only operate within the scope defined by the active DoneContract for GTM Studio.

## Current Phase

GTM Studio Phase 0 — Inventory/Dry Run. Aider is used only for **read-only repository mapping** in this phase.

## Phase 0 Allowed Prompt

```
Read the GTM Studio repository and summarize the architecture.
Do not edit files.
Do not create files.
Identify: entrypoints, workers, schedulers, API routes, tests, config, external side effects, proof/audit paths.
Output a concise architecture inventory as markdown.
```

## Phase 1+ Allowed Prompt (after DoneContract SEALED)

```
Implement the DoneContract for GTM Studio worker/scheduler healthcheck.
Files you may edit: <from allowed_files list>
Files you may NOT edit: contracts/v1/*, production_api/*, scheduler_triggers/*
Tests you must run: pytest tests/gtm_studio/healthcheck/
Output ProofPacket draft to proof/gtm_studio/
```

## Forbidden for GTM Studio

Aider must NEVER:
- Edit `contracts/v1/` files
- Trigger production schedules
- Send external campaign messages
- Modify database schemas without rollback plan
- Bypass healthcheck requirements
- Skip test requirements

## Proof Requirements

After any Aider implementation:
- File hashes must be captured
- Test results must be recorded
- ProofPacket draft must be emitted
- No external side effects without Mike approval

## Verification

After Aider completes:
```bash
pytest tests/gtm_studio/
# All must pass
python scripts/verify_deerflow_proof.py --run-id <id>
# ProofPacket must be sealed
```