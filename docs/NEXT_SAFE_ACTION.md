# Next Safe Action

## Current Phase
Phase 3: Runtime Kernel — **PASS**

## Next Phase
Phase 4: Control Plane — Registries, Ownership, Health Checks

## What to Do

1. Create `config/service_registry.yaml` with service definitions
2. Create `config/tool_registry.yaml` with tool contracts
3. Create `config/model_registry.yaml` with allowed LLMs
4. Create `runtime/control_plane/registry_loader.py` and `registry_validator.py`
5. Verify every entry has owner, healthcheck, proof path
6. Create tests in `tests/control_plane/`
7. Seal Control Plane ProofPacket

## What NOT to Do

- Do NOT build GEV Loop yet
- Do NOT integrate DeerFlow yet
- Do NOT create Cockpit yet

## Required Proof

```text
proof/control_plane/registry_verified.json
proof/control_plane/healthchecks_passed.json
proof/control_plane/control_plane_proofpacket.json
docs/PHASE_4_CONTROL_PLANE_REPORT.md
```

## Gate Criteria

Phase 4 passes when:
- All registries exist and validate
- Every service has owner, healthcheck, proof path
- Unregistered service blocked
- Control Plane tests pass
