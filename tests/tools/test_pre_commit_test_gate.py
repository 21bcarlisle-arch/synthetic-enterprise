"""Pre-commit TEST GATE selection logic (director P0, 2026-07-17).

The gate's job: whenever a CODE/config file is staged, run the safety-control set + the tests for
each changed source file, and ABORT the commit on any failure -- so a red commit is structurally
impossible. These test the SELECTION logic (which tests run for which changeset); the end-to-end
"a commit with a failing test is REFUSED" is proven live against the real git hook.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GATE_PATH = ROOT / "tools" / "pre_commit_test_gate.py"

spec = importlib.util.spec_from_file_location("pre_commit_test_gate", GATE_PATH)
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def test_pure_docs_or_data_commit_runs_NOTHING():
    # A commit touching only status/report/site/observability cannot break a control -> skip.
    assert gate.select_targets(["docs/status/LATEST.md"]) == []
    assert gate.select_targets(["site/data/dashboard.json", "docs/reports/ANNUAL_REPORT.md"]) == []


def test_any_code_change_runs_the_safety_control_set():
    # Even a code change with no dedicated test file still runs the always-on control set.
    targets = gate.select_targets(["saas/some_new_module.py"])
    assert set(gate.CONTROL_TESTS) <= set(targets)


def test_changed_source_pulls_in_its_own_test_file():
    targets = gate.select_targets(["background/supervisor.py"])
    assert "tests/background/test_supervisor.py" in targets
    assert set(gate.CONTROL_TESTS) <= set(targets)


def test_changed_test_file_maps_to_itself():
    assert gate.tests_for("tests/background/test_fork_reconciler.py") == \
        ["tests/background/test_fork_reconciler.py"]


def test_non_python_file_maps_to_no_tests():
    assert gate.tests_for("docs/status/LATEST.md") == []
    assert gate.tests_for("background/process_manifest.yaml") == []


def test_config_change_triggers_the_control_set_even_without_a_mapped_test():
    # A YAML/config under a code prefix still triggers the gate (it can break a control's inputs).
    targets = gate.select_targets(["background/process_manifest.yaml"])
    assert set(gate.CONTROL_TESTS) <= set(targets)


def test_control_test_files_all_exist():
    # The always-on set must reference real files, or the gate silently protects nothing.
    for t in gate.CONTROL_TESTS:
        assert (ROOT / t).exists(), f"control test missing: {t}"


def test_pytest_subprocess_env_strips_GIT_star(monkeypatch):
    # H24 regression: during a `git commit` the hook inherits GIT_INDEX_FILE/GIT_DIR/GIT_WORK_TREE
    # pointing at the in-progress commit. If those leak into the pytest subprocess, git-touching
    # tests corrupt the REAL worktree index (observed: phantom deletions, once a tree-deleting
    # commit; likely the core.bare=true setter). The gate MUST run pytest with GIT_* scrubbed.
    monkeypatch.setattr(gate, "staged_files", lambda: ["background/supervisor.py"])
    monkeypatch.setattr(gate, "select_targets", lambda files: ["tests/background/test_supervisor.py"])
    for k in ("GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE", "GIT_PREFIX"):
        monkeypatch.setenv(k, "/should/not/leak")
    captured = {}

    class _R:
        returncode = 0

    def _fake_run(cmd, *a, **kw):
        captured["env"] = kw.get("env")
        return _R()

    monkeypatch.setattr(gate.subprocess, "run", _fake_run)
    assert gate.main() == 0
    env = captured["env"]
    assert env is not None, "the pytest subprocess must be given an explicit (scrubbed) env"
    leaked = sorted(k for k in env if k.startswith("GIT_"))
    assert leaked == [], f"GIT_* leaked into the gate's pytest subprocess: {leaked}"


def test_committed_hook_invokes_the_gate_and_aborts_on_failure():
    # Reconstruct-from-repo: the committed hook itself must call the gate and abort on non-zero.
    hook = (ROOT / "tools" / "git-hooks" / "pre-commit").read_text()
    assert "tools/pre_commit_test_gate.py" in hook
    assert "exit 1" in hook                                   # a gate failure ABORTS the commit
    # and the installer that makes it reconstruct-from-repo exists + sets core.hooksPath
    installer = (ROOT / "tools" / "install_git_hooks.sh").read_text()
    assert "core.hooksPath" in installer and "tools/git-hooks" in installer
