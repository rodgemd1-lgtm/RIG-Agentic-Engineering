"""Registry loader — reads all YAML registries from config/."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass
class RegistryStats:
    """Statistics for loaded registries."""
    registry_name: str
    entry_count: int
    loaded: bool
    path: Path


@dataclass
class LoadedRegistries:
    """Container for all loaded registries."""
    service: dict[str, Any] = field(default_factory=dict)
    api: dict[str, Any] = field(default_factory=dict)
    mcp: dict[str, Any] = field(default_factory=dict)
    tool: dict[str, Any] = field(default_factory=dict)
    model: dict[str, Any] = field(default_factory=dict)
    node: dict[str, Any] = field(default_factory=dict)
    app: dict[str, Any] = field(default_factory=dict)
    workflow: dict[str, Any] = field(default_factory=dict)
    proof: dict[str, Any] = field(default_factory=dict)
    approval: dict[str, Any] = field(default_factory=dict)


class RegistryLoader:
    """Load and index all RIGForge registries."""

    REGISTRY_FILES: dict[str, str] = {
        "service": "config/service_registry.yaml",
        "api": "config/api_registry.yaml",
        "mcp": "config/mcp_registry.yaml",
        "tool": "config/tool_registry.yaml",
        "model": "config/model_registry.yaml",
        "node": "config/node_registry.yaml",
        "app": "config/app_registry.yaml",
        "workflow": "config/workflow_registry.yaml",
        "proof": "config/proof_registry.yaml",
        "approval": "config/approval_registry.yaml",
    }

    def __init__(self, repo_root: Path | str = ".") -> None:
        self.repo_root = Path(repo_root)

    def _load_yaml(self, rel_path: str) -> dict[str, Any]:
        """Load a YAML file, return empty dict if missing."""
        path = self.repo_root / rel_path
        if not path.exists():
            return {}
        try:
            with open(path, encoding="utf-8") as f:
                data = yaml.safe_load(f)
                return data if data else {}
        except yaml.YAMLError:
            return {}

    def load(self, name: str) -> dict[str, Any]:
        """Load a specific registry by name."""
        path = self.REGISTRY_FILES.get(name, "")
        if not path:
            return {}
        return self._load_yaml(path)

    def load_service(self) -> dict[str, Any]:
        """Load service registry."""
        data = self._load_yaml(self.REGISTRY_FILES["service"])
        return data.get("services", [])

    def load_api(self) -> dict[str, Any]:
        """Load API registry."""
        data = self._load_yaml(self.REGISTRY_FILES["api"])
        return data.get("apis", [])

    def load_mcp(self) -> dict[str, Any]:
        """Load MCP server registry."""
        data = self._load_yaml(self.REGISTRY_FILES["mcp"])
        return data.get("mcp_servers", [])

    def load_tool(self) -> dict[str, Any]:
        """Load tool registry."""
        data = self._load_yaml(self.REGISTRY_FILES["tool"])
        return data.get("tools", [])

    def load_model(self) -> dict[str, Any]:
        """Load model registry."""
        data = self._load_yaml(self.REGISTRY_FILES["model"])
        return data.get("models", [])

    def load_node(self) -> dict[str, Any]:
        """Load node registry."""
        data = self._load_yaml(self.REGISTRY_FILES["node"])
        return data.get("nodes", [])

    def load_app(self) -> dict[str, Any]:
        """Load app registry."""
        data = self._load_yaml(self.REGISTRY_FILES["app"])
        return data.get("apps", [])

    def load_workflow(self) -> dict[str, Any]:
        """Load workflow registry."""
        data = self._load_yaml(self.REGISTRY_FILES["workflow"])
        return data.get("workflows", [])

    def load_proof(self) -> dict[str, Any]:
        """Load proof path registry."""
        data = self._load_yaml(self.REGISTRY_FILES["proof"])
        return data.get("proof_paths", [])

    def load_approval(self) -> dict[str, Any]:
        """Load approval flow registry."""
        data = self._load_yaml(self.REGISTRY_FILES["approval"])
        return data.get("approval_flows", [])

    def load_all(self) -> LoadedRegistries:
        """Load all registries at once."""
        return LoadedRegistries(
            service=self.load_service(),
            api=self.load_api(),
            mcp=self.load_mcp(),
            tool=self.load_tool(),
            model=self.load_model(),
            node=self.load_node(),
            app=self.load_app(),
            workflow=self.load_workflow(),
            proof=self.load_proof(),
            approval=self.load_approval(),
        )

    # Key aliases for registries whose YAML top-level keys differ from registry name
    KEY_ALIASES = {
        "proof": "proof_paths",
        "approval": "approval_flows",
        "service": "services",
        "api": "apis",
        "mcp": "mcp_servers",
        "tool": "tools",
        "model": "models",
        "node": "nodes",
        "app": "apps",
        "workflow": "workflows",
    }

    def stats(self) -> list[RegistryStats]:
        """Return stats for all registries."""
        stats = []
        for name, rel_path in self.REGISTRY_FILES.items():
            path = self.repo_root / rel_path
            data = self._load_yaml(rel_path)
            key = self.KEY_ALIASES.get(name, f"{name}s")
            entries = data.get(key, [])
            count = len(entries) if isinstance(entries, list) else 0
            stats.append(RegistryStats(
                registry_name=name,
                entry_count=count,
                loaded=path.exists(),
                path=path,
            ))
        return stats


def load_all_registries(repo_root: Path | str = ".") -> LoadedRegistries:
    """Convenience: load all registries."""
    return RegistryLoader(repo_root).load_all()