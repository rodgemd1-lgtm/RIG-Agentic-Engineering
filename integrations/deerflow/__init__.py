"""DeerFlow 2.0 integration layer for RIG Agentic Engineering.

DeerFlow supervises long runs.
Archon owns workflow order.
PyCode builds.
Hermes governs.
Codex verifies.

This package provides:
- deerflow_client: Thin wrapper around DeerFlowClient with RIG boundary checks
- thread_mapping: Rigorous RunEnvelope <-> DeerFlow thread ID mapping
- workspace_mapping: DeerFlow workspace paths <-> RIG worktree paths
- proof_adapter: Every sub-agent result produces a ProofPacket event
- archon_bridge: Archon calls DeerFlow only at approved long-horizon nodes
- pycode_bridge: DeerFlow supervises, PyCode performs generator-owned build steps
"""

from integrations.deerflow.deerflow_client import DeerFlowRigClient
from integrations.deerflow.thread_mapping import ThreadMapping, get_thread_mapping
from integrations.deerflow.workspace_mapping import WorkspaceMapping, get_workspace_mapping
from integrations.deerflow.proof_adapter import emit_proof_event

__all__ = [
    "DeerFlowRigClient",
    "ThreadMapping",
    "get_thread_mapping",
    "WorkspaceMapping",
    "get_workspace_mapping",
    "emit_proof_event",
]
