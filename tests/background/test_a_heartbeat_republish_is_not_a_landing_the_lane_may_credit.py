"""A claim was closed as delivered by a commit whose only overlap with it was the heartbeat.

THE DEFECT, measured 2026-09-19 on this lane's own ledger, and it is the expensive form of a
blindness the seat had already recorded three times. `the-orientation-brief-misreports-the-machine-
it-describes` named six paths. `credit_from_tree` bound it to `851dffdbb` -- an auto-process
republish touching 52 files -- and wrote `last_landing_paths: ["site/data/tick_heartbeat.json"]`,
which is the whole of the intersection and is how the route was identified: only the intersecting
writer produces a single-path tombstone from a 52-file commit. The item was marked done. Its 379
lines of finished work were left in the tree, on the one subject that WAS this blindness.

WHY IT IS WORSE THAN A MISS. A ledger wrong towards "done" is not symmetrical with one that is
silent: a swept row is redrawn and a credited row never is. The publisher commits the liveness
surface several times an hour by construction (`_refresh_published_liveness_on_skip` exists to make
it do exactly that), so before this repair ANY claim naming one of those files was one republish
away from being closed by a timestamp, and the closing was invisible.

WHAT IS GRADED HERE IS THE PROPERTY, NOT THE INSTANCE: **an intersection confined to the publisher's
declared liveness surface does not credit a landing, and an intersection containing anything else
still does.** No sha, id or window from the live ledger appears below.

AND THE SURFACE IS READ, NEVER SPELLED. The fixtures below take their liveness path from
`publish_gate_blocking_read.LIVENESS_SURFACE_FILES` -- the one declaration of what the publisher
commits, the same source the code under test reads. Typing the filename here would make this suite
the second hand-typed copy, which is the defect the repair was written to avoid; it would also go
green against a stale name for ever, which is the direction that matters.

THE DECLARATION MOVED HOME on 2026-09-21 and this suite moved with it, which is the whole reason
the paragraph above insists on reading rather than spelling. It used to live on
`process_run_complete`, and `delivery_lane` importing it from there was REFUSED by
`test_publish_scope::test_the_supervisor_does_not_import_the_publish_path` --
`supervisor -> delivery_lane -> process_run_complete` enrols nearly every `tests/background/**`
module in the publish gate. So it sits in the stdlib-only leaf and the publisher imports it back:
one home, one writer, no edge. A suite that had typed the filename would not have noticed any of
this and would still be green.

NOT VIA `commit_narrative._liveness_surface`, which is the near-identical reader one rung over and
was the first draft's route. The commit gate refused that too, for a different reason: at the time
that function was in the shared working tree and in no commit, so this suite and its subject would
have landed against a supplier that had not. (It landed in dc9e27ccd shortly after, so that
particular premise has expired -- but the readers stayed separate, and merging them is an ordinary
choice for whoever wants to argue it, not a tidy-up to smuggle into a landing.)

THE PARTITION IS ONE STATEMENT, and that is deliberate. A binder that credits NOTHING satisfies
every per-branch check of a refusal, and this project has walked into that trap through three
separate doors in one afternoon. `test_THE_PARTITION_...` asserts the refusal and the credit
together, so neither degenerate binder passes.

MUTATIONS (each must fire, and which leg catches it):
  (a) delete the liveness clause from `_window_hits`, so every commit is a hit -- the partition's
      heartbeat-only leg reds;
  (b) invert it, refusing every commit -- the partition's work leg and its both-commits leg red;
  (c) drop `--name-only` from the `git log`, so no intersection is ever known -- the fake below
      emits filenames only when asked for them, exactly as git does, so (a) reds;
  (d) read an EMPTY printed intersection as liveness-only (`touched <= surface` without the
      `touched and` guard) -- `test_A_COMMIT_GIT_PRINTS_NO_FILENAMES_FOR_IS_NOT_CALLED_A_HEARTBEAT`
      reds, and with it the merge landings that clause protects;
  (e) fall back to "nothing is liveness" when the declaration will not read --
      `test_AN_UNREADABLE_DECLARATION_REFUSES_THE_CREDIT_AND_SAYS_WHICH_CHECK_COULD_NOT_ANSWER`
      reds on both of its halves;
  (f) put the liveness test in `_landed_unbound` instead of `_window_hits`, so the sibling reading
      still calls a heartbeat a landing -- `test_THE_SIBLING_READING_APPLIES_THE_SAME_RULE` reds.
"""
from __future__ import annotations

