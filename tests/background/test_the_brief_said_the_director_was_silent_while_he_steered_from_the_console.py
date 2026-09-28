"""The seat's brief reported `director_inputs: []` for five stretches while the director was
steering from the console, because his words are captured into `docs/staging/console/` and
`director_inputs()` only globbed the root, `done/` and `in_progress/`. "Silence is validation" is
only safe if silence is measured.

Mutation: drop `console_turns_since(...)` from `director_inputs` and the first test goes red; key
the console read on file mtime instead of the turn heading and the second goes red.
"""
from __future__ import annotations

import os
from datetime import datetime, timezone

from background import delivery_seat as seat

SINCE = datetime(2026, 9, 27, 13, 0, tzinfo=timezone.utc)
NOW = datetime(2026, 9, 27, 18, 0, tzinfo=timezone.utc)


def _capture(path, stamps):
    path.parent.mkdir(parents=True, exist_ok=True)
    body = ["# Director console — verbatim record", ""]
    for stamp in stamps:
        body += [f"### {stamp}", "", f"> turn at {stamp}", ""]
    path.write_text("\n".join(body), encoding="utf-8")


def test_a_console_turn_after_since_is_named_and_one_before_is_not(tmp_path, monkeypatch):
    monkeypatch.setattr(seat, "STAGING_DIR", tmp_path)
    _capture(tmp_path / "console" / "DIRECTOR_CONSOLE_2026-09-27.md",
             ["2026-09-27T12:41:28.057Z", "2026-09-27T13:06:46.280Z"])
    # The seat's own replies share the heading shape and must never read as his voice.
    _capture(tmp_path / "console" / "SEAT_REPLY_2026-09-27.md", ["2026-09-27T13:10:00.000Z"])

    assert seat.director_inputs(SINCE, NOW) == [
        "console/DIRECTOR_CONSOLE_2026-09-27.md@2026-09-27T13:06:46.280Z"]


def test_a_freshly_touched_capture_holding_only_old_turns_is_silence(tmp_path, monkeypatch):
    monkeypatch.setattr(seat, "STAGING_DIR", tmp_path)
    capture = tmp_path / "DIRECTOR_CONSOLE_2026-09-27.md"  # in the root, where a new day lands
    _capture(capture, ["2026-09-27T12:41:28.057Z"])
    os.utime(capture, (NOW.timestamp(), NOW.timestamp()))  # mtime after since; the turn is not
    staged = tmp_path / "from_rich_steer.md"
    staged.write_text("x", encoding="utf-8")
    os.utime(staged, (NOW.timestamp(), NOW.timestamp()))

    # The partition's other arm is reachable: a staged file is still named, so the empty console
    # read above is the capture being silent, not the whole reader being dead.
    assert seat.director_inputs(SINCE, NOW) == ["from_rich_steer.md"]
