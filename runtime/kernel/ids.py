"""ULID-style ID generator for RIG RunEnvelope run IDs.

Uses monotonic sortable IDs without external deps.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone


def generate_run_id(prefix: str = "run") -> str:
    """Generate a monotonic, sortable run_id.
    
    Format: run_YYYYMMDD_HHMMSS_xxxxxxxx
    Where the x's are 8 hex chars from UUID4 for collision resistance.
    """
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y%m%d_%H%M%S")
    suffix = uuid.uuid4().hex[:8]
    return f"{prefix}_{timestamp}_{suffix}"


def generate_packet_id(prefix: str = "pp") -> str:
    """Generate a ProofPacket ID.
    Format: pp_xxxxxxxx
    """
    return f"{prefix}_{uuid.uuid4().hex[:12]}"


def generate_event_id() -> str:
    """Generate an event journal entry ID.
    Format: evt_xxxxxxxx
    """
    return f"evt_{uuid.uuid4().hex[:12]}"
