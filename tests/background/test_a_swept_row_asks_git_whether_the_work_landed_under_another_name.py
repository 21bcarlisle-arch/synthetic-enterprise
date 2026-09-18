"""A swept window could not tell LANDED-BUT-UNBOUND from NEVER-STARTED, and read the flattering one.

THE DEFECT (director, 2026-09-16, sixth recorded instance in this lane). `delivery_lane
._disposition` names three things a window that closed with no landing of its own can be, and the
naming is right. But two of the three -- `LANDED_ELSEWHERE` and `PREMISE_SPENT` -- are written only
by a command somebody runs BY HAND, and in eleven weeks nobody ran one. So `NOT_DONE` was not the
residual it is documented as; it was the only value the reading could produce, every row came back
with an empty evidence string, and the orientation brief had to tell every reader to go and check
`git status` themselves before starting anything. A dial wired to a constant reports whatever the
constant says, and here the constant is the flattering answer in both directions at once: it hides
finished work that nothing bound, and it hides nothing else.

The two readings want OPPOSITE actions. Landed-but-unbound: read the commit, bind it, carry on.
Never-started: start. Telling a seat to do the second when the first is true is how SITE4 stayed
frozen for a week one layer up -- a repair that landed and an archival that was never committed.

KEYED TO THE PROPERTY, NEVER TO TODAY'S IDS. The property is: **a window that closed with a commit
on its own named paths inside it is never reported as evidence-free.** No id, path or count from
the live ledger appears below; the ids are synthetic and the paths are this module's own. The one
leg that asks real git asks a question true on any checkout of this repo.

MUTATIONS (each must fire, and which test catches it):
  (a) delete the `_landed_unbound` call from `_disposition` -- the partition control reds;
  (b) return `NOT_DONE` always -- the partition control reds (this is the defect itself);
  (c) drop the `when in bound_at` leg, so another lane's credited landing counts --
      `..._A_COMMIT_ANOTHER_ROW_IS_CREDITED_WITH_IS_NOT_THIS_ONES` goes red;
  (d) drop the window's upper bound, so anything after the draw counts --
      `..._A_COMMIT_OUTSIDE_THE_WINDOW_IS_NOT_IN_IT` goes red;
  (e) drop the pathspec, so any commit in the window counts --
      `..._A_COMMIT_ON_OTHER_PATHS_IS_NOT_THIS_ITEMS` goes red;
  (f) let `_paths_named_in` return its candidates unconfirmed -- `..._A_PATH_GIT_DOES_NOT_TRACK_IS
      _NOT_A_PATH` goes red;
  (g) drop the `.py` peel-back -- `..._THE_PROSE_SPELLING_OF_A_MODULE_RESOLVES` goes red;
  (h) make `record_draw` ignore its new `text` -- `..._THE_DRAW_STAMPS_WHAT_THE_ITEM_NAMED` goes
      red. (This one is listed because a new PARAMETER is the ungraded mutation in this project:
      every fixture that stubs a function with `lambda *a, **k:` swallows it silently.)
  (i) let a git failure raise or read as a hit -- `..._GIT_SILENT_READS_AS_THE_RESIDUAL` goes red.

THE PARTITION CONTROL IS FIRST AND IT IS ONE STATEMENT OVER FIVE READINGS. A `_disposition` that
answered `NOT_DONE` to everything -- which is exactly what shipped -- passes every per-branch test
ever written for it, and this lane has walked into that trap through three separate doors in one
afternoon. So all five are asserted together against one ledger.
"""
from __future__ import annotations

import json

import pytest

from background import delivery_lane as dl
from tests.background.residual_voices import looked_and_found_nothing

#: Synthetic ids. NOT the live ledger's: a control pinned to today's rows goes green the moment the
#: sweep merely gets quieter, which is the failure being fixed wearing a better name.
UNBOUND_ID = "a-window-whose-paths-moved-while-nothing-was-bound-to-it"
MISSED_ID = "a-window-nobody-touched-at-all"
SPENT_ID = "a-window-drawn-against-a-premise-already-spent"
CREDITED_ID = "a-window-whose-work-landed-under-a-better-name"
LENDER_ID = "the-name-it-landed-under"
DELIVERED_ID = "a-window-that-delivered-under-its-own-name"

