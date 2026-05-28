# GTM Studio Proof Gaps

- `proof/gtm-studio/` directory is empty – no ProofPacket for healthcheck or any other artifact.
- No JSON schema defining expected proof contents.
- No automated script to generate proof after healthcheck.

*First bounded fix:* generate a ProofPacket JSON after healthcheck script runs.
