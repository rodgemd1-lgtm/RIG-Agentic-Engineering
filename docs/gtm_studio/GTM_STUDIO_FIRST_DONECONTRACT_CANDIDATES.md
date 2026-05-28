# GTM Studio First DoneContract Candidates

## Candidate 1: Deterministic Healthcheck Script

### Name
GTM Studio Worker/Scheduler Healthcheck Script

### Why this first
- Small, read‑only HTTP GET – no external side effects.
- Provides concrete ProofPacket for Phase 5.
- Improves observability of GTM Studio availability.
- Easy to verify with unit test (mock HTTP response).

### Files likely touched
- `scripts/gtm_healthcheck.py` (new script)
- `proof/gtm-studio/healthcheck.json` (ProofPacket)
- Optional test `tests/gtm_studio/test_healthcheck.py`

### Files forbidden to touch
- `contracts/v1/*` (must remain immutable until DoneContract sealed)
- Any production deployment scripts
- Any database migration files

### Required tests
- Successful 200 response leads to PASS.
- Non‑200 or timeout leads to FAIL/BLOCKED.
- ProofPacket JSON contains `run_id`, `timestamp`, `status`, `http_status`.

### Required proof
- `proof/gtm-studio/healthcheck.json` with fields:
  ```json
  {"run_id": "<run>", "timestamp": "...", "http_status": 200, "result": "OK"}
  ```
- Hash manifest of the script and proof file.

### Rollback path
- Script can be removed without side effects; healthcheck simply not performed.

### Approval needed?
- No – read‑only healthcheck does not affect production state.

### Risk level
Low (read‑only network call, no writes).

---

*No other candidates are listed until the healthcheck is implemented.*