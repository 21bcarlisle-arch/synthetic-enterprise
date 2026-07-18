"""R15 mutation tests for H26 -- the cause-agnostic core.bare corruption guard
(`background/tree_lock.py::assert_repo_not_bare`).

Real incident this session: the main repo's `core.bare` silently flipped to `true` mid-session,
silently breaking EVERY working-tree git operation (commit, publish, status) until manually reset.
The root TRIGGER was already fixed at the source (H24: `tools/pre_commit_test_gate.py` scrubs
`GIT_*` env vars from the pytest subprocess env). This guard is CAUSE-AGNOSTIC defense-in-depth: it
must make ANY future bare-repo state loud, never silent (R15 fail-silent doctrine -- a control that
passes when it can't actually check is a failed control, not a passed one).

CRITICAL SAFETY NOTE: every test here operates on an ISOLATED tmp repo created via
`tempfile.mkdtemp()` + `git init`. The real point of the guarded defect is that flipping
`core.bare=true` on a genuine working tree is DANGEROUS (it is exactly what broke the main repo
this session) -- so this file NEVER touches this repo's own `.git`, and NEVER runs
`git config core.bare true` against the working tree these tests execute inside. Every mutation
happens against a disposable throwaway repo instead.
"""
from __future__ import annotations

import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

from background import tree_lock as tl


def _git(repo_dir: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=str(repo_dir), capture_output=True, text=True, check=True,
    )


@pytest.fixture(autouse=True)
def _isolated_notify_transitions(tmp_path, monkeypatch):
    """Redirect the notify contract's transition-state store to a throwaway file for every test
    in this module (matches tests/background/test_notify_contract.py's own pattern) -- these tests
    must never read or write the real project's docs/observability/.notify_transitions.json."""
    import background.notify as notify_mod
    monkeypatch.setattr(notify_mod, "TRANSITIONS_FILE", tmp_path / ".notify_transitions.json")


@pytest.fixture()
def isolated_repo():
    """A disposable, throwaway git repo in a tmp dir -- never the real project tree."""
    tmp = Path(tempfile.mkdtemp(prefix="h26_core_bare_guard_test_"))
    _git(tmp, "init")
    # A commit isn't required for `git rev-parse --is-bare-repository` to work, but keep the repo
    # in a realistic post-init state.
    _git(tmp, "config", "user.email", "test@example.invalid")
    _git(tmp, "config", "user.name", "H26 Test")
    yield tmp
    shutil.rmtree(tmp, ignore_errors=True)


# ── Mutation direction 1: the named defect actually fires ──────────────────────────────
def test_guard_fires_and_repairs_on_core_bare_true(isolated_repo, monkeypatch):
    """The guard's own named defect: a working tree with core.bare=true. Must RAISE
    RepoBareError AND auto-repair (core.bare flipped back to false) -- proves this is not a
    tautology (it reacts to the real git-reported state) and not fail-open (it does not pass
    silently on the corrupted state)."""
    # Isolate the notify transition store so this test cannot pollute (or be polluted by) the
    # real project's alarm state.
    monkeypatch.setattr(
        tl, "_BARE_REPO_TRANSITION_KEY", "test_h26_core_bare_true", raising=False
    )

    _git(isolated_repo, "config", "core.bare", "true")
    assert _git(isolated_repo, "config", "--get", "core.bare").stdout.strip() == "true"

    with pytest.raises(tl.RepoBareError):
        tl.assert_repo_not_bare(isolated_repo)

    # Auto-repair: core.bare must be back to false afterwards.
    repaired = _git(isolated_repo, "config", "--get", "core.bare").stdout.strip()
    assert repaired == "false", f"expected auto-repair to flip core.bare back to false, got {repaired!r}"


def test_guard_alarms_via_notify_on_core_bare_true(isolated_repo, monkeypatch):
    """The guard must attempt to fire a real_alarm (not swallow the alarm silently), proving the
    alarm wiring is live, not decorative. We don't assert an actual network send (ntfy_utils has
    its own hard pytest guard) -- we assert notify() was invoked with kind='real_alarm'."""
    monkeypatch.setattr(
        tl, "_BARE_REPO_TRANSITION_KEY", "test_h26_core_bare_true_alarm", raising=False
    )
    _git(isolated_repo, "config", "core.bare", "true")

    calls = []
    import background.notify as notify_mod

    def _fake_notify(message, *, kind, **kwargs):
        calls.append((message, kind, kwargs))
        return "test-sent"

    monkeypatch.setattr(notify_mod, "notify", _fake_notify)

    with pytest.raises(tl.RepoBareError):
        tl.assert_repo_not_bare(isolated_repo)

    assert len(calls) == 1, "expected exactly one alarm attempt on the bare-repo defect"
    message, kind, kwargs = calls[0]
    assert kind == "real_alarm"
    assert kwargs.get("transition_key") == "test_h26_core_bare_true_alarm"
    assert "core.bare" in message