NOW = 1789000000.0
#: Older than `CLAIM_STALE_SECONDS`, so every window below has closed, and inside the 24h horizon.
DRAWN_AT = NOW - 4 * 3600
WINDOW_ENDS = DRAWN_AT + dl.CLAIM_STALE_SECONDS

#: A path this repo tracks, so `_paths_named_in` confirms it on any checkout.
SUBJECT_PATH = "background/delivery_lane.py"
OTHER_PATH = "tools/surgical_land.py"

IN_WINDOW = DRAWN_AT + 900
UNBOUND_SHA = "ab12cd34ef567890ab12cd34ef567890ab12cd34"
BOUND_SHA = "99887766554433221100998877665544332211aa"


def _ledger(tmp_path, rows: dict):
    tmp_path.mkdir(parents=True, exist_ok=True)
    store = tmp_path / "claims.json"
    store.write_text("{}", encoding="utf-8")
    dl._ledger_path(store).write_text(json.dumps(rows), encoding="utf-8")
    return store


def _row(**extra):
    row = {"first_drawn_at": DRAWN_AT, "last_drawn_at": DRAWN_AT}
    row.update(extra)
    return row


@pytest.fixture(autouse=True)
def _no_cached_direction_history():
    """`_direction_history_text` caches for the life of the PROCESS, and a test suite is one.

    NOT A CONVENIENCE. The cache is filled on first use, so the first test here that stubs `_git`
    would answer every later test -- including the ones that ask REAL git -- from its fake, and a
    fake that outlives its test is the cross-test fail-open. Cleared on both sides so this file
    neither inherits a map nor leaves one behind for the rest of the suite.
    """
    dl._reset_direction_history()
    yield
    dl._reset_direction_history()


def _fake_git(log_lines, *, tracked=(SUBJECT_PATH, OTHER_PATH), revisions=()):
    """A git that answers ONLY the questions asked of it, from an explicit table.

    STRICTER THAN REAL GIT ON PURPOSE. It returns None for anything it was not told about, so it
    can only make the subject refuse MORE than the real thing would -- a fake more permissive than
    its subject is how a fail-open becomes a green suite here. `log_lines` is a list of
    `(sha, when, subject, paths)`, and the fake applies the pathspec ITSELF, which is what lets
    the pathspec leg below be a discriminator rather than a restatement of the fixture.

    `revisions` is the SECOND question, added with the history reach-back: a list of
    `(sha, yaml_text)` NEWEST FIRST, which is the order real `git log` gives. The two `log` calls
    are told apart by their PATHSPEC and not by their format string, because the pathspec is what
    the subject actually varies -- an id-keyed fixture would still be a fixture if the subject
    stopped asking about `DIRECTION.yaml` at all. `revisions=()` answers "" and None exactly as
    this fake did before the parameter existed, so every test above is untouched by it.
    """
    blobs = dict(revisions)

    def fake(*args):
        if args and args[0] == "ls-files":
            return "\n".join(tracked) + "\n"
        if args and args[0] == "show":
            sha, _, path = str(args[1]).partition(":")
            return blobs.get(sha) if path == dl.DIRECTION_RECORD_PATH else None
        if args and args[0] == "log":
            wanted = list(args[args.index("--") + 1:]) if "--" in args else []
            if wanted == [dl.DIRECTION_RECORD_PATH]:
                return "\n".join(sha for sha, _ in revisions) + "\n" if revisions else ""
            out = []
            for sha, when, subject, paths in log_lines:
                if wanted and not any(
                        p == w or p.startswith(w.rstrip("/") + "/") for p in paths for w in wanted):
                    continue
                out.append("{}\x1f{:.0f}\x1f{}".format(sha, when, subject))
            return "\n".join(out) + "\n" if out else ""
        return None
    return fake


def _record(*items) -> str:
    """A `DIRECTION.yaml` revision naming `items` as focus. Hand-written YAML, not dumped.

    The subject parses this with `yaml.safe_load` and nothing else, so writing it out is what
    makes the fixture a document rather than a round-trip of the subject's own reader.
    """
    body = ["version: 1", "oriented_at: '2026-09-16T04:00:00+00:00'", "focus:"]
    for fid, what in items:
        body.append(f"  - id: {fid}")
        body.append(f"    what: {what}")
    return "\n".join(body) + "\n"


