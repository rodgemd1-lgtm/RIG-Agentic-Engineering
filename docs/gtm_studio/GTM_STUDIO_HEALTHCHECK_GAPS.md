# GTM Studio Healthcheck Gaps

- No healthcheck implementation exists in this repo – only a registry entry.
- No script that performs an HTTP GET to the health endpoint and records results.
- No ProofPacket generation for healthcheck outcomes.

*First bounded fix:* create a Python script `scripts/gtm_healthcheck.py` that pings the endpoint, validates 200 response, and writes a JSON proof to `proof/gtm-studio/healthcheck.json`. This can be done by Aider under a sealed DoneContract.
