"""A window that closed HOURS BEFORE its own subject existed read as an ordinary miss.

THE DEFECT, measured on this lane's live ledger 2026-09-18. `read-the-next12-twelve-alone-once-the-
0358-run-settles` was written at 23:52 carrying its own subject's arrival -- *"ETA near 03:58; do
not draw this before then, the file will not exist"* -- was drawn at 00:07, and its whole 100-minute
window plus the landing grace closed at 02:47. The artefact it exists to read did not exist then and
still did not exist at 05:15 with its producing run ten hours in. No turn under that claim could
have committed anything, and the row read `not_done` with an EMPTY EVIDENCE STRING: the same answer
the ledger gives a lane that was handed usable work and dropped it.

The two readings want OPPOSITE actions, which is what makes conflating them expensive rather than
untidy. A real miss says: draw it again, it is workable. A window that closed before its subject
arrived says: do NOT draw it again yet, and the four previous draws of this exact item each burned
an invocation proving that.

IT IS A FIFTH VALUE AND NOT A FIFTH ROUTE TO AN OLD ONE, and the module's own comment block insists
on that distinction because a partition control stops covering its partition when the vocabulary is
inflated. `PREMISE_NOT_YET_RIPE` is the MIRROR of `PREMISE_SPENT` -- spent says the premise was
already consumed, this says it had not yet arrived -- so reporting either as the other states the
opposite of what was measured.

KEYED TO THE PROPERTY, NEVER TO TODAY'S ROW. The property is: **a window that closed entirely before
the instant its own prose names is never reported as an evidence-free miss.** No live id, path or
count appears below. The one leg that quotes the live sentence quotes it as a GRAMMAR sample, and
asserts what is parsed from it, not that any particular row exists.

MUTATIONS (each must fire, and which test catches it):
  (a) delete the `_drawn_before_stated_start` call from `_disposition` -- the partition control
      reds, because `PREMISE_NOT_YET_RIPE` becomes unreachable from any ledger;
  (b) return `NOT_DONE` always, or `PREMISE_NOT_YET_RIPE` always -- the partition control reds;
  (c) drop `_landing_grace_seconds()` from the window end, or drop `CLAIM_STALE_SECONDS`, so a row
      with usable time is excused -- `..._A_WINDOW_WITH_USABLE_TIME_IS_AN_ORDINARY_MISS` goes red;
  (d) flip the comparison to `window_ends >= until`/`<` -- the same test goes red, from the other
      side, because its two legs straddle the edge;
  (e) ask this BEFORE `_landed_unbound` or `_landed_by_sibling`, so a stated start hides real work
      -- `..._A_STATED_START_NEVER_HIDES_A_COMMIT` goes red;
  (f) drop EITHER digit guard from `_CLOCK_TIME`, so a timestamp's tail is read as a clock time --
      `..._A_DURATION_IS_NOT_A_CLOCK_TIME` goes red. Listed as TWO mutations because dropping both
      together was an EQUIVALENCE on the sample first written, and that is recorded in the test
      rather than papered over: `(?<![:\\d])` is caught only by the timestamp-FIRST ordering and
      `(?![:\\d])` only by the timestamp-LAST one, so a single sample grades one guard at most;
  (g) take `max()` of the candidate times instead of the nearest antecedent --
      `..._THEN_MEANS_THE_NEAREST_ANTECEDENT` goes red;
  (h) anchor `_back_referenced_start` on `now` instead of the DRAW instant --
      `..._THE_ANCHOR_IS_THE_DRAW_SO_A_ROWS_DISPOSITION_DOES_NOT_DRIFT` goes red;
  (i) let an unreadable item text raise rather than decline -- `..._PROSE_THAT_STATES_NOTHING_READS
      _AS_THE_RESIDUAL` goes red;
  (j) collapse the residual's two voices back into one -- return the genuine-miss sentence from the
      branch where the asking RAISED, or the CANNOT-ANSWER sentence from the branch where git was
      asked and answered -- and the legs re-keyed 2026-09-18 go red, one per voice.
  (k)-(n) the RESIDUAL's own branches going silent, constant, or reciting a query they never
      ran -- carried by `..._THE_RESIDUAL_PARTITION_every_reachable_branch_names_what_it_asked
      _or_what_it_broke_on` at the foot of this file, which keeps its own mutation list because
      (n) exists only to separate two legs this index would have shown as one. That test is the
      reachability-before-behaviour half: it asserts the three branches are DISTINCT before it
      examines any wording, so a residual answering one constant dies before the silence leg.

AND THREE OF THOSE LEGS WERE THEMSELVES KEYED TO THE DAY'S ANSWER (repaired 2026-09-18, beside the
claim rather than quietly). They asserted `evidence == ""`, which the opening paragraph above names
as HALF THE DEFECT -- silence is what made a genuine miss and an unanswerable one the same row. When
`_nothing_answered` was given a reason per branch (commit 2984864c7) the code became more honest and
these three went RED, the exact backwards direction CLAUDE.md warns of. The prediction they encoded
is left standing here: the leg that said the residual "stays LOUD" in its docstring asserted it was
silent in its body, and the body was wrong. They are now keyed to WHICH VOICE the residual used,
which the empty string could not express at all.

THE CLASS WAS EIGHT LEGS ACROSS FOUR SUITES, not the three here, and the other five were found by
running the neighbours rather than by grepping for the sentence. `tests/background/residual_voices.py`
is the one home the predicate lives in, because four private copies of it is how the next widening
drifts in three files and nobody notices -- and the point of `2984864c7` was that ONE function
decides which voice the residual used.

THE PARTITION CONTROL IS FIRST AND IT IS ONE STATEMENT OVER SIX READINGS, for the reason the two
sibling files give: a `_disposition` that answers one constant passes every per-branch test ever
written for it, and this lane has walked into that trap through three doors in one afternoon.
"""
from __future__ import annotations