def _five_shapes(tmp_path):
    """One ledger holding the raw material of all five readings at once."""
    return _ledger(tmp_path, {
        UNBOUND_ID: _row(named_paths=[SUBJECT_PATH]),
        MISSED_ID: _row(named_paths=[OTHER_PATH]),
        SPENT_ID: _row(premise_spent={"commit": "deadbeef123", "reason": "already closed"}),
        CREDITED_ID: _row(last_drawn_at=DRAWN_AT - 600, last_landing_at=DRAWN_AT - 60,
                          landed_under=LENDER_ID, last_landing_paths=["site/index.html"]),
        DELIVERED_ID: _row(last_landing_at=DRAWN_AT + 60, last_landing_paths=[SUBJECT_PATH]),
    })


def test_THE_PARTITION_all_five_readings_come_back_from_one_ledger_in_one_statement(
        tmp_path, monkeypatch):
    """Five readings, one ledger, one assertion: a constant answer cannot survive it.

    This is the control the whole repair turns on. What shipped answered `NOT_DONE` to every row
    and passed every test written against it, because each of those tests asked about one branch.
    The four legs that are not the residual are asserted TOGETHER with it, so a reader that has
    lost any one of them reds here whatever else is green.
    """
    store = _five_shapes(tmp_path)
    monkeypatch.setattr(dl, "_git", _fake_git([
        (UNBOUND_SHA, IN_WINDOW, "the resolver was not wired into the other two readers",
         [SUBJECT_PATH]),
    ]))

    seen = {i: dl.disposition_of(i, path=store) for i in
            (UNBOUND_ID, MISSED_ID, SPENT_ID, CREDITED_ID, DELIVERED_ID)}

    saw_landed_unbound = seen[UNBOUND_ID]["disposition"] == dl.LANDED_UNBOUND
    saw_not_done = seen[MISSED_ID]["disposition"] == dl.NOT_DONE
    saw_premise_spent = seen[SPENT_ID]["disposition"] == dl.PREMISE_SPENT
    saw_landed_elsewhere = seen[CREDITED_ID]["disposition"] == dl.LANDED_ELSEWHERE
    saw_delivered = seen[DELIVERED_ID]["disposition"] == dl.DELIVERED

    assert (saw_not_done and saw_landed_elsewhere and saw_premise_spent
            and saw_landed_unbound and saw_delivered), seen
    # The residual still SAYS WHAT IT ASKED -- keyed to the LOOKED-AND-FOUND-NOTHING voice, since
    # this row's paths were queried and came back empty, which is the one residual meaning
    # "workable, draw again". `== ""` stood here until 2026-09-18 and graded nothing once
    # `_nothing_answered` learned to speak: a residual that had quietly become the CANNOT-ANSWER
    # voice satisfies a bare `!= ""` while telling the reader the opposite. And the new value must
    # NAME ITS COMMIT -- a fourth label nobody can follow back to a fact on disk would be a fourth
    # guess.
    assert looked_and_found_nothing(seen[MISSED_ID]), seen[MISSED_ID]
    assert UNBOUND_SHA[:9] in seen[UNBOUND_ID]["evidence"]
    assert SUBJECT_PATH in seen[UNBOUND_ID]["evidence"]


def test_THE_PROPERTY_a_window_with_a_commit_on_its_own_paths_is_never_evidence_free(
        tmp_path, monkeypatch):
    """The property, asked of the LIST reading the orientation actually opens with.

    Keyed to "a commit landed on the paths this row named, inside this row's window" and to
    nothing else -- not to an id, not to a count, not to today's sweep being any particular size.
    """
    store = _ledger(tmp_path, {UNBOUND_ID: _row(named_paths=[SUBJECT_PATH])})
    monkeypatch.setattr(dl, "_git", _fake_git([
        (UNBOUND_SHA, IN_WINDOW, "a landing nothing bound", [SUBJECT_PATH]),
    ]))

    rows = dl.drawn_without_landing(now=NOW, path=store)

    assert [r["id"] for r in rows] == [UNBOUND_ID]
    assert rows[0]["disposition"] == dl.LANDED_UNBOUND
    assert rows[0]["evidence"] != ""


