"""The residual disposition told its reader NOTHING, and silence read as "we looked and found none".

THE DEFECT, measured on this lane's live ledger 2026-09-18 at 08:24. Every reading in
`_disposition` had learned to name its reason except the one that is reached when none of them
concludes, which still ended `return {"disposition": NOT_DONE, "evidence": ""}`. Two of the three
rows the lane held that morning read exactly that. One was `read-next12-alone-...`, whose clauses
two and three DID land as mechanisms and whose first clause was waiting on a run -- so the empty
string reported a partial delivery as nothing at all. The other named no tracked path, so the
commit query could not even be BUILT and git was never asked; it published the identical answer.

THAT IS THE WHOLE PROPERTY THIS FILE IS KEYED TO: **every disposition `disposition_of` can return
carries a reason a reader can act on, and a reason that says WHICH of "the tree said no" and "the
tree was never asked" it is.** Not "the residual names its window" -- that would pin today's
branches. The residual is the disposition every failed route arrives at, which is precisely why it
is the one place a declared `None` and a silent `None` collapse into the flattering branch.

THE PARTITION IS DISCOVERED, NOT TYPED. `_declared_dispositions` reads the module's own return
sites with `ast`, so the set this control covers is whatever the module can actually return. A
hand-kept list here would go stale the first time a sixth value is added -- and this lane has added
two in three days -- leaving a partition control that no longer covers its partition, which is the
R15 shape one rung up from the defect being fixed.

MUTATIONS (each must fire, and which leg catches it):
  (a) restore `"evidence": ""` at the residual's return -- `..._CARRIES_A_REASON` reds on the
      runtime leg AND `..._NO_RETURN_SITE_WRITES_AN_EMPTY_REASON` reds on the static one;
  (b) give `NOT_DRAWN` or a path-less `DELIVERED` back its empty string -- same two legs;
  (c) make `_nothing_answered` return ONE sentence for all four of its branches -- the non-empty
      legs are satisfied by a constant, so `..._CANNOT_ANSWER_IS_NOT_THE_SAME_ANSWER_AS_NOTHING_
      LANDED` is what reds. This is the leg that stops this file being a guard that refuses
      everything and passes;
  (d) swallow a raised join without recording it, so a crashed query reads as a clean miss --
      `..._A_JOIN_THAT_RAISED_IS_NEVER_REPORTED_AS_A_CLEAN_MISS` reds;
  (e) add a sixth disposition value anywhere in the module and do not build it a row here --
      `..._CARRIES_A_REASON` reds on its reachability clause, naming the value. That is the
      "a later branch cannot be added without one" clause, and it is deliberately a RED rather
      than a skip.

REUSE: the three sibling partition controls (`test_a_swept_row_names_which_of_the_three_...`,
`..._asks_git_whether_the_work_landed_under_another_name`, `..._names_the_sibling_that_holds_its_
windows_commit`, `test_a_window_that_closed_before_its_own_subject_existed_says_so`) each assert
WHICH value a row gets, with private fixtures keyed to the arrival of one value. None of them can
hold this property: it is about every value at once, it is discovered from the module rather than
enumerated, and its subject is the `evidence` string those files pin as empty. Their legs are
corrected in this same change rather than duplicated here.
"""
from __future__ import annotations

import ast
import json
import pathlib

import pytest

from background import delivery_lane as dl

#: Synthetic ids, never the live ledger's. A control pinned to today's rows goes green when the
#: sweep merely gets quieter, which is the defect wearing a better name.
MISSED_ID = "a-window-whose-paths-git-had-nothing-to-say-about"
MUTE_ID = "a-window-whose-item-names-no-tracked-path"
UNBOUND_ID = "a-window-whose-paths-moved-while-nothing-was-bound-to-it"
SIBLING_ID = "a-window-whose-commit-another-row-holds"
HOLDER_ID = "the-row-that-holds-that-commit"
SPENT_ID = "a-window-drawn-against-a-premise-already-spent"
CREDITED_ID = "a-window-whose-work-landed-under-a-better-name"
DELIVERED_ID = "a-window-that-delivered-under-its-own-name"
EARLY_ID = "a-window-that-closed-before-its-own-subject-existed"
NEVER_ID = "an-id-this-ledger-has-never-heard-of"

NOW = 1789000000.0
#: Older than the window plus the grace, so every row below has closed.
DRAWN_AT = NOW - 8 * 3600
WINDOW_ENDS = DRAWN_AT + dl.CLAIM_STALE_SECONDS + dl._landing_grace_seconds()
IN_WINDOW = DRAWN_AT + 900
#: A SECOND in-window instant, and it must differ from the first. `_bound_by` is keyed to the
#: commit's own second, so one instant shared by the unbound commit and the sibling's landing makes
#: the unbound row read as bound -- a fixture defect indistinguishable from the reading being dead.
SIBLING_INSTANT = DRAWN_AT + 1500

