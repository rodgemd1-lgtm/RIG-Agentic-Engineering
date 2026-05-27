# RIGForge Agentic Engineering Platform — Canonical Build Card

This is the canonical build-order card for **RIGForge**, the RIG Agentic Engineering Platform.

RIGForge is the deterministic build factory for turning RIG application ideas, studio retrofits, and agentic engineering missions into proof-backed software. It coordinates the CLI, runtime kernel, control plane, Generator-Evaluator-Verifier loop, DeerFlow long-horizon harness, cockpit, ProofPackets, and retrofit protocol.

This card exists so PiCode / PyCode, Codex, Hermes, and any future build agent know **what to build first, what to defer, what proves each phase is complete, and when to stop**.

## Core Law

```text
Do not dump all build cards into the repo at once.
Run the build in phases.
No phase may start until the previous phase has proof.
No proof = BLOCKED.
No RunEnvelope = no run.
No DoneContract = no code.
No ProofPacket = no PASS.
No registry entry = no production use.
No approval = no external side effect.
```

---

## 1. Product Name

Use this naming stack:

| Layer | Name |
|---|---|
| Whole platform | **RIGForge Agentic Engineering Platform** |
| CLI | **rigforge** |
| UI | **RIG Mission Control / Cockpit** |
| Runtime | **RIG Runtime Kernel** |
| Agent loop | **GEV Loop** — Generator → Evaluator → Verifier |
| Long-run layer | **DeerFlow supervised harness** |
| Governor | **Hermes** |
| Builder | **PyCode / PiCode** |
| Verifier | **Codex CLI, stateless verifier mode** |

Short definition:

```text
RIGForge is the deterministic build factory where coding agents are only allowed to operate through contracts, registries, gates, tests, approvals, and ProofPackets.
```

---

## 2. Agent Roles

### Coordinator — Codex

Codex may coordinate the build order, read the manifest, enforce phase sequencing, open issues, call the builder, call the evaluator, and perform stateless final verification when explicitly acting as verifier.

**Allowed:**
- read BUILD_CARD_MANIFEST.md
- decide current phase
- block unsafe progression
- summarize state
- invoke PyCode / PiCode for implementation
- invoke evaluator for critique
- invoke verifier mode for final check

**Forbidden:**
- skip phases
- mark missing proof as PASS
- allow external side effects without approval
- let verifier see generator/evaluator chat history

### Generator — PyCode / PiCode

PyCode or PiCode owns implementation.

**Allowed:**
- create files
- write tests
- run local commands
- fix failing implementation
- emit ProofPacket drafts

**Forbidden:**
- build before DoneContract when GEV phase begins
- self-verify final PASS
- change frozen doctrine without approval
- perform external actions without approval

### Evaluator — Claude Code / Gemini / Kimi / Critic Agent

Evaluator critiques the proposed contract and implementation.

**Allowed:**
- challenge weak tests
- challenge missing artifacts
- challenge missing edge cases
- challenge rollback gaps
- challenge proof gaps
- return PASS_TO_VERIFIER, LOOP_BACK, or BLOCK

**Forbidden:**
- edit code directly unless explicitly assigned a generator role
- approve its own work
- act as final verifier

### Verifier — Codex CLI Stateless Mode

Verifier judges final artifacts only.

**Required inputs:**
- spec.md
- DoneContract
- final file tree
- test commands
- ProofPacket
- hashes

**Forbidden inputs:**
- Generator chat history
- Evaluator chat history
- private reasoning transcripts

**Verifier may return only:**
- PASS
- FAIL
- BLOCKED

### Hermes — Governor / Auditor

Hermes audits proof, enforces doctrine, escalates blockers, and preserves state after failure.

### Mike — Human Approval Authority

Mike approves risky actions, production changes, external sends, schedule activation, deployment, rollback, destructive operations, and gate waivers.

---

## 3. Required Repository Manifest

Create this file immediately:

```text
docs/rigforge-build-cards/BUILD_CARD_MANIFEST.md
```

The manifest must contain:

```text
1. active phase
2. active card
3. reference-only cards
4. blocked cards
5. phase owner
6. generator agent
7. evaluator agent
8. verifier agent
9. required proof
10. next safe action
```

The manifest is the repo-level source of truth. Agents must read it before acting.

---

## 4. Seven-Phase Build Order

### Phase 1 — Repo Bootstrap + Doctrine Pack

#### Purpose
Create the repo skeleton, doctrine files, agent role files, and initial manifest. This phase teaches the agents the operating law before they write meaningful code.

#### Required files
```text
AGENTS.md
CODEX.md
PYCODE.md
EVALUATOR.md
VERIFIER.md
HERMES.md
RIG_DOCTRINE.md
BUILD_CARD_MANIFEST.md
README.md
pyproject.toml or package equivalent
Makefile or task runner equivalent
config/
contracts/
workflows/
agents/
studios/
scripts/
tests/
evals/
proof/
docs/
```