# ── Mutation direction 2: the healthy case passes silently ─────────────────────────────
def test_guard_passes_silently_on_core_bare_false(isolated_repo, monkeypatch):
    """A normal working tree (core.bare=false, the git-init default) must pass with no exception
    and no alarm -- proves the guard doesn't cry wolf on the ordinary case."""
    monkeypatch.setattr(
        tl, "_BARE_REPO_TRANSITION_KEY", "test_h26_core_bare_false", raising=False
    )
    assert _git(isolated_repo, "config", "--get", "core.bare").stdout.strip() == "false"

    calls = []
    import background.notify as notify_mod
    monkeypatch.setattr(notify_mod, "notify", lambda *a, **k: calls.append((a, k)) or "test-sent")

    tl.assert_repo_not_bare(isolated_repo)  # must not raise

    assert calls == [], "a healthy (core.bare=false) tree must never alarm"


# ── Fail-safe direction: undeterminable must neither crash nor silently pass as "safe" ──
def test_guard_is_fail_safe_not_fail_open_when_undeterminable(isolated_repo, monkeypatch, capsys):
    """When git is unavailable / the result can't be parsed, the guard must NOT raise (a commit
    must never be blocked by a transient git hiccup -- fail-SAFE) but must also NOT silently
    behave as though it confirmed a healthy tree: it must log a distinguishable warning.
    Proves this is neither a fail-open theatre control (silently 'passes' with no trace) nor a
    fail-closed control that would block all commits on an undeterminable read."""
    monkeypatch.setattr(tl, "_is_bare_repo", lambda repo_dir=None: None)

    calls = []
    import background.notify as notify_mod
    monkeypatch.setattr(notify_mod, "notify", lambda *a, **k: calls.append((a, k)) or "test-sent")

    tl.assert_repo_not_bare(isolated_repo)  # must not raise despite undeterminable state

    assert calls == [], "an undeterminable read must not fire the same alarm as a confirmed bare repo"
    captured = capsys.readouterr()
    assert "undeterminable" in captured.err.lower(), (
        "an undeterminable result must be logged, not silently treated as a confirmed pass"
    )


def test_is_bare_repo_returns_none_when_git_missing(isolated_repo, monkeypatch):
    """Direct unit check of the fail-safe primitive: a FileNotFoundError from subprocess.run
    (git not on PATH) must surface as None (undeterminable), never as False (a false 'confirmed
    healthy' claim would be a fail-open lie)."""

    def _raise_not_found(*args, **kwargs):
        raise FileNotFoundError("git not found")

    monkeypatch.setattr(tl.subprocess, "run", _raise_not_found)
    assert tl._is_bare_repo(isolated_repo) is None


def test_is_bare_repo_detects_true_and_false(isolated_repo):
    """Ground-truth sanity check of the detection primitive itself (no mocking): it must actually
    reflect git's own reported state in both directions on the isolated repo."""
    assert tl._is_bare_repo(isolated_repo) is False
    _git(isolated_repo, "config", "core.bare", "true")
    assert tl._is_bare_repo(isolated_repo) is True
    # Clean up before the fixture's teardown removes the dir anyway (defensive, not load-bearing).
    _git(isolated_repo, "config", "core.bare", "false")


# ── Wiring proof: tree_lock().__enter__ actually calls the guard ───────────────────────
def test_tree_lock_enter_raises_on_bare_repo(isolated_repo, monkeypatch, tmp_path):
    """Proves the guard is actually WIRED into tree_lock().__enter__ (H26 item 2), not merely
    defined and unused. Points tree_lock's PROJECT_DIR-derived check at the isolated bare repo (via
    monkeypatching assert_repo_not_bare's default target) and confirms entering the context raises
    RepoBareError -- so a corrupted core.bare fails loud at the very next real commit attempt."""
    monkeypatch.setattr(tl, "LOCK_FILE", tmp_path / ".tree.lock")
    monkeypatch.setattr(
        tl, "_BARE_REPO_TRANSITION_KEY", "test_h26_tree_lock_wiring", raising=False
    )
    _git(isolated_repo, "config", "core.bare", "true")

    # Redirect PROJECT_DIR so tree_lock's internal assert_repo_not_bare() call (which uses the
    # default repo_dir=None -> PROJECT_DIR) checks the isolated repo, not the real project tree.
    monkeypatch.setattr(tl, "PROJECT_DIR", isolated_repo)

    import background.notify as notify_mod
    monkeypatch.setattr(notify_mod, "notify", lambda *a, **k: "test-sent")

    with pytest.raises(tl.RepoBareError):
        with tl.tree_lock(timeout=5):
            pytest.fail("should never reach the with-block body on a bare repo")

    # The lock must still have been released (no stuck holder) despite the raise.
    with tl.tree_lock(timeout=2):
        pass


# ── Publish-gate scope (R10): DAEMON-LIFECYCLE test module, matching test_tree_lock.py ──
pytestmark = pytest.mark.operational
