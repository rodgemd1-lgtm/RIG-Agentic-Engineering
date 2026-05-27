# Build Card 4 — Control Plane: Registries, Ownership, Health Checks

**Status:** ⚪ Pending  
**Phase:** 4 of 7  
**Owner:** PyCode / Generator  
**Critique:** Claude Code / Evaluator  
**Verifier:** Codex CLI (stateless)  
**Gate:** G03 — Control Plane Ready
**Unblocked by:** Phase 3 ProofPacket sealed

## Goal

Make the platform know what exists, where it runs, who owns it, and how to prove it is healthy. Infrastructure hardening becomes built-in instead of bolted on later.

## Required Cards

1. **BUILD CARD** — RIG Agentic Engineering Control Plane
2. **RIG Node Factory Control Plane** — Master Install, Registry, Cockpit, Proof, Rollback
3. **RIG Verification OS** — Cockpit UI, Master Makefile, and CI Pipeline (reference)

## What the Agent Builds

```
config/
├── service_registry.yaml     # Service definitions
├── api_registry.yaml         # API surface registry
├── mcp_registry.yaml         # MCP server registry
├── tool_registry.yaml        # Tool contract registry
├── model_registry.yaml       # LLM model registry
├── node_registry.yaml        # Node/compute registry
├── app_registry.yaml         # Application registry
├── workflow_registry.yaml    # Workflow registry
├── proof_registry.yaml       # Proof path registry
└── approval_registry.yaml    # Approval flow registry

runtime/control_plane/
├── registry_loader.py        # Load and validate registries
├── registry_validator.py     # Validate registry entries
├── healthcheck_runner.py     # Run health checks
├── ownership_validator.py    # Validate owner fields
└── proof_path_validator.py   # Validate proof paths

tests/control_plane/
├── __init__.py
├── test_registry_required_fields.py
├── test_healthchecks.py
├── test_owner_required.py
├── test_proof_path_required.py
└── test_unregistered_service_blocked.py
```

## Core Law

```
If it is not registered, it does not exist.
If it has no healthcheck, it is not ready.
If it has no owner, it is not allowed in production.
If it has no proof path, it cannot participate in a RIG workflow.
```

## Required Commands

```bash
rigforge bootstrap --phase control-plane
rigforge status              # Show registry health
python scripts/verify_control_plane.py
pytest tests/control_plane/ -v
```

## Registry Schemas

### `config/service_registry.yaml`
```yaml
services:
  - id: "linkedin-scheduler"
    name: "LinkedIn Studio Scheduler"
    owner: "mike"
    studio: "linkedin"
    healthcheck:
      type: "http"
      endpoint: "http://localhost:8080/health"
      interval: "60s"
    proof_path: "proof/linkedin-scheduler/"
    allowed_agents: ["pycode", "claude"]
    external: true
```

### `config/tool_registry.yaml`
```yaml
tools:
  - id: "web_search"
    name: "Web Search"
    owner: "mike"
    allowed_agents: ["hermes", "codex"]
    requires_approval: true
    proof_required: true
```

### `config/model_registry.yaml`
```yaml
models:
  - id: "gpt-4o"
    name: "GPT-4o"
    owner: "mike"
    allowed_use_cases: ["evaluation", "generation", "verification"]
    temperature_default: 0.0
    max_tokens: 4096
```

## Exit Criteria

```text
[ ] All 10 registries exist
[ ] Every service has owner field
[ ] Every service has healthcheck
[ ] Every tool has allowed_agents list
[ ] Every model has allowed_use_case
[ ] Every workflow has proof_path
[ ] Unregistered service is blocked
[ ] Cockpit can read registry status
[ ] Registry verification ProofPacket emitted
[ ] Build Card 5 is unblocked
```

## Proof Required

```json
{
  "phase": "control-plane",
  "run_id": "control_plane_YYYYMMDD_HHMMSS",
  "status": "pass",
  "evidence": {
    "registry_count": 10,
    "services_with_owner": "100%",
    "services_with_healthcheck": "100%",
    "tools_with_allowed_agents": "100%",
    "models_with_use_cases": "100%",
    "unregistered_blocked": true,
    "test_count": "≥5",
    "test_status": "pass"
  }
}
```

## Next Phase

Phase 5 is unblocked when all registries pass validation.
