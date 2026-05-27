# Build Card 3 — Runtime Kernel: RunEnvelope, State Machine, Event Bus

**Status:** ⚪ Pending  
**Phase:** 3 of 7  
**Owner:** PyCode / Generator  
**Critique:** Claude Code / Evaluator  
**Verifier:** Codex CLI (stateless)  
**Gate:** G02 — Runtime Kernel Ready
**Unblocked by:** Phase 2 ProofPacket sealed

## Goal

Create the deterministic spine of the whole system. Every mission, tool call, test, approval, incident, proof packet, and build artifact must attach to the same `run_id`.

## Required Cards

1. **BUILD CARD** — RIG Runtime Kernel: RunEnvelope, State Machine, and Event Bus
2. **MASTER CONTROL PLAN** (parent reference)
3. **Failure Runbook** (reference for blocked/failed states)

## What the Agent Builds

```
contracts/v1/
├── run_envelope.py          # RunEnvelope Pydantic model
├── mission.py               # Mission definition
├── workflow_state.py        # Workflow state transitions
├── event_journal.py         # Append-only event log
├── state_transition.py      # Valid transition rules
├── gate_result.py           # Gate result schema
├── proof_packet.py          # ProofPacket schema
├── approval_packet.py       # Approval schema
└── incident.py              # Incident schema

runtime/kernel/
├── state_machine.py         # Core state machine
├── event_bus.py             # Event publishing/subscription
├── run_store.py             # Run persistence
└── ids.py                   # ID generation (ULID)

tests/runtime/
├── __init__.py
├── test_run_envelope.py
├── test_state_transitions.py
├── test_event_journal.py
└── test_invalid_transitions.py

scripts/
└── verify_runtime_kernel.py  # Runtime kernel verification
```

## Core Law

```
No RunEnvelope, no run.
No run_id, no proof.
No state machine, no long-horizon autonomy.
No event journal, no debugging.
```

## Required Commands

```bash
rigforge bootstrap --phase runtime-kernel
python scripts/verify_runtime_kernel.py
pytest tests/runtime/ -v
```

## Files to Create

### `contracts/v1/run_envelope.py`
```python
class RunEnvelope(BaseModel):
    run_id: str               # ULID
    studio: str               # "app", "agent", "api", "web"
    idea: str                 # One-line description
    created_at: datetime
    status: str               # "draft" | "building" | "needs_approval" | "completed" | "failed"
    harness: str              # "local" | "deerflow" | "archon"
    harness_args: dict
    tool_registry_path: str   # Path to tool contract registry
```

### `runtime/kernel/state_machine.py`
Valid transitions:
```
draft → building
building → needs_approval
building → failed
needs_approval → completed (with approval)
needs_approval → failed
failed → blocked (terminal)
```

Forbidden transitions:
```
failed → completed          # Must restart
needs_approval → completed  # Without approval
building → completed        # Without verify
```

### `runtime/kernel/event_bus.py`
- Append-only event journal
- Every event: `(timestamp, run_id, phase, event_type, payload)`
- No deletion, no modification
- Event types: `mission_started`, `phase_completed`, `proof_emitted`, `approval_requested`, `approval_granted`, `failure_detected`, `incident_opened`

### `contracts/v1/proof_packet.py`
```python
class ProofPacket(BaseModel):
    packet_id: str
    run_id: str
    phase: str                # "bootstrap" | "environment" | "runtime" | "gev" | "deerflow" | "cockpit"
    status: str               # "pass" | "fail" | "blocked"
    evidence: dict            # Arbitrary evidence dict
    timestamp: datetime
    verifier: str             # "codex" | "hermes" | "mike"
    signature: Optional[str]  # GPG or API key signature
```

## Exit Criteria

```text
[ ] RunEnvelope schema exists and validates
[ ] run_id propagates through test mission
[ ] mission_id propagates through workflow
[ ] event journal writes append-only events
[ ] invalid state transitions raise RuntimeError
[ ] failed → completed is blocked
[ ] needs_approval → completed without approval is blocked
[ ] Runtime tests pass
[ ] Runtime ProofPacket written
[ ] Build Card 4 is unblocked
```

## Proof Required

```json
{
  "phase": "runtime-kernel",
  "run_id": "runtime_kernel_YYYYMMDD_HHMMSS",
  "status": "pass",
  "evidence": {
    "run_envelope_valid": true,
    "state_transitions_valid": true,
    "invalid_transitions_blocked": true,
    "event_journal_append_only": true,
    "test_count": "≥4",
    "test_status": "pass",
    "forbidden_transitions_tested": ["failed→completed", "needs_approval→completed"]
  }
}
```

## Why This Matters

This prevents the mess of retrofit chaos. The Runtime Kernel means every build has:
- One state
- One trace
- One event journal
- One proof trail
- One answer to: "What happened?"

## Next Phase

Phase 4 is unblocked when Runtime Kernel tests pass.
