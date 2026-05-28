# GTM Studio Test Gaps

- No tests located under `tests/` that target GTM Studio endpoints or workers.
- No integration tests verifying healthcheck or API responses.
- No mock fixtures for external services.

*Suggested next step:* add a minimal pytest module `tests/gtm_studio/test_healthcheck.py` (to be implemented after DoneContract is sealed).