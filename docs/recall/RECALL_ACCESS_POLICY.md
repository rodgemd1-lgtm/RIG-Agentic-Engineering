# Recall Access Policy (Read‑Only)

## Scope

Pi may use Recall **only** to retrieve build‑card context for RIGForge. This is a **read‑only** operation; no writes, no modifications, no creation of Recall cards.

## Security Rules

- **Never** print or log the `RECALL_API_KEY`.  
- **Never** commit the key to the repository.  
- **Never** include the key in any ProofPacket, doc, or log file.  
- The key may be read **only** from the environment variable `RECALL_API_KEY`.
- If Pi uses Recall MCP (browser OAuth) it must not request an API key at all.
- The key must **not** be exposed to Aider, the Evaluator, or the Verifier.

## Allowed Operations

1. Search for RIGForge build cards.  
2. Retrieve card content.  
3. Store retrieved markdown locally under `docs/recall/cards/`.  
4. Assemble a **context pack** (`docs/recall/RIGFORGE_CONTEXT_PACK.md`).  
5. Compare current repo state against exit criteria from the cards.

## Forbidden Operations

- Modifying any Recall content.  
- Storing the API key anywhere in the repo.  
- Printing the key to stdout/stderr.  
- Using Recall as a runtime data source for GTM Studio production workflows.  
- Allowing Aider or any other generator tool to see the key.

## Compliance Checks

`script/recall_check.py` will verify:
- The key exists in the environment (but is not printed).  
- `.gitignore` protects `.env*` files.  
- The policy document exists.

If any check fails the status will be **BLOCKED**.