import datetime
import json

import pytest

from background import delivery_lane as dl
from tests.background.residual_voices import could_not_ask, looked_and_found_nothing

#: Synthetic ids. A control pinned to the live ledger's rows goes green when the sweep merely gets
#: quieter, which is the failure being fixed wearing a better name.
EARLY_ID = "a-window-that-closed-before-its-own-subject-existed"
MISSED_ID = "a-window-nobody-touched-at-all"
SPENT_ID = "a-window-drawn-against-a-premise-already-spent"
CREDITED_ID = "a-window-whose-work-landed-under-a-better-name"
UNBOUND_ID = "a-window-whose-paths-moved-while-nothing-was-bound-to-it"
DELIVERED_ID = "a-window-that-delivered-under-its-own-name"

NOW = 1789000000.0
#: Older than `CLAIM_STALE_SECONDS` plus the grace, so every window below has closed.
DRAWN_AT = NOW - 8 * 3600
WINDOW_ENDS = DRAWN_AT + dl.CLAIM_STALE_SECONDS + dl._landing_grace_seconds()

SUBJECT_PATH = "background/delivery_lane.py"
#: A SECOND tracked path, so the partition's early row and its unbound row cannot be handed the
#: same commit by one fake. Sharing one path made the early row read `landed_unbound` -- a fixture
#: defect that looked exactly like the new reading being unreachable.
QUIET_PATH = "tools/surgical_land.py"
UNBOUND_SHA = "ab12cd34ef567890ab12cd34ef567890ab12cd34"
IN_WINDOW = DRAWN_AT + 900


def _hhmm(stamp: float) -> str:
    return datetime.datetime.fromtimestamp(stamp).strftime("%H:%M")


def _states_start_at(stamp: float) -> str:
    """Prose naming `stamp` in the BACK-REFERENCED spelling, built from the instant itself.

    Built rather than typed so the legs below move with `CLAIM_STALE_SECONDS` and the grace instead
    of pinning a clock time that a change to either would make meaningless -- the keyed-to-today's-
    answer shape this file exists one rung away from.
    """
    return ("Read the artefact once the run settles. ETA near {}; do not draw this before then, "
            "the file will not exist.".format(_hhmm(stamp)))


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


