# Build Card 2 - Environment Bootstrap / Doctor / Install Proof

**Status:** 🟢 Verified (DEGRADED — optional tools missing, core ready)
**Phase:** 2 of 7
**Owner:** PyCode / Generator
**Critique:** Claude Code / Evaluator
**Verifier:** Codex CLI (stateless)
**Gate:** G01 — Environment Ready
**Unblocked by:** Phase 1 ProofPacket sealed

## Goal

Prove the machine can run the stack before any real agentic build starts. Verify the boring stuff first: Python, Node, Docker, Git, uv, Spec Kit, Archon, DeerFlow prerequisites, LiteLLM, Promptfoo, DeepEval, Playwright, Postgres, Qdrant, Neo4j, Langfuse, and AionUI.

## Required Cards

1. **BUILD CARD** - RIG Environment Bootstrap for DeerFlow, PyCode, Archon, Spec Kit, and Verification Stack
2. **RIG Agentic Engineering Control Plane** (reference only)
3. **RIG Verification OS** cards (reference for testing expectations)

## What the Agent Builds

```
scripts/
├── doctor.py                 # Runtime health check
├── verify_environment.py     # Full environment probe
├── verify_versions.py        # Version matrix check
├── verify_services.py        # Service connectivity check
└── write_environment_proof.py  # ProofPacket writer

config/
├── environment.yaml          # Required tools + versions
├── runtime_versions.yaml     # Exact version matrix
└── local_paths.yaml          # Local installation paths

proof/
└── environment/
    ├── doctor_report.json
    ├── version_report.json
    └── environment_proofpacket.json
```

## Required Commands

```bash
rigforge doctor              # Health check → READY / DEGRADED / BLOCKED
rigforge bootstrap --phase environment
python scripts/verify_environment.py
```

## Files to Create

### `scripts/doctor.py`
- Checks Python version (≥3.10)
- Checks Node version (≥18)
- Checks Docker availability
- Checks Git availability
- Checks uv availability
- Checks test runner (pytest)
- Checks Playwright
- Checks Promptfoo or eval runner
- Checks database connectivity (Postgres, Qdrant, Neo4j)
- Checks LiteLLM proxy
- Returns: READY / DEGRADED / BLOCKED with exact blockers

### `config/environment.yaml`
```yaml
required:
  python: "3.10+"
  node: "18+"
  docker: true
  git: true
  uv: true

optional:
  playwright: true
  promptfoo: true
  deepeval: true

services:
  postgres:
    host: localhost
    port: 5432
    required: false
  qdrant:
    host: localhost
    port: 6333
    required: false
  neo4j:
    host: localhost
    port: 7687
    required: false
  langfuse:
    host: localhost
    port: 3000
    required: false
```

### `config/runtime_versions.yaml`
```yaml
python: "3.14.5"
node: "22.x"
uv: "0.11.7"
playwright: "1.49"
```

## Exit Criteria

```text
[ ] Python version verified (≥3.10)
[ ] Node version verified (≥18)
[ ] Docker verified (running or BLOCKED)
[ ] Git verified
[ ] uv verified
[ ] Test runner verified (pytest works)
[ ] Playwright verified (or marked optional BLOCKED)
[ ] Promptfoo or eval runner verified (or marked optional BLOCKED)
[ ] Database connectivity verified or marked BLOCKED
[ ] Environment manifest exists
[ ] Environment ProofPacket sealed
[ ] Build Card 3 is unblocked
```

## Rule

No install proof, no runtime.
No verification proof, no build.
No environment manifest, no agent execution.

## Proof Required

```json
{
  "phase": "environment",
  "run_id": "env_bootstrap_YYYYMMDD_HHMMSS",
  "status": "pass|degraded|blocked",
  "evidence": {
    "python": "3.14.5",
    "node": "22.x",
    "docker": true,
    "git": true,
    "uv": true,
    "pytest": true,
    "playwright": "optional|blocked",
    "services": {
      "postgres": "connected|blocked",
      "qdrant": "connected|blocked",
      "neo4j": "connected|blocked"
    },
    "blockers": [],
    "manifest_path": "config/environment.yaml"
  }
}
```

## Blocker Path

If environment is BLOCKED:
- Blocker must specify exact missing component
- Next safe action must be: install X or skip phase with waiver
- Build Card 3 remains blocked until blocker resolved

## Degraded Mode

If environment is DEGRADED (optional services missing):
- System runs with reduced capability
- Missing services noted in ProofPacket
- Build Card 3 proceeds with degraded flag

## Next Phase

Phase 3 is unblocked when environment is READY or DEGRADED with known waivers.
