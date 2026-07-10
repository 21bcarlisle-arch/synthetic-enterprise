"""Tests for the PreToolUse lifecycle hooks in .claude/hooks/.

HARNESS_BEST_PRACTICE_ADOPTION.md item 1: sudo ban (1b) and the
unevidenced-claim pixel rule (1c). Each hook is a standalone script reading
a Claude Code PreToolUse JSON payload on stdin and signalling block via
exit code 2 (per the verified real hooks schema, docs/design/
HARNESS_BEST_PRACTICE_ASSESSMENT.md).
"""
import json
import subprocess
import sys
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
BLOCK_SUDO = REPO_ROOT / ".claude" / "hooks" / "block_sudo.py"
BLOCK_CLAIM = REPO_ROOT / ".claude" / "hooks" / "block_unevidenced_claim.py"
MARKER = REPO_ROOT / "docs" / "observability" / ".last_live_verification"


def _run(script: Path, payload: dict) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps(payload),
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


class TestBlockSudo:
    def test_blocks_plain_sudo(self):
        result = _run(BLOCK_SUDO, {"tool_name": "Bash", "tool_input": {"command": "sudo apt-get install foo"}})
        assert result.returncode == 2
        assert "sudo is banned" in result.stderr

    def test_blocks_sudo_after_chain_operator(self):
        result = _run(BLOCK_SUDO, {"tool_name": "Bash", "tool_input": {"command": "cd /tmp && sudo rm -rf /"}})
        assert result.returncode == 2

    def test_allows_normal_command(self):
        result = _run(BLOCK_SUDO, {"tool_name": "Bash", "tool_input": {"command": "ls -la"}})
        assert result.returncode == 0
        assert result.stderr == ""

    def test_allows_word_containing_sudo_substring(self):
        # "pseudocode" contains "sudo" as a substring but not as a command word.
        result = _run(BLOCK_SUDO, {"tool_name": "Bash", "tool_input": {"command": "echo pseudocode"}})
        assert result.returncode == 0

    def test_ignores_non_bash_tool(self):
        result = _run(BLOCK_SUDO, {"tool_name": "Read", "tool_input": {"file_path": "sudo_readme.txt"}})
        assert result.returncode == 0

    def test_ignores_malformed_json(self):
        result = subprocess.run(
            [sys.executable, str(BLOCK_SUDO)],
            input="not json",
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        assert result.returncode == 0


class TestBlockUnevidencedClaim:
    def setup_method(self):
        if MARKER.exists():
            MARKER.unlink()

    def teardown_method(self):
        if MARKER.exists():
            MARKER.unlink()

    def test_blocks_claim_with_no_marker(self):
        cmd = "python3 -c \"from background.ntfy_utils import send_ntfy; send_ntfy('Bug fixed and confirmed live')\""
        result = _run(BLOCK_CLAIM, {"tool_name": "Bash", "tool_input": {"command": cmd}})
        assert result.returncode == 2
        assert "no evidence marker exists" in result.stderr

    def test_allows_claim_with_fresh_marker(self):
        MARKER.parent.mkdir(parents=True, exist_ok=True)
        MARKER.touch()
        cmd = "python3 -c \"from background.ntfy_utils import send_ntfy; send_ntfy('Bug fixed and confirmed live')\""
        result = _run(BLOCK_CLAIM, {"tool_name": "Bash", "tool_input": {"command": cmd}})
        assert result.returncode == 0

    def test_blocks_claim_with_stale_marker(self):
        MARKER.parent.mkdir(parents=True, exist_ok=True)
        MARKER.touch()
        old = time.time() - (31 * 60)
        import os
        os.utime(MARKER, (old, old))
        cmd = "python3 -c \"from background.ntfy_utils import send_ntfy; send_ntfy('Deployed and verified live')\""
        result = _run(BLOCK_CLAIM, {"tool_name": "Bash", "tool_input": {"command": cmd}})
        assert result.returncode == 2
        assert "old" in result.stderr

    def test_allows_non_claim_ntfy_message(self):
        cmd = "python3 -c \"from background.ntfy_utils import send_ntfy; send_ntfy('Status update: still investigating')\""
        result = _run(BLOCK_CLAIM, {"tool_name": "Bash", "tool_input": {"command": cmd}})
        assert result.returncode == 0

    def test_ignores_non_send_ntfy_bash_command(self):
        cmd = "echo 'this is fixed and live'"
        result = _run(BLOCK_CLAIM, {"tool_name": "Bash", "tool_input": {"command": cmd}})
        assert result.returncode == 0

    def test_ignores_non_bash_tool(self):
        result = _run(BLOCK_CLAIM, {"tool_name": "Write", "tool_input": {"content": "fixed and live"}})
        assert result.returncode == 0

    def test_allows_prose_describing_send_ntfy_without_calling_it(self):
        # Regression: a git commit message *describing* the hook (e.g. "blocks
        # a send_ntfy() call claiming fixed/live/deployed") must not itself
        # trip the hook -- it never imports or invokes send_ntfy for real.
        cmd = (
            "git commit -m 'Add hook that blocks a send_ntfy() call claiming "
            "fixed/live/deployed/confirmed/verified unless evidence exists'"
        )
        result = _run(BLOCK_CLAIM, {"tool_name": "Bash", "tool_input": {"command": cmd}})
        assert result.returncode == 0
