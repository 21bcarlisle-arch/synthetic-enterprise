"""The draw ledger credits an item by its work, and reads a landing in flight as mid-landing.

THE DEFECT (direction `the-draw-ledger-credits-by-the-items-work-not-by-path-overlap`, 2026-10-16;
finding `SEAT_FINDING_THE_DRAW_LEDGER_GRADES_BY_PATH_SO_MID_LANDING_SPENT_AND_OVERLAPPING_WORK_READ_
ALIKE_2026-10-07`). The ledger asked origin one question -- did a commit touch this item's paths --
and that question cannot tell three states apart:

  * `retention-guard-nets-the-companys-own-bad-debt-belief` read `landed_unbound` on `81732ffe2`,
    a heating draw sharing one path of its long list, with no netting code on any ref; and a strike
    item was credited with `8a1a7a51a`, the prereg record, for `badd57e8e`'s work.
  * b7-slice-3 (2026-10-06) and weighted-per-win-envelope (2026-10-07, `surgical_land` pid 2895736)
    read `not_done` with their landings running, and the queue re-offered them.

THE RULE. An item is landed only on a commit that names it -- a `--landed` bind or its id in the
message -- and a live `surgical_land` or owned worktree holding it reads `mid_landing`.

MUTATIONS (run 2026-10-16, each recorded with what it redded):
  (a) `_binds_item` back to `holder is None or holder == focus_id` (the path match): the
      path-only control reds -- the one-shared-path commit reads `landed_unbound`.
  (b) `_disposition` without its `_mid_landing` call: the partition reds on `mid_landing`.
  (c) `_binds_item` -> `return False` (the guard that refuses everything): both controls red on
      their rare branch, the commit that names the id.
"""
from __future__ import annotations

import json

import pytest

from background import delivery_lane as dl

NOW = 1789000000.0
DRAWN_AT = NOW - 4 * 3600
IN_WINDOW = DRAWN_AT + 900

SUBJECT = "background/retention_guard.py"
OTHERS = ["simulation/heating.py", "company/bad_debt.py", "saas/churn.py"]

LANDED_ID = "an-item-whose-commit-names-it"
MID_ID = "an-item-a-live-landing-holds"
MISSED_ID = "an-item-nothing-touched"
OVERLAP_ID = "an-item-sharing-one-path-with-another-draw"

OWN_SHA = "a1" * 20
OVERLAP_SHA = "b2" * 20


def _prose(fid: str) -> str:
    return f"Change {SUBJECT} so the guard nets the belief, and edit " + ", ".join(OTHERS) + "."


def _fake_git(commits):
    """`(sha, instant, message, paths)` rows; the pathspec and `%B` are answered per commit."""
    def fake(*args, cwd=None):
        if args[:3] == ("log", "-1", "--format=%B"):
            return next((c[2] for c in commits if c[0] == args[3]), None)
        if args and args[0] == "ls-files":
            return "\n".join([SUBJECT, *OTHERS]) + "\n"
        if args and args[0] == "log":
            wanted = list(args[args.index("--") + 1:]) if "--" in args else []
            if wanted == [dl.DIRECTION_RECORD_PATH]:
                return ""
            out = []
            for sha, when, message, paths in commits:
                hit = [p for p in paths if p in wanted]
                if wanted and not hit:
                    continue
                out.append("{}\x1f{:.0f}\x1f{}".format(sha, when, message.splitlines()[0]))
                out.extend(hit)
            return "\n".join(out) + "\n" if out else ""
        return None
    return fake


@pytest.fixture(autouse=True)
def _isolated(monkeypatch):
    dl._reset_direction_history()
    monkeypatch.setattr(dl, "_item_text", _prose)
    monkeypatch.setattr(dl, "_dirty_with_mtimes", lambda paths: [])
    monkeypatch.setattr(dl, "_holders_for_the_ledger", lambda: [])
    yield
    dl._reset_direction_history()


