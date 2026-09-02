"""THE CURE BECAME THE NEXT CAUSE: 29 empty merges, one every 6m20s, for three and a quarter hours.

Director, 2026-09-02: *"The reconcile you built to stop the behind-origin refusal is now
manufacturing the HEAD-moved refusal on a loop. Cure became the next cause, same shape as the
banner on the 20th. Fix the mechanism, not the instance: reconcile only when there is something of
ours to land, never on a cadence, and never while a gate is running."*

THE MECHANISM, established from the repository rather than assumed:

  1. another lane held `tools/head_green_census.py` and its test staged, and origin had landed its
     own version of both;
  2. so `git merge --ff-only origin/main` refused -- correctly, git will not overwrite 554
     modified files -- and the shared tree stayed at `83c63ac58`;
  3. reconcile merged origin into that stale HEAD inside a worktree and pushed. Every one of those
     merges has `p1 = 83c63ac58` and a tree byte-identical to `p2`: it changed nothing;
  4. origin advanced by one, the shared tree did not, so the next cadence read BEHIND -- one
     deeper -- and merged again. **There was no terminating condition.**

And the refusal it was built to clear is the one it manufactured. The gate's own log at 18:02:
*"Provenance banner commit REFUSED before staging: origin/main is 30 commit(s) AHEAD of HEAD ...
would widen the fork by one more."* Publishing had been down thirteen hours behind it.

The fix is one branch that did not exist: **a merge requires something of ours to land.**
"""
from __future__ import annotations

import pytest

from background import origin_reconcile as orc


