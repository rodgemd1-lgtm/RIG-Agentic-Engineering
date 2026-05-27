# RIG Agentic Engineering

**Deterministic CLI + DeerFlow 2.0 Integration for RIG App Studio.**

> The CLI is the deterministic backend.
> The App Studio is the visual cockpit over the CLI.
> Agents call the CLI. The UI calls the CLI/API.

## Architecture

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

### Core Law

```
DeerFlow supervises long runs.
Archon owns workflow order.
PyCode builds.
Hermes governs.
Codex verifies.
```

## Commands

```bash
rigforge doctor          # Check runtime → READY / DEGRADED / BLOCKED
rigforge init            # Initialize RIG runtime in a repo
rigforge bootstrap       # Run 10-phase master control plan
rigforge new <studio>    # Create a build mission
rigforge retrofit <s>    # Retrofit a studio with RIG capabilities
rigforge build <studio>  # GEV build via Archon or DeerFlow
rigforge verify <studio> # Verification stack
rigforge approve <run>   # Route approval (no auto-approve)
rigforge cockpit         # Open App Studio cockpit
rigforge learn <incident># Turn failure into regression test
rigforge promote-skill   # Promote pattern → deterministic skill
rigforge status          # Platform status
```

## DeerFlow Integration

### Thread Mapping
Every DeerFlow thread maps 1:1 to a RIG RunEnvelope.
No DeerFlow thread without RunEnvelope. No exception.

### Workspace Mapping
| DeerFlow Path | RIG Path |
|---|---|
| `/mnt/user-data/uploads` | `runs/<run_id>/inputs/` |
| `/mnt/user-data/workspace` | `worktrees/<run_id>//` |
| `/mnt/user-data/outputs` | `runs/<run_id>/outputs/` |

### Boundaries
- DeerFlow **cannot** modify Archon workflows
- DeerFlow **cannot** bypass RIG gates
- DeerFlow **cannot** perform external side effects
- Every sub-agent result → ProofPacket event
- All outputs hashed into ProofPacket evidence

## Install

```bash
cd rig-runtime
uv pip install -e .
rigforge --help
```

## Config

- `config/deerflow_rig.yaml` — DeerFlow permissions, limits, tracing
- See `integrations/deerflow/` for adapter implementations

## Tests

```bash
python -m pytest tests/ -v
# 83 tests, all passing
```

## License

MIT