def _fake_git(commits):
    """`_git` answering `log` with `commits`, APPLYING THE PATHSPEC ITSELF.

    Applying it here is what makes the pathspec load-bearing: a subject that stopped passing the
    paths to `git log` would still get an empty answer from this fake for the off-subject rows.

    `""`, NOT `None`, FOR "NO MATCHES" (corrected 2026-09-18, same correction as the copy of this
    helper in `test_every_disposition_names_what_was_checked.py`). Real `git log` exits 0 and prints
    nothing when the pathspec matches nothing; `None` is reserved for a git that could not run at
    all. The fake said `None` to both, which is the conflation `_git_or_raise` was written to end,
    and it went unnoticed for as long as the subject collapsed the two anyway.

    AND IT ANSWERS `ls-files` (corrected 2026-09-18, later the same day, when `_tracked_files` was
    given the same treatment). This fake said `None` to everything that was not `log`, so the tracked
    set came back EMPTY and `_paths_named_in` could confirm no spelling of anything -- which meant
    the no-paths branch below was reached by GIT'S SILENCE rather than by the road its own comment
    claims, an item whose prose names nothing we track. The leg was green and grading the wrong
    thing: a fake more permissive than its subject, holding open exactly the conflation the subject
    was being repaired to close. It now lists the two real paths this file already uses, so the
    no-paths branch is reached only by prose that genuinely names none of them.
    """
    def run(*args, **kwargs):
        if args and args[0] == "ls-files":
            return "\n".join((SUBJECT_PATH, QUIET_PATH))
        if not args or args[0] != "log":
            return None
        wanted = set(args[args.index("--"):][1:]) if "--" in args else set()
        lines = []
        for sha, when, subject, paths in commits:
            if wanted and not (set(paths) & wanted):
                continue
            lines.append("{}\x1f{:.0f}\x1f{}".format(sha, when, subject))
        return "\n".join(lines)
    return run


@pytest.fixture(autouse=True)
def _no_cached_direction_history():
    """`_direction_history_text` caches for the life of the PROCESS, and a suite is one process.

    A fake that outlives its test is the cross-test fail-open: the first test here to stub `_git`
    would otherwise answer every later one, including those that mean to ask real git.
    """
    dl._reset_direction_history()
    yield
    dl._reset_direction_history()


@pytest.fixture
def prose(monkeypatch):
    """Stub `_item_text` per id. The item stores hold no synthetic row, so the reader needs this."""
    texts: dict[str, str] = {}
    monkeypatch.setattr(dl, "_item_text", lambda fid: texts.get(str(fid), ""))
    return texts


