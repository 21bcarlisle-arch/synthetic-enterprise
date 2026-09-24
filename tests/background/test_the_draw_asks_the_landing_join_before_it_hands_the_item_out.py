"""A drawn item whose work was already in a ref was handed to a whole worker tick anyway.

THE DEFECT, measured 2026-09-24 on this lane's own ledger.
`the-refuted-bill-stress-knee-is-unbounded-beside-a-saturating-size-term` landed at `3b01193a8` on
2026-09-23 17:54. The landing was BOUND -- `--landed` ran, `last_landing_at` holds the commit's own
`%ct`, `last_landing_paths` names the files. Seventeen hours and forty-two minutes later, at
11:36:32, the same id was drawn again and dispatched to a fresh worker with no check of any kind,
and the fact that would have stopped it was sitting in git and in this module's own ledger the
whole time.

`premise_note` could not see it. That reading re-measures the commit ids an item's PROSE cites, and
this item's prose cited none -- so the one draw-time check that asks "is this already done?" is
silent on every item whose author did not happen to write a sha. `_landed_unbound` could see it,
and does: it runs exactly this join over a row's named paths. But it runs on the way OUT, in
`_disposition`, over a CLOSED window, 100 minutes after the tick it would have saved. The join was
written; nothing asked it on the way IN.

WHAT THE WASTE IS. Not a wrong answer -- a whole invocation spent re-deriving that the work was
already done, which is the most expensive thing this lane can do with a tick and the one failure
`draw`'s own docstring is longest about.

KEYED TO THE PROPERTY, NEVER TO TODAY'S IDS OR SHAS. The property is: **an item whose own subject
paths have moved in git since the row was last accounted for is never handed out silently.**
Nothing from the live ledger appears below.

THE BOUND CASE IS THE ONE THE INSTANCE TURNS ON, and it is the easy one to lose. The reference
instant IS the bound landing's instant, so a join written with a strict `>` -- the natural way to
write "since" -- excludes the very commit that proves the item is finished and reports the quiet
answer on the only shape that was measured. `test_THE_ROWS_OWN_BOUND_LANDING_IS_THE_FIRST_HIT` is
the leg that refuses it.

MEASURED FIRING RATE, so a later reader can tell a note that went quiet from a lane that did:
222 of the live ledger's 336 rows with a landing inside git's 14-day horizon carry a note, and 108
of those carry the CREDITED voice. Nothing below is keyed to those figures -- they are here as the
baseline the numbers in this file's reasoning came from.

WHY THERE ARE TWO VOICES AND NOT THREE, because the obvious "improvement" is to split the movement
by ownership the way `_landed_unbound` does, and it was built that way first and the numbers killed
it. `_bound_instants` knows only commits THIS LANE bound to one of its own rows -- a few hundred
against every commit in the tree -- so over a multi-hour reference span `unbound` means very nearly
"a commit". Measured 2026-09-24 over the live ledger's 336 rows with a landing inside git's 14-day
horizon: 222 fired and `unbound` appeared in 200 of them. `test_THE_MOVEMENT_VOICE_MAKES_NO_CLAIM
_ABOUT_WHO_OWNS_A_COMMIT` is what stops it coming back.

MUTATIONS (each must fire, and which test catches it):
  (a) drop the `landed_since_note` call from `doorbell` --
      `test_THE_DOORBELL_CARRIES_THE_LANDING_CHECK_ABOVE_THE_WORK` reds;
  (b) move the reference edge off `last_landing_at`, or make the comparison strict so the bound
      landing at exactly that instant is excluded --
      `test_THE_ROWS_OWN_BOUND_LANDING_IS_THE_FIRST_HIT` reds;
  (c) collapse the two voices into one, or lose either --
      `test_THE_PARTITION_credited_and_moved_are_two_distinct_voices` reds;
  (d) turn the note into a filter -- have `next_item`/`doorbell` withhold the item -- both the
      partition leg and `test_IT_ANNOTATES_AND_NEVER_WITHHOLDS_THE_WORK` red;
  (e) let a git that cannot be asked raise out of the note --
      `test_AN_UNANSWERABLE_GIT_IS_SILENT_AND_NEVER_RAISES` reds;
  (f) speak on a row the ledger does not hold, i.e. a first draw --
      `test_A_FIRST_DRAW_IS_SILENT_AND_ASKS_GIT_NOTHING` reds;
  (g) ignore `_window_hits`' new `until` and keep the derived upper edge, so the reading stops
      100 minutes past the reference and cannot see anything that landed since --
      `test_THE_UPPER_EDGE_IS_NOW_AND_NOT_THE_CLAIMS_OWN_WINDOW` reds;
  (h) drop the `landed_at` guard, so a row with NO landing credits itself with whatever commit
      happens to share a second with its first draw --
      `test_A_ROW_WITH_NO_LANDING_CREDITS_ITSELF_WITH_NOTHING` reds.

ONE MUTATION IS AN EQUIVALENCE and it is established by running it rather than assumed to be the
flattering answer: making `_hit_phrase` take the OLDEST hit of a class instead of the newest
changes which sha is printed and nothing else. It is graded directly, at the function, in
`test_A_CLASS_NAMES_ITS_NEWEST_COMMIT_BECAUSE_THAT_IS_THE_ONE_A_READER_OPENS` -- claiming it as a
mutation of the doorbell would have been an equivalence dressed as a control.
"""
from __future__ import annotations