class _Proc:
    def __init__(self, rc=0, out="", err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


@pytest.fixture
def spy(monkeypatch):
    """Everything that could touch the world, watched. Nothing here reaches git or origin."""
    calls = {"merge": 0, "push": 0, "worktree": 0, "ff": 0}

    def _ff(project, *args, **kw):
        if args[:2] == ("merge", "--ff-only"):
            calls["ff"] += 1
            return calls.setdefault("ff_result", _Proc(0))
        return _Proc(0)

    monkeypatch.setattr(orc, "_git", _ff)
    return calls


def _run(spy, behind, ahead, *, gate=False, merge_rc=0, push_rc=0, after=None):
    def runner(_wt):
        spy["merge"] += 1
        return _Proc(merge_rc, "MERGE CONFLICT x" if merge_rc else "")

    def pusher(_where):
        spy["push"] += 1
        return _Proc(push_rc)

    def make(_p, _w):
        spy["worktree"] += 1
        return True, ""

    states = [(behind, ahead)] + list(after or [])

    def state_fn(_project=None):
        return states.pop(0) if len(states) > 1 else states[0]

    return orc.reconcile(state_fn=state_fn, runner=runner, pusher=pusher, make_worktree=make,
                         drop_worktree=lambda p, w: None, gate_fn=lambda _p=None: gate)


# ── THE BRANCH THAT DID NOT EXIST ───────────────────────────────────────────────────────────
def test_behind_with_NOTHING_OF_OURS_never_commits_and_never_pushes(spy):
    """THE 29, AND THE ONE RULE THAT PREVENTS ALL OF THEM.

    With nothing of ours to land, a merge builds a commit whose tree is ALREADY origin's, so it
    changes no content and exists only to move a ref. Pushing it moves origin by one and leaves
    the shared tree where it was -- which is the loop.

    MUTATION: fall through to the worktree merge when `ahead == 0` (the shipped behaviour until
    2026-09-02) and this fails on both counts.
    """
    spy["ff_result"] = _Proc(1, err="Your local changes would be overwritten")
    r = _run(spy, behind=30, ahead=0)
    assert r["status"] == orc.NOT_ADVANCED
    assert spy["merge"] == 0, "it merged with nothing of ours to contribute"
    assert spy["push"] == 0, "it moved origin with nothing of ours to contribute"
    assert spy["worktree"] == 0, "it built a worktree for a merge that had no reason to happen"


def test_the_loop_cannot_recur_however_many_times_it_is_called(spy):
    """The property, not the instance. A stuck shared tree is a STABLE state now: ten cadences
    produce ten reports and zero commits, where they used to produce ten commits and a fork ten
    deeper."""
    spy["ff_result"] = _Proc(1, err="Your local changes would be overwritten")
    for _ in range(10):
        assert _run(spy, behind=30, ahead=0)["status"] == orc.NOT_ADVANCED
    assert (spy["merge"], spy["push"]) == (0, 0)


def test_when_the_tree_CAN_advance_it_advances_without_making_a_commit(spy):
    """The right action with nothing of ours is to ADVANCE, not to commit. No commit, and origin
    is not touched at all."""
    spy["ff_result"] = _Proc(0)
    r = _run(spy, behind=3, ahead=0)
    assert r["status"] == orc.FAST_FORWARDED
    assert (spy["merge"], spy["push"], spy["ff"]) == (0, 0, 1)


def test_a_real_fork_with_work_of_ours_still_merges(spy):
    """The fix must not become a refusal to reconcile at all. When both sides moved, the gated
    merge in isolation is exactly right and is unchanged."""
    r = _run(spy, behind=2, ahead=1, after=[(0, 0)])
    assert r["status"] == orc.RECONCILED
    assert (spy["merge"], spy["push"]) == (1, 1)


# ── THE STATUS MUST DESCRIBE THE SUBJECT, NOT THE STEPS ─────────────────────────────────────
def test_a_merge_that_left_the_tree_behind_is_NOT_reported_as_reconciled(spy):
    """IT REPORTED SUCCESS 29 TIMES WHILE THE FORK GREW. The old version returned RECONCILED
    whenever the merge and push succeeded and put "shared tree NOT advanced" in a detail string
    nothing read.

    MUTATION: delete the re-read and return RECONCILED on the steps succeeding, and this fails --
    which is the exact line that let a loop report health for three hours.
    """
    r = _run(spy, behind=2, ahead=1, after=[(3, 0)])
    assert r["status"] == orc.NOT_ADVANCED
    assert "did NOT advance" in r["detail"]


def test_reconciled_means_the_tree_was_OBSERVED_level_afterwards(spy):
    r = _run(spy, behind=2, ahead=1, after=[(0, 0)])
    assert r["status"] == orc.RECONCILED
    assert "re-read after the fact" in r["detail"]


# ── NEVER WHILE A GATE IS RUNNING ───────────────────────────────────────────────────────────
def test_nothing_moves_while_the_publish_gate_holds_its_lock(spy):
    """A push that lands mid-gate turns a green run into a non-fast-forward refusal at the last
    step -- five to twenty-five minutes spent and discarded, and on a cadence, every time."""
    r = _run(spy, behind=5, ahead=2, gate=True)
    assert r["status"] == orc.GATE_RUNNING
    assert (spy["merge"], spy["push"], spy["ff"]) == (0, 0, 0)


def test_even_a_pure_push_waits_for_the_gate(spy):
    """Being only AHEAD still moves origin, which is what the running gate will be judged against."""
    assert _run(spy, behind=0, ahead=4, gate=True)["status"] == orc.GATE_RUNNING
    assert spy["push"] == 0


def test_agreement_is_reported_without_consulting_the_gate_at_all(spy):
    """LEVEL touches nothing, so a held lock is irrelevant to it. A check that refused to report
    agreement while a gate ran would make the fork look open every time one did."""
    assert _run(spy, behind=0, ahead=0, gate=True)["status"] == orc.LEVEL


def test_an_unreadable_lock_reads_as_a_gate_that_may_be_running(tmp_path, monkeypatch):
    """Fails toward TRUE. Refusing to act on an unreadable lock costs one cadence; acting on it
    costs a gate run. `fail_closed_on_unreadable_input`."""
    lock = tmp_path / "docs" / "observability" / ".process_run_complete.lock"
    lock.parent.mkdir(parents=True)
    lock.write_text("")
    assert orc.gate_is_running(tmp_path) is False

    def _boom(*a, **kw):
        raise OSError("no fd")

    monkeypatch.setattr("builtins.open", _boom)
    assert orc.gate_is_running(tmp_path) is True


def test_an_absent_lock_is_not_a_running_gate(tmp_path):
    """A machine that has never run the gate has no lock file, and must not be frozen by its
    absence -- the mirror error, and one this project has made (`a_correct_refusal_is_not_a
    _population`)."""
    assert orc.gate_is_running(tmp_path) is False


def test_a_held_lock_is_detected(tmp_path):
    import fcntl

    lock = tmp_path / "docs" / "observability" / ".process_run_complete.lock"
    lock.parent.mkdir(parents=True)
    lock.write_text("")
    with open(lock, "w") as fh:
        fcntl.flock(fh, fcntl.LOCK_EX | fcntl.LOCK_NB)
        assert orc.gate_is_running(tmp_path) is True
    assert orc.gate_is_running(tmp_path) is False


# ── unreadable state still acts on nothing ──────────────────────────────────────────────────
def test_an_unknown_ahead_count_acts_on_nothing(spy):
    """`ahead` now decides whether a merge is legitimate at all, so not knowing it is not knowing
    whether to act -- and the answer to that is never "act"."""
    r = _run(spy, behind=4, ahead=None)
    assert r["status"] == orc.UNREADABLE
    assert (spy["merge"], spy["push"], spy["ff"]) == (0, 0, 0)
