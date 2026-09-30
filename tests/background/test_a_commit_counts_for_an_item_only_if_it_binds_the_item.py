"""A commit that merely touches one of an item's named paths is not that item's work.

THE DEFECT (director's direction `the-lane-0-ledger-attributes-by-the-item-not-by-a-path`,
2026-09-30). The lane-0 ledger misgraded three ab6 items in one day, and each misgrade told the
next worker "not yours to redo" about work nobody had done:

  * `grade-the-ab6-bridge-leg` read `landed_elsewhere` under `51417dba4` -- the commit that
    LAUNCHED ab6 and wrote the prereg the grade was to append to, bound to its own row. The grade
    itself landed later as `504b42a37`.
  * `grade-ab6-pilots-once-runp2-exists` read `landed_unbound` under `dd5f33581`, a W1_14 weather
    commit, because the row's stamp (taken from the DOORBELL, whose PATH CHECK lines name other
    files) held `maturity_map.yaml`, which the item's prose never asked to change.
  * another item's 09:55 bytes, sitting uncommitted on a stamped path the grade never asked for,
    were read as the grade's own strand.

THE RULE. A commit binds an item only by: a `--landed` bind to its id, its id in the commit
message, or -- for a commit no row is bound to -- a diff to a path the item's prose asks to
CHANGE. Anything else is published as `path_touched_by <sha>`, a hint and not a disposition.

ONE PARTITION, NOT A LEG PER BRANCH. A predicate that refuses everything passes every "is it
refused" assertion, so the three misgrades and two true bindings are asserted in one statement.
Synthetic ids and shas; the shapes are the live instances', nothing is read from the live ledger.

MUTATIONS (run 2026-09-30, each recorded with what it redded):
  (a) `_binds_item` -> `return True` (the path match back): the partition reds on the bridge
      instance -- `landed_elsewhere` under the launch commit.
  (b) `_claim_subject_paths` back to `stamp - mentioned` (the path match via the stamp): the
      partition reds on the pilots instance (`landed_unbound` on the weather commit) and the
      09:55 test reds (`stranded`).
  (c) `_binds_item` without its message leg (`return holder is None or holder == focus_id`): the
      partition reds on the rare branch -- a sibling-held commit that NAMES this id is no longer
      credited, which is the guard that refuses everything.
"""
from __future__ import annotations

import json

import pytest

from background import delivery_lane as dl

NOW = 1789000000.0
DRAWN_AT = NOW - 4 * 3600
IN_WINDOW = DRAWN_AT + 900

PREREG = "docs/staging/records/SEAT_PREREG_A_SYNTHETIC_AB_2026-09-30.md"
MAP = "docs/design/maturity_map.yaml"
TOOL = "tools/run_value_cycle_ab.py"

BRIDGE_ID = "grade-a-bridge-leg"
PILOTS_ID = "grade-the-pilots-once-the-run-exists"
BYTES_ID = "grade-a-leg-whose-stamp-holds-anothers-bytes"
NAMED_ID = "grade-a-leg-another-row-landed-by-name"
UNBOUND_ID = "grade-a-leg-whose-own-work-landed-unbound"
LAUNCH_ID = "launch-the-ab"

PROSE = {
    BRIDGE_ID: f"Grade B1 and B2. Append the grade to {PREREG} and land it by pathspec.",
    PILOTS_ID: f"Grade P1-P3. Append all of it to {PREREG} and land by pathspec.",
    BYTES_ID: f"Grade X1. Append the grade to {PREREG} and land it by pathspec.",
    NAMED_ID: f"Grade Y1. Append the grade to {PREREG} and land it by pathspec.",
    UNBOUND_ID: f"Grade Z1. Append the grade to {PREREG} and land it by pathspec.",
}

LAUNCH_SHA = "51417dba4" + "0" * 31
WEATHER_SHA = "dd5f33581" + "0" * 31
NAMED_SHA = "abcdef012" + "0" * 31
OWN_SHA = "fedcba987" + "0" * 31

#: (sha, instant, subject line, full message, touched paths)
COMMITS = [
    (LAUNCH_SHA, IN_WINDOW, "ab launched", "ab launched on the single-roll world", [PREREG]),
    (WEATHER_SHA, IN_WINDOW + 60, "W1_14 weather", "the world's weather covers the roster", [MAP]),
    (NAMED_SHA, IN_WINDOW + 120, "Y1 graded", f"Y1 graded.\n\nThis is {NAMED_ID}'s grade.",
     [PREREG]),
    (OWN_SHA, IN_WINDOW + 180, "Z1 graded", "Z1 graded", [PREREG]),
]


def _row(named, **extra):
    row = {"first_drawn_at": DRAWN_AT, "last_drawn_at": DRAWN_AT, "named_paths": list(named)}
    row.update(extra)
    return row


def _holder(instant: float) -> dict:
    return {"first_drawn_at": DRAWN_AT - 7200, "last_drawn_at": DRAWN_AT - 7200,
            "last_landing_at": instant, "last_landing_paths": [PREREG]}


