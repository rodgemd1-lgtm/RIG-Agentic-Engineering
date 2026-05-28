# GTM Studio Architecture Map

*No internal source code present in this repo.*

- **External Service**: GTM Studio runs as a Docker container exposing HTTP API on port 8081.
- **Healthcheck**: Defined in `config/app_registry.yaml` (`http://localhost:8081/health`).
- **Workers**: Background job workers (outside this repo).
- **Database**: External DB (not managed here).
- **Integrations**: Email/SMS/Ad platforms (external side‑effects).

*This map is a high‑level overview for planning.*