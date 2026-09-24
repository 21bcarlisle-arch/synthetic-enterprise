"""On a diverged tree no working-tree path is the cause, and the two RENDERERS said one was.

THE DEFECT, measured on the live shared tree 2026-09-24 at `ahead = 10, behind = 9`. Three pieces
of code were asked about that one tree inside the same second:

  * `origin_reconcile.advance_shared_tree` -- *"git refused the fast-forward because this tree has
    DIVERGED -- 10 local commit(s) that origin/main does not have. NO WORKING-TREE PATH IS THE
    CAUSE and clearing twins would delete files and still not advance, so nothing was touched."*
    Correct. It has asked `commits_ahead` before judging any path since 2026-09-05.
  * `origin_reconcile._blocking_clause` -- *"Refused by 4 path(s): ... THE STEP IS TO LAND OR
    REVERT THOSE PATHS."*
  * `process_run_complete._refused_advance_cause` -- *"a tracked file this tree has edited is
    HOLDING THE SHARED TREE BEHIND ORIGIN ... `isolate_hunks --survey` is how that lane lands its
    hunks."*

The second and third are false, and false in the direction that costs something: `blocking_tests`
was EMPTY and `total_red` was 0, so those sentences were the whole of what any reader had. The
delivery seat was then commissioned, in almost exactly those words, to go and clear three of the
four named paths -- three files deleted to buy an advance that divergence had already made
impossible. That is `advance_shared_tree`'s own named worst case ("a deletion bought for no
advance"), reached through the door beside the one its guard watches.

ONE RULE, THREE IMPLEMENTATIONS, THE FIX LANDED IN ONE. The rule -- *divergence is not a collision,
and on a fork no path is the cause* -- was learned and paid for on 2026-09-05. Nineteen days later
the two reader-facing renderers in the same file and its closest sibling still did not know it.
That is the shape CLAUDE.md names as this project's most expensive recurring defect, and it is only
visible from a vantage that can hold the instrument and its output at once.

WHAT EACH CONTROL WOULD CATCH, and every one names its own defect:

  * `test_the_three_tree_states_are_reachable_and_give_three_distinct_answers` -- REACHABILITY and
    DISTINCTNESS over the whole partition, first, because every leg below asserts what ONE state
    says and a renderer collapsed to one string passes any of them alone.
  * `test_a_diverged_tree_gets_no_landing_step_from_either_renderer` -- the defect itself, in the
    shape that cost three files.
  * `test_the_two_renderers_agree_with_the_advance_they_describe` -- the control keyed to the
    PROPERTY rather than to today's wording: whatever the three say, they may not disagree about
    whether a path is the cause. This is the leg that would have gone red on 2026-09-05 and stayed
    red for nineteen days.
  * `test_an_unreadable_ahead_count_withholds_the_landing_step_rather_than_assuming_no_fork` --
    fail-closed on the new question, matching the `blocking is None` leg beside it.
  * `test_the_clause_cannot_be_rendered_without_asking_divergence` -- the argument is REQUIRED. An
    optional `ahead=None` would have left every existing caller unrepaired, which is the defect
    with a new name.
"""
from __future__ import annotations

import inspect
from pathlib import Path

import pytest

from background import origin_reconcile as orc
from background import process_run_complete as prc

#: The remedy `_landing_clause` attaches. Its presence IS the claim "these paths are the cause".
LANDING_STEP = "THE STEP IS TO LAND OR REVERT THOSE PATHS"

_NOWHERE = Path("/nonexistent")


def _untracked(path: str) -> dict:
    return {"path": path, "kind": orc.FF_UNTRACKED}


def _modified(path: str) -> dict:
    return {"path": path, "kind": orc.FF_MODIFIED}


#: The live 2026-09-24 blocking set, kind for kind: one lane's tracked file and three untracked
#: staging drafts. Kept as the fixture because it is the set the seat was told to clear.
LIVE_BLOCKING = [
    _modified("docs/staging/reference/CLASS_PUBLISH_GATE_AND_WEDGE_2026-08-12.md"),
    _untracked("docs/staging/SEAT_FINDING_THE_ALARM_FAMILY_FILES_EIGHT_DISTINCT_NAMES.md"),
    _untracked("docs/staging/SEAT_FINDING_THE_HEADER_IS_STAMPED_ONCE.md"),
    _untracked("docs/staging/SEAT_FINDING_THREE_ALARM_FAMILIES_BYPASS_NOTIFY.md"),
]


