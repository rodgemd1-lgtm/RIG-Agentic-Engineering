# Build Card 7 — Cockpit, Proof Packets, Retrofit Protocol, First Real Studio

**Status:** ⚪ Pending  
**Phase:** 7 of 7  
**Owner:** PyCode / Generator  
**Critique:** Claude Code / Evaluator  
**Verifier:** Codex CLI (stateless)  
**Gate:** G06 — Cockpit Ready + First Studio Retrofit Complete  
**Unblocked by:** Phase 6 ProofPacket sealed

## Goal

Make the system visible, operable, and useful on a real app/studio. RIGForge becomes something you can actually run without staring at terminal logs.

## Required Cards

1. **BUILD CARD** — RIG Cockpit and Mission Control for Agentic Engineering Runs
2. **BUILD CARD** — RIG Studio Retrofit Protocol for Existing Studios
3. **BUILD CARD** — RIG Agentic Engineering Failure Runbook and Incident Response
4. **RIG Verification OS** — Cockpit UI, Master Makefile, and CI Pipeline
5. **LinkedIn Studio / GTM Studio** hardening cards (retrofit examples)

## What the Agent Builds

```
apps/cockpit/
├── backend/
│   ├── main.py               # FastAPI / equivalent
│   ├── routes_runs.py          # Active runs endpoint
│   ├── routes_approvals.py     # Approval queue endpoint
│   ├── routes_proof.py         # ProofPacket viewer endpoint
│   └── routes_health.py        # Health check endpoint
├── frontend/
│   ├── RunsPage.tsx            # Active runs list
│   ├── ApprovalsPage.tsx       # Approval queue
│   ├── ProofPacketsPage.tsx    # ProofPacket viewer
│   ├── RegistryStatusPage.tsx  # Registry health
│   └── IncidentPage.tsx        # Incident log
└── tests/
    ├── __init__.py
    ├── test_dashboard_loads.py
    ├── test_cancel_run.py
    ├── test_approval_queue.py
    └── test_proof_viewer.py

runtime/retrofit/
├── studio_inventory.py         # Studio discovery
├── retrofit_planner.py         # Retrofit plan generator
├── smoke_test_generator.py     # Smoke test creation
├── proof_packet_adapter.py   # ProofPacket integration
└── hardening_report.py        # Retrofit report generator
```

## Core Law

```
No existing studio is grandfathered in.
Every studio must use the same proof-backed process.
If a studio can bypass its workflow, it is not production-ready.
```

## Required Commands

```bash
rigforge cockpit              # Start cockpit UI
rigforge retrofit <studio> --dry-run   # Dry-run retrofit
rigforge retrofit <studio>    # Execute retrofit
rigforge verify <studio>        # Verify retrofitted studio
```

## Cockpit Features

### Dashboard
- Active runs list with status
- Current gate for each run
- Progress indicator
- Agent assignments

### Approvals
- Queue of pending approvals
- Approve / reject / request more info
- Audit trail
- Required fields: `--by`, `--signature`, `--run-id`

### Proof Packets
- All ProofPackets for a run
- Filter by phase, status, agent
- Evidence viewer
- Hash verification

### Registry Health
- Service status (registered / unregistered)
- Health check results
- Missing healthchecks highlighted
- Unregistered services flagged

### Incidents
- Incident log
- Linked regression tests
- Resolution status
- Rollback paths

## Retrofit Protocol

### Steps
1. **Inventory** — Discover studio components
2. **Assess** — Identify missing healthchecks, proof paths, registries
3. **Plan** — Generate retrofit plan with milestones
4. **Dry-run** — `rigforge retrofit <studio> --dry-run`
5. **Execute** — `rigforge retrofit <studio>`
6. **Verify** — `rigforge verify <studio>`
7. **Seal** — ProofPacket + Cockpit visibility

### Required Hardening
```text
[ ] Tool registry entries
[ ] Worker schedule healthcheck
[ ] Pipeline e2e test
[ ] Deterministic ProofPacket
[ ] Approval gate for external posting/scheduling
[ ] Cockpit visibility
[ ] Regression test for the original failure
[ ] Final verifier PASS
```

## First Real Mission

Best candidate: **LinkedIn Studio or GTM Studio**

Why: wounds, hardening fixes, health checks, worker schedule tests, e2e tests, and proof packet patterns already exist.

The first mission:
```bash
rigforge retrofit linkedin-studio --dry-run
rigforge retrofit linkedin-studio
rigforge verify linkedin-studio
```

## Exit Criteria

```text
[ ] Cockpit loads and shows active runs
[ ] Current gate visible for each run
[ ] Approval queue works
[ ] ProofPacket viewer works
[ ] Registry health visible
[ ] Mike can pause/cancel/resume
[ ] Studio retrofit dry-run works
[ ] Studio smoke test exists
[ ] End-to-end pipeline test passes
[ ] Missing ProofPacket rate is 0
[ ] Silent failure count is 0
[ ] RIGForge is production-ready
```

## Proof Required

```json
{
  "phase": "cockpit",
  "run_id": "cockpit_retrofit_YYYYMMDD_HHMMSS",
  "status": "pass",
  "evidence": {
    "cockpit_loads": true,
    "active_runs_visible": true,
    "approval_queue_works": true,
    "proof_viewer_works": true,
    "registry_health_visible": true,
    "pause_cancel_resume": true,
    "retrofit_dry_run_works": true,
    "smoke_test_exists": true,
    "e2e_pipeline_passed": true,
    "missing_proof_rate": 0,
    "silent_failure_count": 0,
    "first_studio_retrofit": "linkedin-studio|gtm-studio",
    "verifier_passed": true
  }
}
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

## Why This Matters

The Retrofit Protocol says no existing studio is grandfathered in; every studio must use the same proof-backed process. If a studio can bypass its workflow, it is not production-ready.

That means the hardening added to GTM Studio and LinkedIn Studio becomes reusable infrastructure:
- health checks
- worker schedule connection tests
- end-to-end pipeline tests
- deterministic ProofPackets
- approval gates
- regression tests
- rollback checks
- cockpit visibility

In the old mode, these were added after the system hurt you.

In RIGForge, these are part of the default build contract.

## System Complete

When this card is verified, RIGForge Agentic Engineering Platform is production-ready.
