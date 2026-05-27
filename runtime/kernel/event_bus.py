"""Append-only event bus for RIG Runtime Kernel.

Core law:
    No event journal, no debugging.
    Events are append-only. No deletion. No modification.

Every event: (timestamp, run_id, phase, event_type, payload)
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable


@dataclass
class Event:
    """Single event in the append-only journal."""
    event_id: str
    timestamp: str
    run_id: str
    phase: str
    event_type: str
    payload: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class EventBus:
    """Append-only event bus with file-backed persistence.
    
    Events are written to disk and never modified.
    Subscribers receive events in order.
    """
    
    def __init__(self, journal_dir: Path | str = ".rig_journal") -> None:
        self.journal_dir = Path(journal_dir)
        self.journal_dir.mkdir(parents=True, exist_ok=True)
        self._subscribers: list[Callable[[Event], None]] = []
    
    def _get_journal_path(self, run_id: str) -> Path:
        """Path to append-only journal for a specific run."""
        return self.journal_dir / f"{run_id}.jsonl"
    
    def emit(self, event: Event) -> None:
        """Emit an event: append to journal + notify subscribers."""
        journal_path = self._get_journal_path(event.run_id)
        
        # Append-only write — never modify existing content
        with open(journal_path, "a+", encoding="utf-8") as f:
            json.dump(event.to_dict(), f)
            f.write("\n")
        
        # Notify subscribers
        for callback in self._subscribers:
            callback(event)
    
    def subscribe(self, callback: Callable[[Event], None]) -> None:
        """Subscribe to all events."""
        self._subscribers.append(callback)
    
    def get_events(self, run_id: str) -> list[Event]:
        """Read all events for a run (read-only, never modifies)."""
        journal_path = self._get_journal_path(run_id)
        events: list[Event] = []
        
        if not journal_path.exists():
            return events
        
        with open(journal_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                data = json.loads(line)
                events.append(Event(**data))
        
        return events
    
    def get_all_runs(self) -> list[str]:
        """List all run_ids that have events."""
        return sorted([p.stem for p in self.journal_dir.glob("*.jsonl")])
    
    def count_events(self, run_id: str) -> int:
        """Count events for a run."""
        return len(self.get_events(run_id))
    
    def event_types(self, run_id: str) -> list[str]:
        """List all event types for a run."""
        return sorted({e.event_type for e in self.get_events(run_id)})
