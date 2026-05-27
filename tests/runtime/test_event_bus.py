"""Tests for RIG Runtime Kernel Event Bus.

Verifies append-only event journal and publisher/subscriber pattern.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from runtime.kernel.event_bus import Event, EventBus


@pytest.fixture
def bus(tmp_path: Path) -> EventBus:
    return EventBus(journal_dir=tmp_path / ".rig_journal")


class TestEventBus:
    def test_emit_and_read(self, bus: EventBus) -> None:
        """Events can be emitted and read back."""
        event = Event(
            event_id="evt_001",
            timestamp="2026-05-27T00:00:00Z",
            run_id="run_abc",
            phase="bootstrap",
            event_type="mission_started",
        )
        bus.emit(event)
        events = bus.get_events("run_abc")
        assert len(events) == 1
        assert events[0].event_type == "mission_started"

    def test_events_append_only(self, bus: EventBus) -> None:
        """Multiple events append to the same journal."""
        bus.emit(Event(event_id="evt_1", timestamp="2026-05-27T00:00:00Z", run_id="run_multi", phase="bootstrap", event_type="phase1"))
        bus.emit(Event(event_id="evt_2", timestamp="2026-05-27T00:01:00Z", run_id="run_multi", phase="bootstrap", event_type="phase2"))
        events = bus.get_events("run_multi")
        assert len(events) == 2
        assert events[0].event_id == "evt_1"
        assert events[1].event_id == "evt_2"

    def test_different_runs_isolated(self, bus: EventBus) -> None:
        """Each run has its own journal."""
        bus.emit(Event(event_id="evt_a", timestamp="2026-05-27T00:00:00Z", run_id="run_A", phase="build", event_type="start"))
        bus.emit(Event(event_id="evt_b", timestamp="2026-05-27T00:00:00Z", run_id="run_B", phase="build", event_type="start"))
        assert len(bus.get_events("run_A")) == 1
        assert len(bus.get_events("run_B")) == 1
        assert bus.get_events("run_A")[0].event_id == "evt_a"
        assert bus.get_events("run_B")[0].event_id == "evt_b"

    def test_subscriber_notified(self, bus: EventBus) -> None:
        """Subscribers receive events."""
        received: list[Event] = []
        bus.subscribe(lambda e: received.append(e))
        event = Event(event_id="evt_sub", timestamp="2026-05-27T00:00:00Z", run_id="run_sub", phase="bootstrap", event_type="test")
        bus.emit(event)
        assert len(received) == 1
        assert received[0].run_id == "run_sub"

    def test_count_events(self, bus: EventBus) -> None:
        """Event count is accurate."""
        bus.emit(Event(event_id="e1", timestamp="2026-05-27T00:00:00Z", run_id="run_count", phase="build", event_type="a"))
        bus.emit(Event(event_id="e2", timestamp="2026-05-27T00:00:00Z", run_id="run_count", phase="build", event_type="b"))
        assert bus.count_events("run_count") == 2

    def test_event_types(self, bus: EventBus) -> None:
        """Event types are listed."""
        bus.emit(Event(event_id="e1", timestamp="2026-05-27T00:00:00Z", run_id="run_types", phase="build", event_type="mission_started"))
        bus.emit(Event(event_id="e2", timestamp="2026-05-27T00:00:00Z", run_id="run_types", phase="build", event_type="proof_emitted"))
        types = bus.event_types("run_types")
        assert "mission_started" in types
        assert "proof_emitted" in types

    def test_persistence(self, tmp_path: Path) -> None:
        """Events survive EventBus recreation."""
        journal_dir = tmp_path / ".rig_journal"
        bus1 = EventBus(journal_dir=journal_dir)
        bus1.emit(Event(event_id="e1", timestamp="2026-05-27T00:00:00Z", run_id="run_persist", phase="build", event_type="x"))
        # Recreate bus — reads from disk
        bus2 = EventBus(journal_dir=journal_dir)
        events = bus2.get_events("run_persist")
        assert len(events) == 1
        assert events[0].event_type == "x"
