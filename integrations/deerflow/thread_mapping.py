"""Thread mapping: Rigorous RunEnvelope <-> DeerFlow thread ID mapping.

Core law:
    No DeerFlow thread without RunEnvelope.
    No RunEnvelope long-horizon mission without DeerFlow thread mapping.

The mapping store is a JSON file at rig-runtime/.deerflow_mappings.json by default.
It is the single source of truth for all DeerFlow thread <-> RIG run associations.
"""

from __future__ import annotations

import json
import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

DEFAULT_MAPPING_PATH = Path("rig-runtime/.deerflow_mappings.json")


class ThreadMapping:
    """Manages the bidirectional RunEnvelope <-> DeerFlow thread_id mapping store."""

    def __init__(self, store_path: Path = DEFAULT_MAPPING_PATH) -> None:
        self.store_path = store_path
        self._mappings: dict[str, dict[str, Any]] = {}
        self._load()

    def _load(self) -> None:
        """Load mappings from disk."""
        if self.store_path.exists():
            try:
                with open(self.store_path) as f:
                    data = json.load(f)
                self._mappings = data.get("mappings", {})
            except (json.JSONDecodeError, KeyError) as e:
                logger.error(f"Corrupt mapping store at {self.store_path}: {e}")
                self._mappings = {}
        else:
            self._mappings = {}

    def _save(self) -> None:
        """Persist mappings to disk."""
        self.store_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.store_path, "w") as f:
            json.dump(
                {
                    "version": "0.1.0",
                    "updated_at": datetime.now(timezone.utc).isoformat(),
                    "mappings": self._mappings,
                },
                f,
                indent=2,
            )

    def create(
        self,
        rig_run_id: str,
        rig_mission_id: str,
        deerflow_thread_id: str,
        studio: str,
        workflow_id: str,
        worktree_path: str,
        deerflow_workspace: str,
    ) -> dict[str, Any]:
        """
        Create a new thread mapping.

        Args:
            rig_run_id: RIG RunEnvelope.run_id
            rig_mission_id: Human-readable mission identifier
            deerflow_thread_id: DeerFlow thread ID (df_xxx)
            studio: RIG studio name
            workflow_id: Archon workflow ID
            worktree_path: Path to git worktree for this run
            deerflow_workspace: DeerFlow thread workspace path

        Returns:
            The mapping record dict

        Raises:
            ValueError: If mapping already exists for this run_id
        """
        if rig_run_id in self._mappings:
            raise ValueError(
                f"Mapping already exists for run {rig_run_id}. "
                f"Use get_by_run_id() to retrieve or delete() first."
            )

        record = {
            "rig_run_id": rig_run_id,
            "rig_mission_id": rig_mission_id,
            "deerflow_thread_id": deerflow_thread_id,
            "studio": studio,
            "workflow_id": workflow_id,
            "worktree_path": worktree_path,
            "deerflow_workspace": deerflow_workspace,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
        }

        self._mappings[rig_run_id] = record
        self._save()
        logger.info(
            f"Thread mapping created: run={rig_run_id} ↔ thread={deerflow_thread_id}"
        )
        return record

    def get_by_run_id(self, run_id: str) -> Optional[dict[str, Any]]:
        """Look up mapping by RIG run ID."""
        return self._mappings.get(run_id)

    def get_by_thread_id(self, thread_id: str) -> Optional[dict[str, Any]]:
        """Look up mapping by DeerFlow thread ID."""
        for record in self._mappings.values():
            if record.get("deerflow_thread_id") == thread_id:
                return record
        return None

    def update_status(self, run_id: str, status: str) -> None:
        """Update the status of a mapping (active, paused, completed, failed)."""
        if run_id not in self._mappings:
            raise KeyError(f"No mapping for run {run_id}")
        self._mappings[run_id]["status"] = status
        self._mappings[run_id]["updated_at"] = datetime.now(timezone.utc).isoformat()
        self._save()

    def delete(self, run_id: str) -> None:
        """Remove a mapping."""
        if run_id in self._mappings:
            del self._mappings[run_id]
            self._save()

    def list_all(self) -> list[dict[str, Any]]:
        """List all mappings."""
        return list(self._mappings.values())

    def to_yaml(self) -> str:
        """Export all mappings as YAML."""
        import yaml
        return yaml.dump(
            {"mappings": self._mappings},
            default_flow_style=False,
        )


# ── Module-level singleton ───────────────────────────────────────────────────

_default_store: Optional[ThreadMapping] = None


def get_thread_mapping(store_path: Path = DEFAULT_MAPPING_PATH) -> ThreadMapping:
    """Get or create the module-level ThreadMapping singleton."""
    global _default_store
    if _default_store is None:
        _default_store = ThreadMapping(store_path)
    return _default_store


def reset_default_store() -> None:
    """Reset the singleton (for testing)."""
    global _default_store
    _default_store = None