def test_A_COMMIT_OUTSIDE_THE_WINDOW_IS_NOT_IN_IT_whichever_side_it_falls(tmp_path, monkeypatch):
    """The window is the one the item was GIVEN, not "any time since".

    Both sides are asserted in one statement for the same reason the partition is: a reader that
    lost the lower bound would credit this row with work done before it was ever handed out, and
    one that lost the upper bound would credit it with everything that has happened since.

    THE UPPER EDGE WAS PINNED AT `WINDOW_ENDS + 60` AND WENT RED WHEN THE SUBJECT BECAME MORE
    HONEST -- repaired 2026-09-18, beside the claim. On 2026-09-17 `_landing_grace_seconds` was
    added because the one row the credit half exists for landed 606 seconds after the given window:
    a gated landing takes time, so the window a claim's EVIDENCE falls in is not the window the
    claim was GIVEN. This fixture had pinned the pre-grace edge, so a commit that is now correctly
    inside the window read as a failure of the test rather than a change in the subject -- the
    keyed-to-today's-answer shape, one file away from where it was just corrected.

    THE REPAIR IS NOT "WIDEN UNTIL GREEN", and the third leg is what makes that checkable. The
    edges are derived from the same two quantities the subject derives them from, and the middle
    leg asserts that a commit INSIDE the grace is credited -- so a subject that dropped the grace
    entirely, or one that widened the window to everything since, both red here.
    """
    store = _ledger(tmp_path, {UNBOUND_ID: _row(named_paths=[SUBJECT_PATH])})
    grace = dl._landing_grace_seconds()
    outer_edge = WINDOW_ENDS + grace
    monkeypatch.setattr(dl, "_git", _fake_git([
        ("1111111111111111111111111111111111111111", DRAWN_AT - 60, "before the draw",
         [SUBJECT_PATH]),
        ("2222222222222222222222222222222222222222", outer_edge + 60, "after the gate could run",
         [SUBJECT_PATH]),
    ]))
    assert dl.disposition_of(UNBOUND_ID, path=store)["disposition"] == dl.NOT_DONE

    # AND THE GRACE IS LOAD-BEARING, not a widening that made a red go away. A commit past the
    # given window but inside the cost of the gate that produced it is this claim's own landing.
    monkeypatch.setattr(dl, "_git", _fake_git([
        (UNBOUND_SHA, WINDOW_ENDS + grace / 2.0, "landed late through a gate that took its time",
         [SUBJECT_PATH]),
    ]))
    inside = dl.disposition_of(UNBOUND_ID, path=store)
    assert grace > 0.0 and inside["disposition"] == dl.LANDED_UNBOUND, (grace, inside)


def test_A_COMMIT_ON_OTHER_PATHS_IS_NOT_THIS_ITEMS_however_busy_the_window_was(
        tmp_path, monkeypatch):
    """Several lanes commit into this tree every hour; a commit in the window is not evidence.

    The fake applies the pathspec itself, so this leg fails if the pathspec is dropped from the
    `git log` call -- which is the mutation that would turn this reading into "was anybody busy".
    """
    store = _ledger(tmp_path, {UNBOUND_ID: _row(named_paths=[SUBJECT_PATH])})
    monkeypatch.setattr(dl, "_git", _fake_git([
        (UNBOUND_SHA, IN_WINDOW, "another lane, same hour, different subject", [OTHER_PATH]),
    ]))

    assert dl.disposition_of(UNBOUND_ID, path=store)["disposition"] == dl.NOT_DONE


