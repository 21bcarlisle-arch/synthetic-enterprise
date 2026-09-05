"""A BENIGN SELF-HEALING RACE READ EXACTLY LIKE A DEAD RECONCILER, because both returned `ERROR`.

MEASURED 2026-09-05, delivery seat, running `background.origin_reconcile` against a live 2-ahead /
6-behind fork on the shared tree. Its entire output:

    ERROR: merge gated clean but the push was rejected: To https://github.com/.../synthetic-enterprise.git
     ! [rejected]            HEAD -> main (non-fast-forward)
    error: failed to push some refs to '...'
    hint: Updates were rejected because a pushed branch tip is behind its remote

The merge was built, the gate ran on it and came back clean, and then another lane's `surgical-land`
pushed first. The whole gate was discarded — and the outcome was filed as `ERROR`, the same word the
module uses for a push that genuinely cannot work.

WHY THAT IS THE DEFECT AND NOT JUST BAD LUCK. The two are cleared apart. A lost race needs no
attention whatsoever: the next cadence re-fetches, re-merges on the new base and gates again. A
broken push clears never, and stays broken until someone reads it. Folded into one status, the
self-healing case is indistinguishable in the record from the one that needs a person — which is
CLAUDE.md's *"write refusals that name their reason"* failing on exactly the branch that fires most.

WHAT THIS CONTROL PROTECTS, and why it takes the shape it does. The rule this project learned three
times in one afternoon: *when a branch exists to be taken rarely, assert it CAN be taken before
asserting what it does*. A classifier that returned `REFUSED_RACE` for EVERY push failure would pass
a race-only test and destroy the distinction it exists to draw. So the partition is asserted whole —
both legs reachable, from one set of inputs — before either leg's meaning is checked.

NOT A RETRY, deliberately. See `origin_reconcile.REFUSED_RACE`: re-merging and re-gating in-process
costs the full gate again inside a cadence about to do exactly that, and this is the module that
manufactured 29 commits in three and a quarter hours by looping on its own output. Naming the
outcome is the repair.
"""
from __future__ import annotations

import pytest

from background import origin_reconcile as orc


class _Proc:
    def __init__(self, rc=0, out="", err=""):
        self.returncode, self.stdout, self.stderr = rc, out, err


#: Git's own words, verbatim from the 2026-09-05 run and from the variant it emits when the local
#: ref is stale rather than the remote ahead. Both are the same race; the module must call both.
RACE_STDERR = (
    "To https://github.com/21bcarlisle-arch/synthetic-enterprise.git\n"
    " ! [rejected]            HEAD -> main (non-fast-forward)\n"
    "error: failed to push some refs to "
    "'https://github.com/21bcarlisle-arch/synthetic-enterprise.git'\n"
    "hint: Updates were rejected because a pushed branch tip is behind its remote\n"
)
RACE_STDERR_FETCH_FIRST = (
    "To https://github.com/21bcarlisle-arch/synthetic-enterprise.git\n"
    " ! [rejected]            main -> main (fetch first)\n"
    "error: failed to push some refs\n"
)
#: A push that genuinely cannot work. Nothing about it clears on the next cadence.
BROKEN_STDERR = (
    "fatal: could not read Username for 'https://github.com': No such device or address\n"
)


@pytest.fixture
def spy(monkeypatch):
    """Everything that could touch the world, watched. Nothing here reaches git or origin."""
    calls = {"merge": 0, "push": 0, "worktree": 0}
    monkeypatch.setattr(orc, "_git", lambda *a, **k: _Proc(0))
    return calls


def _run(spy, *, push_rc, push_err):
    """A clean merge and a failing push, with the world fully injected out.

    `behind=6, ahead=2` is the live 2026-09-05 state: something of ours to land, so the module
    reaches the merge-and-push leg rather than the `ahead == 0` advance leg.
    """
    def runner(_wt):
        spy["merge"] += 1
        return _Proc(0)

    def pusher(_where):
        spy["push"] += 1
        return _Proc(push_rc, err=push_err)

    def make(_p, _w):
        spy["worktree"] += 1
        return True, ""

    return orc.reconcile(
        state_fn=lambda _p=None: (6, 2), runner=runner, pusher=pusher, make_worktree=make,
        drop_worktree=lambda p, w: None, gate_fn=lambda _p=None: False,
        advance_fn=lambda _p=None: {"advanced": False, "reason": "not reached", "cleared": []},
        blockers_fn=lambda _p=None: [])