import json

import pytest

from background import delivery_lane as dl

#: Synthetic ids. NOT the live ledger's -- a control pinned to today's rows goes green the moment
#: the lane merely gets quieter, which is the failure being fixed wearing a better name.
BOUND_ID = "a-row-whose-own-landing-is-bound-and-was-drawn-again-the-next-morning"
UNBOUND_ID = "a-row-whose-paths-moved-while-nothing-in-the-ledger-was-credited"
ELSEWHERE_ID = "a-row-whose-subject-another-lane-landed-while-it-waited"
QUIET_ID = "a-row-nobody-has-touched-since-it-was-first-drawn"
FIRST_DRAW_ID = "a-row-the-ledger-has-never-heard-of"
HOLDER_ID = "the-sibling-row-that-actually-landed-it"
#: A row that has NEVER landed, whose first draw shares a second with a commit. Without the
#: `landed_at` guard it credits itself with a commit it has no binding to at all.
NO_LANDING_ID = "a-row-that-has-never-landed-and-was-first-drawn-on-a-commits-own-second"

NOW = 1790250000.0
#: The measured shape: first drawn, landed the same evening, re-drawn the NEXT MORNING. The gap is
#: what makes this a waste rather than a race -- far outside anything a claim window could cover.
FIRST_DRAWN = NOW - 30 * 3600
BOUND_LANDING = NOW - 18 * 3600
#: Deliberately more than `CLAIM_STALE_SECONDS` past the reference, so a reading that kept the
#: closed-window upper edge cannot see it. That is mutation (g).
LATE_HIT = NOW - 3 * 3600
#: A SECOND late instant, and it has to be distinct rather than tidy: `_bound_by` keys ownership by
#: the commit's INSTANT, so an unbound commit sharing a second with the sibling's landing is read
#: as the sibling's -- correctly, by that function's own documented tie-break, and it would make
#: the unbound class unreachable in this fixture while every per-class assertion still passed.
LATE_UNBOUND_HIT = NOW - 4 * 3600

SUBJECT_PATH = "background/delivery_lane.py"
OTHER_PATH = "tools/surgical_land.py"
UNTOUCHED_PATH = "docs/design/maturity_map.yaml"

BOUND_SHA = "3b01193a8bac491bd5ac9909e42e085a22cba1e3"
UNBOUND_SHA = "ab12cd34ef567890ab12cd34ef567890ab12cd34"
ELSEWHERE_SHA = "5544332211009988776655443322110099887766"


@pytest.fixture(autouse=True)
def _no_cached_direction_history():
    """`_direction_history_text` caches for the life of the PROCESS, and a test suite is one.

    The first test here that stubs `_git` would otherwise answer every later one from its fake.
    Cleared on both sides so this file neither inherits a map nor leaves one behind.
    """
    dl._reset_direction_history()
    yield
    dl._reset_direction_history()


def _ledger(tmp_path, rows: dict):
    tmp_path.mkdir(parents=True, exist_ok=True)
    store = tmp_path / "claims.json"
    store.write_text("{}", encoding="utf-8")
    dl._ledger_path(store).write_text(json.dumps(rows), encoding="utf-8")
    return store


def _row(paths, **extra):
    row = {"first_drawn_at": FIRST_DRAWN, "last_drawn_at": NOW, "named_paths": list(paths)}
    row.update(extra)
    return row