def _cause(blocking, ahead):
    """The publish path's reader-facing `(verdict, clause)` with both git reads injected."""
    return prc._refused_advance_cause(_NOWHERE, lambda _p: blocking, lambda _p: ahead)


# ── the whole partition first, before any leg claims what one state says ─────────────────────
def test_the_three_tree_states_are_reachable_and_give_three_distinct_answers():
    """REACHABILITY AND DISTINCTNESS, written as one control over the partition rather than a leg
    per branch -- CLAUDE.md's rule, learned by entering the unreachable-branch trap three times in
    one afternoon through three different doors.

    A guard keyed to the condition that selects the diverged route would make the OTHER two
    unreachable and would pass every refusal assertion below while doing so.

    MUTATION: collapse the `ahead` branch of `_blocking_clause` into the level one, or return a
    constant from either renderer, and the `len(set(...)) == 3` assertions red.
    """
    clauses = {
        "diverged": orc._blocking_clause(LIVE_BLOCKING, 10),
        "level_and_dirty": orc._blocking_clause(LIVE_BLOCKING, 0),
        "ahead_unreadable": orc._blocking_clause(LIVE_BLOCKING, None),
    }
    verdicts = {state: _cause(LIVE_BLOCKING, ahead)[0]
                for state, ahead in (("diverged", 10), ("level_and_dirty", 0),
                                     ("ahead_unreadable", None))}

    assert len(set(clauses.values())) == 3, (
        "a fork, a dirty level tree and an unreadable ahead-count are three different states and "
        "must reach the reader as three different clauses, got: {}".format(clauses))
    assert len(set(verdicts.values())) == 3, (
        "the same three states must give three different VERDICTS too -- the verdict is the "
        "sentence a reader acts on, got: {}".format(verdicts))


def test_a_diverged_tree_gets_no_landing_step_from_either_renderer():
    """THE DEFECT. Both renderers told the reader to land or revert paths that were not the cause,
    on a tree where landing every one of them would have advanced nothing.

    Asserted over BOTH renderers and over every blocking shape, because the live instance happened
    to contain an `FF_MODIFIED` path and a guard written against that one shape would leave the
    all-untracked case -- the commoner one -- saying it anyway.

    MUTATION: drop the `if ahead:` branch from `_blocking_clause` and every clause here regains
    `LANDING_STEP`; drop it from `_refused_advance_cause` and the verdict assertions red.
    """
    for blocking in (LIVE_BLOCKING,
                     [_modified("tools/run_value_cycle_ab.py")],
                     [_untracked("docs/staging/A.md"), _untracked("docs/staging/B.md")]):
        clause = orc._blocking_clause(blocking, 7)
        assert LANDING_STEP not in clause, (
            "a diverged tree was handed the landing remedy for paths that are not the cause: "
            "{}".format(clause))
        assert "DIVERGED" in clause, \
            "the clause must send the reader at the fork by name: {}".format(clause)

        verdict, _ = _cause(blocking, 7)
        assert "DIVERGED" in verdict, \
            "the verdict must name the fork rather than a path: {}".format(verdict)
        assert "holding the shared tree behind origin" not in verdict, (
            "the 2026-09-24 sentence, verbatim: no path was holding anything -- {}".format(
                verdict))