def test_A_COMMIT_ANOTHER_ROW_IS_CREDITED_WITH_IS_NOT_THIS_ONES_unbound_is_the_word(
        tmp_path, monkeypatch):
    """`landed_unbound` claims NOTHING BOUND IT, and that clause has to be load-bearing.

    Lanes share files constantly here. Without this leg the busiest module in the repo would read
    as delivered work for every row that ever named it, which is the flattering direction and the
    one that would make the new value worthless within a week.

    THE FIRST LEG ASSERTED `== NOT_DONE` AND THAT WAS KEYED TO THE ANSWER, NOT THE PROPERTY --
    corrected 2026-09-18 beside the claim rather than rewritten over it. The property this test is
    named for is that `landed_unbound` MEANS nothing bound it; `not_done` was merely what the
    module happened to fall to next while `LANDED_ELSEWHERE` had no derived writer. It has one now
    (`_landed_by_sibling`), a bound commit is reported as the sibling's, and the old assertion went
    red on a module that had become MORE honest -- exactly the shape this project keeps paying for.
    The leg now says what it always meant: whatever this row is called, it is NOT credited with a
    commit somebody else holds.
    """
    store = _ledger(tmp_path, {
        UNBOUND_ID: _row(named_paths=[SUBJECT_PATH]),
        "somebody-elses-row-that-bound-it": _row(last_landing_at=IN_WINDOW,
                                                 last_landing_paths=[SUBJECT_PATH]),
    })
    monkeypatch.setattr(dl, "_git", _fake_git([
        (BOUND_SHA, IN_WINDOW, "landed and bound, by another row", [SUBJECT_PATH]),
    ]))

    bound_only = dl.disposition_of(UNBOUND_ID, path=store)
    assert bound_only["disposition"] != dl.LANDED_UNBOUND, bound_only

    # THE POISON ROUND: the same ledger, the same window, the same fake -- with a SECOND commit
    # nothing is credited with. If the leg above passed because the fake declined to speak rather
    # than because the commit was bound, this cannot go green.
    monkeypatch.setattr(dl, "_git", _fake_git([
        (BOUND_SHA, IN_WINDOW, "landed and bound, by another row", [SUBJECT_PATH]),
        (UNBOUND_SHA, IN_WINDOW + 1, "landed and nobody bound it", [SUBJECT_PATH]),
    ]))
    again = dl.disposition_of(UNBOUND_ID, path=store)
    assert again["disposition"] == dl.LANDED_UNBOUND
    assert UNBOUND_SHA[:9] in again["evidence"] and BOUND_SHA[:9] not in again["evidence"]


def test_A_PATH_GIT_DOES_NOT_TRACK_IS_NOT_A_PATH_so_the_prose_cannot_invent_a_subject(
        tmp_path, monkeypatch):
    """Every path is confirmed against `git ls-files`, which is what keeps this a join.

    Prose is written by a seat, not by a form. It names things that were deleted, things that were
    proposed and never built, and things in other repositories. A reading that accepted those would
    be asking git about a subject nobody has -- and `git log -- <unknown path>` answers EMPTY, so
    the failure would be silent in the direction that matters least. Confirming first is what makes
    an unconfirmable name reach the residual instead.
    """
    monkeypatch.setattr(dl, "_git", _fake_git([], tracked=(SUBJECT_PATH,)))

    assert dl._paths_named_in("touch background/a_module_that_was_never_written.py") == []
    assert dl._paths_named_in("see " + SUBJECT_PATH) == [SUBJECT_PATH]


def test_THE_PROSE_SPELLING_OF_A_MODULE_RESOLVES_against_the_real_repo(monkeypatch):
    """`background/delivery_lane._disposition` is a path with a symbol glued on, and it is how
    this project's prose names code -- the item that asked for this repair spelled it that way in
    its first line. Asked against REAL git, because the fact is true on any checkout of this repo:
    `background/delivery_lane.py` is tracked here or nothing else in this suite can run.
    """
    named = dl._paths_named_in(
        "give background/delivery_lane._disposition (line ~669) a git-side join, and land it with "
        "tools/surgical_land")

    assert SUBJECT_PATH in named
    # A BARE DIRECTORY IS NOT A SUBJECT. The first draft kept one as a pathspec prefix and the
    # retrospective sweep caught it: a row whose only names were `docs/design` and one html file
    # came back `landed_unbound` on a commit from a different lane entirely, because `docs/design`
    # is a room everybody writes in. Every item's prose says "file it in docs/staging/"; if that
    # counted, every swept row would name whatever anyone did that hour.
    assert dl._paths_named_in("file it in docs/staging/ with its severity header") == []