def _fake_git(log_lines, *, tracked=(SUBJECT_PATH, OTHER_PATH, UNTOUCHED_PATH)):
    """A git that answers ONLY what it was told, and applies the pathspec ITSELF.

    STRICTER THAN REAL GIT ON PURPOSE: `None` for any question not in the table, so this fake can
    only make the subject refuse MORE than the real thing would. A fake more permissive than its
    subject is how a fail-open becomes a green suite here. Applying the pathspec AND the window in
    the fake is what lets the path and edge legs discriminate rather than restate the fixture.
    """
    def fake(*args, cwd=None):
        if args and args[0] == "ls-files":
            return "\n".join(tracked) + "\n"
        if args and args[0] == "log":
            wanted = list(args[args.index("--") + 1:]) if "--" in args else []
            if wanted == [dl.DIRECTION_RECORD_PATH]:
                return ""
            out = []
            for sha, when, subject, paths in log_lines:
                if wanted and not any(p == w for p in paths for w in wanted):
                    continue
                out.append("{}\x1f{:.0f}\x1f{}".format(sha, when, subject))
            return "\n".join(out) + "\n" if out else ""
        return None
    return fake


def _three_shapes(tmp_path):
    """One ledger holding both voices, the quiet residual, and the never-landed row at once."""
    return _ledger(tmp_path, {
        BOUND_ID: _row([SUBJECT_PATH], last_landing_at=BOUND_LANDING,
                       last_landing_paths=[SUBJECT_PATH]),
        UNBOUND_ID: _row([OTHER_PATH]),
        ELSEWHERE_ID: _row([SUBJECT_PATH]),
        QUIET_ID: _row([UNTOUCHED_PATH]),
        NO_LANDING_ID: _row([OTHER_PATH], first_drawn_at=LATE_UNBOUND_HIT),
        HOLDER_ID: {"first_drawn_at": FIRST_DRAWN - 7200, "last_drawn_at": FIRST_DRAWN - 7200,
                    "last_landing_at": LATE_HIT, "last_landing_paths": [SUBJECT_PATH]},
    })


def _the_three_commits():
    return [
        (BOUND_SHA, BOUND_LANDING, "the refuted bill-stress term is bounded", [SUBJECT_PATH]),
        (UNBOUND_SHA, LATE_UNBOUND_HIT, "nobody in this lane is credited with this one",
         [OTHER_PATH]),
        (ELSEWHERE_SHA, LATE_HIT, "the sibling's landing", [SUBJECT_PATH]),
    ]


def test_THE_ROWS_OWN_BOUND_LANDING_IS_THE_FIRST_HIT(tmp_path, monkeypatch):
    """The measured instance, whole: bound the evening before, drawn again the next morning.

    This is the leg the repair turns on. The reference instant IS the bound landing's instant, so
    the obvious spelling of "since" -- a strict `>` -- drops the one commit that proves the item is
    finished and answers with silence on the only shape anybody has measured. The note must name
    the sha, and it must say the item is ALREADY CREDITED with it rather than reporting it as
    somebody's loose work.
    """
    store = _three_shapes(tmp_path)
    monkeypatch.setattr(dl, "_git", _fake_git(_the_three_commits()))

    note = dl.landed_since_note({"id": BOUND_ID}, now=NOW, path=store)

    assert BOUND_SHA[:9] in note, note
    assert "ALREADY CREDITED WITH A LANDING" in note, note
    # The action has to be reachable from the note, or a reader who believes it still has to go and
    # find out how to record it -- which is the friction that left both hand-written dispositions
    # unrun for eleven weeks.
    assert "--premise-spent {}".format(BOUND_ID) in note, note


def test_THE_PARTITION_credited_and_moved_are_two_distinct_voices(tmp_path, monkeypatch):
    """Three rows, one ledger, one statement: a constant answer cannot survive it.

    Asserted TOGETHER and over the WHOLE partition rather than a leg per voice, for the reason this
    project has now paid for three times: a reading that has collapsed both voices into one, or
    lost either, passes every per-branch test written against the branch it kept. The third row is
    the silence -- a note that can never be quiet is a note nobody reads.
    """
    store = _three_shapes(tmp_path)
    monkeypatch.setattr(dl, "_git", _fake_git(_the_three_commits()))

    seen = {i: dl.landed_since_note({"id": i}, now=NOW, path=store)
            for i in (BOUND_ID, UNBOUND_ID, QUIET_ID)}

    credited = ("ALREADY CREDITED WITH A LANDING" in seen[BOUND_ID]
                and BOUND_SHA[:9] in seen[BOUND_ID])
    moved = ("subject paths have moved since" in seen[UNBOUND_ID]
             and UNBOUND_SHA[:9] in seen[UNBOUND_ID])
    quiet = seen[QUIET_ID] == ""

    assert credited and moved and quiet, seen
    # DISTINCTNESS, not just reachability: two voices that render the same sentence are one voice
    # with two names, and both membership tests above would still pass.
    assert seen[BOUND_ID] != seen[UNBOUND_ID], seen


