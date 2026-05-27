"""Test that Phase 1 bootstrap produced all required files and directories.

This test verifies the Repo Bootstrap + Doctrine Pack phase.
"""

from __future__ import annotations

from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).parent.parent


# Required files at repo root
REQUIRED_FILES = [
    "AGENTS.md",
    "CODEX.md",
    "PYCODE.md",
    "EVALUATOR.md",
    "VERIFIER.md",
    "HERMES.md",
    "RIG_DOCTRINE.md",
    "README.md",
    "pyproject.toml",
    "Makefile",
]

# Required directories
REQUIRED_DIRS = [
    "agents/generator",
    "agents/evaluator",
    "agents/verifier",
    "agents/hermes",
    "config",
    "contracts",
    "workflows",
    "studios",
    "scripts",
    "tests",
    "evals",
    "proof",
    "docs",
]

# Required agent doctrine files (relative to agents/)
AGENT_DOCTRINE_FILES = [
    "generator/AGENTS.md",
    "evaluator/AGENTS.md",
    "verifier/AGENTS.md",
    "hermes/AGENTS.md",
]


class TestRequiredFiles:
    @pytest.mark.parametrize("filename", REQUIRED_FILES)
    def test_file_exists(self, filename: str) -> None:
        """Each required file must exist at repo root."""
        path = REPO_ROOT / filename
        assert path.is_file(), f"Missing required file: {filename}"


class TestRequiredDirectories:
    @pytest.mark.parametrize("dirname", REQUIRED_DIRS)
    def test_dir_exists(self, dirname: str) -> None:
        """Each required directory must exist."""
        path = REPO_ROOT / dirname
        assert path.is_dir(), f"Missing required directory: {dirname}"


class TestAgentDoctrine:
    @pytest.mark.parametrize("agent_file", AGENT_DOCTRINE_FILES)
    def test_agent_doctrine_exists(self, agent_file: str) -> None:
        """Each agent must have a doctrine file with required sections."""
        path = REPO_ROOT / "agents" / agent_file
        assert path.is_file(), f"Missing agent doctrine: {agent_file}"
        content = path.read_text()
        # Required sections (Identity or Role are both acceptable)
        required_sections = [("Identity", "Role"), "Allowed Actions", "Forbidden Actions"]
        for section in required_sections:
            if isinstance(section, tuple):
                found = any(s in content for s in section)
                label = section[0]
            else:
                found = section in content
                label = section
            assert found, f"{agent_file} missing section: {label}"


class TestManifest:
    def test_manifest_exists(self) -> None:
        """BUILD_CARD_MANIFEST.md must exist in the build cards directory."""
        path = REPO_ROOT / "docs" / "rigforge-build-cards" / "BUILD_CARD_MANIFEST.md"
        assert path.is_file(), "BUILD_CARD_MANIFEST.md not found"

    def test_manifest_has_hard_laws(self) -> None:
        """Manifest must contain the hard laws."""
        path = REPO_ROOT / "docs" / "rigforge-build-cards" / "BUILD_CARD_MANIFEST.md"
        content = path.read_text()
        hard_laws = [
            "No RunEnvelope, no run",
            "No DoneContract, no code",
            "No ProofPacket, no PASS",
            "No registry entry, no production use",
            "No approval, no external side effect",
            "Verifier must not receive Generator or Evaluator chat history",
        ]
        for law in hard_laws:
            assert law in content, f"Manifest missing hard law: {law}"

    def test_manifest_has_build_order(self) -> None:
        """Manifest must define the 7-phase build order."""
        path = REPO_ROOT / "docs" / "rigforge-build-cards" / "BUILD_CARD_MANIFEST.md"
        content = path.read_text()
        phases = [
            "Repo Bootstrap",
            "Environment Bootstrap",
            "Runtime Kernel",
            "Control Plane",
            "GEV Loop",
            "DeerFlow",
            "Cockpit",
        ]
        for phase in phases:
            assert phase in content, f"Manifest missing phase: {phase}"


class TestRigDoctrine:
    def test_doctrine_exists(self) -> None:
        """RIG_DOCTRINE.md must exist."""
        path = REPO_ROOT / "RIG_DOCTRINE.md"
        assert path.is_file(), "RIG_DOCTRINE.md not found"

    def test_doctrine_has_core_principles(self) -> None:
        """Doctrine must contain core principles."""
        path = REPO_ROOT / "RIG_DOCTRINE.md"
        content = path.read_text()
        principles = [
            "Local-first",
            "Deterministic before agentic",
            "A1 first",
            "Research before synthesis",
            "Escalate instead of failing",
            "ProofPacket or it did not happen",
            "temperature=0",
        ]
        for principle in principles:
            assert principle in content, f"Doctrine missing principle: {principle}"
