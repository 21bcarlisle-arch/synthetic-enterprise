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

from background import delivery_lane as dl

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


def _fake_git(log_lines, *, tracked=(SUBJECT_PATH, OTHER_PATH)):
    """A git that answers ONLY the two questions asked of it, from an explicit table.

    STRICTER THAN REAL GIT ON PURPOSE. It returns None for anything it was not told about, so it
    can only make the subject refuse MORE than the real thing would -- a fake more permissive than
    its subject is how a fail-open becomes a green suite here. `log_lines` is a list of
    `(sha, when, subject, paths)`, and the fake applies the pathspec ITSELF, which is what lets
    the pathspec leg below be a discriminator rather than a restatement of the fixture.
    """
    def fake(*args):
        if args and args[0] == "ls-files":
            return "\n".join(tracked) + "\n"
        if args and args[0] == "log":
            wanted = list(args[args.index("--") + 1:]) if "--" in args else []
            out = []
            for sha, when, subject, paths in log_lines:
                if wanted and not any(
                        p == w or p.startswith(w.rstrip("/") + "/") for p in paths for w in wanted):
                    continue
                out.append("{}\x1f{:.0f}\x1f{}".format(sha, when, subject))
            return "\n".join(out) + "\n" if out else ""
        return None
    return fake


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
    # The residual is still the shape with NO evidence, and the new value must NAME ITS COMMIT --
    # a fourth label nobody can follow back to a fact on disk would be a fourth guess.
    assert seen[MISSED_ID]["evidence"] == ""
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
    """
    store = _ledger(tmp_path, {UNBOUND_ID: _row(named_paths=[SUBJECT_PATH])})
    monkeypatch.setattr(dl, "_git", _fake_git([
        ("1111111111111111111111111111111111111111", DRAWN_AT - 60, "before the draw",
         [SUBJECT_PATH]),
        ("2222222222222222222222222222222222222222", WINDOW_ENDS + 60, "after the sweep",
         [SUBJECT_PATH]),
    ]))

    assert dl.disposition_of(UNBOUND_ID, path=store)["disposition"] == dl.NOT_DONE


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
    """
    store = _ledger(tmp_path, {
        UNBOUND_ID: _row(named_paths=[SUBJECT_PATH]),
        "somebody-elses-row-that-bound-it": _row(last_landing_at=IN_WINDOW,
                                                 last_landing_paths=[SUBJECT_PATH]),
    })
    monkeypatch.setattr(dl, "_git", _fake_git([
        (BOUND_SHA, IN_WINDOW, "landed and bound, by another row", [SUBJECT_PATH]),
    ]))

    assert dl.disposition_of(UNBOUND_ID, path=store)["disposition"] == dl.NOT_DONE

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