def test_THE_MOVEMENT_VOICE_MAKES_NO_CLAIM_ABOUT_WHO_OWNS_A_COMMIT(tmp_path, monkeypatch):
    """The ownership split is REFUSED here, and this is the leg that stops it coming back.

    Splitting movement into `unbound` and `landed_elsewhere` the way `_disposition` does is the
    obvious next change, and it is wrong at this window. `_bound_instants` knows only commits this
    lane bound to one of its own rows, so over a multi-hour reference span `unbound` is true of
    very nearly every hit -- 200 of the 222 live rows that fired on 2026-09-24. A label that is
    true of almost everything discriminates nothing and reads as though it discriminates a great
    deal.

    So two rows whose movement differs ONLY in whether a sibling is credited with the commit must
    say the same kind of thing. `ELSEWHERE_ID`'s hit is held by `HOLDER_ID`; `UNBOUND_ID`'s is held
    by nobody. Both are movement, and a reading that has reintroduced the split reds here.
    """
    store = _three_shapes(tmp_path)
    monkeypatch.setattr(dl, "_git", _fake_git(_the_three_commits()))

    owned = dl.landed_since_note({"id": ELSEWHERE_ID}, now=NOW, path=store)
    unowned = dl.landed_since_note({"id": UNBOUND_ID}, now=NOW, path=store)

    assert "subject paths have moved since" in owned, owned
    assert "subject paths have moved since" in unowned, unowned
    assert ELSEWHERE_SHA[:9] in owned, owned
    # KEYED TO THE PROPERTY -- no OTHER ROW'S ID, rather than "not this one". Naming a single
    # expected holder is how the first draft of this leg passed against a reading that DID publish
    # ownership: the note happened to name a different row than the one asserted against, and the
    # mutation went green while biting perfectly well. The property is that the movement voice
    # names commits and never rows, so every id in the ledger but the subject's own is a violation.
    for other in (BOUND_ID, UNBOUND_ID, QUIET_ID, NO_LANDING_ID, HOLDER_ID):
        assert other not in owned, (other, owned)


def test_A_ROW_WITH_NO_LANDING_CREDITS_ITSELF_WITH_NOTHING(tmp_path, monkeypatch):
    """`first_drawn_at` is not a binding, and a second it happens to share is not one either.

    The credited voice is an equality against `last_landing_at` -- the commit's own `%ct`, written
    by `_remember_landing`, which IS the binding. With no landing the reference falls back to the
    first draw, and an unguarded equality would then read any commit committed in that same second
    as this row's own landing and tell a tick its work is done. The fixture puts exactly that
    collision on disk: `NO_LANDING_ID` was first drawn at `LATE_UNBOUND_HIT`, which is also
    `UNBOUND_SHA`'s committer instant.
    """
    store = _three_shapes(tmp_path)
    monkeypatch.setattr(dl, "_git", _fake_git(_the_three_commits()))

    note = dl.landed_since_note({"id": NO_LANDING_ID}, now=NOW, path=store)

    assert UNBOUND_SHA[:9] in note, note
    assert "ALREADY CREDITED" not in note, note
    assert "subject paths have moved since" in note, note


def test_THE_UPPER_EDGE_IS_NOW_AND_NOT_THE_CLAIMS_OWN_WINDOW(tmp_path, monkeypatch):
    """`_window_hits` had one upper edge, derived from the draw, and it is the wrong one here.

    Both closed-window readings stop at `drawn + CLAIM_STALE_SECONDS + grace`. A pre-draw reading
    that inherited that edge would see nothing more than 100 minutes past its reference -- and the
    measured instance is SEVENTEEN HOURS wide. `UNBOUND_SHA` sits deliberately outside the derived
    edge and inside `now`, so a reading that ignores `until` answers empty here and stays green on
    every other leg in this file.
    """
    store = _three_shapes(tmp_path)
    monkeypatch.setattr(dl, "_git", _fake_git(_the_three_commits()))
    derived_edge = FIRST_DRAWN + dl.CLAIM_STALE_SECONDS + dl._landing_grace_seconds()
    assert LATE_UNBOUND_HIT > derived_edge, (LATE_UNBOUND_HIT, derived_edge)

    assert UNBOUND_SHA[:9] in dl.landed_since_note({"id": UNBOUND_ID}, now=NOW, path=store)


