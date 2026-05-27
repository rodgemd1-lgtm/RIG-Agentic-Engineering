# RIG Master Doctrine

## Prime Directive

**RIGForge is not another vibe-coding agent. It is a deterministic build factory where agents are only allowed to operate through contracts, registries, gates, tests, approvals, and ProofPackets.**

## Core Principles

1. **Local-first** — Prefer local execution over remote API calls
2. **Deterministic before agentic** — A1 logic first, then A2 bounded LLM, then A3 governed workflow, then A4 high-ambiguity
3. **A1 first** — Gate 00-12 for apps/releases. Python-only deterministic core before any model involvement
4. **Research before synthesis** — Never generate without context
5. **Escalate instead of failing** — `IntentKey.UNKNOWN` and escalate
6. **ProofPacket or it did not happen** — No build step counts without evidence
7. **temperature=0** — Every LLM call uses `temperature=0` unless contract explicitly overrides
8. **No smart guesses** — A1 logic never contains smart, fuzzy, best-guess, or confidence-branch logic
9. **No auto-approve** — External sends, account changes, private data export, calendar writes, payments, and destructive actions require Mike approval
10. **Never print secrets** — No printing of tokens, cookies, session state, or raw credential files

## Failure Routing

```
A3 failure → A2 fallback → A1 fallback → IntentKey.UNKNOWN → ProofPacket → Escalate
```

## Build Ladder

| Mode | Description | When to Use |
|---|---|---|
| **A1** | Deterministic Core — Python, schemas, tests, health checks, no model in decision path | Default for all logic, registries, gates |
| **A2** | Bounded LLM — Structured model calls, typed outputs, source/proof requirements | Evaluation, generation when deterministic alone is insufficient |
| **A3** | Governed Agent Workflow — Archon/DeerFlow/state machines, approval nodes, budget limits, max iterations | Multi-step missions requiring agent coordination |
| **A4** | High-Ambiguity / Red-Team / Falsification — Multi-agent review, adversarial critique, external-risk gates | Mike approval required. Used for security review, production deployment |

## Lattice Geometry

Every build resolves to a coordinate:

```
Level × Diamond × BMS Mode × IQRSQPI Step

X-axis: Level / Altitude (L1-L7)
Y-axis: Triple Diamond (D1 Physical, D2 Cognitive, D3 Nature)
Z-axis: BMS Confidence / Build Mode (A1-A4)
Inside every coordinate: Intent → Question → Research → Solution → Quality → Proof → Integrate
```

## Hard Rules

- No edits to `contracts/v1/` — Frozen after `a1-contracts-v1` tag
- New contract work goes to `contracts/v2/`
- Every commit triggers ProofPacket replay
- `mutmut` kill rate must stay at or above 85%
- Unknown A1 intent returns `IntentKey.UNKNOWN` and escalates
- No DeerFlow thread without RunEnvelope
- No long-horizon mission without DeerFlow thread mapping
- DeerFlow cannot: choose Archon nodes, skip nodes, edit workflow YAML, mark runs complete without verifier, perform external side effects, modify audit logs

## Agent Hierarchy

```
Hermes (govern, audit, doctrine enforcement)
    ↓
Archon (workflow order, deterministic gates)
    ↓
DeerFlow 2.0 (long-horizon supervision, multi-hour runs)
    ↓
PyCode (build, implementation, generator)
    ↓
Codex (verify, stateless judgment, final check)
```

## Communication Protocol

All agents communicate through:
1. **RunEnvelope** — Mission context, run_id, studio
2. **DoneContract** — Build contract, must-haves, must-passes, must-nevers
3. **ProofPacket** — Evidence of completion, files touched, hashes, trace URIs
4. **Event Journal** — Append-only log of all actions
5. **Approval Packet** — Signed approval for risky actions

## Verifier Isolation

The Verifier MUST NOT receive:
- Generator chat history
- Evaluator chat history
- Intermediate drafts
- Self-assessments from other agents

The Verifier receives ONLY:
- spec.md
- DoneContract.yaml
- Final file tree
- Test commands
- ProofPacket paths
- Hash manifest

## Exit Criteria for Any Phase

```text
[ ] Declared files exist
[ ] Deterministic tests pass
[ ] Registry entries created
[ ] Health checks present
[ ] ProofPacket sealed
[ ] Verifier result recorded
[ ] Rollback or blocker path documented
[ ] Cockpit visibility where applicable
```

## System is Real When

```text
One executable control plan
One run state
One proof chain
One approval path
```