def test_THE_PARTITION_all_six_readings_come_back_from_one_ledger_in_one_statement(
        tmp_path, monkeypatch, prose):
    """Six readings, one ledger, one assertion: a constant answer cannot survive it.

    The five that already existed are asserted here TOGETHER with the new one, not because they
    lack their own file, but because adding a value to a partition without restating the whole
    partition is how the next reading quietly swallows an older one. A `_disposition` that answered
    `PREMISE_NOT_YET_RIPE` to everything would be the same defect as the `NOT_DONE`-always reader
    it replaces, and only a statement over all six catches it.
    """
    store = _ledger(tmp_path, {
        EARLY_ID: _row(named_paths=[QUIET_PATH]),
        MISSED_ID: _row(named_paths=[QUIET_PATH]),
        UNBOUND_ID: _row(named_paths=[SUBJECT_PATH]),
        # `at` IS PART OF THE SHAPE, not decoration: `note_premise_spent` is the only writer of
        # this field and has stamped all three keys since the field existed, and `_disposition`
        # compares that instant against THIS draw so a stated premise cannot explain a later
        # window. A fixture without it asserts a row no producer can make -- which is how the
        # across-windows fail-open on this branch stayed invisible until 2026-09-19.
        SPENT_ID: _row(premise_spent={"commit": "deadbeef123", "reason": "already closed",
                                      "at": DRAWN_AT + 60}),
        CREDITED_ID: _row(last_drawn_at=DRAWN_AT - 600, last_landing_at=DRAWN_AT - 60,
                          landed_under="the-name-it-landed-under",
                          last_landing_paths=["site/index.html"]),
        DELIVERED_ID: _row(last_landing_at=DRAWN_AT + 60, last_landing_paths=[SUBJECT_PATH]),
    })
    prose[EARLY_ID] = _states_start_at(WINDOW_ENDS + 3600)
    monkeypatch.setattr(dl, "_git", _fake_git([
        (UNBOUND_SHA, IN_WINDOW, "a landing nothing bound", [SUBJECT_PATH]),
    ]))

    seen = {i: dl.disposition_of(i, path=store) for i in
            (EARLY_ID, MISSED_ID, UNBOUND_ID, SPENT_ID, CREDITED_ID, DELIVERED_ID)}

    assert (seen[EARLY_ID]["disposition"] == dl.PREMISE_NOT_YET_RIPE
            and seen[MISSED_ID]["disposition"] == dl.NOT_DONE
            and seen[UNBOUND_ID]["disposition"] == dl.LANDED_UNBOUND
            and seen[SPENT_ID]["disposition"] == dl.PREMISE_SPENT
            and seen[CREDITED_ID]["disposition"] == dl.LANDED_ELSEWHERE
            and seen[DELIVERED_ID]["disposition"] == dl.DELIVERED), seen

    # The residual is STILL what is left when no join holds -- that is what makes it the residual
    # and not a sixth guess -- but what makes it CHECKABLE is that it says what it asked. Keyed to
    # the LOOKED-AND-FOUND-NOTHING voice specifically: this row's paths were queried and came back
    # empty, so it is the one residual that means "workable, draw again". A partition whose residual
    # quietly became the CANNOT-ANSWER voice would still satisfy a bare `!= ""` and would be telling
    # the reader the opposite. And the new value must NAME THE INSTANT it is claiming, or it is a
    # label a reader cannot check against the item's own prose.
    assert looked_and_found_nothing(seen[MISSED_ID]), seen[MISSED_ID]
    assert _hhmm(WINDOW_ENDS + 3600) in seen[EARLY_ID]["evidence"]

    # AND THE NEW VALUE IS THE MIRROR OF `PREMISE_SPENT`, NEVER THE SAME VALUE. Both rows are in
    # this ledger at once and they must not collapse: one premise was consumed, the other had not
    # arrived, and a reader given the wrong one is told to do the opposite of the right thing.
    assert dl.PREMISE_NOT_YET_RIPE != dl.PREMISE_SPENT


def test_A_WINDOW_WITH_USABLE_TIME_IS_AN_ORDINARY_MISS_however_it_was_stamped(
        tmp_path, monkeypatch, prose):
    """The clause that stops this becoming an excuse any item can claim.

    A row drawn five minutes before its subject appears had ninety-five usable minutes; the stated
    instant explains nothing there and this reading must not say it does. Both sides of the edge
    are asserted in ONE test because that is what makes "widen until green" visible: the edges are
    derived from the same two quantities the subject derives them from, so a fix that dropped the
    grace, dropped the stale window, or flipped the comparison reds one leg or the other.
    """
    store = _ledger(tmp_path, {EARLY_ID: _row(named_paths=[SUBJECT_PATH])})
    monkeypatch.setattr(dl, "_git", _fake_git([]))

    # INSIDE: the subject arrived while the claim was still live, so the turn had time to work.
    prose[EARLY_ID] = _states_start_at(WINDOW_ENDS - 1800)
    usable = dl.disposition_of(EARLY_ID, path=store)
    # ORDINARY MISS means the LOOKED-AND-FOUND-NOTHING voice, not merely "not the ripe one": the
    # whole point of the edge is that this row is workable and should be drawn again, which is the
    # single thing that voice says and the CANNOT-ANSWER one denies.
    assert looked_and_found_nothing(usable), usable

    # OUTSIDE: not one minute of the window, nor of the grace a gated landing costs, was usable.
    prose[EARLY_ID] = _states_start_at(WINDOW_ENDS + 1800)
    unusable = dl.disposition_of(EARLY_ID, path=store)
    assert unusable["disposition"] == dl.PREMISE_NOT_YET_RIPE, unusable

    # AND THE GRACE IS LOAD-BEARING rather than a widening that made a red go away: an instant
    # inside the grace is still usable time, and a subject that dropped the term reads it as not.
    assert dl._landing_grace_seconds() > 0.0
    prose[EARLY_ID] = _states_start_at(WINDOW_ENDS - dl._landing_grace_seconds() / 2.0)
    in_grace = dl.disposition_of(EARLY_ID, path=store)
    assert in_grace["disposition"] == dl.NOT_DONE, in_grace