#### Minimum tests
```text
tests/test_repo_bootstrap.py
```

This test must verify required files and directories exist.

#### Required proof
```text
proof/bootstrap_repo.json
docs/PHASE_1_BOOTSTRAP_REPORT.md
docs/NEXT_SAFE_ACTION.md
docs/BLOCKERS.md
```

#### Exit criteria
```text
[ ] repo scaffold exists
[ ] doctrine files exist
[ ] role files exist
[ ] manifest exists
[ ] test setup exists
[ ] bootstrap test passes
[ ] bootstrap proof exists
[ ] next safe action written
```

#### Gate output
```text
PHASE_1_PASS
```

or

```text
PHASE_1_BLOCKED
```

Do not start Phase 2 until Phase 1 passes.

---

### Phase 2 — Environment Bootstrap / Doctor / Install Proof

#### Purpose
Prove the machine can run RIGForge before building the runtime.

Core law:
```text
No install proof, no runtime.
No verification proof, no build.
No environment manifest, no agent execution.
```

#### Required files
```text
scripts/doctor.py
scripts/verify_environment.py
scripts/verify_versions.py
scripts/verify_services.py
scripts/write_environment_proof.py

config/environment.yaml
config/runtime_versions.yaml
config/local_paths.yaml

proof/environment/doctor_report.json
proof/environment/version_report.json
proof/environment/environment_proofpacket.json

tests/environment/test_doctor.py
tests/environment/test_required_versions.py
tests/environment/test_required_paths.py
```

#### Required command
```bash
rigforge doctor
```

#### Required checks
```text
Python
Node
Docker
Git
uv
pytest
Playwright availability or documented blocker
Promptfoo availability or documented blocker
DeepEval availability or documented blocker
Postgres availability or documented blocker
Qdrant availability or documented blocker
Neo4j availability or documented blocker
Langfuse availability or documented blocker
AionUI availability or documented blocker
```

Use explicit statuses:
```text
READY
DEGRADED
BLOCKED
NOT_INSTALLED
NOT_CONFIGURED
```

#### Exit criteria
```text
[ ] doctor command works
[ ] required versions checked
[ ] optional missing services do not falsely PASS
[ ] blockers are explicit
[ ] environment proof files written
[ ] tests pass
```

#### Gate output
```text
PHASE_2_PASS
```

or

```text
PHASE_2_BLOCKED
```

Do not start Phase 3 until Phase 2 passes.

---

### Phase 3 — Runtime Kernel: RunEnvelope, State Machine, Event Bus

#### Purpose
Create the deterministic spine of RIGForge. Every mission, tool call, approval, incident, ProofPacket, memory event, and artifact must attach to a shared `run_id`.

Core law:
```text
No RunEnvelope, no run.
No run_id, no proof.
No state machine, no long-horizon autonomy.
No event journal, no debugging.
```

#### Required files
```text
contracts/v1/run_envelope.py
contracts/v1/mission.py
contracts/v1/workflow_state.py
contracts/v1/event_journal.py
contracts/v1/state_transition.py
contracts/v1/gate_result.py
contracts/v1/proof_packet.py
contracts/v1/approval_packet.py
contracts/v1/incident.py

runtime/kernel/state_machine.py
runtime/kernel/event_bus.py
runtime/kernel/run_store.py
runtime/kernel/ids.py

tests/runtime/test_run_envelope.py
tests/runtime/test_state_transitions.py
tests/runtime/test_event_journal.py
tests/runtime/test_invalid_transitions.py

scripts/verify_runtime_kernel.py
```

#### Required blocked transitions
```text
failed → completed
blocked → completed
needs_approval → completed without signed approval
cancelled → running
completed → running
```

#### Required command
```bash
rigforge bootstrap --phase runtime-kernel
python scripts/verify_runtime_kernel.py
pytest tests/runtime
```

#### Exit criteria
```text
[ ] RunEnvelope schema exists
[ ] run_id propagates through test mission
[ ] mission_id propagates through workflow
[ ] event journal writes append-only events
[ ] invalid transitions fail
[ ] failed → completed is blocked
[ ] needs_approval → completed without approval is blocked
[ ] runtime ProofPacket written
```

#### Gate output
```text
PHASE_3_PASS
```

or

```text
PHASE_3_BLOCKED
```

Do not start Phase 4 until Phase 3 passes.

---

### Phase 4 — Control Plane: Registries, Ownership, Health Checks

#### Purpose
Make RIGForge know what exists, where it runs, who owns it, which agent can use it, what healthcheck proves readiness, and what proof path it emits.

