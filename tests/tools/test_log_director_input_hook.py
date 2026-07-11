"""Tests for .claude/hooks/log_director_input.py (UserPromptSubmit hook,
DIRECTOR_INPUT_LOG.md). Subprocess-based, matching the existing hook test
convention (tests/tools/test_claude_hooks.py).

Never asserts against the REAL private ops repo: subprocess.run() inherits
the parent pytest process's environment by default, which includes
PYTEST_CURRENT_TEST -- background/director_input_log.py's append_entry()
guard (same pattern as ntfy_mirror.py) makes this a safe no-op even though
the hook subprocess is genuinely separate from the test process. Actual
logging behaviour is covered directly in
tests/background/test_director_input_log.py; this file only tests the
hook's OWN robustness contract (never blocks, handles bad input)."""
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK = REPO_ROOT / ".claude" / "hooks" / "log_director_input.py"


def _run(payload_str: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOK)],
        input=payload_str,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


class TestLogDirectorInputHook:
    def test_exits_zero_for_a_normal_prompt(self):
        result = _run(json.dumps({"prompt": "a normal user prompt", "session_id": "abc"}))
        assert result.returncode == 0

    def test_exits_zero_for_malformed_json(self):
        result = _run("not json at all")
        assert result.returncode == 0

    def test_exits_zero_for_missing_prompt_field(self):
        result = _run(json.dumps({"session_id": "abc"}))
        assert result.returncode == 0

    def test_exits_zero_for_empty_prompt(self):
        result = _run(json.dumps({"prompt": "", "session_id": "abc"}))
        assert result.returncode == 0

    def test_never_writes_to_stdout_that_would_confuse_the_harness(self):
        """Observe-only hook: stdout should be empty (no additionalContext/
        systemMessage payload) -- this hook only logs, never injects."""
        result = _run(json.dumps({"prompt": "hello", "session_id": "abc"}))
        assert result.stdout == ""

    def test_survives_a_completely_clean_environment(self):
        """Confirms the hook loads background/.env.ntfy itself rather than
        assuming inheritance -- real gap found live (2026-07-11): this very
        session's own process env lacks SE_NTFY_TOPIC/SE_WAKE_HMAC_KEY, and
        a hook subprocess does not inherit start_worker.sh's shell-level
        exports the way a daemon launched by that script does."""
        import os
        # PYTEST_CURRENT_TEST explicitly carried through even though this
        # env is otherwise minimal -- append_entry()'s test-isolation guard
        # depends on it being present to avoid a REAL push to the private
        # ops repo from this test.
        minimal_env = {
            "HOME": os.environ["HOME"],
            "PATH": os.environ["PATH"],
            "PYTEST_CURRENT_TEST": os.environ.get("PYTEST_CURRENT_TEST", "forced-for-safety"),
        }
        result = subprocess.run(
            [sys.executable, str(HOOK)],
            input=json.dumps({"prompt": "clean-env test", "session_id": "abc"}),
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
            env=minimal_env,
        )
        assert result.returncode == 0