import pytest

from background import delivery_lane as dl
from background import publish_gate_blocking_read as liveness_home
from tests.background import residual_voices

#: Taken from the one declaration, never typed. See the module docstring.
LIVENESS_PATH = sorted(str(p) for p in liveness_home.LIVENESS_SURFACE_FILES)[0]

#: A path the publisher's liveness commit cannot touch, so an intersection containing it is work.
WORK_PATH = "background/delivery_lane.py"

FOCUS_ID = "a-claim-that-names-both-a-real-subject-and-the-heartbeat"
DRAWN_AT = 1_700_000_000.0
IN_WINDOW = DRAWN_AT + 60.0

HEARTBEAT_SHA = "a" * 40
WORK_SHA = "b" * 40
MERGE_SHA = "c" * 40


def _row() -> dict:
    """A drawn row naming BOTH kinds of path — which is the case the defect needs to exist.

    A claim naming only work paths was never at risk, and one naming only liveness paths is
    uncreditable either way. The mixed row is where crediting the wrong one is possible, and it is
    the shape the live instance had.
    """
    return {"first_drawn_at": DRAWN_AT, "last_drawn_at": DRAWN_AT,
            "named_paths": [WORK_PATH, LIVENESS_PATH]}


def _fake_git(commits: list[tuple[str, list[str]]]):
    """A `_git` that answers `log` the way git does, INCLUDING printing names only when asked.

    The `--name-only` fidelity is not decoration: it is what makes mutation (c) fire. A fake that
    printed filenames regardless would leave the intersection knowable even after the flag was
    dropped from the query, and the suite would grade a code path production no longer takes.
    """
    def fake(*args: str) -> str | None:
        if not args or args[0] != "log":
            return ""
        want_names = "--name-only" in args
        lines = []
        for sha, touched in commits:
            lines.append("{}\x1f{:.0f}\x1f{}".format(sha, IN_WINDOW, "a subject"))
            if want_names:
                lines.append("")
                lines.extend(touched)
        return "\n".join(lines) + "\n"
    return fake


def _credit(monkeypatch, commits: list[tuple[str, list[str]]]) -> dict | None:
    """What `_landed_unbound` makes of a window holding exactly `commits`. The reader under test."""
    monkeypatch.setattr(dl, "_git", _fake_git(commits))
    return dl._landed_unbound(FOCUS_ID, _row(), DRAWN_AT, {})


def test_THE_PARTITION_a_heartbeat_intersection_credits_nothing_and_a_real_one_still_credits(
        monkeypatch):
    """The whole partition in one statement, because half of it passes for the wrong reason alone.

    Three windows, one rule. A binder that returns `None` to everything satisfies the middle leg
    on its own and is exactly the failure this project keeps rebuilding; a binder that credits the
    newest commit satisfies the first two and fails the third. Only a binder that judges the
    INTERSECTION passes all three.
    """
    work_only = _credit(monkeypatch, [(WORK_SHA, [WORK_PATH])])
    heartbeat_only = _credit(monkeypatch, [(HEARTBEAT_SHA, [LIVENESS_PATH])])
    both = _credit(monkeypatch, [(HEARTBEAT_SHA, [LIVENESS_PATH]), (WORK_SHA, [WORK_PATH])])

    assert (work_only and work_only["commit"] == WORK_SHA
            and heartbeat_only is None
            and both and both["commit"] == WORK_SHA), (work_only, heartbeat_only, both)


def test_A_COMMIT_CARRYING_THE_HEARTBEAT_ALONGSIDE_REAL_WORK_IS_STILL_A_LANDING(monkeypatch):
    """The rule is CONFINED-to, not TOUCHES. The auto-process republish is both kinds at once.

    `851dffdbb` touched 52 files including the heartbeat, and would have been a perfectly good
    landing for a claim naming any of the other 51. Refusing every commit that touches a liveness
    file would be the over-correction, and it would be invisible: it removes credits rather than
    adding them, so the ledger would simply go quiet again.
    """
    verdict = _credit(monkeypatch, [(WORK_SHA, [LIVENESS_PATH, WORK_PATH])])

    assert verdict and verdict["commit"] == WORK_SHA, verdict