Core law:
```text
If it is not registered, it does not exist.
If it has no healthcheck, it is not ready.
If it has no owner, it is not allowed in production.
If it has no proof path, it cannot participate in a RIG workflow.
```

#### Required files
```text
config/service_registry.yaml
config/api_registry.yaml
config/mcp_registry.yaml
config/tool_registry.yaml
config/model_registry.yaml
config/node_registry.yaml
config/app_registry.yaml
config/workflow_registry.yaml
config/proof_registry.yaml
config/approval_registry.yaml

runtime/control_plane/registry_loader.py
runtime/control_plane/registry_validator.py
runtime/control_plane/healthcheck_runner.py
runtime/control_plane/ownership_validator.py
runtime/control_plane/proof_path_validator.py

tests/control_plane/test_registry_required_fields.py
tests/control_plane/test_healthchecks.py
tests/control_plane/test_owner_required.py
tests/control_plane/test_proof_path_required.py
tests/control_plane/test_unregistered_service_blocked.py
```

#### Required command
```bash
rigforge bootstrap --phase control-plane
rigforge status
python scripts/verify_control_plane.py
pytest tests/control_plane
```

#### Exit criteria
```text
[ ] all registries exist
[ ] every service has owner
[ ] every service has healthcheck
[ ] every tool has allowed agents
[ ] every model has allowed use case
[ ] every workflow has proof path
[ ] unregistered service is blocked
[ ] cockpit can read registry status or a cockpit-ready API exists
[ ] registry verification ProofPacket emitted
```

#### Gate output
```text
PHASE_4_PASS
```

or

```text
PHASE_4_BLOCKED
```

Do not start Phase 5 until Phase 4 passes.

---

### Phase 5 — GEV Loop + DoneContract

#### Purpose
Create the controlled two-agent-plus-verifier system.

Use the formal GEV loop:

```text
Spec
↓
DoneContract negotiation
↓
Generator builds
↓
Evaluator critiques
↓
Generator repairs
↓
Verifier checks statelessly
↓
ProofPacket sealed
↓
Approval if needed
```

Core law:
```text
No DoneContract, no code.
No acceptance criteria, no mission.
No required artifacts, no verifier package.
No verifier package, no PASS.
```

#### Required files
```text
contracts/v1/done_contract.py
contracts/v1/verifier_package.py
contracts/v1/required_artifact.py
contracts/v1/acceptance_criterion.py
contracts/v1/forbidden_action.py

runtime/gev/generator_runner.py
runtime/gev/evaluator_runner.py
runtime/gev/verifier_runner.py
runtime/gev/done_contract_negotiator.py
runtime/gev/verifier_package_builder.py

agents/generator/AGENTS.md
agents/evaluator/AGENTS.md
agents/verifier/AGENTS.md
agents/hermes/AGENTS.md

tests/gev/test_done_contract_required.py
tests/gev/test_generator_cannot_build_without_contract.py
tests/gev/test_evaluator_must_challenge.py
tests/gev/test_verifier_cannot_see_chat_history.py
tests/gev/test_missing_proof_blocks_pass.py
```

#### Required commands
```bash
rigforge specify <studio>
rigforge plan <studio>
rigforge build <studio>
rigforge verify <studio>
pytest tests/gev
```

#### Exit criteria
```text
[ ] DoneContract schema exists
[ ] Generator cannot write code before contract is sealed
[ ] Evaluator challenges weak tests, missing artifacts, rollback gaps, proof gaps
[ ] Generator revises once after evaluator challenge
[ ] Verifier package excludes generator/evaluator chat history
[ ] Verifier only uses files, tests, schemas, hashes, and ProofPackets
[ ] Missing ProofPacket returns BLOCKED, not PASS
[ ] GEV smoke mission passes
```

#### Gate output
```text
PHASE_5_PASS
```

or

```text
PHASE_5_BLOCKED
```

Do not start Phase 6 until Phase 5 passes.

---

### Phase 6 — Archon + DeerFlow Long-Horizon Harness

#### Purpose
Add long-running supervised execution only after deterministic runtime, registries, and GEV exist.

DeerFlow does not come first.

Correct order:
```text
Master Control Plan
↓
Environment
↓
Runtime Kernel
↓
Control Plane
↓
DoneContract / GEV
↓
Archon workflow order
↓
DeerFlow long-horizon supervision
↓
Cockpit visibility
```

#### Use DeerFlow when
```text
[ ] the run is multi-hour
[ ] context may rot
[ ] subagents need isolated workspaces
[ ] the mission needs pause/resume
[ ] there are multiple worktrees
[ ] long-term memory or compressed context is needed
```

#### Do not use DeerFlow for
```text
[ ] first repo bootstrap
[ ] raw installation without health checks
[ ] choosing the platform architecture
[ ] bypassing Archon workflow order
[ ] external side effects
[ ] unapproved production changes
```

