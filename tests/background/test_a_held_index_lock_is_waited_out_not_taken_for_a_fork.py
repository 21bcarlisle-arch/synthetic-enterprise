"""THE DEFECT: the publish advance met another lane's `.git/index.lock` and the cycle was refused
`behind_origin` -- the third Monday refusal of run 4ae8da9b0f (2026-10-26 06:58Z).

The advance loop is terminal on every refusal to advance, because a real fork, a collision and an
unreadable origin are STATES (`test_the_publisher_dropped_a_cycle_after_a_single_lost_race_...`).
A held lock is a moment: a git process holds it and will finish. So that one refusal waits for the
lock to go and re-runs the advance; a lock that never goes stays a refusal and is never deleted.

The loop's control flow is driven by the sibling file's `_drive`, so everything downstream of the
scripted divergence reads and advance verdicts is the publisher's own code.
"""
from __future__ import annotations

from background import process_run_complete as prc
from tests.background.test_the_publisher_dropped_a_cycle_after_a_single_lost_race_it_could_have_re_run import (  # noqa: E501
    ADVANCED,
    GIT_REFUSED,
    _committed,
    _drive,
)

LOCKED = {"advanced": False, "reason": "git REFUSED the fast-forward (rc=128) -- git said: error: "
                                       "Unable to create '/x/.git/index.lock': File exists."}


def test_a_released_lock_is_retried_and_a_stuck_one_still_refuses(tmp_path, monkeypatch):
    """BOTH ENDS OF THE NEW BRANCH IN ONE CONTROL, so a branch that always retries or never
    retries cannot pass it.

    MUTATION: drop the `continue` after the wait and the first leg reds (no commit); make the wait
    return True unconditionally and the second leg reds (it commits, or spends every attempt).
    """
    monkeypatch.setattr(prc, "_await_index_lock_release", lambda *a, **k: True)
    released = _drive(monkeypatch, tmp_path, ahead_reads=[2, 0], advances=[LOCKED, ADVANCED])

    monkeypatch.setattr(prc, "_await_index_lock_release", lambda *a, **k: False)
    stuck = _drive(monkeypatch, tmp_path, ahead_reads=[2], advances=[LOCKED])

    assert _committed(released[4]) and released[3] == 2, "a cleared lock must not cost the cycle"
    assert not _committed(stuck[4]) and stuck[3] == 1 and stuck[1] == prc.BEHIND_ORIGIN
    assert "STILL held" in stuck[2], "a lock outliving the wait must say it may be stale"


def test_a_git_refusal_that_is_not_the_lock_is_still_terminal(tmp_path, monkeypatch):
    """The wait is keyed to git's lock message, never to `rc=128` or `REFUSED`.

    MUTATION: widen `_HELD_INDEX_LOCK` to "REFUSED" and this reds -- the wait is asked for.
    """
    asked = []
    monkeypatch.setattr(prc, "_await_index_lock_release", lambda *a, **k: asked.append(1) or True)
    _r, reason, _e, advances, calls = _drive(
        monkeypatch, tmp_path, ahead_reads=[4], advances=[GIT_REFUSED])

    assert not asked and advances == 1 and reason == prc.BEHIND_ORIGIN and not _committed(calls)


def test_the_wait_reads_the_lock_and_never_removes_it(tmp_path):
    """MUTATION: `return True` at the top of the helper reds the second assertion."""
    (tmp_path / ".git").mkdir()
    assert prc._await_index_lock_release(tmp_path, deadline_s=0, sleep=lambda s: None)

    lock = tmp_path / ".git" / "index.lock"
    lock.write_text("")
    assert not prc._await_index_lock_release(tmp_path, deadline_s=0, sleep=lambda s: None)
    assert lock.exists()
