"""A DOCUMENT ARRIVING ON ORIGIN BLOCKED EVERY LANDING AND THE WHOLE SITE.

Director, 2026-09-02: *"One cause may be mine: I staged a document at 07:45Z, which moved origin
ahead of your local HEAD, and your origin-ahead guard then refuses your commit until you pull. If
that's what's happening, make the pull automatic rather than a refusal — a staged document arriving
should never block your landing."*

It was what was happening, in the machine's own record:

    docs/observability/.last_publish_cause.json
    {"cause": "behind_origin", "evidence": "origin/main is 1 commit(s) AHEAD of HEAD ..."}

The site was 3.2 hours stale and five gated landings sat local-only, all on that one condition.

**THE REFUSAL IS NOT WHAT CHANGED, AND THESE TESTS SAY SO.** `_divergence_refusal` argues its own
case — a gated merge takes longer than a publish cycle, and a daemon merging unattended would move
other lanes' uncommitted work — and both halves are true *of the shared working tree*, where 57
index entries belonging to another lane were sitting that morning. So the merge moved somewhere the
objections cannot apply, and the refusal in the publish path stays exactly as it was.
"""
from __future__ import annotations

import inspect
import subprocess
from pathlib import Path

from background import deadmans_switch
from background import origin_reconcile as orc


def _proc(rc=0, out="", err=""):
    return subprocess.CompletedProcess(args=["git"], returncode=rc, stdout=out, stderr=err)


#: Worktree creation is REAL git and belongs to `_fresh_worktree`'s own tests, not to every caller
#: of `reconcile`. Injected here so these legs are about the DECISIONS -- merge, refuse, push --
#: and never about whether a temp directory could be turned into a checkout.
def _no_worktree(project, path):
    return True, ""


def _no_cleanup(project, path):
    return None


# ── the condition it exists to clear ────────────────────────────────────────────────────────
def test_a_fork_is_closed_automatically(tmp_path):
    """THE DIRECTOR'S CASE. One document on origin, and the machine reconciles itself.

    MUTATION: make `reconcile` return without merging when `behind > 0` and `ahead > 0`, and this
    fails.

    BOTH LEGS ARE STATED, and the mutation names both, because on 2026-09-02 a merge stopped being
    a function of `behind` alone: with nothing of ours to contribute the honest move is to advance,
    not to commit, and `ahead == 0` now returns `NOT_ADVANCED` before the worktree is ever built
    (`test_the_reconciler_manufactured_the_fork_it_existed_to_close.py`). This test named only
    `behind_fn`, so `ahead` fell through to the directory fixture's `fork_state` pin of `(0, 0)` --
    a fixture that had been a neutral default right up until the value `0` became a decision. It
    then asserted a merge against a state that forbids one, and this leg and four below went red
    for the branch working correctly.
    """
    seen = {}

    def _merge(worktree):
        seen["merged"] = True
        return _proc(0, "[surgical-land] landed abc123 (merge)")

    def _push(worktree):
        seen["pushed"] = True
        return _proc(0)

    r = orc.reconcile(tmp_path, worktree=tmp_path / "wt", make_worktree=_no_worktree, drop_worktree=_no_cleanup, behind_fn=lambda p: 1,
                      ahead_fn=lambda p: 1, runner=_merge, pusher=_push)
    assert r["status"] == orc.RECONCILED and r["pushed"] is True
    assert seen == {"merged": True, "pushed": True}


def test_level_does_nothing_at_all(tmp_path):
    """No fork in EITHER direction: no worktree, no merge, no push. A reconciler that acted every
    cadence would be churn.

    `ahead_fn` is explicit because "level" stopped meaning "not behind" when the push half was
    added — a test that only pins one direction would pass while the other read the live world."""
    r = orc.reconcile(tmp_path, worktree=tmp_path / "wt", make_worktree=_no_worktree,
                      drop_worktree=_no_cleanup, behind_fn=lambda p: 0, ahead_fn=lambda p: 0,
                      runner=lambda w: _proc(1, "should not run"),
                      pusher=lambda w: _proc(1, "should not run"))
    assert r["status"] == orc.LEVEL and r["pushed"] is False


