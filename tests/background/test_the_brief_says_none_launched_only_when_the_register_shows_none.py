"""The brief says no long job LAUNCHED only when the register shows none launched.

`ended_since` skipped every live record, and the empty sentence then read "NO `launch_long_job`
JOB LAUNCHED OR ENDED" about a stretch whose register held three read-instruction arms launched at
23:45Z and 00:19Z. A seat that trusts that line can relaunch a running 3.7 GB arm.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from background import delivery_seat as seat

SINCE = datetime(2026, 10, 20, 23, 0, tzinfo=timezone.utc)


def _register(tmp_path, rows):
    path = tmp_path / ".launch_records.json"
    path.write_text(json.dumps(rows), encoding="utf-8")
    return path


def _live(job, launched):
    return {"job": job, "unit": "longjob-" + job, "claim": "live", "launched_at": launched,
            "settled_at": None, "artefact": None, "log": "/var/tmp/" + job + ".log"}


def _prompt(ended):
    return seat._prompt({
        "substantive_count": 0, "levels_recorded": [], "levels_moved": {},
        "director_inputs": [], "findings": {}, "live_direction_age_hours": 1.0, "ended": ended,
        "shape": {"available": True, "shape_is_wrong": False, "count": 3,
                  "carrying_work": 3, "changed_nothing": 0, "findings": []}})


def test_a_live_launch_inside_the_stretch_is_listed_and_never_denied(tmp_path):
    """THE PARTITION FIRST: an empty register CAN print the 'none launched' sentence, so the
    control below is not passing against a branch that no longer exists. Then a live row launched
    inside the window, with nothing ended, must be named and must not be denied; one launched
    before the window is not this stretch's.

    MUTATION: restore the old empty-jobs sentence and the second leg reds on "LAUNCHED OR ENDED".
    """
    empty = _prompt(seat.ended_since(SINCE, register=_register(tmp_path, [])))
    assert "JOB LAUNCHED OR ENDED IN THIS STRETCH" in empty

    path = _register(tmp_path, [_live("read-instruction-off", "2026-10-20T23:45:39Z"),
                                _live("before-window", "2026-10-20T20:00:00Z")])
    ended = seat.ended_since(SINCE, register=path)
    assert [j["job"] for j in ended["launched_live"]] == ["read-instruction-off"]
    text = _prompt(ended)
    assert "LAUNCHED OR ENDED" not in text
    assert "NO `launch_long_job` JOB ENDED IN THIS STRETCH" in text
    assert "read-instruction-off" in text and "before-window" not in text
