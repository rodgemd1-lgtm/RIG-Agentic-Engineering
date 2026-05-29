# V10 Readiness Design

## Status

**DESIGN ONLY** — this artifact defines the V10 target, proof paths, and safe next steps. It does **not** claim final PASS.

## 1. V10 Product Promise

RIGForge becomes a product-grade GitHub repo that:

- runs as a deterministic Git-aware engineering agent for issue → proof workflows
- exposes a local CLI that humans and CI can trust first
- publishes a small MCP surface for agent clients once the interface is sealed
- keeps proof, approvals, and weekly improvement loops human-governed

## 2. Future-Back Product Animation

At V10, this repo looks like a deterministic build factory with:

- `rigforge` as the primary local and CI command surface
- contract-gated planner / generator / evaluator / verifier roles
- proof-first run directories under `runs/<run_id>/`
- MCP metadata and transports that expose only approved tools, resources, and prompts
- weekly self-improvement that can propose repairs and tests but cannot self-approve, deploy, or schedule new automation

## 3. User Workflow Animation

1. Human opens an issue or selects an existing backlog item.
2. Human runs `rigforge doctor --json` to confirm deterministic readiness.
3. Human creates or updates a run with `rigforge new`, `rigforge specify`, and `rigforge plan`.
4. Generator builds only after a sealed contract exists.
5. Evaluator critiques tests, proof, and rollback gaps.
6. Verifier checks only files, tests, hashes, and ProofPackets.
7. Human reviews proof and approves any risky action.

## 4. Agent Workflow Animation

| Role | Default lane | Expected routing |
|---|---|---|
| Coordinator | Codex / Hermes | Enforce manifest order, stop unsafe progress |
| Generator | PyCode / PiCode | Write code, tests, and proof drafts only after contract |
| Evaluator | Claude / Gemini / Kimi | Critique missing tests, proof, rollback, and risk |
| Verifier | Codex CLI | Stateless PASS / FAIL / BLOCKED from files and proof only |
| Operator | Mike / human | Approve risky actions, waivers, deployment, schedules |

## 5. CLI Surface

### Deterministic commands available now

- `rigforge doctor`
- `rigforge status`
- `rigforge init`
- `rigforge bootstrap`
- `rigforge new`
- `rigforge interview`
- `rigforge specify`
- `rigforge plan`
- `rigforge build`
- `rigforge verify`
- `rigforge approve`
- `rigforge retrofit`
- `rigforge learn`
- `rigforge promote-skill`

### First deterministic local smoke command

```bash
rigforge doctor --json
```

Why this is first:

- it is non-destructive
- it checks local readiness before agentic work starts
- it gives CI and humans the same machine-readable baseline

## 6. MCP Surface

Runtime MCP implementation is intentionally deferred until the repo has a sealed contract for transport, auth, regression tests, and proof. The current `config/mcp_registry.yaml` is readiness metadata, not a production MCP server.

### Planned MCP tool surface

- `rig.doctor` → deterministic readiness snapshot
- `rig.status` → current runs, blocked runs, approval queue
- `rig.new_run` → create a governed run envelope and contract stub
- `rig.verify_run` → stateless verifier entrypoint
- `rig.list_proof_paths` → enumerate approved proof locations

### Planned MCP resource surface

- run envelope JSON
- DoneContract YAML
- ProofPacket JSON
- blocker ledger
- build card manifest
- registry snapshots

### Planned MCP prompt surface

- issue-to-contract planning
- verifier evidence review
- weekly improvement review

## 7. Data Animation

- GitHub issue, run files, and proof stay repo-local first.
- QNAP / Obsidian can be consumers of exported proof, never secret sources injected into commits.
- Telemetry stays approval-gated and must not include secrets, cookies, or browser session state.
- ProofPacket paths remain the system of record for completed work.

## 8. Deterministic Layer Animation

The deterministic layer stays A1-first:

- doctor, status, registries, contracts, proof paths, and tests run locally
- model calls are optional and never the only source of truth
- unknown intent escalates instead of guessing

## 9. Design-System Animation

Rig Design Studio standards apply at the repo boundary through:

- one CLI vocabulary (`rigforge`) for humans, CI, and agents
- cockpit visibility as a downstream consumer of run and proof state
- no UI-only state that bypasses run files, registries, or approvals

## 10. Quality Animation

### Model routing expectations

- **A1:** `doctor`, registries, contracts, proof validation, tests — no model in the decision path
- **A2:** bounded critique/summarization with registered models at `temperature=0`
- **A3:** governed generator/evaluator/verifier workflow with explicit stop conditions
- **A4:** red-team or high-ambiguity work only with human approval

### Quality gates

- no DoneContract, no code
- no ProofPacket, no PASS
- verifier cannot see generator or evaluator chat history
- evaluator must challenge weak tests and missing rollback paths
- external side effects require human approval

## 11. Weekly Improvement Animation

Weekly improvement should:

1. run deterministic readiness and status checks
2. summarize blocked runs, flaky tests, missing proof, and repeated incidents
3. propose doc, test, contract, and skill improvements as PR-safe changes
4. require human approval before any merge, publish, deploy, secret use, or schedule change

### Must never run without human approval

- deployment or publication
- new scheduled automation
- secret creation or rotation
- approval packet generation on behalf of a human
- external messaging or ticket changes outside the repo

## 12. Blockers and Gaps

Current blockers to V10 productization:

- no sealed MCP transport/auth contract yet
- no deterministic MCP tool/resource/prompt tests yet
- no weekly-improvement workflow doc or proof artifact yet
- no explicit GitHub Actions proof workflow for weekly readiness summaries yet
- GEV / DoneContract phase is still the active build gap

Missing assets to add next:

- MCP interface contract and regression tests
- weekly improvement workflow spec and proof path
- docs tying CLI smoke, verifier package, and GitHub workflow usage together
- tests for the planned MCP and weekly-improvement surfaces

## 13. Proof Paths and Test Commands

### Proof paths

- `docs/V10_READINESS_DESIGN.md`
- `proof/v10/v10_readiness_design.json`
- `config/proof_registry.yaml`
- `tests/test_v10_readiness_design.py`

### Test commands

- `python3 -m pytest tests/test_v10_readiness_design.py -q`
- `python3 -m pytest tests/test_doctor.py -q`
- `rigforge doctor --json`