def test_an_unreadable_origin_is_not_a_reason_to_act(tmp_path):
    """`None` is a distinct answer from `0`. A reconciler that cannot read origin must not decide
    anything about it — the same fail-closed direction the refusal it replaces already took."""
    r = orc.reconcile(tmp_path, worktree=tmp_path / "wt", make_worktree=_no_worktree, drop_worktree=_no_cleanup, behind_fn=lambda p: None,
                      runner=lambda w: _proc(1, "should not run"),
                      pusher=lambda w: _proc(1, "should not run"))
    assert r["status"] == orc.UNREADABLE and r["pushed"] is False


# ── what it must NOT automate ───────────────────────────────────────────────────────────────
def test_a_conflict_still_refuses_and_is_never_pushed(tmp_path):
    """A conflict is two lanes editing one file, and choosing between them is a judgement, not a
    cadence. Inherited from `surgical_land --merge`, which refuses on conflict — this module adds
    isolation and a caller, and no new way to commit.

    MUTATION: treat a non-zero merge as retryable, or push anyway, and this fails.

    `ahead_fn` is explicit for the reason given on `test_a_fork_is_closed_automatically`: reaching
    the merge at all needs work of ours to contribute.
    """
    pushed = []
    r = orc.reconcile(tmp_path, worktree=tmp_path / "wt", make_worktree=_no_worktree, drop_worktree=_no_cleanup, behind_fn=lambda p: 2,
                      ahead_fn=lambda p: 1,
                      runner=lambda w: _proc(1, "[surgical-land] REFUSED: MERGE CONFLICT between "
                                                "a and b -- 1 conflicted path(s): docs/x.md"),
                      pusher=lambda w: pushed.append(1) or _proc(0))
    assert r["status"] == orc.REFUSED_CONFLICT
    assert r["pushed"] is False and pushed == []
    assert "docs/x.md" in r["detail"], "the refusal must name the paths, not just the condition"


def test_a_red_gate_refuses_and_is_told_apart_from_a_conflict(tmp_path):
    """Different things to a reader: a conflict wants a decision, a red gate is a defect and
    merging it would publish a regression. Neither is retried."""
    r = orc.reconcile(tmp_path, worktree=tmp_path / "wt", make_worktree=_no_worktree, drop_worktree=_no_cleanup, behind_fn=lambda p: 1,
                      ahead_fn=lambda p: 1,
                      runner=lambda w: _proc(1, "[surgical-land] REFUSED: GATE RED on the "
                                                "resulting tree (rc=1)"),
                      pusher=lambda w: _proc(0))
    assert r["status"] == orc.REFUSED_GATE and r["pushed"] is False


def test_a_failed_push_is_never_reported_as_reconciled(tmp_path):
    r = orc.reconcile(tmp_path, worktree=tmp_path / "wt", make_worktree=_no_worktree, drop_worktree=_no_cleanup, behind_fn=lambda p: 1,
                      ahead_fn=lambda p: 1,
                      runner=lambda w: _proc(0, "landed"),
                      pusher=lambda w: _proc(1, "", "! [rejected] non-fast-forward"))
    assert r["status"] == orc.ERROR and r["pushed"] is False


def test_it_never_raises_into_the_cadence(tmp_path):
    """A reconciler that took the deadman down would trade a stale site for a dead watchdog."""
    def _boom(worktree):
        raise OSError("git vanished")

    r = orc.reconcile(tmp_path, worktree=tmp_path / "wt", make_worktree=_no_worktree, drop_worktree=_no_cleanup, behind_fn=lambda p: 1,
                      ahead_fn=lambda p: 1, runner=_boom, pusher=lambda w: _proc(0))
    assert r["status"] == orc.ERROR and "OSError" in r["detail"]


