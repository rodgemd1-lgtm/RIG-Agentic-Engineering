"""Run persistence — store and retrieve RunEnvelope by run_id.

The source of truth for run state. Every mutation is logged.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

from rigforge.models import RunEnvelope


class RunStore:
    """Persistent store for RunEnvelope records.
    
    Each run is stored as a JSON file keyed by run_id.
    Writes are atomic: write to temp, then rename.
    """
    
    def __init__(self, store_dir: Path | str = ".rig_runs") -> None:
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
    
    def save(self, envelope: RunEnvelope) -> None:
        """Save or update a RunEnvelope."""
        path = self.store_dir / f"{envelope.run_id}.json"
        # Atomic write
        temp = path.with_suffix(".tmp")
        temp.write_text(envelope.model_dump_json(indent=2))
        temp.replace(path)
    
    def load(self, run_id: str) -> Optional[RunEnvelope]:
        """Load a RunEnvelope by run_id."""
        path = self.store_dir / f"{run_id}.json"
        if not path.exists():
            return None
        data = json.loads(path.read_text())
        return RunEnvelope(**data)
    
    def exists(self, run_id: str) -> bool:
        """Check if a run exists."""
        return (self.store_dir / f"{run_id}.json").exists()
    
    def list_all(self) -> list[str]:
        """List all run_ids."""
        return sorted([p.stem for p in self.store_dir.glob("*.json")])
    
    def update_status(self, run_id: str, status: str, metadata: dict[str, Any] | None = None) -> bool:
        """Update the status of a run. Returns True if updated."""
        envelope = self.load(run_id)
        if envelope is None:
            return False
        
        envelope.status = status
        if metadata:
            envelope.metadata.update(metadata)
        envelope.metadata["last_updated"] = datetime.now(timezone.utc).isoformat()
        self.save(envelope)
        return True
    
    def delete(self, run_id: str) -> bool:
        """Remove a run (emergency cleanup only — usually immutable)."""
        path = self.store_dir / f"{run_id}.json"
        if path.exists():
            path.unlink()
            return True
        return False
