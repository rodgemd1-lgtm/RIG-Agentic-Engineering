#!/usr/bin/env python3
"""Recall access health‑check.

Checks:
  - RECALL_API_KEY env var present (without printing).
  - .gitignore protects .env files.
  - Recall policy doc exists.

Outputs a JSON status object and exits 0 for READY/DEGRADED, 1 for BLOCKED.
"""

import json
import os
import sys
from pathlib import Path

def env_key_present():
    return "RECALL_API_KEY" in os.environ

def gitignore_protects_env():
    gi = Path('.gitignore')
    if not gi.is_file():
        return False
    content = gi.read_text()
    return any(pat in content for pat in (".env", ".env.*"))

def policy_exists():
    return Path('docs/recall/RECALL_ACCESS_POLICY.md').is_file()

def main():
    key_present = env_key_present()
    protect = gitignore_protects_env()
    policy = policy_exists()

    blockers = []
    status = "READY"
    if not key_present:
        blockers.append("RECALL_API_KEY missing")
    if not protect:
        blockers.append(".gitignore does not protect .env files")
    if not policy:
        blockers.append("Recall policy doc missing")

    if blockers:
        status = "BLOCKED"
    elif not key_present or not protect:
        status = "DEGRADED"

    report = {
        "recall_api_key_present": key_present,
        "recall_api_key_printed": False,  # we never print it
        "gitignore_protects_env": protect,
        "policy_doc_exists": policy,
        "status": status,
        "blockers": blockers,
        "next_safe_action": "" if status == "READY" else "Fix blockers",
    }
    print(json.dumps(report, indent=2))
    sys.exit(0 if status in ("READY", "DEGRADED") else 1)

if __name__ == "__main__":
    main()