def test_THE_DRAW_STAMPS_WHAT_THE_ITEM_NAMED_so_the_join_survives_the_prose(tmp_path, monkeypatch):
    """`record_draw` gained a parameter, and a gained parameter is this project's ungraded mutation.

    By the time a swept window is read the item may have left `DIRECTION.yaml` and the continuation
    store both -- that is the normal case, not the edge one, because a finished stretch clears
    them. So the paths are stamped on the row at draw time. Making `record_draw` ignore `text`
    reds here and nowhere else: every other fixture in this lane stubs it or passes no text at all.
    """
    store = tmp_path / "claims.json"
    store.write_text("{}", encoding="utf-8")
    dl._ledger_path(store).write_text("{}", encoding="utf-8")
    monkeypatch.setattr(dl, "_git", _fake_git([]))

    dl.record_draw(UNBOUND_ID, DRAWN_AT, path=store,
                   text="rewrite " + SUBJECT_PATH + " and nothing else")
    row = json.loads(dl._ledger_path(store).read_text(encoding="utf-8"))[UNBOUND_ID]

    assert row["named_paths"] == [SUBJECT_PATH]
    # A draw carrying no prose leaves the key ABSENT rather than empty, so `_landed_unbound`'s
    # reach-back into the live stores still runs for it.
    dl.record_draw(MISSED_ID, DRAWN_AT, path=store)
    assert "named_paths" not in json.loads(
        dl._ledger_path(store).read_text(encoding="utf-8"))[MISSED_ID]


def test_GIT_SILENT_READS_AS_THE_RESIDUAL_and_never_raises_into_the_brief(tmp_path, monkeypatch):
    """An unavailable check is a FAILED check, and the direction it fails in is the whole repair.

    Three ways the join can go dark -- git refusing, git raising, and the row naming nothing
    confirmable -- and all three must land on the loud residual rather than on the flattering new
    value. Asserted together because a reader that lost one of them would be green on the other
    two, and `drawn_without_landing` is read by an orientation that must not lose its other twenty
    keys to this.
    """
    store = _ledger(tmp_path, {UNBOUND_ID: _row(named_paths=[SUBJECT_PATH])})

    monkeypatch.setattr(dl, "_git", lambda *a: None)
    silent = dl.disposition_of(UNBOUND_ID, path=store)

    def boom(*_a):
        raise OSError("git is not here")

    monkeypatch.setattr(dl, "_git", boom)
    raised = dl.disposition_of(UNBOUND_ID, path=store)
    listed = dl.drawn_without_landing(now=NOW, path=store)

    monkeypatch.setattr(dl, "_git", _fake_git([
        (UNBOUND_SHA, IN_WINDOW, "a landing on paths this row never named", [SUBJECT_PATH]),
    ]))
    unnamed = dl.disposition_of(MISSED_ID, path=_ledger(tmp_path / "b", {MISSED_ID: _row()}))

    assert (silent["disposition"] == dl.NOT_DONE and raised["disposition"] == dl.NOT_DONE
            and unnamed["disposition"] == dl.NOT_DONE), (silent, raised, unnamed)
    assert [r["disposition"] for r in listed] == [dl.NOT_DONE]


# ---------------------------------------------------------------------------------------------
# THE REACH, not the join (2026-09-16, second pass on this mechanism).
#
# The join above was right and it ran on a fifth of its room. Measured on the live ledger before
# any of this was written: 67 rows had closed a window with nothing landed, 9 of them could be
# given a subject at all, 8 named a path git tracks, and the join returned 2 hits. The other 58
# were not silent because their prose never existed -- a doorbell was printed for every one of
# them -- but because BOTH STORES `_item_text` READ ARE LIVE STORES, and an item's prose leaves
# them within hours while its ledger row survives for months. Reading `DIRECTION.yaml`'s COMMITTED
# HISTORY takes the same measurement to 48 with a subject, 45 with a tracked path, and 21 hits.
#
# KEYED TO THE PROPERTY, NEVER TO THOSE NUMBERS. The property is: **a row whose prose has left
# every live store is still given the subject its prose named, and the live stores still outrank a
# revision that has since been rewritten.** The numbers are the finding; the controls below are
# synthetic end to end and would hold on an empty ledger.
#
# MUTATIONS (each must fire, and which test catches it):
#   (j) delete the history fallback from `_item_text` -- `..._A_ROW_WHOSE_PROSE_LEFT_EVERY_LIVE
#       _STORE` reds (this is the defect itself);
#   (k) consult the history ALWAYS instead of only when the live stores are silent --
#       `..._THE_LIVE_STORES_OUTRANK_A_REVISION_SINCE_REWRITTEN` reds;
#   (l) take the OLDEST revision naming an id, or merge every revision's prose --
#       `..._THE_NEWEST_REVISION_IS_THE_ONE_THAT_DESCRIBES_THE_WINDOW` reds;
#   (m) let one unparseable revision abort the walk -- `..._A_REVISION_THAT_WILL_NOT_PARSE`  reds;
#   (n) drop `_reset_direction_history`, or stop calling it -- nothing reds HERE, which is the
#       point of the autouse fixture: the cache is process-wide, and a stub that outlives its test
#       is not a defect this file can assert about itself. It is asserted from the other side, by
#       `..._THE_CACHE_IS_BUILT_ONCE_AND_RESETTABLE`.


