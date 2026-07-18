"""Pre-commit TEST GATE selection logic (director P0, 2026-07-17).

The gate's job: whenever a CODE/config file is staged, run the safety-control set + the tests for
each changed source file, and ABORT the commit on any failure -- so a red commit is structurally
impossible. These test the SELECTION logic (which tests run for which changeset); the end-to-end
"a commit with a failing test is REFUSED" is proven live against the real git hook.
"""
from __future__ import annotations

import importlib.util
import os
import subprocess
import tempfile
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


def test_gitless_env_strips_all_GIT_star_directly():
    # Direct unit proof of the helper the shipped fix actually calls: no GIT_* survives, and
    # everything else passes through untouched.
    fake_env = {
        "GIT_DIR": "/fake/.git",
        "GIT_INDEX_FILE": "/fake/.git/index",
        "GIT_WORK_TREE": "/fake",
        "GIT_PREFIX": "",
        "PATH": "/usr/bin:/bin",
        "HOME": "/home/nobody",
    }
    result = gate._gitless_env(fake_env)
    assert [k for k in result if k.startswith("GIT_")] == []
    assert result["PATH"] == "/usr/bin:/bin"
    assert result["HOME"] == "/home/nobody"


def _run_git(args, cwd, env):
    return subprocess.run(
        ["git", *args], cwd=cwd, env=env, capture_output=True, text=True,
    )


def _make_isolated_repo(clean_env):
    """A throwaway repo in its own tempdir -- NEVER the real .git. Returns its path with an
    initial commit (so it has a real index/HEAD) and core.bare confirmed false."""
    repo = tempfile.mkdtemp(prefix="h24_isolated_repo_")
    _run_git(["init", "-q"], cwd=repo, env=clean_env)
    _run_git(["config", "user.email", "h24-test@example.invalid"], cwd=repo, env=clean_env)
    _run_git(["config", "user.name", "H24 Mutation Test"], cwd=repo, env=clean_env)
    (Path(repo) / "seed.txt").write_text("seed\n")
    _run_git(["add", "seed.txt"], cwd=repo, env=clean_env)
    _run_git(["commit", "-q", "-m", "initial"], cwd=repo, env=clean_env)
    baseline_bare = _run_git(
        ["config", "--get", "core.bare"], cwd=repo, env=clean_env
    ).stdout.strip()
    assert baseline_bare == "false", "isolated repo fixture must start non-bare"
    return repo


def _repo_core_bare(repo, clean_env):
    return _run_git(["config", "--get", "core.bare"], cwd=repo, env=clean_env).stdout.strip()


def test_r15_scrub_prevents_leaked_git_dir_corruption__mutation_proof():
    """R15 mutation proof (CONTROLS_THAT_CANNOT_FAIL): prove the GIT_* scrub in
    tools/pre_commit_test_gate.py::_gitless_env is the thing standing between a leaked
    GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE and a corrupted repo -- in BOTH directions -- entirely
    against a throwaway isolated repo, never the real worktree.

    Named defect (H26/H24 incident): a gate-run test inherits GIT_DIR/GIT_WORK_TREE/GIT_INDEX_FILE
    pointing at an in-progress commit; an unscrubbed subprocess env lets a stray `git` invocation
    obey those leaked vars and mutate that repo's state (e.g. flip core.bare) regardless of its own
    cwd -- observed as index corruption / a tree-deleting commit / core.bare=true in the real
    incident.
    """
    clean_env = gate._gitless_env(dict(os.environ))  # our own test process must not leak either
    isolated_repo = _make_isolated_repo(clean_env)

    # A neutral cwd that is NOT a git repo at all (and is neither the isolated repo nor the real
    # worktree) -- so the only way `git config` can succeed is by obeying a leaked GIT_DIR.
    neutral_cwd = tempfile.mkdtemp(prefix="h24_neutral_cwd_")

    leaked_env = dict(clean_env)
    leaked_env["GIT_DIR"] = str(Path(isolated_repo) / ".git")
    leaked_env["GIT_WORK_TREE"] = isolated_repo
    leaked_env["GIT_INDEX_FILE"] = str(Path(isolated_repo) / ".git" / "index")

    # --- WITH the shipped scrub (the real code path: gate._gitless_env applied to the leak) ---
    scrubbed_env = gate._gitless_env(leaked_env)
    assert [k for k in scrubbed_env if k.startswith("GIT_")] == []
    with_scrub = _run_git(
        ["config", "core.bare", "true"], cwd=neutral_cwd, env=scrubbed_env,
    )
    assert with_scrub.returncode != 0, (
        "with GIT_* scrubbed and a non-repo cwd, `git config` must FAIL -- if it succeeds, "
        "the leaked GIT_DIR is still reaching it somehow"
    )
    assert _repo_core_bare(isolated_repo, clean_env) == "false", (
        "the scrub must leave the isolated repo untouched"
    )

    # --- WITHOUT the scrub (the mutation: same leak, but passed straight through unscrubbed,
    # exactly what the pre-fix gate did) -- this must REPRODUCE the corruption, proving the
    # defect is real and the scrub is what prevents it. ---
    without_scrub = _run_git(
        ["config", "core.bare", "true"], cwd=neutral_cwd, env=leaked_env,
    )
    assert without_scrub.returncode == 0, (
        "expected the unscrubbed leaked GIT_DIR to let `git config` succeed against the "
        "isolated repo -- if it didn't, this test can't demonstrate the defect"
    )
    assert _repo_core_bare(isolated_repo, clean_env) == "true", (
        "the unscrubbed leak must reproduce the corruption (core.bare flipped) on the "
        "ISOLATED repo -- proving the named H24/H26 defect is real"
    )


def test_committed_hook_invokes_the_gate_and_aborts_on_failure():
    # Reconstruct-from-repo: the committed hook itself must call the gate and abort on non-zero.
    hook = (ROOT / "tools" / "git-hooks" / "pre-commit").read_text()
    assert "tools/pre_commit_test_gate.py" in hook
    assert "exit 1" in hook                                   # a gate failure ABORTS the commit
    # and the installer that makes it reconstruct-from-repo exists + sets core.hooksPath
    installer = (ROOT / "tools" / "install_git_hooks.sh").read_text()
    assert "core.hooksPath" in installer and "tools/git-hooks" in installer
