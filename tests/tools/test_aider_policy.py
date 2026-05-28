import json
import subprocess
import sys
from pathlib import Path


def run_verify():
    script = Path(__file__).parents[2] / "scripts" / "verify_aider.py"
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    return result

def test_aider_verification_success():
    result = run_verify()
    assert result.returncode == 0, f"Aider verification failed: {result.stdout}\n{result.stderr}"
    data = json.loads(result.stdout)
    # All checks must be pass
    for check in data["checks"].values():
        assert check["status"] == "pass"
    assert data["status"] == "AVAILABLE"

def test_aider_registry_entry_exists():
    repo_root = Path(__file__).parents[2]
    pending = repo_root / "docs" / "pending_registry_entries" / "aider_generator_tool.yaml"
    live = repo_root / "config" / "tool_registry.yaml"
    assert pending.exists() or live.exists()
