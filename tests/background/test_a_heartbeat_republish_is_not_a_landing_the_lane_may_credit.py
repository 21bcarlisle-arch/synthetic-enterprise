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

THE RULE WAS ON THE READER ONLY UNTIL 2026-09-21, WHICH IS THE OTHER HALF OF THE SAME DEFECT, and
the legs below the `--- THE WRITER ---` banner are that half. Everything above grades
`_window_hits`, which DESCRIBES the ledger. `record_landing` is what FILLS IT IN, it takes
`commit: str = "HEAD"` because every documented call is the bare `--landed <id>`, and 28 of the
last 200 HEADs on this record are pure liveness republishes -- so the writer went on binding
exactly the commits the reader had learned to refuse. A control pinning the reader is blind to a
cap in the writer; this project has a register entry for the shape and walked into it again here.

WRITER MUTATIONS (each must fire, and which leg catches it):
  (g) delete the liveness clause from `record_landing` -- the writer partition's heartbeat leg
      reds, and its work and mixed legs are what stop a binder that refuses everything passing;
  (h) leave the clause but not the cause-naming in `refusal_reason` --
      `test_THE_WRITERS_REFUSAL_NAMES_THE_HEARTBEAT_AND_THE_COMMIT_FLAG_THAT_ESCAPES_IT` reds;
  (i) judge the INTERSECTION with the claim's named paths here rather than the whole commit (the
      reader's question, asked in the wrong place) -- the writer's heartbeat leg reds, because the
      row below names a liveness path and the intersection would be non-empty either way;
  (j) fall back to "nothing is liveness" when the declaration will not read --
      `test_AN_UNREADABLE_DECLARATION_REFUSES_THE_WRITE_TOO` reds.
