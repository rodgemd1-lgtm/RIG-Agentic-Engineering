# RIGForge Agent Operating Model

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

## Agent Roles

| Role | Agent | Job | Scope |
|---|---|---|---|
| Governor | **Hermes** | Doctrine enforcement, audit, escalation | Full system |
| Coordinator | **Codex** | Reads manifest, enforces phase order, blocks unsafe progress | Per mission |
| Generator | **PyCode / PiCode** | Writes code, tests, files, runs local commands | Per build |
| Evaluator | **Claude Code / Gemini / Kimi** | Critiques scope, tests, edge cases, risk, missing proof | Per build |
| Verifier | **Codex CLI** | Stateless final check from files/tests/proof only | Per build |
| Operator | **Mike via Cockpit** | Approves risky actions, deploys, waivers | Human |

## Communication Rules

### All agents communicate through:
1. **RunEnvelope** — Mission context, run_id, studio, status
2. **DoneContract** — Build contract (must-haves, must-passes, must-nevers)
3. **ProofPacket** — Evidence (files touched, hashes, trace URIs)
4. **Event Journal** — Append-only log
5. **Approval Packet** — Signed approval for risky actions

### Forbidden Communication:
- Evaluator cannot edit code directly
- Verifier cannot see generator chat history
- Generator cannot auto-approve its own work
- No agent can bypass the RunEnvelope / DoneContract / ProofPacket chain

## Phase Enforcement

The Coordinator (Codex) reads `BUILD_CARD_MANIFEST.md` and enforces:
- Which card is active now
- Which cards are reference-only
- Which card is blocked until previous gates pass
- No skipping phases
- No phase proceeds without ProofPacket

## Failure Routing

```
A3 failure → A2 fallback → A1 fallback → IntentKey.UNKNOWN → ProofPacket → Escalate to Hermes/Mike
```

## Verifier Isolation

The Verifier receives ONLY:
- `spec.md`
- `DoneContract.yaml`
- Final file tree snapshot
- Test commands
- ProofPacket paths
- Hash manifest

The Verifier MUST NOT receive:
- Generator chat history
- Evaluator chat history
- Intermediate drafts
- Self-assessments from other agents

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

## For All Agents

- Use `temperature=0` unless contract explicitly overrides
- A1 logic never contains smart, fuzzy, best-guess, or confidence-branch logic
- Unknown intent returns `IntentKey.UNKNOWN` and escalates
- No external side effects without approval
- No printing secrets, tokens, cookies, session state
- Every action that changes state must emit a ProofPacket
