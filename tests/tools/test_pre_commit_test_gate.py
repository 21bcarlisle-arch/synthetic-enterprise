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


def test_committed_hook_invokes_the_gate_and_aborts_on_failure():
    # Reconstruct-from-repo: the committed hook itself must call the gate and abort on non-zero.
    hook = (ROOT / "tools" / "git-hooks" / "pre-commit").read_text()
    assert "tools/pre_commit_test_gate.py" in hook
    assert "exit 1" in hook                                   # a gate failure ABORTS the commit
    # and the installer that makes it reconstruct-from-repo exists + sets core.hooksPath
    installer = (ROOT / "tools" / "install_git_hooks.sh").read_text()
    assert "core.hooksPath" in installer and "tools/git-hooks" in installer
