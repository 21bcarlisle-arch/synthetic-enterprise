"""The brief's `previous_focus` and `since` come from the last row that WROTE a record.

The defect this names: `build_brief` read `last_orientation()`, "skip or not". Under tick mode
slow the 2026-10-16 ledger ended in four skip rows after the 17:25Z oriented row, so the brief
handed the 08:22Z session an empty `previous_focus` (the steer grade read "no previous focus"
while four focus items were live) and a 3h, 1-commit stretch where 17 commits had landed.

The ledger here is a real file read through the real `direction.read_decisions`; only the
level-zero pass (~145 s of subprocesses, owned by `test_delivery_seat.py`) is stubbed.
"""
from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone

from background import delivery_seat as ds

FOCUS = ["focus-one", "focus-two", "focus-three", "focus-four"]


def _ledger(tmp_path, monkeypatch, now, *, skips_after: int):
    written = now - timedelta(hours=15)
    rows = [{"at": (written - timedelta(hours=3)).isoformat(), "outcome": "oriented",
             "focus": ["an-older-focus"], "map_levels": {}},
            {"at": written.isoformat(), "outcome": "oriented", "focus": FOCUS, "map_levels": {},
             "wrong": [{"what": "an error", "corrected": False}]}]
    rows += [{"at": (written + timedelta(hours=3 * (i + 1))).isoformat(), "outcome": "skipped",
              "why": "tick mode slow", "map_levels": {}} for i in range(skips_after)]
    path = tmp_path / "decisions.jsonl"
    path.write_text("".join(json.dumps(r) + "\n" for r in rows), encoding="utf-8")
    monkeypatch.setattr(ds.direction_mod, "DECISIONS_PATH", path)
    monkeypatch.setattr("tools.level_zero_contradicted_by_its_own_controls.assess",
                        lambda *a, **k: ([], []))
    return written, rows[-1]


def test_a_SKIP_ROW_NEWEST_still_hands_back_the_last_written_records_focus_and_window(
        tmp_path, monkeypatch):
    now = datetime.now(timezone.utc)
    written, newest = _ledger(tmp_path, monkeypatch, now, skips_after=4)
    # THE BRANCH CAN BE TAKEN: the newest row really is a skip with no focus, so a reader of the
    # newest row would get exactly the empty answer this control exists to refuse.
    assert newest["outcome"] == "skipped" and not newest.get("focus")

    brief = ds.build_brief(now)

    assert brief["previous_focus"] == FOCUS, (
        "a skip row is newest and `previous_focus` came back {!r} -- the brief is reading the last "
        "TICK, not the last written record".format(brief["previous_focus"]))
    assert brief["previous_wrong"] == [{"what": "an error", "corrected": False}]
    assert datetime.fromisoformat(brief["since"]) == written, (
        "the stretch starts at {} rather than at the last written record {} -- skips cut it short"
        .format(brief["since"], written.isoformat()))
    # AND THE OTHER WINDOW IS STATED BESIDE IT, not lost.
    assert brief["last_tick"] == {"at": newest["at"], "outcome": "skipped"}


def test_with_NO_skip_the_newest_oriented_row_is_the_record(tmp_path, monkeypatch):
    """The control over the partition: the newest-row case still picks the NEWEST oriented row,
    not merely any oriented row."""
    now = datetime.now(timezone.utc)
    written, newest = _ledger(tmp_path, monkeypatch, now, skips_after=0)
    assert ds.last_written_record()["at"] == written.isoformat() == newest["at"]
    assert ds.last_orientation()["at"] == newest["at"]
