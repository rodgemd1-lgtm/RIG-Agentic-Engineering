# Phase 2 Environment Report

## Status
**DEGRADED** (acceptable — optional tools/services missing, core required tools all READY)

## Core Required Tools

| Tool | Status | Version | Path |
|---|---|---|---|
| Python | ✅ READY | 3.14.5 | /opt/homebrew/bin/python3 |
| Node | ✅ READY | 26.0.0 | /opt/homebrew/bin/node |
| Git | ✅ READY | — | /opt/homebrew/bin/git |
| uv | ✅ READY | 0.11.7 | /opt/homebrew/bin/uv |

## Optional Tools

| Tool | Status | Detail |
|---|---|---|
| Playwright | ✅ READY | found |
| Promptfoo | ✅ READY | found |
| DeepEval | ⚪ NOT_INSTALLED | pip install deepeval |
| Spec Kit | ⚪ NOT_INSTALLED | Install specify |

## Services

| Service | Status | Detail |
|---|---|---|
| Docker | ✅ READY | found (daemon not running) |
| Postgres | ✅ READY | localhost:5432 reachable |
| Neo4j | ⚪ NOT_CONFIGURED | localhost:7687 unreachable |
| Qdrant | ⚪ NOT_CONFIGURED | Install qdrant |
| Langfuse | ✅ READY | localhost:3000 reachable |
| AionUI | ⚪ NOT_INSTALLED | Install AionUI |

## Version Matrix

| Component | Expected | Actual | Status |
|---|---|---|---|
| Python | 3.14.5 | 3.14.5 | ✅ READY |
| Node | 22.x | 26.0.0 | ✅ READY |
| uv | 0.11.7 | 0.11.7 | ✅ READY |
| pytest | 9.0.3 | 9.0.3 | ✅ READY |
| pydantic | 2.x | 2.12.5 | ✅ READY |
| typer | 0.15.x | 0.25.1 | ✅ READY |
| httpx | 0.28.x | 0.28.1 | ✅ READY |
| Playwright | 1.49 | 1.58.0 | ⚪ MISMATCH (acceptable) |
| ruff | 0.15.10 | installed | ⚪ INSTALLED |
| rich | 14.x | not importable | ⚪ NOT_INSTALLED |

## Test Results

- Total tests: **129**
- Passed: **129**
- Failed: **0**
- New environment tests: **46** (added in Phase 2)

## Proof Artifacts

```
proof/environment/
├── doctor_report.json              ← Environment tool check results
├── version_report.json             ← Version matrix check
├── services_report.json            ← Service connectivity check
└── environment_proofpacket.json    ← Combined ProofPacket
```

## Blockers

None. All required tools are READY.

## DEGRADED Items (Optional — Not Blocking)

- Docker daemon not running (needed only for containerized services)
- DeepEval not installed (optional eval framework)
- Spec Kit not installed (optional spec phase tool)
- Qdrant not installed (optional vector DB)
- Neo4j not running (optional graph DB)
- AionUI not installed (optional frontend)
- Playwright version mismatch 1.49 → 1.58.0 (acceptable)

## Next Safe Action

**Phase 3: Runtime Kernel** — All required tools verified. Proceed to RunEnvelope, State Machine, and Event Bus implementation.

```bash
rigforge bootstrap --phase runtime-kernel
```