def test_A_COMMIT_GIT_PRINTS_NO_FILENAMES_FOR_IS_NOT_CALLED_A_HEARTBEAT(monkeypatch):
    """An empty set is vacuously a subset, and reading it as one would open the opposite blindness.

    Under a pathspec `git log` simplifies history, so a merge can come back with no filenames
    printed under it. Calling that "confined to the liveness surface" would make every such commit
    uncreditable — a new fail-silent in the direction the repair was not aimed at. The evidence
    that keeping them is safe rather than lucky is in `_window_hits`' docstring: across the last
    fourteen days of the record every `chore(liveness)` and `Auto-process run complete` commit is
    single-parent, so a commit whose intersection git will not print is never the publisher's.
    """
    verdict = _credit(monkeypatch, [(MERGE_SHA, [])])

    assert verdict and verdict["commit"] == MERGE_SHA, verdict


def test_AN_UNREADABLE_DECLARATION_REFUSES_THE_CREDIT_AND_SAYS_WHICH_CHECK_COULD_NOT_ANSWER(
        monkeypatch):
    """The three-valued discipline: a check that cannot answer is a FAILED check, and it speaks.

    Both halves are asserted because either alone is satisfied by the wrong code. That the credit
    is refused is satisfied by a binder that refuses everything; that the residual says so is
    satisfied by a reader that says it while crediting anyway. The flattering fallback available
    here is "the declaration is empty, so nothing is liveness, so credit everything" — which is
    the fail-open arriving through the check's own failure.

    IT BREAKS THE REAL DECLARATION, not a stub of the reader: emptying
    `publish_gate_blocking_read.LIVENESS_SURFACE_FILES` is the state a publisher-side mistake
    actually produces, and it reaches the code under test through the same import production takes.
    This leg is also what forces the reader to fetch the declaration as an ATTRIBUTE rather than
    binding it with `from ... import` -- a bound name would snapshot the real tuple and ignore the
    substitution, and the fail-closed branch below would be green without ever being reached.
    """
    monkeypatch.setattr(dl, "_git", _fake_git([(HEARTBEAT_SHA, [LIVENESS_PATH])]))
    monkeypatch.setattr(liveness_home, "LIVENESS_SURFACE_FILES", ())

    with pytest.raises(dl.LivenessSurfaceUnreadable):
        dl._landed_unbound(FOCUS_ID, _row(), DRAWN_AT, {})

    verdict = dl._disposition(_row(), DRAWN_AT, focus_id=FOCUS_ID, bound_at={})

    assert verdict["disposition"] == dl.NOT_DONE and residual_voices.could_not_ask(verdict) and \
        "LivenessSurfaceUnreadable" in verdict["evidence"], verdict


def test_THE_SIBLING_READING_APPLIES_THE_SAME_RULE_because_a_heartbeat_explains_no_miss(
        monkeypatch):
    """A heartbeat is not somebody ELSE's landing either, which is why the clause lives in the join.

    `_landed_by_sibling` exists to say "the commit your window produced is owned by that row over
    there". A republish that happened to touch the heartbeat is not the commit this window
    produced, and naming it would send a reader to `git show` a chore. Putting the liveness test in
    `_landed_unbound` alone would leave this reading calling it a landing — the two dispositions
    disagreeing about one second, which is what `_window_hits` is a single function to prevent.
    """
    monkeypatch.setattr(dl, "_git", _fake_git([(HEARTBEAT_SHA, [LIVENESS_PATH])]))

    sibling = dl._landed_by_sibling(FOCUS_ID, _row(), DRAWN_AT, {IN_WINDOW: "some-other-claim"})

    assert sibling is None, sibling


def test_THE_RESIDUAL_SAYS_TWELVE_HEARTBEATS_TOUCHED_YOUR_PATHS_rather_than_nothing_did(
        monkeypatch):
    """A window emptied by this rule must not be reported as though git returned nothing.

    "No commit touched your paths" sends a reader to look and find that several did, and the next
    thing they stop believing is the disposition. This is the ANSWERED voice, not `CANNOT ANSWER`:
    git was asked, on the right paths, over the right window, and what came back carried no work —
    so "workable, draw it again" is the correct instruction.
    """
    monkeypatch.setattr(dl, "_git", _fake_git([(HEARTBEAT_SHA, [LIVENESS_PATH])]))

    verdict = dl._disposition(_row(), DRAWN_AT, focus_id=FOCUS_ID, bound_at={})

    assert (verdict["disposition"] == dl.NOT_DONE
            and residual_voices.looked_and_found_nothing(verdict)
            and "liveness surface" in verdict["evidence"]), verdict