def test_THE_REACH_a_row_whose_prose_left_every_live_store_still_gets_its_subject(
        tmp_path, monkeypatch):
    """The widening, as one statement over the partition it splits.

    ONE LEDGER, ONE ROW, TWO GITS. The row has no `named_paths` stamp (it predates it, which is
    what all 58 of them are) and neither live store holds it. With a git whose `DIRECTION.yaml`
    history names it, the subject is recovered and the window's commit is found; with a git whose
    history is empty, the same row falls to the loud residual. Asserting both together is what
    makes this the reach and not a restatement of the join -- a `_item_text` that returned the
    item's prose unconditionally would pass the first leg and fail the second.
    """
    store = _ledger(tmp_path, {MISSED_ID: _row()})
    landing = [(UNBOUND_SHA, IN_WINDOW, "the work, landed under nobody's name", [SUBJECT_PATH])]

    monkeypatch.setattr(dl, "_git", _fake_git(landing, revisions=(
        ("rev1", _record((MISSED_ID, "rewrite " + SUBJECT_PATH + " so the join has a subject"))),
    )))
    reached = dl.disposition_of(MISSED_ID, path=store)

    dl._reset_direction_history()
    monkeypatch.setattr(dl, "_git", _fake_git(landing, revisions=()))
    unreached = dl.disposition_of(MISSED_ID, path=store)

    assert reached["disposition"] == dl.LANDED_UNBOUND, reached
    assert UNBOUND_SHA[:9] in reached["evidence"] and SUBJECT_PATH in reached["evidence"]
    assert unreached["disposition"] == dl.NOT_DONE, unreached


def test_THE_LIVE_STORES_OUTRANK_a_revision_since_rewritten(tmp_path, monkeypatch):
    """A row a live store still describes is described by THAT, and git is not consulted for it.

    WHY THE FALLBACK IS NOT A THIRD VOICE. The history holds every revision the record ever had,
    including subjects its owner has since narrowed or dropped. Splicing those in beside the live
    text can only ADD paths, more paths is more chance of a commit landing on one, and a hit
    manufactured from a subject the item no longer claims is evidence in the flattering direction
    -- which is the failure `LANDED_UNBOUND` was written to end, one layer in.

    The discriminator is that the stale revision names `OTHER_PATH` and the live store does not,
    and the only commit in the window is on `OTHER_PATH`. A `_item_text` that unioned the two
    would report this window as landed-but-unbound on a file the item stopped naming.
    """
    store = _ledger(tmp_path, {MISSED_ID: _row()})
    monkeypatch.setattr(dl.direction_mod, "unreachable_focus", lambda *_a, **_k: [
        {"id": MISSED_ID, "what": "rewrite " + SUBJECT_PATH, "why": "", "done_means": ""},
    ])
    monkeypatch.setattr(dl, "_git", _fake_git(
        [(UNBOUND_SHA, IN_WINDOW, "a landing on the subject this item DROPPED", [OTHER_PATH])],
        revisions=(("rev1", _record((MISSED_ID, "an older cut of this item, over " + OTHER_PATH))),
                   )))

    assert dl.disposition_of(MISSED_ID, path=store)["disposition"] == dl.NOT_DONE
    # ...and the same fixture with the live store SILENT is the positive half, so the leg above
    # is proven to be the live store winning rather than the history simply never working here.
    dl._reset_direction_history()
    monkeypatch.setattr(dl.direction_mod, "unreachable_focus", lambda *_a, **_k: [])
    assert dl.disposition_of(MISSED_ID, path=store)["disposition"] == dl.LANDED_UNBOUND


