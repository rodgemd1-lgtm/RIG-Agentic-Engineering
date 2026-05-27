# Next Safe Action

## Current Phase
Phase 1: Repo Bootstrap + Doctrine Pack — **PASS**

## Next Phase
Phase 2: Environment Bootstrap / Doctor / Install Proof

## What to Do

1. Run `rigforge doctor` to establish baseline environment status
2. Create `config/environment.yaml` with required tools + versions
3. Create `scripts/verify_environment.py` probe
4. Verify all required tools: Python, Node, Docker, Git, uv, pytest
5. Mark optional services as READY/DEGRADED/BLOCKED with exact status
6. Seal environment ProofPacket
7. Update BUILD_CARD_MANIFEST: Phase 1 → Verified, Phase 2 → Active

## What NOT to Do

- Do NOT build Runtime Kernel yet
- Do NOT build Control Plane yet
- Do NOT integrate DeerFlow yet
- Do NOT create Cockpit UI yet
- This phase is ONLY environment verification and install proof

## Required Proof

```text
proof/environment/doctor_report.json
proof/environment/version_report.json
proof/environment/environment_proofpacket.json
docs/PHASE_2_ENVIRONMENT_REPORT.md
```

## Gate Criteria

Phase 2 passes when:
- `rigforge doctor` returns READY or DEGRADED with known waivers
- All required tools verified
- Environment manifest exists
- Environment ProofPacket sealed
- Tests for environment verification pass