#### Required files
```text
config/deerflow_rig.yaml
config/archon_workflows.yaml
config/long_horizon_policy.yaml

runtime/deerflow/deerflow_bridge.py
runtime/deerflow/thread_run_mapper.py
runtime/deerflow/workspace_mapper.py
runtime/deerflow/context_compressor.py
runtime/deerflow/pause_resume.py
runtime/deerflow/proof_adapter.py

workflows/rigforge_build.yaml
workflows/rigforge_verify.yaml
workflows/studio_retrofit.yaml
workflows/app_build_mission.yaml

tests/deerflow/test_thread_maps_to_run_id.py
tests/deerflow/test_workspace_maps_to_worktree.py
tests/deerflow/test_deerflow_cannot_bypass_archon.py
tests/deerflow/test_pause_resume.py
tests/deerflow/test_proof_events_emitted.py
```

#### Exit criteria
```text
[ ] DeerFlow thread_id maps to RunEnvelope run_id
[ ] DeerFlow workspace maps to mission worktree
[ ] subagents have isolated contexts
[ ] context compression policy exists
[ ] DeerFlow cannot override Archon workflow order
[ ] DeerFlow emits ProofPacket events
[ ] pause/resume works
[ ] DeerFlow first mission runs without bypassing gates
```

#### Gate output
```text
PHASE_6_PASS
```

or

```text
PHASE_6_BLOCKED
```

Do not start Phase 7 until Phase 6 passes.

---

### Phase 7 — Cockpit + Retrofit First Studio

#### Purpose
Make RIGForge visible, operable, approvable, and useful on one real studio.

This phase turns previous LinkedIn Studio / GTM Studio hardening lessons into reusable platform infrastructure:

```text
health checks
worker schedule connection tests
end-to-end pipeline tests
deterministic ProofPackets
approval gates
regression tests
rollback checks
cockpit visibility
```

#### Required files
```text
apps/cockpit/backend/main.py
apps/cockpit/backend/routes_runs.py
apps/cockpit/backend/routes_approvals.py
apps/cockpit/backend/routes_proof.py
apps/cockpit/backend/routes_health.py

apps/cockpit/frontend/RunsPage.tsx
apps/cockpit/frontend/ApprovalsPage.tsx
apps/cockpit/frontend/ProofPacketsPage.tsx
apps/cockpit/frontend/RegistryStatusPage.tsx
apps/cockpit/frontend/IncidentPage.tsx

apps/cockpit/tests/test_dashboard_loads.py
apps/cockpit/tests/test_cancel_run.py
apps/cockpit/tests/test_approval_queue.py
apps/cockpit/tests/test_proof_viewer.py

runtime/retrofit/studio_inventory.py
runtime/retrofit/retrofit_planner.py
runtime/retrofit/smoke_test_generator.py
runtime/retrofit/proof_packet_adapter.py
runtime/retrofit/hardening_report.py
```

#### Required commands
```bash
rigforge cockpit
rigforge retrofit <studio> --dry-run
rigforge retrofit <studio>
rigforge verify <studio>
```

#### First real studio target
Start with one existing studio, preferably **LinkedIn Studio** or **GTM Studio**.

Do not start with the whole RIG lattice.

#### Required proof for first studio retrofit
```text
[ ] tool registry entries
[ ] worker schedule healthcheck
[ ] pipeline end-to-end test
[ ] deterministic ProofPacket
[ ] approval gate for external posting/scheduling
[ ] cockpit visibility
[ ] regression test for the original failure
[ ] final verifier PASS
```

#### Exit criteria
```text
[ ] active run visible
[ ] current gate visible
[ ] approval queue works
[ ] ProofPacket viewer works
[ ] registry health visible
[ ] Mike can pause/cancel/resume
[ ] studio retrofit dry-run works
[ ] studio smoke test exists
[ ] end-to-end pipeline test passes
[ ] missing ProofPacket rate is 0
[ ] silent failure count is 0
```

#### Gate output
```text
PHASE_7_PASS
```

or

```text
PHASE_7_BLOCKED
```

---

## 5. RIG Lattice Connection

RIGForge must resolve every significant build mission into the RIG lattice:

```text
Level × Diamond × BMS Mode × IQRSQPI Step
```

Permanent geometry:

```text
X-axis: Level / Altitude
  L1 → L7

Y-axis: Triple Diamond
  D1 Physical
  D2 Cognitive
  D3 Nature

Z-axis: BMS Confidence / Build Mode
  A1 Python-only
  A2 Hybrid / bounded LLM
  A3 Agent-bounded workflow
  A4 LLM-agent-free / red-team / high ambiguity

Inside every coordinate:
  Intent → Question → Research → Solution → Quality → Proof → Integrate
```

Promotion ladder:

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
