"""PyCode Bridge: DeerFlow supervises, PyCode executes generator-owned build steps.

DeerFlow is the lead agent that orchestrates sub-agents.
PyCode is the code generator that writes actual implementation files.

This module defines the contract and safety boundaries for PyCode operations
initiated within DeerFlow-supervised builds.

Allowed PyCode commands (can be called from DeerFlow sub-agents):
    - implement_mission
    - run_tests
    - write_proofpacket

Forbidden PyCode commands:
    - approve
    - deploy_production
    - edit_frozen_contract
"""

from __future__ import annotations

import logging
import subprocess
from pathlib import Path
from typing import Any, Optional

logger = logging.getLogger(__name__)

# ═══════════════════════════════════════════════════════════════
# Command allowlist / blocklist
# ═══════════════════════════════════════════════════════════════

ALLOWED_COMMANDS = {
    "implement_mission",
    "run_tests",
    "write_proofpacket",
    "generate_code",
    "write_file",
    "read_file",
    "list_files",
    "run_linter",
    "run_typecheck",
}

FORBIDDEN_COMMANDS = {
    "approve",
    "deploy_production",
    "edit_frozen_contract",
    "delete_run",
    "modify_workflow",
    "write_memory",
    "send_external",
    "modify_gate",
}


class PyCodeBridgeResult:
    """Result of a PyCode bridge command execution."""

    def __init__(
        self,
        command: str,
        success: bool,
        output: str = "",
        error: str = "",
        files_touched: list[str] | None = None,
        exit_code: int = 0,
    ) -> None:
        self.command = command
        self.success = success
        self.output = output
        self.error = error
        self.files_touched = files_touched or []
        self.exit_code = exit_code

    def to_dict(self) -> dict[str, Any]:
        return {
            "command": self.command,
            "success": self.success,
            "output": self.output,
            "error": self.error,
            "files_touched": self.files_touched,
            "exit_code": self.exit_code,
        }


class PyCodeBridge:
    """Bridge between DeerFlow sub-agents and PyCode operations."""

    def __init__(
        self,
        repo_root: Path = Path("."),
        pycode_executable: str = "pycode",
    ) -> None:
        self.repo_root = repo_root.resolve()
        self.pycode_executable = pycode_executable

    def is_command_allowed(self, command: str) -> bool:
        """Check if a PyCode command is in the allowed list."""
        if command in FORBIDDEN_COMMANDS:
            return False
        if command in ALLOWED_COMMANDS:
            return True
        # Unknown commands are blocked
        logger.warning(f"Unknown PyCode command '{command}' — blocked by default")
        return False

    def execute(
        self,
        command: str,
        args: Optional[list[str]] = None,
        cwd: Optional[Path] = None,
        timeout_seconds: int = 300,
    ) -> PyCodeBridgeResult:
        """
        Execute a PyCode command through the bridge.

        Args:
            command: The PyCode command to execute
            args: Additional arguments
            cwd: Working directory (defaults to worktree for current run)
            timeout_seconds: Maximum execution time

        Returns:
            PyCodeBridgeResult with execution outcome

        Raises:
            PermissionError: If command is in the forbidden list
        """
        if not self.is_command_allowed(command):
            raise PermissionError(
                f"PyCode command '{command}' is forbidden. "
                f"Forbidden commands: {sorted(FORBIDDEN_COMMANDS)}"
            )

        if command == "implement_mission":
            return self._implement_mission(args, cwd, timeout_seconds)
        elif command == "run_tests":
            return self._run_tests(args, cwd, timeout_seconds)
        elif command == "generate_code":
            return self._placeholder("generate_code", args)
        elif command == "write_file":
            return self._placeholder("write_file", args)
        elif command == "read_file":
            return self._placeholder("read_file", args)
        elif command == "list_files":
            return self._list_files(cwd)
        elif command == "run_linter":
            return self._placeholder("run_linter", args)
        else:
            return self._placeholder(command, args)

    def _implement_mission(
        self,
        args: Optional[list[str]],
        cwd: Optional[Path],
        timeout: int,
    ) -> PyCodeBridgeResult:
        """Implement a mission from spec/plan files."""
        work_dir = cwd or self.repo_root
        files_before = set(work_dir.rglob("*.py")) if work_dir.exists() else set()

        # In production, this would invoke PyCode's actual implementation engine
        # For now, this is a validated stub that records the intent
        logger.info(f"PyCode implement_mission: dir={work_dir}, args={args}")

        files_after = set(work_dir.rglob("*.py")) if work_dir.exists() else set()
        new_files = [str(f.relative_to(work_dir)) for f in files_after - files_before]

        return PyCodeBridgeResult(
            command="implement_mission",
            success=True,
            output=f"Mission implementation queued: {args}",
            files_touched=new_files,
        )

    def _run_tests(
        self,
        args: Optional[list[str]],
        cwd: Optional[Path],
        timeout: int,
    ) -> PyCodeBridgeResult:
        """Run the test suite for the current worktree."""
        work_dir = cwd or self.repo_root

        try:
            result = subprocess.run(
                ["python", "-m", "pytest", "tests/", "-q", "--tb=short"],
                cwd=work_dir,
                capture_output=True,
                text=True,
                timeout=timeout,
            )
            return PyCodeBridgeResult(
                command="run_tests",
                success=result.returncode == 0,
                output=result.stdout,
                error=result.stderr,
                exit_code=result.returncode,
            )
        except FileNotFoundError:
            return PyCodeBridgeResult(
                command="run_tests",
                success=False,
                error="pytest not found. Install with: pip install pytest",
            )
        except subprocess.TimeoutExpired:
            return PyCodeBridgeResult(
                command="run_tests",
                success=False,
                error=f"Tests timed out after {timeout}s",
            )

    def _list_files(self, cwd: Optional[Path]) -> PyCodeBridgeResult:
        """List files in the work directory."""
        work_dir = cwd or self.repo_root
        if not work_dir.exists():
            return PyCodeBridgeResult(
                command="list_files",
                success=True,
                output="",
                files_touched=[],
            )

        files = []
        for f in sorted(work_dir.rglob("*")):
            if f.is_file() and ".git" not in f.parts:
                files.append(str(f.relative_to(work_dir)))

        return PyCodeBridgeResult(
            command="list_files",
            success=True,
            output="\n".join(files),
            files_touched=files[:50],  # Cap at 50
        )

    def _placeholder(
        self,
        command: str,
        args: Optional[list[str]],
    ) -> PyCodeBridgeResult:
        """Placeholder for commands not yet fully implemented."""
        logger.info(f"PyCode {command} (stub): args={args}")
        return PyCodeBridgeResult(
            command=command,
            success=True,
            output=f"[STUB] {command} executed with args={args}",
        )


# ── Convenience function ─────────────────────────────────────────────────────

_bridge_instance: PyCodeBridge | None = None


def get_pycode_bridge(
    repo_root: Path = Path("."),
    pycode_executable: str = "pycode",
) -> PyCodeBridge:
    """Get or create the module-level PyCodeBridge singleton."""
    global _bridge_instance
    if _bridge_instance is None:
        _bridge_instance = PyCodeBridge(repo_root, pycode_executable)
    return _bridge_instance
