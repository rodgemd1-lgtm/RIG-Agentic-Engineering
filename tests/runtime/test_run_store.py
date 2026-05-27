"""Tests for RIG Runtime Kernel Run Store.

Verifies RunEnvelope persistence and retrieval.
"""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pytest

from contracts.v1.run_envelope import RunEnvelope
from runtime.kernel.run_store import RunStore


@pytest.fixture
def store(tmp_path: Path) -> RunStore:
    return RunStore(store_dir=tmp_path / ".rig_runs")


class TestRunStore:
    def test_save_and_load(self, store: RunStore) -> None:
        """A RunEnvelope can be saved and loaded."""
        env = RunEnvelope(
            run_id="run_test_001",
            studio="app",
            idea="test mission",
            status="draft",
            harness="archon",
        )
        store.save(env)
        loaded = store.load("run_test_001")
        assert loaded is not None
        assert loaded.run_id == "run_test_001"
        assert loaded.studio == "app"
        assert loaded.idea == "test mission"

    def test_load_missing_returns_none(self, store: RunStore) -> None:
        """Loading a non-existent run returns None."""
        assert store.load("run_nonexistent") is None

    def test_exists(self, store: RunStore) -> None:
        """exists() reflects stored runs."""
        env = RunEnvelope(run_id="run_exists", studio="app")
        store.save(env)
        assert store.exists("run_exists") is True
        assert store.exists("run_not_saved") is False

    def test_list_all(self, store: RunStore) -> None:
        """list_all returns all run_ids."""
        store.save(RunEnvelope(run_id="run_a", studio="app"))
        store.save(RunEnvelope(run_id="run_b", studio="app"))
        assert sorted(store.list_all()) == ["run_a", "run_b"]

    def test_update_status(self, store: RunStore) -> None:
        """update_status changes the run status and metadata."""
        env = RunEnvelope(run_id="run_update", studio="app", status="draft")
        store.save(env)
        
        result = store.update_status("run_update", "building")
        assert result is True
        
        loaded = store.load("run_update")
        assert loaded is not None
        assert loaded.status == "building"
        assert "last_updated" in loaded.metadata

    def test_update_status_missing_returns_false(self, store: RunStore) -> None:
        """updating status of non-existent run returns False."""
        assert store.update_status("run_nope", "building") is False

    def test_delete(self, store: RunStore) -> None:
        """delete removes a run."""
        env = RunEnvelope(run_id="run_delete", studio="app")
        store.save(env)
        assert store.exists("run_delete") is True
        store.delete("run_delete")
        assert store.exists("run_delete") is False

    def test_atomic_write(self, store: RunStore) -> None:
        """Writes use atomic temp+rename."""
        env = RunEnvelope(run_id="run_atomic", studio="app")
        store.save(env)
        # Should exist without temp files
        temp_files = list(store.store_dir.glob("*.tmp"))
        assert len(temp_files) == 0


class TestRunEnvelope:
    def test_run_id_generated(self) -> None:
        """Default run_id is auto-generated."""
        env = RunEnvelope(studio="app")
        assert env.run_id.startswith("run_")

    def test_studio_field(self) -> None:
        """Studio field is set correctly."""
        env = RunEnvelope(studio="app", idea="test")
        assert env.studio == "app"

    def test_run_id_propagation(self) -> None:
        """run_id is the unique key across the system."""
        env = RunEnvelope(run_id="run_propagate", studio="app", idea="test")
        assert env.run_id == "run_propagate"

    def test_run_id_in_filename(self, store: RunStore) -> None:
        """run_id is used as the filename for persistence."""
        env = RunEnvelope(run_id="run_file", studio="app")
        store.save(env)
        assert (store.store_dir / "run_file.json").exists()