SUBJECT_PATH = "background/delivery_lane.py"
QUIET_PATH = "tools/surgical_land.py"
SIBLING_PATH = "background/delivery_seat.py"
UNBOUND_SHA = "ab12cd34ef567890ab12cd34ef567890ab12cd34"
SIBLING_SHA = "99ffee8877665544332211009988776655443322"


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

    Applying it here is what keeps the pathspec load-bearing: a subject that stopped passing paths
    to `git log` would still get an empty answer from this fake for the off-subject rows, so the
    "asked about these paths" clause in the evidence cannot be satisfied by a fake that ignores it.

    IT ANSWERED `None` FOR "NO MATCHES" UNTIL 2026-09-18, AND THAT IS THE DEFECT IT WAS TESTING,
    COPIED. Real `git log -- paths` with nothing to show exits 0 and prints nothing, so `_git`
    returns `""`; only a git that could not RUN returns `None`. A fake that says `None` to both is
    wrong about its subject in exactly the direction that hid the residual's third voice -- and
    while `_window_hits` read the two through one falsy test the error was invisible, because both
    sides of the lie produced the same branch. Now that the subject tells them apart, the fake has
    to as well: `""` here is "asked, nothing found", which is what these legs mean to set up.
    """
    def run(*args, **kwargs):
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


def _states_start_after_the_window() -> str:
    """Prose putting the item's subject an hour past its own window's end.

    Built from the window rather than typed so it moves with `CLAIM_STALE_SECONDS` and the grace.
    """
    import datetime
    when = datetime.datetime.fromtimestamp(WINDOW_ENDS + 3600).strftime("%H:%M")
    return ("Read the artefact once the run settles. ETA near {}; do not draw this before then, "
            "the file will not exist.".format(when))


@pytest.fixture(autouse=True)
def _no_cached_direction_history():
    """`_direction_history_text` caches for the life of the PROCESS, and a suite is one process."""
    dl._reset_direction_history()
    yield
    dl._reset_direction_history()


@pytest.fixture
def prose(monkeypatch):
    """Stub `_item_text` per id: the item stores hold no synthetic row, so the reader needs this."""
    texts: dict[str, str] = {}
    monkeypatch.setattr(dl, "_item_text", lambda fid: texts.get(str(fid), ""))
    return texts


@pytest.fixture
def whole_partition(tmp_path, monkeypatch, prose):
    """One ledger holding a row for EVERY disposition the module can return, plus the un-drawn id.

    It is one fixture and not one per leg because the property is about the partition: a reading
    that answered a single constant would satisfy any per-row fixture written for it, and this
    lane has entered that trap through three doors in one afternoon.
    """
    store = _ledger(tmp_path, {
        MISSED_ID: _row(named_paths=[QUIET_PATH]),
        MUTE_ID: _row(),
        UNBOUND_ID: _row(named_paths=[SUBJECT_PATH]),
        SIBLING_ID: _row(named_paths=[SIBLING_PATH]),
        HOLDER_ID: _row(last_drawn_at=DRAWN_AT - 600, last_landing_at=SIBLING_INSTANT,
                        last_landing_paths=[SIBLING_PATH]),
        SPENT_ID: _row(premise_spent={"commit": "deadbeef123", "reason": "already closed"}),
        CREDITED_ID: _row(last_drawn_at=DRAWN_AT - 600, last_landing_at=DRAWN_AT - 60,
                          landed_under="the-name-it-landed-under",
                          last_landing_paths=["site/index.html"]),
        DELIVERED_ID: _row(last_landing_at=DRAWN_AT + 60, last_landing_paths=[SUBJECT_PATH]),
        EARLY_ID: _row(named_paths=[QUIET_PATH]),
    })
    prose[EARLY_ID] = _states_start_after_the_window()
    monkeypatch.setattr(dl, "_git", _fake_git([
        (UNBOUND_SHA, IN_WINDOW, "a landing nothing bound", [SUBJECT_PATH]),
        (SIBLING_SHA, SIBLING_INSTANT, "a landing another row holds", [SIBLING_PATH]),
    ]))
    return store


def _declared_dispositions() -> set[str]:
    """Every value the module's own `return {"disposition": ...}` sites can carry.

    DISCOVERED FROM THE SOURCE so the partition below cannot go stale behind the module. Names are
    resolved against `dl` rather than assumed: a constant renamed without a value change keeps this
    green, and a new constant appears here the moment its return site does.
    """
    tree = ast.parse(pathlib.Path(dl.__file__).read_text(encoding="utf-8"))
    out = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        for key, value in zip(node.keys, node.values):
            if not (isinstance(key, ast.Constant) and key.value == "disposition"):
                continue
            if isinstance(value, ast.Name):
                resolved = getattr(dl, value.id, None)
                if isinstance(resolved, str):
                    out.add(resolved)
            elif isinstance(value, ast.Constant) and isinstance(value.value, str):
                out.add(value.value)
    return out


def _empty_reason_return_sites() -> list[int]:
    """Line numbers of `{"disposition": ..., "evidence": ""}` literals in the module. Should be []."""
    tree = ast.parse(pathlib.Path(dl.__file__).read_text(encoding="utf-8"))
    bad = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Dict):
            continue
        keys = {k.value for k in node.keys if isinstance(k, ast.Constant)}
        if "disposition" not in keys:
            continue
        for key, value in zip(node.keys, node.values):
            if (isinstance(key, ast.Constant) and key.value == "evidence"
                    and isinstance(value, ast.Constant) and value.value == ""):
                bad.append(node.lineno)
    return bad


def test_THE_PARTITION_every_disposition_of_can_return_CARRIES_A_REASON(whole_partition):
    """One statement over the whole partition: no reading of a row answers with silence.

    TWO CLAUSES AND BOTH ARE LOAD-BEARING. The first is the property -- every answer carries a
    reason. The second is REACHABILITY: the rows below must between them produce every value the
    module declares, or the first clause is being asserted over a partition smaller than the one
    that exists, and a sixth value could be added tomorrow with an empty string and nothing here
    would move. A guard that refuses everything passes every per-branch test ever written for it;
    a guard asserted over a partition it does not cover is the same failure with better manners.
    """
    ids = (MISSED_ID, MUTE_ID, UNBOUND_ID, SIBLING_ID, SPENT_ID, CREDITED_ID, DELIVERED_ID,
           EARLY_ID, NEVER_ID)
    seen = {i: dl.disposition_of(i, path=whole_partition) for i in ids}

    silent = {i: r for i, r in seen.items() if not str(r.get("evidence") or "").strip()}
    assert not silent, silent

    reached = {r["disposition"] for r in seen.values()}
    missing = _declared_dispositions() - reached
    assert not missing, (
        "these dispositions exist in background/delivery_lane.py and no row here produces one, so "
        "the reason property is untested for them: {}".format(sorted(missing)))


def test_NO_RETURN_SITE_WRITES_AN_EMPTY_REASON_however_it_is_reached():
    """The static half, and it catches what reachability cannot.

    A new branch returning an EXISTING disposition with an empty string adds no value to the
    partition, so the reachability clause above stays green while the reader is handed silence
    again -- which is exactly how the residual got here, as one more `NOT_DONE` return among
    several. This reads the source instead of the answer, so a branch nothing has built a row for
    is graded the moment it is written.
    """
    assert _empty_reason_return_sites() == [], (
        "background/delivery_lane.py lines {} return a disposition with an empty evidence "
        "string".format(_empty_reason_return_sites()))


def test_CANNOT_ANSWER_IS_NOT_THE_SAME_ANSWER_AS_NOTHING_LANDED(whole_partition):
    """The two residuals that were one string, and the leg a constant sentence cannot pass.

    `MISSED_ID` named a tracked path and git had nothing to say about it: the tree WAS asked and
    the answer was no. `MUTE_ID` names no path at all, so `_claim_paths` is empty and no query
    could be built: the tree was NEVER asked. They want opposite actions from the reader -- one is
    a genuine miss to pick up, the other is an item whose prose has to be recovered before the
    lane can say anything about it -- and for eleven weeks both printed the empty string.
    """
    asked = dl.disposition_of(MISSED_ID, path=whole_partition)
    never_asked = dl.disposition_of(MUTE_ID, path=whole_partition)

    assert asked["disposition"] == never_asked["disposition"] == dl.NOT_DONE, (asked, never_asked)
    assert asked["evidence"] != never_asked["evidence"], asked

    # The one that WAS asked names what it asked about, so a reader can judge whether the paths
    # were the right ones -- the failure mode a bare "we found nothing" cannot be checked against.
    assert QUIET_PATH in asked["evidence"], asked
    # The one that was NOT asked says so in the reader's own terms, and does not name a path,
    # because naming one would be the fabricated-probe shape: evidence of a query never run.
    assert "CANNOT ANSWER" in never_asked["evidence"], never_asked
    assert QUIET_PATH not in never_asked["evidence"], never_asked


def test_A_JOIN_THAT_RAISED_IS_NEVER_REPORTED_AS_A_CLEAN_MISS(whole_partition, monkeypatch):
    """A crashed query and a quiet tree are different facts, and only one licenses "nothing landed".

    `_disposition` swallows each join's exceptions on purpose: this reading feeds the orientation
    brief and must not take its other twenty keys down with it. But swallowing is not the same as
    having nothing to say, and before this the two arrived identical. A reader told "we looked and
    found nothing" about a window whose commit join never ran may redo work that already exists.
    """
    boom = dl._landed_unbound

    def raises(*args, **kwargs):
        raise RuntimeError("the join could not run")

    monkeypatch.setattr(dl, "_landed_unbound", raises)
    crashed = dl.disposition_of(MISSED_ID, path=whole_partition)
    monkeypatch.setattr(dl, "_landed_unbound", boom)
    quiet = dl.disposition_of(MISSED_ID, path=whole_partition)

    assert crashed["disposition"] == quiet["disposition"] == dl.NOT_DONE, (crashed, quiet)
    assert crashed["evidence"] != quiet["evidence"], crashed
    assert "CANNOT ANSWER" in crashed["evidence"], crashed
    assert "RuntimeError" in crashed["evidence"], crashed
