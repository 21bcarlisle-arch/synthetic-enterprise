"""A window whose commit another row already owns read `not_done` with an empty evidence string.

THE DEFECT, measured 2026-09-18 on this lane's own ledger. The delivery seat drew the same publisher
subject three times in thirteen hours and bound nothing, and asked why. One of the three --
`the-commit-hook-chain-has-grown-five-fold-and-that-is-what-the-publisher-keeps-losing-to`, drawn at
1789674037 naming `background/process_run_complete.py` -- had its answer sitting in the two stores
the reader was already holding. `bfbc2b4e9` touched exactly that path 57 minutes later, inside the
window, and the row still came back evidence-free, because the commit is credited to a sibling:
`decouple-the-early-exit-floor-from-the-regime-constant-then-re-date-the-stale-hook-chain-measurement`.

`_landed_unbound` is RIGHT to decline it -- that work is not unbound, and crediting this row with it
would double-bind one commit to two claims. But declining is not the same as having nothing to say.
The sibling's id was in the very dict the join was testing membership against: `_bound_instants`
reduced the ledger to a set of instants and threw the holder away, so the one disposition that
explains the miss was unreachable by construction while its evidence sat one comprehension away.

THE TWO READINGS WANT OPPOSITE ACTIONS, which is why the conflation is expensive rather than untidy.
`landed_elsewhere` says: the subject was worked, read that commit, decide whether anything is still
owed. `not_done` with no evidence says: nobody has started, start. A seat told the second when the
first is true spends a whole invocation re-deriving work that is already in a ref -- which is what
the three empty rows above bought.

KEYED TO THE PROPERTY, NEVER TO TODAY'S IDS OR SHAS. The property is: **a window that closed with a
commit on its own named paths inside it is never reported as evidence-free, whoever owns that
commit.** Nothing from the live ledger appears below.

MUTATIONS (each must fire, and which test catches it):
  (a) delete the `_landed_by_sibling` call from `_disposition`, or return `NOT_DONE` always --
      `test_THE_PARTITION_...` reds;
  (b) ask the sibling reading BEFORE the unbound one, so a sibling's landing hides creditable work
      on the same paths -- `test_AN_UNBOUND_COMMIT_OUTRANKS_A_SIBLINGS_ON_THE_SAME_PATHS` reds;
  (c) drop the sibling id from the evidence string -- `test_THE_EVIDENCE_NAMES_BOTH_THE_SIBLING_AND
      _THE_COMMIT` reds;
  (d) let `_bound_by` key by id instead of by instant, or drop a row -- `test_BOUND_BY_IS_BOUND
      _INSTANTS_PLUS_THE_HOLDER` reds, and the credit half it shares a key with cannot drift;
  (e) let a silent git read as a hit -- `test_A_SILENT_GIT_LEAVES_THE_RESIDUAL_LOUD` reds, and so
      does the partition.

TWO MUTATIONS DO NOT FIRE THROUGH THE READER AND BOTH ARE EQUIVALENCES, established by running them
rather than assumed to be the flattering answer. Both guards inside `_landed_by_sibling` --
`bound_by.get(when)` (the commit is owned at all) and `!= focus_id` (owned by somebody ELSE) -- are
vacuously true by the time `disposition_of` reaches this function:

  * ownership: `_landed_by_sibling` is asked only after `_landed_unbound` declined, and it declines
    only when NO hit is unbound, so every remaining hit is owned by construction;
  * self: to own an in-window instant a row needs `last_landing_at >= drawn`, and such a row is
    answered `DELIVERED` several branches earlier and never arrives here at all.

Neither is dead code -- they are what the function MEANS, and a direct caller can exercise both --
so they are graded where they can actually fire, at the function, in
`test_THE_TWO_GUARDS_ARE_GRADED_AT_THE_FUNCTION_BECAUSE_THE_READER_CANNOT_REACH_THEM`. Claiming
either as a mutation of the reader would have been an equivalence dressed as a control.
"""
from __future__ import annotations

import json

import pytest

from background import delivery_lane as dl
from tests.background.residual_voices import looked_and_found_nothing

#: Synthetic ids. NOT the live ledger's -- a control pinned to today's rows goes green the moment
#: the sweep merely gets quieter, which is the failure being fixed wearing a better name.
SIBLING_OWNED_ID = "a-window-whose-commit-another-row-is-credited-with"
UNBOUND_ID = "a-window-whose-paths-moved-while-nothing-was-bound-to-it"
MISSED_ID = "a-window-nobody-touched-at-all"
BOTH_ID = "a-window-carrying-one-owned-commit-and-one-nobody-claims"
HOLDER_ID = "the-row-that-actually-landed-it"

NOW = 1789000000.0
#: Older than `CLAIM_STALE_SECONDS`, so every window below has closed, and inside the 24h horizon.
DRAWN_AT = NOW - 4 * 3600

#: Paths this repo tracks, so the readings below hold on any checkout of it.
SUBJECT_PATH = "background/delivery_lane.py"
OTHER_PATH = "tools/surgical_land.py"

