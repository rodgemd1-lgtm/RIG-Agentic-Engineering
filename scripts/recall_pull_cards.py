#!/usr/bin/env python3
"""Recall card pull script (read‑only).

If a real Recall MCP or API client exists, implement the search/retrieval here.
For now this script is a placeholder that records the intent and marks the
status as BLOCKED_PENDING_RECALL_API_IMPLEMENTATION.
"""

import json
import os
import sys
from pathlib import Path

def main():
    # Check for env key – we will not use it yet.
    has_key = "RECALL_API_KEY" in os.environ
    # Verify the pull list exists
    pull_list = Path('docs/recall/RIGFORGE_CARD_PULL_LIST.md')
    if not pull_list.is_file():
        print(json.dumps({"status": "BLOCKED", "reason": "pull list missing"}, indent=2))
        sys.exit(1)
    # Placeholder – no actual Recall integration.
    report = {
        "status": "BLOCKED_PENDING_RECALL_API_IMPLEMENTATION",
        "reason": "Recall API/MCP client not implemented",
        "cards_requested": [],
        "cards_found": [],
        "cards_missing": [],
    }
    print(json.dumps(report, indent=2))
    sys.exit(0)

if __name__ == "__main__":
    main()