def _grade(tmp_path, monkeypatch, focus_id, commits, holders=()):
    (tmp_path / focus_id).mkdir()
    store = tmp_path / focus_id / "claims.json"
    store.write_text("{}", encoding="utf-8")
    row = {"first_drawn_at": DRAWN_AT, "last_drawn_at": DRAWN_AT,
           "named_paths": [SUBJECT, *OTHERS]}
    dl._ledger_path(store).write_text(json.dumps({focus_id: row}), encoding="utf-8")
    monkeypatch.setattr(dl, "_git", _fake_git(commits))
    monkeypatch.setattr(dl, "_holders_for_the_ledger", lambda: list(holders))
    return dl.disposition_of(focus_id, path=store)


def _landing(message: str = "", paths=()) -> dict:
    return {"holder": "surgical_land pid 4242", "artefact": "(a gated landing)",
            "names": {"surgical_land pid 4242"}, "paths": set(paths), "identifiers": set(),
            "copies": {}, "message": message}


def test_THE_PARTITION_landed_mid_landing_and_not_done_are_each_reachable(tmp_path, monkeypatch):
    """One statement over the three states the ledger must tell apart.

    Mid-landing is reached BOTH ways a holder holds an item -- its landing's message names the id,
    or it holds a path the item asks to change -- so neither leg can quietly be the only one.
    """
    landed = _grade(tmp_path, monkeypatch, LANDED_ID, [
        (OWN_SHA, IN_WINDOW, f"the guard nets\n\nNEXT: none -- direction item {LANDED_ID}, finished",
         [SUBJECT])])
    by_name = _grade(tmp_path, monkeypatch, MID_ID, [],
                     [_landing(f"gating\n\nNEXT: none -- direction item {MID_ID}, finished")])
    by_path = _grade(tmp_path, monkeypatch, MID_ID + "-by-path", [],
                     [_landing("an unnamed landing", [SUBJECT])])
    missed = _grade(tmp_path, monkeypatch, MISSED_ID, [],
                    [_landing("another item's landing", ["docs/elsewhere.md"])])

    assert (landed["disposition"] == dl.LANDED_UNBOUND
            and by_name["disposition"] == dl.MID_LANDING
            and by_path["disposition"] == dl.MID_LANDING
            and missed["disposition"] == dl.NOT_DONE), (landed, by_name, by_path, missed)
    assert "surgical_land pid 4242" in by_name["evidence"] and SUBJECT in by_path["evidence"]


def test_A_COMMIT_SHARING_ONLY_A_PATH_CREDITS_NO_ITEM_and_the_same_commit_naming_it_does(
        tmp_path, monkeypatch):
    """The `81732ffe2` shape: another draw's commit on one path of a long list is not this work.

    The rare branch is in the same statement: the identical commit, its message naming the id, IS
    credited -- so a reader that refused every commit cannot pass.
    """
    shared = _grade(tmp_path, monkeypatch, OVERLAP_ID, [
        (OVERLAP_SHA, IN_WINDOW, "W2_20: the heating draw", [SUBJECT])])
    named = _grade(tmp_path, monkeypatch, OVERLAP_ID + "-named", [
        (OVERLAP_SHA, IN_WINDOW,
         f"W2_20: the heating draw\n\nNEXT: none -- direction item {OVERLAP_ID}-named, finished",
         [SUBJECT])])

    assert (shared["disposition"] not in (dl.LANDED_UNBOUND, dl.LANDED_ELSEWHERE)
            and named["disposition"] == dl.LANDED_UNBOUND), (shared, named)
    # The declined commit is still SAID, as a hint, so the reader can open it in one `git show`.
    assert "path_touched_by " + OVERLAP_SHA[:9] in shared["evidence"], shared


def test_A_LANDING_ARGV_YIELDS_ITS_MESSAGE_AND_THE_PATHS_IT_WRITES():
    argv = ["python3", "-m", "tools.surgical_land", "-m", "the work", "--attempts", "2",
            "--content", "docs/a.md=/tmp/a", "--drops=docs/b.md", "--merge", "origin/main",
            "background/c.py"]
    assert dl._landing_argv(argv) == ("the work", {"docs/a.md", "docs/b.md", "background/c.py"})
    assert dl._landing_argv(["python3", "-m", "tools.isolate_hunks", "docs/a.md"]) is None