# ── the property that makes it legal at all ─────────────────────────────────────────────────
def test_the_merge_never_runs_in_the_shared_tree():
    """THE WHOLE SAFETY ARGUMENT. `_divergence_refusal` refuses because *"a daemon that merged
    unattended would be deciding, every twelve minutes, to move other people's work"* — and that
    morning the shared index held 57 entries belonging to another lane.

    A throwaway worktree has its own index, so the objection dissolves rather than being
    overridden. This asserts the merge subprocess is run with `cwd` set to the WORKTREE.

    MUTATION: run the merge with `cwd=PROJECT_DIR` and this fails — which is the state that would
    sweep another lane's staged work into a merge commit.
    """
    src = inspect.getsource(orc._run_merge)
    assert "cwd=str(worktree)" in src
    assert "PROJECT_DIR" not in src.split("cwd=")[1].split(",")[0]


def test_it_uses_the_sanctioned_door_rather_than_a_second_one():
    """Hook-bypass is a wall. The merge is `tools.surgical_land --merge`, so the gate and the
    conflict refusal are inherited; this module contributes isolation and a caller."""
    src = inspect.getsource(orc._run_merge)
    assert "tools.surgical_land" in src and "--merge" in src
    assert "--no-verify" not in inspect.getsource(orc)


def test_the_shared_tree_is_only_ever_FAST_FORWARDED_and_git_may_refuse():
    """It cannot advance a shared tree past uncommitted work and does not try: `--ff-only`, and
    git's own refusal is the safety net rather than a failure. Never `--force`, ever."""
    src = inspect.getsource(orc.reconcile)
    assert '"merge", "--ff-only"' in src
    assert "--force" not in src


def test_the_worktree_is_declared_in_use_while_the_merge_runs():
    """The reaper is armed and on this same cadence, and `fork_salvage` sweeps dirty worktrees. A
    merge in progress is exactly the state both are built to clean up after, so it takes the one
    sanctioned marker — which carries a lease, so an abandoned reconciliation frees itself."""
    from background.seat_executor import OWNER_MARKER
    src = inspect.getsource(orc._fresh_worktree)
    assert "OWNER_MARKER" in src and OWNER_MARKER


def test_the_publish_paths_refusal_is_untouched():
    """The refusal was RIGHT and is not what changed. If it ever starts merging inline, the
    objection it argues against itself becomes real: a gated merge is longer than a publish cycle,
    and the shared index carries other lanes' work.

    Asserted on the BODY with the docstring stripped -- that docstring discusses merging at length,
    and a check that reads prose cannot tell an argument about merging from an act of it.
    """
    import ast

    from background import process_run_complete as prc
    fn = ast.parse(inspect.getsource(prc._divergence_refusal)).body[0]
    body = fn.body[1:] if isinstance(fn.body[0], ast.Expr) else fn.body
    code = "\n".join(ast.unparse(n) for n in body)
    assert "AHEAD of HEAD" in code, "it must still say the state"
    assert "subprocess" not in code and "run(" not in code, "it must still only REPORT"


# ── and it is actually called ───────────────────────────────────────────────────────────────
def test_the_reconciler_is_on_the_cadence():
    """An unwired reconciler is prose — the lesson of the worktree reaper, which sat uncalled from
    July to yesterday.

    MUTATION: remove `_check_origin_fork()` from `run_cycle` and this fails.
    """
    assert "_check_origin_fork()" in inspect.getsource(deadmans_switch.run_cycle)
    body = inspect.getsource(deadmans_switch._check_origin_fork)
    assert "origin_reconcile" in body and "reconcile()" in body


def test_a_fork_that_cannot_be_closed_pages_as_BLOCKED_WORK():
    """While it stands, nothing this machine does can reach origin — that is blocked work, not
    drift, and it is the difference between a message he acts on and one he batches."""
    body = inspect.getsource(deadmans_switch._check_origin_fork)
    assert "BLOCKED_WORK" in body
    assert "clear_transition" in body, "a closed fork must clear its own alarm"


