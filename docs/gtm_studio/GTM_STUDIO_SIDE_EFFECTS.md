# GTM Studio Side Effects

- **Campaign Sends** – triggers external email/SMS APIs.
- **Schedule Activations** – may enqueue jobs that call third‑party services.
- **Data Export** – writes campaign results to external storage.
- **API Calls** – to ad platforms for tracking.

*All side‑effects must be gated behind approval and must not be executed by Aider during inventory.*