"""
from __future__ import annotations

import pytest

from background import delivery_lane as dl
from background import publish_gate_blocking_read as liveness_home
from background import seat_work_in_hand as claims_mod
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


# --- THE WRITER -------------------------------------------------------------------------------
# Everything above grades the reading. `record_landing` is the WRITE, and until 2026-09-21 it had
# none of this: see the module docstring's second half for why that is the more expensive side.


def _fake_git_commit(touched: list[str]):
    """A `_git` answering the three queries `_commit_facts` asks of a single-parent commit.

    A SEPARATE FAKE FROM `_fake_git`, deliberately, and not a flag on it. That one's whole value is
    that it prints filenames only when `--name-only` is in the ARGS, which is what makes the
    reader's mutation (c) fire; the writer asks `show` and always passes the flag, so folding the
    two together would either lose that property or grow a branch nobody grades. Going through
    `_commit_facts` for real rather than stubbing it keeps `record_landing`'s own ordering under
    test: the clause has to sit after the paths are known and before the bind.
    """
    def fake(*args: str) -> str | None:
        if not args:
            return ""
        if args[0] == "rev-list":
            return "{} {}".format(args[-1], "d" * 40)
        if args[0] == "show" and "-s" in args:
            return "{:.0f}\n".format(IN_WINDOW)
        if args[0] == "show":
            return "\n".join(touched) + "\n"
        return ""
    return fake


def _bind(monkeypatch, tmp_path, touched: list[str]) -> list[str]:
    """What `record_landing` binds to a live claim from a commit touching exactly `touched`."""
    store = tmp_path / "claims.json"
    claims_mod.claim(FOCUS_ID, "doing the thing", paths=[], path=store, now=DRAWN_AT)
    monkeypatch.setattr(dl, "_git", _fake_git_commit(touched))
    return dl.record_landing(FOCUS_ID, commit=WORK_SHA, path=store)


def test_THE_WRITERS_PARTITION_a_heartbeat_binds_nothing_and_real_work_still_binds(
        monkeypatch, tmp_path):
    """The writer's whole partition in one statement, for the reason the reader's is one too.

    A binder that returns `[]` to everything satisfies the middle leg alone, and this project has
    entered that trap through three separate doors in one afternoon. The third leg is the one that
    separates the rule from an over-correction: the publisher's 52-file republish is a perfectly
    good landing for a claim naming any of the other fifty-one, so CONFINED-to is the test and
    TOUCHES is not.
    """
    work_only = _bind(monkeypatch, tmp_path / "a", [WORK_PATH])
    heartbeat_only = _bind(monkeypatch, tmp_path / "b", [LIVENESS_PATH])
    mixed = _bind(monkeypatch, tmp_path / "c", [LIVENESS_PATH, WORK_PATH])

    assert (work_only == [WORK_PATH]
            and heartbeat_only == []
            and sorted(mixed) == sorted([LIVENESS_PATH, WORK_PATH])), (
        work_only, heartbeat_only, mixed)


def test_THE_WRITER_JUDGES_THE_WHOLE_COMMIT_not_its_overlap_with_the_claims_named_paths(
        monkeypatch, tmp_path):
    """The reader's question asked here would be the wrong one, and it would look right.

    `_window_hits` judges a commit's INTERSECTION with the claim's paths because it is choosing
    among commits that already touched them. `record_landing` has no intersection to take -- the
    caller named a commit, not a claim's paths -- and a claim that happens to name a liveness path
    would then have a republish's overlap read as "work confined to nothing else", or not, on a
    fact about the CLAIM rather than about the COMMIT. Judging the whole commit is the stricter
    side and the one keyed to the property: did this commit carry work at all?

    The claim here names NO paths, so an intersection-based binder has nothing to intersect and
    every branch of it would have to invent an answer. The commit is still a heartbeat.
    """
    store = tmp_path / "claims.json"
    claims_mod.claim(FOCUS_ID, "a claim naming nothing", paths=[], path=store, now=DRAWN_AT)
    monkeypatch.setattr(dl, "_git", _fake_git_commit([LIVENESS_PATH]))

    assert dl.record_landing(FOCUS_ID, commit=HEARTBEAT_SHA, path=store) == []


def test_THE_WRITERS_REFUSAL_NAMES_THE_HEARTBEAT_AND_THE_COMMIT_FLAG_THAT_ESCAPES_IT(
        monkeypatch, tmp_path):
    """A refusal that does not say WHY gets the wrong repair, and here both wrong ones are dear.

    Read as "the lane is broken" it gets the bind retried against the same republish; read as "my
    work did not land" it gets the work done again. What it means is neither: you landed real work
    and then bound the wrong commit, because `--landed <id>` defaults to HEAD and a republish got
    there first. So the reason names the class AND the escape, and both are asserted -- a reason
    saying "heartbeat" without telling a caller who has never passed `--commit` that it exists
    leaves them with a correct diagnosis and no move.
    """
    store = tmp_path / "claims.json"
    claims_mod.claim(FOCUS_ID, "doing the thing", paths=[], path=store, now=DRAWN_AT)
    monkeypatch.setattr(dl, "_git", _fake_git_commit([LIVENESS_PATH]))

    reason = dl.refusal_reason(FOCUS_ID, commit=HEARTBEAT_SHA, path=store)

    assert ("HEARTBEAT" in reason and LIVENESS_PATH in reason and "--commit" in reason), reason


def test_AN_UNREADABLE_DECLARATION_REFUSES_THE_WRITE_TOO(monkeypatch, tmp_path):
    """The three-valued discipline on the writing side: a check that cannot answer refuses.

    The flattering fallback is the same one the reader had available -- "the declaration is empty,
    so nothing is liveness, so bind it" -- and it is worse here, because the reader's version of
    that mistake writes a sentence and this one writes the ledger.

    THE REFUSAL IS TOTAL, AND SAYING SO IS THE POINT. An unreadable declaration refuses the bind
    for a commit of plain work too, because nothing can be shown to carry work when the thing that
    says what does not carry work will not read. The cost is one unbound increment and a sweep, and
    a swept row is redrawn. So this leg's own danger is that "refused" is what a permanently broken
    binder looks like -- which is why the control is the SAME work commit through an INTACT
    declaration, in the same statement: only a binder that reads the declaration passes both.

    IT BREAKS THE REAL DECLARATION, for the reason the reader's twin gives: emptying
    `publish_gate_blocking_read.LIVENESS_SURFACE_FILES` is the state a publisher-side mistake
    actually produces, and it reaches the code under test through the import production takes.
    """
    with_declaration = _bind(monkeypatch, tmp_path / "intact", [WORK_PATH])
    monkeypatch.setattr(liveness_home, "LIVENESS_SURFACE_FILES", ())
    heartbeat = _bind(monkeypatch, tmp_path / "broken-heartbeat", [LIVENESS_PATH])
    work = _bind(monkeypatch, tmp_path / "broken-work", [WORK_PATH])

    assert (with_declaration == [WORK_PATH] and heartbeat == [] and work == []), (
        with_declaration, heartbeat, work)
