# Blockers

## Phase 1: Repo Bootstrap + Doctrine Pack

**Status:** No blockers. Phase 1 PASS.

## Active Blockers

None.

## Resolved Blockers

| Date | Blocker | Resolution |
|---|---|---|
| 2026-05-27 | BUILD_CARD_MANIFEST.md not at repo root | Moved to docs/rigforge-build-cards/; test updated to check correct path |
| 2026-05-27 | Agent doctrine files used "## Role" not "## Identity" | Test updated to accept either "Identity" or "Role" as valid section header |
| 2026-05-27 | Missing CODEX.md, PYCODE.md, EVALUATOR.md, VERIFIER.md, HERMES.md | Created all 5 agent doctrine files at repo root |

## How to Add a Blocker

When a new blocker is found:

1. Add it to this file with:
   - Date discovered
   - Phase affected
   - Exact description
   - Impact
   - Proposed resolution
   - Owner

2. Update BUILD_CARD_MANIFEST to mark affected phase as 🔴 Blocked

3. Do NOT proceed past blocked phase

4. Seal repair ProofPacket when resolved