def test_A_STATED_START_NEVER_HIDES_A_COMMIT_because_it_is_asked_last(
        tmp_path, monkeypatch, prose):
    """The louder readings keep first refusal, and this proves the ORDER and not just the branch.

    A row can carry both a stated start and a commit on its own paths -- the item was drawn early,
    re-drawn, and landed. Reported as `PREMISE_NOT_YET_RIPE` a reader is told there was nothing to
    do, over a commit sitting in the window. The unbound reading is the creditable one and must
    win; this is asked only once it has declined.
    """
    store = _ledger(tmp_path, {
        EARLY_ID: _row(named_paths=[SUBJECT_PATH]),
        "a-sibling-row-that-bound-it": _row(last_landing_at=IN_WINDOW,
                                            last_landing_paths=[SUBJECT_PATH]),
    })
    prose[EARLY_ID] = _states_start_at(WINDOW_ENDS + 3600)

    monkeypatch.setattr(dl, "_git", _fake_git([
        (UNBOUND_SHA, IN_WINDOW + 1, "landed and nobody bound it", [SUBJECT_PATH]),
    ]))
    assert dl.disposition_of(EARLY_ID, path=store)["disposition"] == dl.LANDED_UNBOUND

    # THE SIBLING READING IS ALSO LOUDER. Same prose, same window -- only the commit's ownership
    # changes -- so a subject that asked the stated start before either of them reds on both legs.
    monkeypatch.setattr(dl, "_git", _fake_git([
        ("99887766554433221100998877665544332211aa", IN_WINDOW, "landed, and a sibling holds it",
         [SUBJECT_PATH]),
    ]))
    assert dl.disposition_of(EARLY_ID, path=store)["disposition"] == dl.LANDED_ELSEWHERE

    # AND WITH NO COMMIT AT ALL the stated start is what is left -- the poison round. Without it
    # both legs above would pass on a subject that had lost the new reading entirely.
    monkeypatch.setattr(dl, "_git", _fake_git([]))
    assert dl.disposition_of(EARLY_ID, path=store)["disposition"] == dl.PREMISE_NOT_YET_RIPE


def test_A_DURATION_IS_NOT_A_CLOCK_TIME_so_a_timestamps_tail_states_nothing():
    """`20:11:48` offers BOTH `20:11` and `11:48`, and each guard is what refuses one of them.

    ONE SAMPLE WAS NOT ENOUGH AND THE MUTATION PROVED IT, recorded here rather than quietly fixed.
    The first draft quoted only the live sentence and asserted both guards were exercised by it.
    Dropping both guards left the answer UNCHANGED -- an equivalence, not a caught defect -- because
    there the timestamp sits BEFORE the ETA, so the nearest-antecedent rule discards it anyway and
    the guards never had to.

    So the two orderings are both asserted, and each is the only one that can fail for its guard:

      * timestamp FIRST (the live spelling) -- with the leading guard gone, `20:11` is refused for
        the colon that follows it and the scan then offers `11:48`, which is nearer the instruction
        than the ETA and wins;
      * timestamp LAST -- with the trailing guard gone, `20:11` is taken, and it is nearest.

    The assertion is on the INSTANT parsed in both, so a lost guard changes the answer rather than
    merely the match count.
    """
    anchor = datetime.datetime(2026, 9, 18, 0, 7).timestamp()
    expected = datetime.datetime(2026, 9, 18, 3, 58).timestamp()

    timestamp_first = ("The run exec'd 20:11:48, 13.0 min per arm-leg, ETA near 03:58; do not "
                       "draw this before then, the file will not exist.")
    timestamp_last = "ETA near 03:58 (run exec'd 20:11:48); do not draw this before then."

    assert dl._back_referenced_start(timestamp_first, anchor) == expected
    assert dl._back_referenced_start(timestamp_last, anchor) == expected


