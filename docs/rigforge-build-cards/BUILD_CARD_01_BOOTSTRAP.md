# Build Card 1 — RIGForge Repo Bootstrap + Doctrine Pack

**Status:** 🔵 Active  
**Phase:** 1 of 7  
**Owner:** PyCode / Generator  
**Critique:** Claude Code / Evaluator  
**Verifier:** Codex CLI (stateless)  
**Gate:** G00 — Repo Skeleton

## Goal

Create the repo skeleton, agent doctrine, and deterministic command surface. This is where you give Codex/PyCode the rules of the game before it writes code.

## Required Cards

1. **MASTER CONTROL PLAN** — RIG Agentic Engineering Platform Full How-To
2. **BUILD CARD** — rigforge CLI: One Command Surface for RIG Agentic Engineering
3. **RIG Master Agent Doctrine** — Hermes, OpenClaw/Jake, Pi Coding/PyCode, Claude Code, and Codex
4. **BUILD CARD** — RIG Role-Specific AGENTS.md Files for Generator, Evaluator, Verifier, and Hermes

## What the Agent Builds

```
rigforge/
├── AGENTS.md                    # Global agent operating model
├── CODEX.md                     # Codex coordinator + verifier rules
├── PYCODE.md                    # PyCode generator rules
├── EVALUATOR.md                 # Evaluator critique rules
├── VERIFIER.md                  # Verifier stateless judgment rules
├── HERMES.md                    # Hermes governance rules
├── RIG_DOCTRINE.md             # Core deterministic doctrine
├── BUILD_CARD_MANIFEST.md      # Build order + status
├── pyproject.toml              # Package definition
├── Makefile                    # Standard targets
├── README.md                   # System overview
├── .gitignore                  # Standard ignores
├── config/                     # Configuration files
│   ├── environment.yaml
│   ├── runtime_versions.yaml
│   └── local_paths.yaml
├── contracts/                  # Contract schemas (v1 frozen, v2 active)
│   ├── v1/
│   │   ├── __init__.py
│   │   ├── run_envelope.py     # [v2] if this is the active version
│   │   ├── tool_registry.py    # Tool contract registry pattern
│   │   └── ...
│   └── v2/
│       └── ...
├── workflows/                  # Archon workflow definitions
│   └── ...
├── agents/                     # Agent-specific directories
│   ├── generator/
│   │   └── AGENTS.md
│   ├── evaluator/
│   │   └── AGENTS.md
│   ├── verifier/
│   │   └── AGENTS.md
│   └── hermes/
│       └── AGENTS.md
├── studios/                    # Studio definitions
│   └── ...
├── scripts/                    # Operational scripts
│   ├── doctor.py
│   ├── verify_environment.py
│   ├── verify_versions.py
│   ├── verify_services.py
│   └── write_environment_proof.py
├── tests/                      # Test suite
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_doctor.py
│   ├── test_init.py
│   ├── test_retrofit.py
│   ├── test_build.py
│   ├── test_verify.py
│   ├── test_approve.py
│   ├── test_learn.py
│   ├── test_promote_skill.py
│   └── deerflow/
│       ├── __init__.py
│       ├── test_thread_mapping.py
│       ├── test_workspace_mapping.py
│       ├── test_archon_boundary.py
│       └── test_proof_adapter.py
├── evals/                      # Evaluation benchmarks
│   └── ...
├── proof/                      # ProofPacket storage
│   └── bootstrap/
│       └── bootstrap_repo.json
└── docs/
    └── rigforge-build-cards/   # Build card directory
        ├── BUILD_CARD_MANIFEST.md
        ├── BUILD_CARD_01_BOOTSTRAP.md
        ├── BUILD_CARD_02_ENVIRONMENT.md
        ├── BUILD_CARD_03_RUNTIME.md
        ├── BUILD_CARD_04_CONTROL_PLANE.md
        ├── BUILD_CARD_05_GEV.md
        ├── BUILD_CARD_06_DEERFLOW.md
        └── BUILD_CARD_07_COCKPIT.md
```

## Required Commands

```bash
rigforge doctor          # Runtime health check
rigforge init --repo .   # Initialize RIG runtime
rigforge status          # Platform status
```

## Files to Create

### `pyproject.toml`
- Typer CLI entry point: `rigforge = rigforge.cli:app`
- Dependencies: `typer`, `pydantic`, `rich`, `pyyaml`, `httpx`
- Test dependencies: `pytest`, `pytest-cov`

### `Makefile`
- `make install` — uv pip install -e .
- `make test` — pytest tests/ -v
- `make lint` — ruff check
- `make format` — ruff format
- `make doctor` — rigforge doctor
- `make build` — uv build
- `make clean` — remove build artifacts

### `AGENTS.md`
Global operating model. Must include:
- RIG lattice geometry (L1-L7, D1-D3, A1-A4)
- Agent role definitions
- Communication rules (ProofPacket, RunEnvelope)
- Forbidden patterns (no chat in verifier, no auto-approve)
- Failure routing (A3→A2→A1→UNKNOWN)

### `RIG_DOCTRINE.md`
Core doctrine. Must include:
- Local-first, deterministic before agentic
- A1 first, Gate 00-12 for apps/releases
- Research before synthesis
- Escalate instead of failing
- ProofPacket or it did not happen
- temperature=0 unless contract explicitly overrides
- IntentKey.UNKNOWN escalation

### `BUILD_CARD_MANIFEST.md`
Build order, status tracker, agent assignments.

## Exit Criteria

```text
[✓] Repo scaffold exists
[✓] AGENTS.md files exist (global + per-agent)
[✓] RIG_DOCTRINE.md exists
[✓] BUILD_CARD_MANIFEST.md exists
[✓] pyproject.toml defines rigforge CLI
[✓] Makefile has install/test/lint/doctor targets
[✓] rigforge CLI stub runs (doctor, init, status)
[✓] make test runs (≥1 test passes)
[✓] proof/bootstrap_repo.json exists
[✓] Build Card 2 is unblocked
```

## Proof Required

```json
{
  "phase": "bootstrap",
  "run_id": "bootstrap_repo_YYYYMMDD_HHMMSS",
  "status": "pass",
  "evidence": {
    "files_created": ["AGENTS.md", "RIG_DOCTRINE.md", "BUILD_CARD_MANIFEST.md", "pyproject.toml", "Makefile"],
    "cli_commands": ["rigforge doctor", "rigforge init", "rigforge status"],
    "test_count": "≥1",
    "test_status": "pass",
    "doctrine_loaded": true,
    "manifest_valid": true
  }
}
```

## Blocker Path

If this phase fails:
- No build cards can proceed
- System is not initialized
- All agents must use manual mode only

## Next Phase

Phase 2 is unblocked when this ProofPacket is sealed.