IN_WINDOW = DRAWN_AT + 900
LATER_IN_WINDOW = DRAWN_AT + 1800
OWNED_SHA = "5544332211009988776655443322110099887766"
UNBOUND_SHA = "ab12cd34ef567890ab12cd34ef567890ab12cd34"


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


def _holder(instant: float):
    """The sibling row: drawn before this window and credited with `instant`.

    Its OWN draw is older so it is not itself a swept row under test, and its landing is what makes
    `_bound_by` name it. A holder with no landing would lend nothing, which is the shape
    `note_landing_under` already refuses by hand.
    """
    return {"first_drawn_at": DRAWN_AT - 7200, "last_drawn_at": DRAWN_AT - 7200,
            "last_landing_at": instant, "last_landing_paths": [SUBJECT_PATH]}


@pytest.fixture(autouse=True)
def _no_cached_direction_history():
    """`_direction_history_text` caches for the life of the PROCESS, and a test suite is one.

    The first test here that stubs `_git` would otherwise answer every later one from its fake.
    Cleared on both sides so this file neither inherits a map nor leaves one behind.
    """
    dl._reset_direction_history()
    yield
    dl._reset_direction_history()


def _fake_git(log_lines, *, tracked=(SUBJECT_PATH, OTHER_PATH)):
    """A git that answers ONLY what it was told, and applies the pathspec ITSELF.

    STRICTER THAN REAL GIT ON PURPOSE: `None` for any question not in the table, so this fake can
    only make the subject refuse MORE than the real thing would. A fake more permissive than its
    subject is how a fail-open becomes a green suite here. Applying the pathspec in the fake is
    what lets the path leg discriminate rather than restate the fixture.
    """
    def fake(*args):
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
    """One ledger holding all three readings of a closed window at once."""
    return _ledger(tmp_path, {
        SIBLING_OWNED_ID: _row(named_paths=[SUBJECT_PATH]),
        UNBOUND_ID: _row(named_paths=[OTHER_PATH]),
        MISSED_ID: _row(named_paths=["docs/design/maturity_map.yaml"]),
        HOLDER_ID: _holder(IN_WINDOW),
    })


def test_THE_PARTITION_owned_unowned_and_untouched_come_back_differently_from_one_ledger(
        tmp_path, monkeypatch):
    """Three windows, one ledger, one statement: a constant answer cannot survive it.

    This is the control the repair turns on. What shipped answered `NOT_DONE` to the owned case and
    passed every test written against the other two, because each of those asked about one branch.
    All three are asserted TOGETHER, so a reader that has lost any one reds here whatever is green.
    """
    store = _three_shapes(tmp_path)
    monkeypatch.setattr(dl, "_git", _fake_git([
        (OWNED_SHA, IN_WINDOW, "one constant was setting two things that pull opposite ways",
         [SUBJECT_PATH]),
        (UNBOUND_SHA, IN_WINDOW + 7, "the landing door now names the path it refused on",
         [OTHER_PATH]),
    ]))

    seen = {i: dl.disposition_of(i, path=store)
            for i in (SIBLING_OWNED_ID, UNBOUND_ID, MISSED_ID)}

    saw_elsewhere = seen[SIBLING_OWNED_ID]["disposition"] == dl.LANDED_ELSEWHERE
    saw_unbound = seen[UNBOUND_ID]["disposition"] == dl.LANDED_UNBOUND
    saw_not_done = seen[MISSED_ID]["disposition"] == dl.NOT_DONE

    assert saw_elsewhere and saw_unbound and saw_not_done, seen
    # The residual is STILL the only shape the sibling reading has not widened into, and this line
    # is what says so -- now by the VOICE it answered in rather than by its silence. Keyed to
    # LOOKED-AND-FOUND-NOTHING: this row's paths were asked and came back empty.
    assert looked_and_found_nothing(seen[MISSED_ID]), seen[MISSED_ID]
    assert seen[SIBLING_OWNED_ID]["evidence"] != ""


def test_AN_UNBOUND_COMMIT_OUTRANKS_A_SIBLINGS_ON_THE_SAME_PATHS(tmp_path, monkeypatch):
    """One claim, two commits on its paths: the one nothing owns wins, and it must.

    THE ORDER IS THE MECHANISM, not a tidiness. `landed_unbound` is the reading `credit_from_tree`
    acts on -- it BINDS the commit and the row stops being a miss. `landed_elsewhere` only explains.
    Asking the explanation first would let any sibling's landing on a busy shared file bury
    creditable work on the same file, which is the fail-silent direction and the exact shape the
    residual was already failing in.
    """
    store = _ledger(tmp_path, {
        BOTH_ID: _row(named_paths=[SUBJECT_PATH]),
        HOLDER_ID: _holder(IN_WINDOW),
    })
    monkeypatch.setattr(dl, "_git", _fake_git([
        (OWNED_SHA, IN_WINDOW, "the sibling's landing", [SUBJECT_PATH]),
        (UNBOUND_SHA, LATER_IN_WINDOW, "nobody is credited with this one", [SUBJECT_PATH]),
    ]))

    got = dl.disposition_of(BOTH_ID, path=store)
    assert got["disposition"] == dl.LANDED_UNBOUND, got
    assert UNBOUND_SHA[:9] in got["evidence"], got