def test_THEN_MEANS_THE_NEAREST_ANTECEDENT_and_not_the_largest_time_in_the_sentence():
    """`max()` is right for two dated stamps that disagree and wrong for one referent.

    Two well-formed clock times, the LATER one further from the instruction. A reader taking the
    largest -- which is what the dated grammar correctly does -- returns the distractor, so this
    leg is the one that keeps the two resolvers from being quietly unified.
    """
    anchor = datetime.datetime(2026, 9, 18, 0, 7).timestamp()
    text = "Ignore the 22:30 checkpoint. ETA near 03:58; do not draw this before then."

    got = dl._back_referenced_start(text, anchor)

    assert got == datetime.datetime(2026, 9, 18, 3, 58).timestamp(), (
        got and datetime.datetime.fromtimestamp(got))


def test_THE_ANCHOR_IS_THE_DRAW_SO_A_ROWS_DISPOSITION_DOES_NOT_DRIFT():
    """A date-less stamp resolved against `now` re-answers differently on every sweep.

    The row does not change; the reading must not either. Two anchors a day apart, one sentence,
    and each resolves to the next occurrence AFTER its own anchor -- which is the only reading
    consistent with an ETA being in its item's future when written.
    """
    text = "ETA near 03:58; do not draw this before then."
    monday = datetime.datetime(2026, 9, 18, 0, 7).timestamp()
    tuesday = datetime.datetime(2026, 9, 19, 0, 7).timestamp()

    assert dl._back_referenced_start(text, monday) == datetime.datetime(
        2026, 9, 18, 3, 58).timestamp()
    assert dl._back_referenced_start(text, tuesday) == datetime.datetime(
        2026, 9, 19, 3, 58).timestamp()

    # AND AN INSTANT ALREADY PAST ON THE ANCHOR'S OWN DAY ROLLS FORWARD, never backward: an ETA
    # behind the draw would make every late-drawn item claim its window was unusable.
    late = datetime.datetime(2026, 9, 18, 21, 0).timestamp()
    assert dl._back_referenced_start(text, late) == datetime.datetime(
        2026, 9, 19, 3, 58).timestamp()


def test_PROSE_THAT_STATES_NOTHING_READS_AS_THE_RESIDUAL_and_an_unreadable_item_does_too(
        tmp_path, monkeypatch):
    """The residual stays LOUD when this reading cannot run -- the direction R15 requires.

    Three ways it cannot run, asserted together: prose that names no instant, an item store that
    has forgotten the row, and a reader that raises. A subject that let any of them become
    `PREMISE_NOT_YET_RIPE` would excuse every miss whose prose it could not parse, which is the
    fail-open this value is most exposed to.
    """
    store = _ledger(tmp_path, {EARLY_ID: _row(named_paths=[SUBJECT_PATH])})
    monkeypatch.setattr(dl, "_git", _fake_git([]))

    # PROSE THAT PARSES BUT NAMES NOTHING, and an item store that has forgotten the row: the reading
    # declined, git WAS asked on this row's paths, and nothing came back. Workable, draw again.
    monkeypatch.setattr(dl, "_item_text", lambda fid: "Read the artefact and report the sign.")
    assert looked_and_found_nothing(dl.disposition_of(EARLY_ID, path=store))

    monkeypatch.setattr(dl, "_item_text", lambda fid: "")
    assert looked_and_found_nothing(dl.disposition_of(EARLY_ID, path=store))

    def _boom(fid):
        raise RuntimeError("both item stores are unreadable")

    # AND THE RAISING ONE IS THE DIFFERENT ANSWER, which is what "stays LOUD" above means and what
    # `evidence == ""` used to deny in the same breath as asserting it. The asking BROKE here, so a
    # louder disposition may have been true and been lost; a reader told "genuine miss" redoes work
    # that may exist. This leg is the only one of the three that must NOT read as the other two.
    monkeypatch.setattr(dl, "_item_text", _boom)
    raised = dl.disposition_of(EARLY_ID, path=store)
    assert could_not_ask(raised), raised