def test_the_two_renderers_agree_with_the_advance_they_describe():
    """KEYED TO THE PROPERTY, NOT TO TODAY'S WORDING -- the leg that would have caught this on
    2026-09-05 and stayed red for the nineteen days it was live.

    `advance_shared_tree` is the authority on whether a path is the cause: it is the thing that
    would do the clearing. Whatever the three say, they may not DISAGREE about that. A control
    pinned to the current strings would go green the moment someone reworded either renderer and
    would say nothing about the next divergence of this kind.

    MUTATION: make either renderer's diverged branch offer the landing step again and this reds,
    because `advance_shared_tree` still refuses to clear anything.
    """
    class _Refused:
        returncode = 128
        stdout = ""
        stderr = "fatal: Not possible to fast-forward, aborting."

    def _never(*_a, **_k):
        raise AssertionError("the advance touched a path on a diverged tree")

    advance = orc.advance_shared_tree(
        _NOWHERE,
        ff_fn=_Refused,
        ahead_fn=lambda _p: 10,
        blockers_fn=lambda _p: LIVE_BLOCKING,
        twins_fn=lambda _p, _b: [b["path"] for b in LIVE_BLOCKING],
        tracked_twins_fn=lambda _p, _b: [],
        remover=_never, restorer=_never, locker=_never)

    assert advance["advanced"] is False and advance["cleared"] == [], \
        "the advance itself must still clear nothing on a fork: {}".format(advance)
    clears_nothing = "No working-tree path is the cause" in advance["reason"]
    assert clears_nothing, \
        "the advance's own reason is the authority this pins to: {}".format(advance["reason"])

    # THE AGREEMENT. The advance says no path is the cause; neither renderer may name a step that
    # only makes sense if one is.
    clause = orc._blocking_clause(LIVE_BLOCKING, 10)
    verdict, _ = _cause(LIVE_BLOCKING, 10)
    assert LANDING_STEP not in clause and LANDING_STEP not in verdict, (
        "the advance says no path is the cause and a renderer beside it still names the landing "
        "step -- that disagreement IS the defect: clause={!r} verdict={!r}".format(clause, verdict))


def test_an_unreadable_ahead_count_withholds_the_landing_step_rather_than_assuming_no_fork():
    """FAIL CLOSED on the new question, exactly as the `blocking is None` leg does on the old one.

    `commits_ahead` returns `None` when git would not answer, and folding that into `0` would make
    "I could not tell whether this is a fork" read as "it is not one" -- the reassuring verdict,
    which is the one that costs the reader an orientation.

    MUTATION: write `if ahead:` without the `ahead is None` leg above it and `None` falls through
    to the level-tree branch, restoring the landing step on an unread state.
    """
    clause = orc._blocking_clause(LIVE_BLOCKING, None)
    assert LANDING_STEP not in clause, \
        "a landing step was named on a tree nobody established was level: {}".format(clause)
    assert "could NOT be established" in clause, \
        "the gap must be named, not merely left out: {}".format(clause)

    verdict, _ = _cause(LIVE_BLOCKING, None)
    assert "could NOT be established" in verdict, \
        "an unestablished fork is not a clean bill: {}".format(verdict)


def test_the_clause_cannot_be_rendered_without_asking_divergence():
    """THE ARGUMENT IS REQUIRED, and that is the repair rather than a style choice.

    An optional `ahead=None` would keep every existing caller compiling and every existing caller
    wrong; the only ones repaired would be those that already knew to ask. Required means a caller
    that has not put the question to git cannot render the sentence at all -- the difference
    between a fix and the defect under a new name.

    MUTATION: give `ahead` a default and this reds, while every behavioural leg above still passes
    because they all NAME the argument.
    """
    with pytest.raises(TypeError):
        orc._blocking_clause(LIVE_BLOCKING)  # noqa: PLE1120 -- that it raises IS the control

    params = inspect.signature(orc._blocking_clause).parameters
    assert params["ahead"].default is inspect.Parameter.empty, \
        "`ahead` must have no default: a default is the fail-open this control exists to refuse"


def test_a_level_dirty_tree_still_gets_the_landing_step_it_has_always_had():
    """THE OTHER SIDE OF THE REACHABILITY ARGUMENT, as its own leg because it is the case the
    repair could most easily have broken.

    A guard that withheld the landing remedy from every tree would pass every refusal assertion
    above and would silently delete the one working diagnosis this pair has -- a lane holding a
    tracked file dirty IS a wedge with an owner and a named remedy.

    MUTATION: drop the `ahead` test and return the diverged string unconditionally; this reds
    while every diverged assertion above stays green.
    """
    clause = orc._blocking_clause([_modified("tools/run_value_cycle_ab.py")], 0)
    assert LANDING_STEP in clause, \
        "a level tree with a lane's dirty file must still be told to land it: {}".format(clause)
    assert "DIVERGED" not in clause, \
        "a level tree must not be told it has diverged: {}".format(clause)

    verdict, _ = _cause([_modified("tools/run_value_cycle_ab.py")], 0)
    assert "isolate_hunks" in verdict, \
        "the holder-work remedy is the one correct reading this pair had: {}".format(verdict)
