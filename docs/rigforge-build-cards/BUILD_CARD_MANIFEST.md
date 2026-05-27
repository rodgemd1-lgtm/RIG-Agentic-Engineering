# RIGForge Build Card Manifest

## Prime Directive

RIGForge is not complete because code exists.
RIGForge is complete only when every phase has:
- declared files
- deterministic tests
- registry entries
- health checks
- ProofPackets
- verifier result
- rollback or blocker path
- cockpit visibility where applicable

No RunEnvelope, no run.
No DoneContract, no code.
No ProofPacket, no PASS.
No registry entry, no production use.
No approval, no external side effect.

## System Architecture

```
Hermes (govern)
    ↓
Archon (workflow order)
    ↓
DeerFlow 2.0 (long-horizon supervision)
    ↓
PyCode (build)
    ↓
Codex (verify)
```

## Naming

| Layer | Name | Purpose |
|---|---|---|
| Whole system | **RIGForge Agentic Engineering Platform** | The complete build, verification, proof, retrofit, and app-generation system |
| CLI | **`rigforge`** | The deterministic command surface agents call instead of improvising |
| UI | **RIG Mission Control / Cockpit** | The operator surface where you watch runs, approve actions, see proof, and pause/cancel/resume |
| Runtime | **RIG Runtime Kernel** | RunEnvelope, state machine, event journal, proof chain |
| Agent loop | **GEV Loop** | Generator → Evaluator → Verifier |
| Long-run harness | **DeerFlow** | Only for multi-hour supervised execution after the core runtime exists |

## Agent Roles

| Role | Agent | Job |
|---|---|---|
| Coordinator / Governor | **Codex or Hermes** | Reads manifest, enforces phase order, blocks unsafe progress |
| Generator | **PyCode / PiCode** | Writes code, tests, files |
| Evaluator | **Claude Code, Gemini, or Kimi** | Critiques scope, tests, edge cases, risk, missing proof |
| Verifier | **Codex CLI** | Stateless final check from files/tests/proof only |
| Operator | **Mike via Cockpit/AionUI** | Approves risky actions, deploys, waivers, external side effects |

The Verifier must not receive Generator or Evaluator chat history.

## Build Order

| Phase | Card | Status | Owner | Blocker |
|---|---|---|---|---|
| 1 | Repo Bootstrap + Doctrine Pack | 🟢 Verified | PyCode | — |
| 2 | Environment Bootstrap | 🔵 Active | PyCode | Phase 1 |
| 3 | Runtime Kernel | ⚪ Pending | PyCode | Phase 2 |
| 4 | Control Plane | ⚪ Pending | PyCode | Phase 3 |
| 5 | GEV Loop + DoneContract | ⚪ Pending | PyCode | Phase 4 |
| 6 | Archon + DeerFlow Harness | ⚪ Pending | PyCode | Phase 5 |
| 7 | Cockpit + Retrofit Protocol | ⚪ Pending | PyCode | Phase 6 |

## Card Status Legend

- 🔵 **Active** — Current build target. Generator is implementing.
- 🟡 **Review** — Implementation complete. Evaluator is critiquing.
- 🟢 **Verified** — Verifier has passed. ProofPacket sealed.
- ⚪ **Pending** — Waiting on previous phase.
- 🔴 **Blocked** — Blocker identified. Cannot proceed.

## Build Card Directory

```
docs/rigforge-build-cards/
├── BUILD_CARD_MANIFEST.md          ← This file
├── BUILD_CARD_01_BOOTSTRAP.md      ← Repo scaffold + doctrine
├── BUILD_CARD_02_ENVIRONMENT.md    ← Doctor + install proof
├── BUILD_CARD_03_RUNTIME.md        ← RunEnvelope + state machine
├── BUILD_CARD_04_CONTROL_PLANE.md ← Registries + health checks
├── BUILD_CARD_05_GEV.md            ← Generator-Evaluator-Verifier
├── BUILD_CARD_06_DEERFLOW.md       ← Long-horizon harness
└── BUILD_CARD_07_COCKPIT.md        ← Cockpit + retrofit
```

## Global Exit Criteria

All phases must pass before RIGForge is production-ready:

```text
[ ] All 7 build cards verified
[ ] rigforge doctor passes
[ ] rigforge status reports READY
[ ] Runtime Kernel tests pass
[ ] Control Plane registries exist
[ ] GEV smoke mission passes
[ ] DeerFlow thread mapping works
[ ] Cockpit loads and shows active runs
[ ] First studio retrofit complete with ProofPacket
[ ] No missing ProofPacket rate > 0
[ ] No unregistered services in production
```

## Deterministic Build Ladder

```text
A1 — Deterministic Core
  Python, schemas, tests, health checks, no model in decision path.

A2 — Bounded LLM
  Structured model calls only, typed outputs, source/proof requirements.

A3 — Governed Agent Workflow
  Archon/DeerFlow/state machines, approval nodes, budget limits, max iterations.

A4 — High-Ambiguity / Red-Team / Falsification
  Multi-agent review, adversarial critique, external-risk gates, Mike approval.
```

## Lattice Coordinate for Every Build

```text
Every app build must resolve into:
Level × Diamond × BMS Mode × IQRSQPI Step

Example:
Mission: Retrofit LinkedIn Studio scheduler proof path
Coordinate: L2 × D1 × A1
Step: Proof / Integrate
Mode: Deterministic Python first
Required artifacts:
  - scheduler healthcheck
  - worker connection test
  - e2e pipeline test
  - ProofPacket
  - cockpit status row
Verifier: Codex stateless
Approval: Mike only if production schedule activation changes
```