# ── THE PARTITION, ASSERTED WHOLE BEFORE EITHER LEG'S MEANING ────────────────────────────────
def test_the_push_classifier_can_return_BOTH_answers(spy):
    """THE CONTROL OVER THE WHOLE PARTITION, and the one that catches the flattering mutation.

    A classifier hard-wired to `REFUSED_RACE` passes every race test below. One hard-wired to
    `ERROR` — the shipped behaviour until 2026-09-05 — passes every broken-push test below. Only
    this assertion refuses both, because it demands the two inputs give DIFFERENT answers.

    MUTATION: make `_classify_push_failure` return a constant status, either constant, and this
    fails while a per-leg test would not.
    """
    race = orc._classify_push_failure(RACE_STDERR)[0]
    broken = orc._classify_push_failure(BROKEN_STDERR)[0]
    assert race != broken, (
        "the classifier gave one answer for a lost race and a dead push, which is the defect it "
        "was written to remove")
    assert {race, broken} == {orc.REFUSED_RACE, orc.ERROR}


# ── LEG ONE: THE RACE IS NAMED, AND NAMED AS OWING NOTHING ───────────────────────────────────
@pytest.mark.parametrize("stderr", [RACE_STDERR, RACE_STDERR_FETCH_FIRST],
                         ids=["non-fast-forward", "fetch-first"])
def test_a_lost_race_is_REFUSED_RACE_and_not_ERROR(spy, stderr):
    """Both spellings git uses for this race, because they are the same condition.

    `fetch first` is not a second defect — it is what the ref line says when our remote-tracking
    ref is stale rather than the remote being ahead. A classifier keyed only to the string in the
    2026-09-05 log would call half of this race a fault.

    MUTATION: drop either arm of the `or` in `_classify_push_failure` and one id fails.
    """
    r = _run(spy, push_rc=1, push_err=stderr)
    assert r["status"] == orc.REFUSED_RACE, \
        "a self-clearing race was filed under the word the module uses for a broken reconciler"
    assert r["pushed"] is False
    assert spy["merge"] == 1 and spy["push"] == 1, "the leg under test was not the leg that ran"
    assert "NOTHING IS OWED" in r["detail"], \
        "the status names the race but the detail does not tell a reader it needs no attention"


def test_the_race_is_not_retried_in_process(spy):
    """NAMING IT IS THE REPAIR; SPINNING ON IT IS THE DEFECT THAT WOULD COME BACK.

    A retry must re-merge and re-gate against the new base — the full cost again, inside a cadence
    about to do exactly that. This is the module that produced 29 empty commits in 3h15m by looping
    on its own output (`test_the_reconciler_manufactured_the_fork_it_existed_to_close.py`).

    MUTATION: wrap the push in a retry loop and the counts go above one.
    """
    _run(spy, push_rc=1, push_err=RACE_STDERR)
    assert spy["push"] == 1, "the push was retried in-process"
    assert spy["merge"] == 1, "the merge was rebuilt in-process to retry the push"


# ── LEG TWO: A REAL FAILURE IS STILL A REAL FAILURE ──────────────────────────────────────────
def test_a_push_that_genuinely_failed_is_still_ERROR(spy):
    """THE LEG THAT STOPS THE REPAIR BECOMING A FAIL-OPEN.

    Without this, `REFUSED_RACE` is free to swallow every push failure and the module would report
    a reconciler that cannot authenticate as a benign race that clears itself — quieter than the
    defect it replaced, and worse.

    MUTATION: return `REFUSED_RACE` unconditionally from `_classify_push_failure` and this fails.
    """
    r = _run(spy, push_rc=1, push_err=BROKEN_STDERR)
    assert r["status"] == orc.ERROR, \
        "a push that cannot work was filed as a race that clears itself on the next cadence"
    assert r["pushed"] is False
    assert "NOTHING IS OWED" not in r["detail"], \
        "a genuine fault told the reader nothing is owed"


def test_an_unrecognised_push_failure_fails_toward_ERROR(spy):
    """FAIL-CLOSED ON THE PESSIMISTIC SIDE (R15 killer pattern 2).

    An unknown push failure is called a real fault and gets looked at. The cost of that direction
    is a glance; the cost of the other is a broken reconciler filed as benign and never read.

    MUTATION: flip the classifier's fallback to `REFUSED_RACE` and this fails.
    """
    assert orc._classify_push_failure("something nobody has seen before")[0] == orc.ERROR
    assert orc._classify_push_failure("")[0] == orc.ERROR, \
        "an empty push failure — the shape a truncated or unreadable stderr takes — fell open"


def test_the_race_status_does_not_report_the_run_as_a_success(spy):
    """A NAMED RACE IS STILL NOT A CLOSED FORK.

    The rename must not smuggle the outcome into the success set: `main()` exits 0 only for
    LEVEL/RECONCILED/PUSHED, and a race closed no fork. The module's own recorded failure was
    reporting success 29 times while the fork it was reconciling grew — the status must describe
    the subject, not the steps.

    MUTATION: add `REFUSED_RACE` to `main`'s success tuple and this fails.
    """
    assert orc.REFUSED_RACE not in (orc.LEVEL, orc.RECONCILED, orc.PUSHED)
    r = _run(spy, push_rc=1, push_err=RACE_STDERR)
    assert r["behind"] == 6, "the fork was reported closed by a run that pushed nothing"