def test_THE_DATED_SPELLING_IS_READ_BY_THE_SAME_VALUE_so_the_two_grammars_do_not_split(
        tmp_path, monkeypatch, prose):
    """One cause, one value, whichever spelling the seat happened to use.

    `embargoed_until` already reads `DO NOT DRAW BEFORE 10:45 on 2026-09-18`, and a row stamped
    that way whose window closed early is the SAME cause as the back-referenced one. Splitting
    them across two dispositions would make the dial depend on the author's phrasing -- and the
    module's own docstring says a grammar that honours one spelling and not another is worse than
    honouring none, because it is unpredictable.
    """
    store = _ledger(tmp_path, {EARLY_ID: _row(named_paths=[SUBJECT_PATH])})
    monkeypatch.setattr(dl, "_git", _fake_git([]))
    stated = WINDOW_ENDS + 3600
    when = datetime.datetime.fromtimestamp(stated)
    prose[EARLY_ID] = "DO NOT DRAW BEFORE {} on {}".format(
        when.strftime("%H:%M"), when.strftime("%Y-%m-%d"))

    got = dl.disposition_of(EARLY_ID, path=store)

    assert got["disposition"] == dl.PREMISE_NOT_YET_RIPE, got
    assert when.strftime("%H:%M") in got["evidence"]