def test_THE_EVIDENCE_NAMES_BOTH_THE_SIBLING_AND_THE_COMMIT(tmp_path, monkeypatch):
    """A label nobody can follow back to a fact on disk is a fifth guess, not a fifth reading.

    The sibling's id is what makes the answer actionable -- the reader goes to that row and asks
    what it delivered. The sha is what makes it checkable in one `git show`. Either alone leaves
    the reader where the empty string left them.
    """
    store = _three_shapes(tmp_path)
    monkeypatch.setattr(dl, "_git", _fake_git([
        (OWNED_SHA, IN_WINDOW, "one constant was setting two things", [SUBJECT_PATH]),
    ]))

    evidence = dl.disposition_of(SIBLING_OWNED_ID, path=store)["evidence"]
    assert HOLDER_ID in evidence, evidence
    assert OWNED_SHA[:9] in evidence, evidence
    assert SUBJECT_PATH in evidence, evidence


def test_THE_TWO_GUARDS_ARE_GRADED_AT_THE_FUNCTION_BECAUSE_THE_READER_CANNOT_REACH_THEM(
        monkeypatch):
    """A commit must be owned, and owned by SOMEBODY ELSE, before it explains this row's miss.

    WHY NOT THROUGH `disposition_of`: both conditions are vacuously true by the time the reader
    arrives -- see the module docstring, where the two equivalences are established rather than
    assumed. They are graded here, against a direct caller, because that is where they can fire,
    and the alternative was a mutation list with two entries that never go red.

    THE THREE READINGS ARE ASSERTED TOGETHER, one statement over the whole partition. A function
    that returned `None` to everything would satisfy both refusal legs on its own, and that is the
    trap this project has walked into through three separate doors in one afternoon.
    """
    row = {"first_drawn_at": DRAWN_AT, "last_drawn_at": DRAWN_AT, "named_paths": [SUBJECT_PATH]}
    monkeypatch.setattr(dl, "_window_hits",
                        lambda *_a, **_k: ([SUBJECT_PATH], [(OWNED_SHA, IN_WINDOW, "the work")]))

    unowned = dl._landed_by_sibling(SIBLING_OWNED_ID, row, DRAWN_AT, {})
    self_owned = dl._landed_by_sibling(SIBLING_OWNED_ID, row, DRAWN_AT,
                                       {IN_WINDOW: SIBLING_OWNED_ID})
    sibling = dl._landed_by_sibling(SIBLING_OWNED_ID, row, DRAWN_AT, {IN_WINDOW: HOLDER_ID})

    assert (unowned is None and self_owned is None
            and sibling and sibling["disposition"] == dl.LANDED_ELSEWHERE), \
        (unowned, self_owned, sibling)


def test_BOUND_BY_IS_BOUND_INSTANTS_PLUS_THE_HOLDER(tmp_path):
    """The two joins must key on the same fact, and this is what stops them drifting apart.

    `_bound_instants` is what the credit half tests membership against; `_bound_by` is the same
    join with the discarded half put back. If they ever disagree about WHICH instants are bound,
    one reading credits a commit the other calls somebody else's, and the pair of dispositions
    contradict each other about the same second. Asserting set equality, not a count: a count is
    satisfied by any two same-sized sets.
    """
    ledger = {
        HOLDER_ID: _holder(IN_WINDOW),
        "another-holder": _holder(LATER_IN_WINDOW),
        MISSED_ID: _row(),                       # no landing -- must appear in neither
        "not-a-row": "a string the ledger should skip",
    }
    by = dl._bound_by(ledger)
    assert set(by) == dl._bound_instants(ledger)
    assert by == {IN_WINDOW: HOLDER_ID, LATER_IN_WINDOW: "another-holder"}


def test_A_SILENT_GIT_LEAVES_THE_RESIDUAL_LOUD(tmp_path, monkeypatch):
    """A join that cannot run must not settle a window. The unavailable check fails loud (R15).

    A git that answers nothing is indistinguishable from a git that answers "no commits", and both
    must leave the row on the missed list. The tempting alternative -- treat silence as "the
    sibling explanation does not apply, so say something reassuring" -- is how an unavailable
    check becomes a clean bill of health.
    """
    store = _three_shapes(tmp_path)
    monkeypatch.setattr(dl, "_git", lambda *a: None)

    got = dl.disposition_of(SIBLING_OWNED_ID, path=store)
    assert got["disposition"] == dl.NOT_DONE, got
    # LOUD now means it SAYS the window is unexplained, which is what this leg's name always
    # claimed and `== ""` denied in the same breath. HONEST LIMIT, recorded rather than asserted
    # away: `_git` returning None is a git that failed and a git that matched nothing, and the two
    # are indistinguishable AT THE WRAPPER -- this leg's own docstring says so. So the voice here
    # is LOOKED-AND-FOUND-NOTHING, not CANNOT-ANSWER. What the leg guarantees is the part that
    # matters: silence does not settle the window and does not become a clean bill of health.
    assert looked_and_found_nothing(got), got