def _fake_git(commits):
    """Answers the commit query per pathspec, and `log -1 --format=%B <sha>` with that sha only.

    Each row is asked against only its own commits, so one row's window cannot
    see another's work -- the partition is about the PREDICATE, not about shared windows.
    """
    def fake(*args, cwd=None):
        if args[:3] == ("log", "-1", "--format=%B"):
            return next((c[3] for c in commits if c[0] == args[3]), None)
        if args and args[0] == "ls-files":
            return "\n".join([PREREG, MAP, TOOL]) + "\n"
        if args and args[0] == "log":
            wanted = list(args[args.index("--") + 1:]) if "--" in args else []
            if wanted == [dl.DIRECTION_RECORD_PATH]:
                return ""
            out = []
            for sha, when, subject, _msg, paths in commits:
                hit = [p for p in paths if p in wanted]
                if wanted and not hit:
                    continue
                out.append("{}\x1f{:.0f}\x1f{}".format(sha, when, subject))
                out.extend(hit)
            return "\n".join(out) + "\n" if out else ""
        return None
    return fake


@pytest.fixture(autouse=True)
def _isolated(monkeypatch):
    dl._reset_direction_history()
    monkeypatch.setattr(dl, "_item_text", lambda fid: PROSE.get(fid, ""))
    monkeypatch.setattr(dl, "_dirty_with_mtimes", lambda paths: [])
    yield
    dl._reset_direction_history()


def _ledger(tmp_path, rows):
    store = tmp_path / "claims.json"
    store.write_text("{}", encoding="utf-8")
    dl._ledger_path(store).write_text(json.dumps(rows), encoding="utf-8")
    return store


def _one(tmp_path, monkeypatch, focus_id, row, commits, extra_rows=None):
    """One row in its own ledger, against only its own commits."""
    rows = {focus_id: row}
    rows.update(extra_rows or {})
    (tmp_path / focus_id).mkdir()
    store = _ledger(tmp_path / focus_id, rows)
    monkeypatch.setattr(dl, "_git", _fake_git(commits))
    return dl.disposition_of(focus_id, path=store)


LANDED = (dl.LANDED_ELSEWHERE, dl.LANDED_UNBOUND)


def test_THE_PARTITION_a_path_match_grades_nothing_and_a_binding_still_grades(
        tmp_path, monkeypatch):
    bridge = _one(tmp_path, monkeypatch, BRIDGE_ID, _row([PREREG]), [COMMITS[0]],
                  {LAUNCH_ID: _holder(IN_WINDOW)})
    pilots = _one(tmp_path, monkeypatch, PILOTS_ID, _row([PREREG, MAP]), [COMMITS[1]])
    named = _one(tmp_path, monkeypatch, NAMED_ID, _row([PREREG]), [COMMITS[2]],
                 {LAUNCH_ID: _holder(IN_WINDOW + 120)})
    own = _one(tmp_path, monkeypatch, UNBOUND_ID, _row([PREREG]), [COMMITS[3]])

    misgrades_refused = (bridge["disposition"] not in LANDED
                         and pilots["disposition"] not in LANDED)
    bindings_taken = (named["disposition"] == dl.LANDED_ELSEWHERE
                      and own["disposition"] == dl.LANDED_UNBOUND)
    assert misgrades_refused and bindings_taken, (bridge, pilots, named, own)
    # The declined commit is still SAID, as a hint the reader can open in one `git show`.
    assert "path_touched_by 51417dba4" in bridge["evidence"], bridge
    assert "dd5f33581" not in pilots["evidence"], pilots
    assert NAMED_SHA[:9] in named["evidence"] and OWN_SHA == own["commit"], (named, own)


def test_ANOTHER_ITEMS_0955_BYTES_ON_A_STAMPED_PATH_ARE_NOT_THIS_ITEMS_STRAND(
        tmp_path, monkeypatch):
    """Uncommitted bytes on a path the stamp holds but the prose never asks to change are a hint.

    The strand verdict says LAND THESE under this claim's name; said of another item's bytes it
    tells a reader to commit someone else's work. The same bytes on the SUBJECT path must still
    strand -- the rare branch can be taken.
    """
    written = IN_WINDOW                      # the 09:55 draft: inside the window, never landed
    monkeypatch.setattr(dl, "_git", _fake_git([]))

    store = _ledger(tmp_path, {BYTES_ID: _row([PREREG, TOOL])})
    monkeypatch.setattr(dl, "_dirty_with_mtimes", lambda paths: [(TOOL, written)])
    theirs = dl.tree_verdict(BYTES_ID, now=NOW, path=store)
    theirs_disposition = dl.disposition_of(BYTES_ID, path=store)

    monkeypatch.setattr(dl, "_dirty_with_mtimes", lambda paths: [(PREREG, written)])
    mine = dl.tree_verdict(BYTES_ID, now=NOW, path=store)

    assert theirs and theirs["verdict"] not in (dl.STRANDED, dl.CREDITED), theirs
    assert "path_touched" in theirs["evidence"], theirs
    assert theirs_disposition["disposition"] not in LANDED, theirs_disposition
    assert mine and mine["verdict"] == dl.STRANDED, mine


def test_A_MESSAGE_MATCH_IS_A_WHOLE_ID_NOT_A_PREFIX(monkeypatch):
    """`grade-the-ab6-bridge-leg` is a prefix of `...-once-runb6-exists`; naming the second binds
    only the second."""
    monkeypatch.setattr(dl, "_git", lambda *a, cwd=None: "graded under grade-a-leg-once-it-exists")
    assert not dl._message_names("x" * 40, "grade-a-leg")
    assert dl._message_names("x" * 40, "grade-a-leg-once-it-exists")