def test_THE_RESIDUAL_PARTITION_every_reachable_branch_names_what_it_asked_or_what_it_broke_on(
        tmp_path, monkeypatch, prose):
    """The residual's OWN partition, in one statement: no branch of it is ever silent.

    WHY THIS EXISTS, and it is the other half of a repair that landed with only one half. The
    three legs above asserted `evidence == ""` for the residual. When `_nothing_answered` learned
    to say WHY it could not conclude, those legs went red -- for the code becoming more honest,
    which is this project's named backwards shape -- and they were re-keyed off the empty string
    to `the premise-spent instant is absent from the reason`. That removed the pin correctly and
    installed nothing in its place: `x not in ""` is true, so two of the three re-keyed legs pass
    against a residual that has gone back to saying nothing at all. Measured, not reasoned --
    replacing `_nothing_answered`'s whole body with `{"disposition": NOT_DONE, "evidence": ""}`
    leaves seven of the eight tests in this file green. A control that cannot fail on the
    regression it was rewritten for is worse than the pin it replaced, because it reads as cover.

    THE PROPERTY, and it is deliberately not a wording. Every residual a reader can actually be
    handed either NAMES THE QUERY IT MADE -- the paths and the window, so the reader can check
    whether they were the right ones -- or NAMES WHAT STOPPED IT, and never a bare sentence about
    the tree that a reader cannot tell apart from either. Silence is the one answer forbidden
    outright, because silence is what "we looked and found nothing" and "we never looked" were
    both wearing, and those two want opposite actions from the reader.

    REACHABILITY IS ASSERTED BEFORE BEHAVIOUR, because a partition control over branches that
    cannot be taken grades nothing -- the trap this file's header records walking into through
    three doors in one afternoon. The three branches below are distinct answers from one reader,
    so a `_nothing_answered` that returned any single constant fails on the distinctness leg
    before any wording is examined.

    TWO OF THE DOCSTRING'S FOUR BRANCHES ARE NOT REACHABLE THROUGH `disposition_of`, established
    by probe on 2026-09-18 and recorded here rather than left for the next reader to re-derive:
      * "paths, and git returned commits, every one already bound" needs a hit whose instant is
        this row's own `last_landing_at`, and such a row is answered `DELIVERED` (or, with
        `landed_under` set, `LANDED_ELSEWHERE`) by guards that run before `_disposition` does;
      * "composing the commit query raised" cannot be reached because `_landed_unbound` and
        `_landed_by_sibling` both call `_window_hits` first, so the same exception populates
        `unanswered` and the raised branch answers instead.
    Both are fallbacks in the fail-closed direction, so neither is a defect -- but they are
    EQUIVALENCES, not missing tests, and this file says which rather than leaving the flattering
    reading available. They are not asserted below for exactly that reason.

    MUTATIONS, each RUN and each recorded against the leg that ACTUALLY caught it, because the
    first draft of this list guessed and guessed flatteringly:
      (j) return `{"disposition": NOT_DONE, "evidence": ""}` from every branch -- written for the
          no-branch-is-silent leg and CAUGHT BY THE DISTINCTNESS LEG instead, one line earlier.
          Left in the list as a caught mutation, but it does NOT prove the silence leg fires;
      (k) return one constant sentence from every branch -- the distinctness leg reds. Same leg as
          (j), which is why (j) alone could not have graded silence;
      (n) silence ONE branch only -- the no-paths branch returns `""` while the other two keep
          their sentences, so three distinct values survive and (j)'s catcher stays green. THIS is
          the mutation that proves the no-branch-is-silent leg, and it is the whole reason the leg
          is written separately from the distinctness one. It is also the only mutation in this
          file that NO OTHER TEST catches -- eight green, this one red;
      (l) drop the paths or the window bounds from the looked-and-found-nothing branch, so it
          claims a miss the reader cannot check -- the names-its-query leg reds, alone;
      (m) let the no-paths branch print the query it never ran -- the did-not-look leg reds, alone.
    """
    store = _ledger(tmp_path, {EARLY_ID: _row(named_paths=[SUBJECT_PATH])})
    monkeypatch.setattr(dl, "_git", _fake_git([]))

    # BRANCH 1 -- git was asked, over real paths, and answered nothing. The only branch entitled
    # to the sentence "we looked and found nothing", and the only one that must show its working.
    prose[EARLY_ID] = "Read the artefact and report the sign."
    looked = dl.disposition_of(EARLY_ID, path=store)

    # BRANCH 2 -- the item's prose named no tracked path, so no query could be BUILT and git was
    # never asked. Calling this "nothing landed" is the fail-open reading of an unavailable check.
    unasked = _ledger(tmp_path / "unasked", {EARLY_ID: _row()})
    prose[EARLY_ID] = "Report the sign."
    no_paths = dl.disposition_of(EARLY_ID, path=unasked)

    # BRANCH 3 -- a reader raised, so the tree WAS asked and the asking broke. The loudest of the
    # three: a louder disposition may have been true and was lost.
    def _boom(fid):
        raise RuntimeError("both item stores are unreadable")

    monkeypatch.setattr(dl, "_item_text", _boom)
    broke = dl.disposition_of(EARLY_ID, path=store)

    every = (looked, no_paths, broke)
    assert all(r["disposition"] == dl.NOT_DONE for r in every), every

    # REACHABLE AND DISTINCT, asserted before anything about wording: one reader, three inputs,
    # three different answers. A constant residual -- the shape the empty string WAS -- dies here.
    assert len({r["evidence"] for r in every}) == 3, every

    # NO BRANCH IS SILENT. The whole repair in one line, and the leg the re-keying left out.
    assert all(r["evidence"].strip() for r in every), every

    # THE BRANCH THAT LOOKED NAMES ITS QUERY -- which paths, and both edges of the window -- so a
    # reader can check whether the paths were the right ones instead of being sent to `git status`.
    assert SUBJECT_PATH in looked["evidence"], looked
    assert _hhmm(DRAWN_AT) in looked["evidence"], looked
    assert _hhmm(WINDOW_ENDS) in looked["evidence"], looked

    # AND THE TWO THAT DID NOT LOOK DO NOT CLAIM A QUERY THEY NEVER RAN. This is the fail-open
    # that would survive every leg above: a branch that could not ask, reciting the sentence of a
    # branch that did, is exactly the collapse -- a declared `None` wearing a silent one's clothes.
    assert SUBJECT_PATH not in no_paths["evidence"], no_paths
    assert _hhmm(DRAWN_AT) not in no_paths["evidence"], no_paths

    # EACH NAMES WHAT STOPPED IT, in the reader's own terms: the one that could not build a query
    # says so, and the one that crashed names the exception the fixture actually raised.
    assert "no tracked path" in no_paths["evidence"], no_paths
    assert "RuntimeError" in broke["evidence"], broke