def test_A_FIRST_DRAW_IS_SILENT_AND_ASKS_GIT_NOTHING(tmp_path, monkeypatch):
    """Nothing has happened to a first draw, so there is nothing it can have been wasted on.

    The silence is the honest answer and not an optimisation -- but it is ALSO what keeps the
    supervisor's ~2-minute `draw(claim=False)` read free of a `git log`, so the leg asserts git was
    not asked at all rather than only that the note was empty. A reading that asked git and then
    discarded the answer would pass the weaker assertion.
    """
    store = _three_shapes(tmp_path)
    asked = []

    def counting(*args, cwd=None):
        asked.append(args)
        return _fake_git(_the_three_commits())(*args, cwd=cwd)

    monkeypatch.setattr(dl, "_git", counting)

    assert dl.landed_since_note({"id": FIRST_DRAW_ID}, now=NOW, path=store) == ""
    assert asked == [], asked


def test_AN_UNANSWERABLE_GIT_IS_SILENT_AND_NEVER_RAISES(tmp_path, monkeypatch):
    """Fail OPEN, in the direction `premise_note` argues for at length.

    `_window_hits` raises `GitUnavailable` rather than returning empty, precisely so no caller can
    lose the difference in a falsy test. This caller catches it and says nothing, because a missing
    annotation is visible to the tick that then does the work anyway, where an item withheld
    because git hiccuped is visible to nobody. The leg has to be here and not inferred: the raise
    is the newer behaviour and an `except` is the only thing between it and the draw.
    """
    store = _three_shapes(tmp_path)
    monkeypatch.setattr(dl, "_git", lambda *a, **k: None)

    assert dl.landed_since_note({"id": BOUND_ID}, now=NOW, path=store) == ""


def test_THE_DOORBELL_CARRIES_THE_LANDING_CHECK_ABOVE_THE_WORK(tmp_path, monkeypatch):
    """A check the dispatched text does not carry is a check nobody runs.

    `doorbell` is the only thing a worker tick reads, and the note's whole purpose is to be read
    BEFORE the work -- a tick that has read the work has already started. So the leg asserts both
    presence and ORDER, against the standing preamble's own first words.
    """
    store = _three_shapes(tmp_path)
    monkeypatch.setattr(dl, "_git", _fake_git(_the_three_commits()))
    monkeypatch.setattr(dl, "CLAIMS_FILE", store)

    text = dl.doorbell({"id": BOUND_ID, "what": "carry on with the bounded knee",
                        "why": "because the seat said so"})

    assert "LANDING CHECK" in text, text
    assert text.index("LANDING CHECK") < text.index("LANE 0 DELIVERY"), text


def test_IT_ANNOTATES_AND_NEVER_WITHHOLDS_THE_WORK(tmp_path, monkeypatch):
    """The item asked for a note and explicitly refused a refusal, and this is why.

    This join fires on paths several lanes commit into every hour -- `background/delivery_lane.py`
    is its own most-worked file -- so a false positive is not rare, and a false positive that
    SUPPRESSES silences real work with nothing on any surface to say so. That is `draw`'s six-day
    walkover, which cost sixty-eight claimed items and zero delivered. The doorbell must still
    carry the work, the reason, and the `--landed` instruction the lane's bookkeeping depends on.
    """
    store = _three_shapes(tmp_path)
    monkeypatch.setattr(dl, "_git", _fake_git(_the_three_commits()))
    monkeypatch.setattr(dl, "CLAIMS_FILE", store)

    text = dl.doorbell({"id": BOUND_ID, "what": "carry on with the bounded knee",
                        "why": "because the seat said so"})

    assert "carry on with the bounded knee" in text, text
    assert "--landed {}".format(BOUND_ID) in text, text
    assert "this is a note, not a refusal" in text, text


def test_A_CLASS_NAMES_ITS_NEWEST_COMMIT_BECAUSE_THAT_IS_THE_ONE_A_READER_OPENS(tmp_path):
    """Graded at the function, because the doorbell cannot tell the two orders apart.

    Taking the oldest hit instead of the newest changes which sha is printed and nothing else --
    through `landed_since_note` it is an EQUIVALENCE, established by running it rather than assumed
    to be the flattering answer. It is a real choice all the same, and the opposite of
    `_landed_unbound`'s: that reading looks backwards at a closed window and the earliest landing
    is the one the claim produced, where this one wants the most recent state of the subject.
    """
    older = ("1111111111aaaaaaaaaa1111111111aaaaaaaaaa", NOW - 9000, "the older one", [SUBJECT_PATH])
    newer = ("2222222222bbbbbbbbbb2222222222bbbbbbbbbb", NOW - 900, "the newer one", [SUBJECT_PATH])

    phrase = dl._hit_phrase([older, newer])

    assert phrase.startswith(newer[0][:9]), phrase
    assert "(+1 more)" in phrase, phrase
