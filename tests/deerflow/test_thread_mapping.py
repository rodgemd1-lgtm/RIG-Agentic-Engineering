"""Tests for DeerFlow thread mapping: RunEnvelope <-> DeerFlow thread_id.

Core law:
    No DeerFlow thread without RunEnvelope.
    No RunEnvelope long-horizon mission without DeerFlow thread mapping.
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from integrations.deerflow.thread_mapping import (
    ThreadMapping,
    get_thread_mapping,
    reset_default_store,
)


@pytest.fixture(autouse=True)
def _reset_store():
    """Reset the module-level singleton between tests."""
    reset_default_store()
    yield
    reset_default_store()


@pytest.fixture
def tmp_store(tmp_path: Path) -> Path:
    """Path to a temporary mapping store file."""
    return tmp_path / ".deerflow_mappings.json"


@pytest.fixture
def mapping(tmp_store: Path) -> ThreadMapping:
    """ThreadMapping instance using temp store."""
    return ThreadMapping(store_path=tmp_store)


@pytest.fixture
def run_dir(tmp_path: Path) -> Path:
    """Create a run directory with RunEnvelope."""
    rd = tmp_path / "runs" / "run_test_001"
    rd.mkdir(parents=True)
    envelope = {
        "run_id": "run_test_001",
        "studio": "app",
        "idea": "test mission",
    }
    (rd / "RunEnvelope.json").write_text(json.dumps(envelope))
    return rd


class TestThreadMappingCreate:
    def test_create_mapping(self, mapping: ThreadMapping) -> None:
        """Thread mapping can be created with all required fields."""
        record = mapping.create(
            rig_run_id="run_abc123",
            rig_mission_id="soul-id-regression",
            deerflow_thread_id="df_thread_xyz789",
            studio="app",
            workflow_id="first_mission_soul_id",
            worktree_path="worktrees/run_abc123",
            deerflow_workspace="deerflow/.deer-flow/threads/df_thread_xyz789/user-data/workspace",
        )
        assert record["rig_run_id"] == "run_abc123"
        assert record["deerflow_thread_id"] == "df_thread_xyz789"
        assert record["status"] == "active"

    def test_create_duplicate_raises(self, mapping: ThreadMapping) -> None:
        """Cannot create two mappings for the same run_id."""
        mapping.create(
            rig_run_id="run_dup",
            rig_mission_id="mission_1",
            deerflow_thread_id="df_thread_1",
            studio="app",
            workflow_id="wf_1",
            worktree_path="wt_1",
            deerflow_workspace="df_ws_1",
        )
        with pytest.raises(ValueError, match="already exists"):
            mapping.create(
                rig_run_id="run_dup",
                rig_mission_id="mission_2",
                deerflow_thread_id="df_thread_2",
                studio="app",
                workflow_id="wf_2",
                worktree_path="wt_2",
                deerflow_workspace="df_ws_2",
            )

    def test_create_persists(
        self, mapping: ThreadMapping, tmp_store: Path
    ) -> None:
        """Mapping is persisted to disk."""
        mapping.create(
            rig_run_id="run_persist",
            rig_mission_id="mission",
            deerflow_thread_id="df_thread_persist",
            studio="app",
            workflow_id="wf",
            worktree_path="wt",
            deerflow_workspace="df_ws",
        )
        assert tmp_store.exists()
        data = json.loads(tmp_store.read_text())
        assert "run_persist" in data["mappings"]


class TestThreadMappingLookup:
    def test_get_by_run_id(self, mapping: ThreadMapping) -> None:
        """Can look up mapping by run_id."""
        mapping.create(
            rig_run_id="run_lookup",
            rig_mission_id="mission",
            deerflow_thread_id="df_lookup_thread",
            studio="app",
            workflow_id="wf",
            worktree_path="wt",
            deerflow_workspace="df_ws",
        )
        result = mapping.get_by_run_id("run_lookup")
        assert result is not None
        assert result["deerflow_thread_id"] == "df_lookup_thread"

    def test_get_by_run_id_missing(self, mapping: ThreadMapping) -> None:
        """Returns None for unknown run_id."""
        assert mapping.get_by_run_id("run_nonexistent") is None

    def test_get_by_thread_id(self, mapping: ThreadMapping) -> None:
        """Can look up mapping by DeerFlow thread_id."""
        mapping.create(
            rig_run_id="run_reverse",
            rig_mission_id="mission",
            deerflow_thread_id="df_reverse_thread",
            studio="app",
            workflow_id="wf",
            worktree_path="wt",
            deerflow_workspace="df_ws",
        )
        result = mapping.get_by_thread_id("df_reverse_thread")
        assert result is not None
        assert result["rig_run_id"] == "run_reverse"

    def test_get_by_thread_id_missing(self, mapping: ThreadMapping) -> None:
        """Returns None for unknown thread_id."""
        assert mapping.get_by_thread_id("df_nonexistent") is None

    def test_bidirectional_consistency(self, mapping: ThreadMapping) -> None:
        """run_id → thread_id → run_id is consistent."""
        mapping.create(
            rig_run_id="run_bidir",
            rig_mission_id="mission",
            deerflow_thread_id="df_bidir_thread",
            studio="app",
            workflow_id="wf",
            worktree_path="wt",
            deerflow_workspace="df_ws",
        )
        by_run = mapping.get_by_run_id("run_bidir")
        assert by_run is not None
        by_thread = mapping.get_by_thread_id(by_run["deerflow_thread_id"])
        assert by_thread is not None
        assert by_thread["rig_run_id"] == "run_bidir"


class TestThreadMappingStatus:
    def test_update_status(self, mapping: ThreadMapping) -> None:
        """Can update mapping status."""
        mapping.create(
            rig_run_id="run_status",
            rig_mission_id="mission",
            deerflow_thread_id="df_status_thread",
            studio="app",
            workflow_id="wf",
            worktree_path="wt",
            deerflow_workspace="df_ws",
        )
        mapping.update_status("run_status", "completed")
        result = mapping.get_by_run_id("run_status")
        assert result is not None
        assert result["status"] == "completed"

    def test_update_status_missing_raises(self, mapping: ThreadMapping) -> None:
        """Updating status of non-existent mapping raises KeyError."""
        with pytest.raises(KeyError):
            mapping.update_status("run_nonexistent", "completed")


class TestThreadMappingDelete:
    def test_delete(self, mapping: ThreadMapping) -> None:
        """Can delete a mapping."""
        mapping.create(
            rig_run_id="run_delete",
            rig_mission_id="mission",
            deerflow_thread_id="df_del_thread",
            studio="app",
            workflow_id="wf",
            worktree_path="wt",
            deerflow_workspace="df_ws",
        )
        mapping.delete("run_delete")
        assert mapping.get_by_run_id("run_delete") is None


class TestDeerFlowClientRequiresEnvelope:
    """DeerFlow thread cannot start without RunEnvelope."""

    def test_no_envelope_raises(self, tmp_path: Path) -> None:
        """DeerFlowRigClient raises FileNotFoundError without RunEnvelope."""
        from integrations.deerflow.deerflow_client import DeerFlowRigClient

        config_path = tmp_path / "deerflow_rig.yaml"
        config_path.write_text("deerflow:\n  base_url: http://localhost:2026\n")

        client = DeerFlowRigClient(config_path=str(config_path))

        with pytest.raises(FileNotFoundError, match="No RunEnvelope found"):
            import asyncio

            asyncio.run(
                client.run_long_horizon(
                    run_id="run_no_envelope",
                    message="test",
                )
            )

    def test_with_envelope_succeeds(
        self, tmp_path: Path
    ) -> None:
        """DeerFlowRigClient succeeds (stub) with valid RunEnvelope."""
        import uuid
        from integrations.deerflow.deerflow_client import DeerFlowRigClient

        unique_run_id = f"run_env_{uuid.uuid4().hex[:8]}"
        config_path = tmp_path / "deerflow_rig.yaml"
        config_path.write_text("deerflow:\n  base_url: http://localhost:2026\n")

        client = DeerFlowRigClient(config_path=str(config_path))

        with patch.object(client, "_check_run_envelope", return_value={"run_id": unique_run_id, "studio": "app"}):
            import asyncio

            result = asyncio.run(
                client.run_long_horizon(
                    run_id=unique_run_id,
                    message="test mission",
                )
            )
        assert result["status"] == "stub"
        assert "mapping_record" in result
