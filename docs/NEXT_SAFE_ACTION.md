# Next Safe Action

## Current Phase
Phase 2: Environment Bootstrap / Doctor / Install Proof — **DEGRADED PASS**

## What "DEGRADED PASS" Means
- All required tools (Python, Node, Git, uv) are READY
- Optional tools/services are missing but not blocking
- System can proceed with reduced capability flag
- No blockers for Phase 3

## Next Phase
Phase 3: Runtime Kernel — RunEnvelope, State Machine, Event Bus

## What to Do

1. Read BUILD_CARD_03_RUNTIME.md for specifications
2. Create `contracts/v1/run_envelope.py` — RunEnvelope Pydantic model
3. Create `runtime/kernel/state_machine.py` — Valid state transitions
4. Create `runtime/kernel/event_bus.py` — Append-only event journal
5. Create `runtime/kernel/run_store.py` — Run persistence
6. Create tests in `tests/runtime/`
7. Seal Runtime Kernel ProofPacket
8. Update BUILD_CARD_MANIFEST: Phase 2 → Verified, Phase 3 → Active

## What NOT to Do

- Do NOT build Control Plane yet
- Do NOT integrate DeerFlow yet
- Do NOT create Cockpit UI yet
- This phase is ONLY the Runtime Kernel deterministic spine

## Required Proof

```text
proof/runtime/run_envelope_test.json
proof/runtime/state_machine_test.json
proof/runtime/event_journal_test.json
proof/runtime/runtime_kernel_proofpacket.json
docs/PHASE_3_RUNTIME_REPORT.md
```

## Gate Criteria

Phase 3 passes when:
- RunEnvelope schema validates
- State machine blocks invalid transitions
- Event journal is append-only
- All runtime tests pass
- Runtime ProofPacket sealed
