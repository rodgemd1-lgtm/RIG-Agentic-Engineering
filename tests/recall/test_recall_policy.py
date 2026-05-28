import json
import subprocess
import sys
from pathlib import Path


def run_check():
    script = Path(__file__).parents[2] / 'scripts' / 'recall_check.py'
    result = subprocess.run([sys.executable, str(script)], capture_output=True, text=True)
    return result


def test_recall_check_ready_or_degraded():
    result = run_check()
    # The script should exit with 0 (READY or DEGRADED)
    assert result.returncode == 0, f"Recall check failed: {result.stdout}\n{result.stderr}"
    data = json.loads(result.stdout)
    # Must contain required fields
    for key in [
        'recall_api_key_present',
        'gitignore_protects_env',
        'policy_doc_exists',
        'status',
    ]:
        assert key in data
    # Status should be READY, DEGRADED, or BLOCKED (but not BLOCKED in CI env where key may be missing)
    assert data['status'] in ('READY', 'DEGRADED', 'BLOCKED')


def test_policy_doc_exists():
    policy = Path(__file__).parents[2] / 'docs' / 'recall' / 'RECALL_ACCESS_POLICY.md'
    assert policy.is_file(), 'Recall policy doc missing'


def test_gitignore_protects_env():
    gi = Path(__file__).parents[3] / '.gitignore'
    content = gi.read_text()
    assert any(pat in content for pat in ('.env', '.env.*'))