# ── the other half of the fork, which the first version of this module did not have ─────────
def test_a_landing_sitting_local_only_is_PUSHED(tmp_path):
    """THE DIRECTOR'S ACTUAL COMPLAINT: *"landed in the tree, reported as landed, not pushed."*

    Nothing else on this machine pushes a `surgical_land` landing. The publish path pushes its OWN
    commits and carries whatever else is on the branch, so a landing reaches origin only when a
    publish happens to follow it — and a blocked publish path means no landing ever leaves.

    MUTATION: return LEVEL whenever `behind == 0` and this fails. That mutation IS the first
    version of this module, whose own landing then sat unpushed — the defect reproduced inside the
    fix for it, and found by running the verification the finding says to run.
    """
    pushed = []
    r = orc.reconcile(tmp_path, worktree=tmp_path / "wt", make_worktree=_no_worktree,
                      drop_worktree=_no_cleanup, behind_fn=lambda p: 0, ahead_fn=lambda p: 3,
                      runner=lambda w: _proc(1, "should not merge when not behind"),
                      pusher=lambda w: pushed.append(w) or _proc(0))
    assert r["status"] == orc.PUSHED and r["pushed"] is True
    assert "3 gated landing(s)" in r["detail"]
    assert pushed, "it must actually push, not merely report that it would"


def test_level_now_means_AGREEMENT_not_merely_not_behind(tmp_path):
    """"Not behind" and "agrees" are different states and only one of them is done."""
    r = orc.reconcile(tmp_path, worktree=tmp_path / "wt", make_worktree=_no_worktree,
                      drop_worktree=_no_cleanup, behind_fn=lambda p: 0, ahead_fn=lambda p: 0,
                      runner=lambda w: _proc(1), pusher=lambda w: _proc(1))
    assert r["status"] == orc.LEVEL and "agree" in r["detail"]


def test_an_unreadable_ahead_count_does_not_push(tmp_path):
    """Same fail-closed direction as the behind side: do not act on a state not observed."""
    pushed = []
    r = orc.reconcile(tmp_path, worktree=tmp_path / "wt", make_worktree=_no_worktree,
                      drop_worktree=_no_cleanup, behind_fn=lambda p: 0, ahead_fn=lambda p: None,
                      runner=lambda w: _proc(1), pusher=lambda w: pushed.append(1) or _proc(0))
    assert r["status"] == orc.UNREADABLE and pushed == []


def test_a_rejected_push_is_never_reported_as_done(tmp_path):
    r = orc.reconcile(tmp_path, worktree=tmp_path / "wt", make_worktree=_no_worktree,
                      drop_worktree=_no_cleanup, behind_fn=lambda p: 0, ahead_fn=lambda p: 1,
                      runner=lambda w: _proc(1),
                      pusher=lambda w: _proc(1, "", "! [rejected] non-fast-forward"))
    assert r["status"] == orc.ERROR and r["pushed"] is False


def test_the_world_is_read_through_ONE_seam_so_a_pin_cannot_go_partial():
    """A pin against a LIST of functions is fail-open on the next function.

    `tests/background/conftest.py` pinned `commits_behind`, correctly. An hour later the rung grew
    `commits_ahead`, the pin covered half of it, and the same 28 assertions in
    `test_deadmans_switch.py` went red a second time on the same cause. `fork_state` is the module's
    one window onto the world, so a future world-read comes through that door or is a new seam
    visible as one.

    MUTATION: read `commits_behind`/`commits_ahead` directly in `reconcile` and this fails.
    """
    src = inspect.getsource(orc.reconcile)
    assert "(state_fn or fork_state)(project)" in src
    # The per-leg overrides may still exist, but the DEFAULT path must not touch the two readers.
    default_path = src.split("state_fn or fork_state")[0]
    assert "commits_behind(" not in default_path and "commits_ahead(" not in default_path


def test_the_directory_fixture_pins_that_seam():
    """The pin and the seam must be the same thing; a conftest naming a function the rung no longer
    calls is a pin that silently stopped pinning."""
    conftest = Path("tests/background/conftest.py").read_text()
    assert 'origin_reconcile, "fork_state"' in conftest
