"""TWO RECONCILERS, ONE WORKTREE PATH, AND THE SECOND ONE REBUILDS IT UNDER THE FIRST.

`origin_reconcile` argues its isolation carefully and the argument holds against every mechanism
except a second copy of itself. `WORKTREE` is one fixed path (`/var/tmp/se-origin-reconcile`);
nothing in the module takes a lock; and `gate_is_running` answers about the PUBLISH gate, never
about another reconciler. `_fresh_worktree` then opened with an unconditional
`git worktree remove --force`.

The marker it writes one line later exists precisely so *"nothing sweeps it mid-merge"* — and
`fork_salvage` and `fork_reconciler` both honour it, through `seat_executor.worktree_is_live`. The
one caller that never asked was the function that owns the path.

REPRODUCED ON REAL DISK, 2026-09-04 23:39Z, and it is reachable by following the machine's own
instructions: the deadman's reconcile was ~40s into `surgical_land --merge` when a seat ran
`python3 -m background.origin_reconcile` — the command `process_run_complete._divergence_refusal`
PRINTS to every reader of a publish refusal. Three minutes later the marker in that directory held
the second (by then killed) pid while the deadman's merge was still executing against a tree that
had been removed and recreated beneath its cwd.

WHY THE OLD CONTROL DID NOT CATCH IT, which is the reusable half.
`test_the_worktree_is_declared_in_use_while_the_merge_runs` asserts `"OWNER_MARKER" in
inspect.getsource(_fresh_worktree)`. That is true of a function that WRITES the marker and never
READS one, so it was green through the whole defect. A claim is only a claim if somebody checks it,
and a source-text control cannot tell those two apart.
"""
from __future__ import annotations

import subprocess

from background import origin_reconcile as orc
from background import seat_executor


def _proc(rc=0, out="", err=""):
    return subprocess.CompletedProcess(args=["git"], returncode=rc, stdout=out, stderr=err)


def _spy(calls):
    def _git(cwd, *args, **kwargs):
        calls.append(args)
        return _proc()
    return _git


def test_a_live_writers_worktree_is_refused_and_a_dead_ones_is_rebuilt(tmp_path, monkeypatch):
    """ONE CONTROL OVER THE WHOLE PARTITION, not a leg per branch.

    A guard that refuses everything passes every "does it refuse correctly" test ever written, and
    this module's advance is one of the things that would then never run again. So both sides are
    asserted here, against the same directory, differing only in the answer `worktree_is_live`
    gives — which is the one variable.

    MUTATION: delete the `worktree_is_live` call and the LIVE leg fails (the remove happens).
    MUTATION: return `False, ...` unconditionally and the DEAD leg fails (no worktree is ever
    built, so no fork is ever closed).
    """
    path = tmp_path / "se-origin-reconcile"
    path.mkdir()

    live_calls: list = []
    monkeypatch.setattr(seat_executor, "worktree_is_live", lambda p: True)
    monkeypatch.setattr(orc, "_git", _spy(live_calls))
    ok, why = orc._fresh_worktree(tmp_path, path)
    assert ok is False, "a worktree with a live writer in it must not be rebuilt"
    # THE PROPERTY, not the wording: git was never asked to remove anything.
    assert not any("remove" in a for a in live_calls), \
        "the merge already running in there had its checkout removed under it: {}".format(live_calls)
    assert "another writer holds" in why and str(path) in why, \
        "a refusal that does not name its subject sends the next reader looking for a cause"

    dead_calls: list = []
    monkeypatch.setattr(seat_executor, "worktree_is_live", lambda p: False)
    monkeypatch.setattr(orc, "_git", _spy(dead_calls))
    ok, _ = orc._fresh_worktree(tmp_path, path)
    assert ok is True, "an abandoned worktree must still be rebuilt, or a crash wedges the cadence"
    assert any("remove" in a for a in dead_calls), \
        "the stale checkout has to go, otherwise `worktree add` lands on an occupied path"


def test_the_refusal_reaches_a_reader_through_reconciles_own_verdict(tmp_path, monkeypatch):
    """A refusal nothing surfaces is a silent stand-down, and this module has paid for one before.

    `reconcile` renders a `_fresh_worktree` failure as ERROR with the reason attached, so the
    deadman's log line carries the cause. Pinned here because the branch is one `return` away from
    reporting a bare "could not build an isolated worktree" that names nothing.

    MUTATION: drop `why` from reconcile's ERROR detail and this fails.
    """
    monkeypatch.setattr(orc, "fork_state", lambda project=None: (3, 1))
    monkeypatch.setattr(orc, "gate_is_running", lambda project=None: False)
    result = orc.reconcile(
        tmp_path,
        make_worktree=lambda project, path: (False, "another writer holds /var/tmp/x"),
    )
    assert result["status"] == orc.ERROR
    assert result["pushed"] is False, "nothing may reach origin when the isolation was never built"
    assert "another writer holds" in result["detail"]


def test_nothing_else_in_the_module_removes_that_worktree_without_asking(tmp_path, monkeypatch):
    """`_drop_worktree` is the OTHER force-remove on the same path, and it runs in a `finally`.

    A second reconciler that refuses at `_fresh_worktree` must not then tear the directory down on
    its way out — that would move the collision four lines later and leave every symptom identical.
    `reconcile` only reaches `finally` when it built the worktree itself, and this is what says so.

    MUTATION: hoist the `try` above `_fresh_worktree` so `finally` covers the refusal, and this
    fails.
    """
    dropped: list = []
    monkeypatch.setattr(orc, "fork_state", lambda project=None: (3, 1))
    monkeypatch.setattr(orc, "gate_is_running", lambda project=None: False)
    orc.reconcile(
        tmp_path,
        make_worktree=lambda project, path: (False, "another writer holds /var/tmp/x"),
        drop_worktree=lambda project, path: dropped.append(path),
    )
    assert dropped == [], \
        "the refusing reconciler dropped the worktree the writer it stood down for is using"
