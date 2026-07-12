"""Tests for .claude/hooks/log_instructions_loaded.py (InstructionsLoaded
hook, H7_skills_and_rules). Subprocess-based, matching the existing hook
test convention (tests/tools/test_claude_hooks.py,
test_log_director_input_hook.py).

Does not assert against the REAL docs/observability/instructions_loaded_log.jsonl
-- each test points the hook at an isolated tmp_path log file via monkeypatched
cwd/PROJECT_DIR is not practical for a subprocess, so instead these tests
invoke the hook's own main() function in-process with a monkeypatched
LOG_PATH, the same isolation pattern background/decision_log.py's own tests
use. A separate subprocess smoke test confirms the script never blocks/exits
non-zero regardless of input, matching the sibling hook tests' own contract.
"""
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
HOOK_PATH = REPO_ROOT / ".claude" / "hooks" / "log_instructions_loaded.py"

sys.path.insert(0, str(REPO_ROOT / ".claude" / "hooks"))
import log_instructions_loaded as hook  # noqa: E402


@pytest.fixture(autouse=True)
def _isolate(tmp_path, monkeypatch):
    monkeypatch.setattr(hook, "LOG_PATH", tmp_path / "instructions_loaded_log.jsonl")


def _run_main(payload: dict, monkeypatch):
    # The hook's own PYTEST_CURRENT_TEST guard would otherwise no-op this
    # in-process main() call -- pytest re-sets this env var fresh for every
    # test, so deleting it here (to exercise the real write path against the
    # isolated tmp_path LOG_PATH from the fixture above) cannot leak into
    # other tests. Same convention as tests/background/test_director_input_log.py.
    # Deliberately called only from here, never from the subprocess smoke
    # tests below -- monkeypatch.delenv edits THIS process's os.environ,
    # which subprocess.run() would inherit by default, silently defeating
    # the guard those tests exist specifically to prove engages for real.
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)
    import io
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps(payload)))
    return hook.main()


def test_logs_a_path_glob_match_entry(monkeypatch):
    rc = _run_main(
        {"load_reason": "path_glob_match", "file_path": "/repo/.claude/rules/epistemic-wall-company.md",
         "file_name": "epistemic-wall-company.md"},
        monkeypatch,
    )
    assert rc == 0
    entries = [json.loads(l) for l in hook.LOG_PATH.read_text().splitlines() if l]
    assert len(entries) == 1
    assert entries[0]["load_reason"] == "path_glob_match"
    assert entries[0]["file_name"] == "epistemic-wall-company.md"


def test_appends_multiple_entries_not_overwrite(monkeypatch):
    _run_main({"load_reason": "session_start", "file_path": "/repo/CLAUDE.md", "file_name": "CLAUDE.md"}, monkeypatch)
    _run_main({"load_reason": "path_glob_match", "file_path": "/repo/x.md", "file_name": "x.md"}, monkeypatch)
    entries = [json.loads(l) for l in hook.LOG_PATH.read_text().splitlines() if l]
    assert len(entries) == 2


def test_malformed_stdin_degrades_gracefully(monkeypatch):
    monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)  # exercise the JSON-parse path, not the test-guard's own early return
    import io
    monkeypatch.setattr(sys, "stdin", io.StringIO("not json at all"))
    rc = hook.main()
    assert rc == 0
    assert not hook.LOG_PATH.exists()


def test_pytest_guard_no_ops_even_with_valid_payload(monkeypatch):
    """The guard itself, exercised directly (PYTEST_CURRENT_TEST left set,
    the real condition inside a live test run): main() must return 0
    without writing anything, even given an otherwise-valid payload -- this
    is what stopped the real pollution incident the subprocess tests below
    would otherwise reproduce on every CI run."""
    import io
    monkeypatch.setattr(sys, "stdin", io.StringIO(json.dumps({
        "load_reason": "path_glob_match", "file_path": "/x/y.md", "file_name": "y.md",
    })))
    rc = hook.main()
    assert rc == 0
    assert not hook.LOG_PATH.exists()


def test_missing_fields_do_not_crash(monkeypatch):
    rc = _run_main({}, monkeypatch)
    assert rc == 0
    entries = [json.loads(l) for l in hook.LOG_PATH.read_text().splitlines() if l]
    assert entries[0]["load_reason"] is None


def _run_subprocess(payload_str: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(HOOK_PATH)],
        input=payload_str,
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


class TestLogInstructionsLoadedHookSubprocess:
    """Smoke tests via a real subprocess invocation -- confirms the script
    itself (not just the imported function) never blocks or exits non-zero,
    the actual contract InstructionsLoaded hooks must honour (exit code is
    ignored by the harness for this event type, but the script must still
    never hang or crash)."""

    def test_real_subprocess_exits_zero_for_normal_payload(self):
        result = _run_subprocess(json.dumps({
            "load_reason": "path_glob_match", "file_path": "/x/company/y.py", "file_name": "y.py",
        }))
        assert result.returncode == 0

    def test_real_subprocess_exits_zero_for_malformed_input(self):
        result = _run_subprocess("{{{not json")
        assert result.returncode == 0