def test_THE_NEWEST_REVISION_IS_THE_ONE_THAT_DESCRIBES_THE_WINDOW(monkeypatch):
    """`git log` is newest-first and the first revision naming an id is the one kept.

    An item rewritten between orientations has several revisions describing it, and the newest is
    the closest thing on disk to the prose the draw was made against. Taking the oldest, or
    merging them all, both pass a single-revision fixture -- so the fixture carries three, and the
    two the walk must NOT return name a path that would change the answer.
    """
    monkeypatch.setattr(dl, "_git", _fake_git([], revisions=(
        ("newest", _record((MISSED_ID, "the current cut, over " + SUBJECT_PATH))),
        ("middle", _record((MISSED_ID, "an earlier cut, over " + OTHER_PATH))),
        ("oldest", _record((MISSED_ID, "the first cut, over " + OTHER_PATH))),
    )))

    assert dl._paths_named_in(dl._item_text(MISSED_ID)) == [SUBJECT_PATH]


def test_A_REVISION_THAT_WILL_NOT_PARSE_does_not_take_the_walk_down(monkeypatch):
    """One bad revision in seventy is a skipped revision, never a lost history.

    `DIRECTION.yaml` is hand-written by the seat and its history contains whatever was committed,
    including mid-edit states. A walk that aborted on the first `yaml` error would go silent for
    every id behind that revision -- and silent here reads as "the item named no subject", which
    is the flattering answer. So the newest revision is deliberately unparseable and the id behind
    it must still come back.
    """
    monkeypatch.setattr(dl, "_git", _fake_git([], revisions=(
        ("broken", "focus:\n  - id: [unterminated\n"),
        ("good", _record((MISSED_ID, "the prose behind the broken revision, "
                                     "over " + SUBJECT_PATH))),
    )))

    assert dl._paths_named_in(dl._item_text(MISSED_ID)) == [SUBJECT_PATH]


def test_THE_CACHE_IS_BUILT_ONCE_AND_RESETTABLE(monkeypatch):
    """The walk costs one `git show` per revision, and the reader asks it PER ROW.

    `drawn_without_landing` runs `_item_text` for every swept row without a stamp, so a walk
    rebuilt per row multiplies the whole history by the population -- the reason the map is
    cached. The cache is process-wide, which is also how a monkeypatched git leaks out of the test
    that installed it, so the reset is part of the mechanism rather than test scaffolding and is
    asserted here as such.
    """
    calls = []
    inner = _fake_git([], revisions=(("rev1", _record((MISSED_ID, "over " + SUBJECT_PATH))),))

    def counting(*args):
        calls.append(args[0] if args else "")
        return inner(*args)

    monkeypatch.setattr(dl, "_git", counting)

    first = dl._direction_history_text()
    walked = calls.count("show")
    again = dl._direction_history_text()

    assert first == again and walked == 1
    assert calls.count("show") == walked, "a second call re-walked the history"

    dl._reset_direction_history()
    dl._direction_history_text()
    assert calls.count("show") == walked + 1, "the reset did not drop the cached map"


def test_THE_CLAIM_NOTE_LEG_IS_NOT_WRITTEN_and_the_store_says_why(tmp_path):
    """The reach-back the instruction asked for, and the measurement that says it cannot fire.

    THE INSTRUCTION NAMED TWO SOURCES AND NEITHER IS THE ONE IMPLEMENTED, which is recorded here
    rather than only in prose, because "we considered it" is unfalsifiable and this is not. The
    claim store is keyed by id and does hold a note -- but `release` and `sweep_stale` POP the
    record, and EVERY row this reach-back serves is by definition one whose window closed and was
    swept. So the leg is not empty today; it is empty for every row it would ever be asked about,
    which is the branch-that-cannot-be-taken shape (R15) rather than a source worth reading.

    Asserted over the STORE'S OWN BEHAVIOUR and not over today's file: claim, sweep, and show that
    what the sweep leaves behind carries no note to read.
    """
    store = tmp_path / "claims.json"
    store.write_text("{}", encoding="utf-8")
    dl.claims_mod.claim(MISSED_ID, note="rewrite " + SUBJECT_PATH, path=store)

    assert (dl.claims_mod._load(store).get(MISSED_ID) or {}).get("note")

    dl.claims_mod.release(MISSED_ID, path=store)

    assert dl.claims_mod._load(store).get(MISSED_ID) is None, (
        "a released claim still holds its note -- if this ever becomes true the claim-note leg "
        "is worth writing, and this control is where that is noticed")
