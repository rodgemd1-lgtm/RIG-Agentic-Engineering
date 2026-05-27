# Build Card 6 — Archon Workflow + DeerFlow Long-Horizon Harness

**Status:** ⚪ Pending  
**Phase:** 6 of 7  
**Owner:** PyCode / Generator  
**Critique:** Claude Code / Evaluator  
**Verifier:** Codex CLI (stateless)  
**Gate:** G05 — Long-Horizon Harness Ready
**Unblocked by:** Phase 5 ProofPacket sealed

## Goal

Add long-running agent execution only after deterministic runtime, registries, and GEV exist. DeerFlow supervises multi-hour tasks while Archon owns deterministic workflow order and PyCode executes build steps.

## DeerFlow is for

```text
[ ] the run is multi-hour
[ ] context may rot
[ ] subagents need isolated workspaces
[ ] the mission needs pause/resume
[ ] there are multiple worktrees
[ ] long-term memory or compressed context is needed
```

## DeerFlow is NOT for

```text
[ ] first repo bootstrap
[ ] raw installation without health checks
[ ] choosing the platform architecture
[ ] bypassing Archon workflow order
[ ] external side effects
[ ] unapproved production changes
```

## Required Cards

1. **BUILD CARD** — RIG DeerFlow 2.0 Long-Horizon Harness Integration
2. **MASTER CONTROL PLAN**
3. **Runtime Kernel** (Phase 3)
4. **Control Plane** (Phase 4)
5. **Role-Specific AGENTS.md** (Phase 5)

## What the Agent Builds

```
config/
├── deerflow_rig.yaml         # DeerFlow permissions, limits, tracing
├── archon_workflows.yaml     # Archon workflow definitions
└── long_horizon_policy.yaml  # When to use DeerFlow vs local

runtime/deerflow/
├── deerflow_bridge.py        # Archon → DeerFlow invocation
├── thread_run_mapper.py      # RunEnvelope ↔ DeerFlow thread mapping
├── workspace_mapper.py     # Workspace path mapping
├── context_compressor.py     # Context compression policy
├── pause_resume.py           # Pause/resume handlers
└── proof_adapter.py          # ProofPacket emission

workflows/
├── rigforge_build.yaml       # Build workflow
├── rigforge_verify.yaml      # Verify workflow
├── studio_retrofit.yaml      # Retrofit workflow
└── app_build_mission.yaml    # App build workflow

scripts/
├── start_deerflow_run.py     # Start DeerFlow run with RunEnvelope
├── verify_deerflow_mapping.py  # Verify thread/workspace mapping
└── verify_deerflow_proof.py   # Verify ProofPacket emission

tests/deerflow/
├── __init__.py
├── test_thread_maps_to_run_id.py
├── test_workspace_maps_to_worktree.py
├── test_deerflow_cannot_bypass_archon.py
├── test_pause_resume.py
└── test_proof_events_emitted.py
```

## Core Law

```
DeerFlow supervises long runs.
Archon owns workflow order.
PyCode builds.
Hermes governs.
Codex verifies.
```

## Required Commands

```bash
rigforge bootstrap --phase deerflow
python scripts/start_deerflow_run.py --run-id <id>
python scripts/verify_deerflow_mapping.py --run-id <id>
python scripts/verify_deerflow_proof.py --run-id <id>
```

## DeerFlow Boundaries

### Thread Mapping
```
Every DeerFlow thread maps 1:1 to a RIG RunEnvelope.
No DeerFlow thread without RunEnvelope.
No RunEnvelope long-horizon mission without DeerFlow thread mapping.
```

### Workspace Mapping
| DeerFlow Path | RIG Path |
|---|---|
| `/mnt/user-data/uploads` | `runs/<run_id>/inputs/` |
| `/mnt/user-data/workspace` | `worktrees/<run_id>//` |
| `/mnt/user-data/outputs` | `runs/<run_id>/outputs/` |

### Permissions
```yaml
deerflow:
  forbidden:
    modify_workflow_yaml: true      # DeerFlow cannot edit Archon workflows
    bypass_rig_gates: true            # DeerFlow cannot skip RIG gates
    perform_external_side_effects: true  # DeerFlow cannot do external sends
    modify_audit_logs: true           # DeerFlow cannot alter logs
```

### Limits
```yaml
deerflow:
  max_runtime_minutes: 240          # 4 hours max
  max_cost_per_mission_usd: 20.0    # $20 per mission max
  max_subagents: 6                  # 6 subagents max
  max_retries_per_subagent: 3       # 3 retries max
  log_every_minutes: 5              # Proof event every 5 min
```

## Exit Criteria

```text
[ ] DeerFlow thread_id maps to RunEnvelope run_id
[ ] DeerFlow workspace maps to mission worktree
[ ] Subagents have isolated contexts
[ ] Context compression policy exists
[ ] DeerFlow cannot override Archon workflow order
[ ] DeerFlow emits ProofPacket events
[ ] Pause/resume works
[ ] DeerFlow first mission runs without bypassing gates
[ ] Build Card 7 is unblocked
```

## Proof Required

```json
{
  "phase": "deerflow",
  "run_id": "deerflow_harness_YYYYMMDD_HHMMSS",
  "status": "pass",
  "evidence": {
    "thread_mapping_works": true,
    "workspace_mapping_works": true,
    "isolated_contexts": true,
    "context_compression": true,
    "archon_order_preserved": true,
    "proof_events_emitted": true,
    "pause_resume": true,
    "first_mission_passed": true,
    "test_count": "≥5",
    "test_status": "pass"
  }
}
```

## Important Distinction

DeerFlow does not come first. The order is:

```
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

## Next Phase

Phase 7 is unblocked when DeerFlow first mission passes all gates.
