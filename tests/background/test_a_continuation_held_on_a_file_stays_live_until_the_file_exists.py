"""A CONTINUATION HELD ON A FILE STAYS LIVE UNTIL THE FILE EXISTS, AND SAYS SO WHEN IT NEVER DOES.

`s12g-rankq-is-graded-when-it-ends` (24 Nov) said `DO NOT DRAW BEFORE /var/tmp/vtn-driver/
grade_rankq.out EXISTS`. The draw honoured the hold, but the store dropped the row six hours after
writing with the run still going, so the reader of the thesis's live test was in `expired()` with
`drawn_at` 0. A file hold now keeps the row live (held, not drawable) until the file appears, then
gives it the ordinary window from the file's mtime; past `FILE_HOLD_LIMIT_SECONDS` it expires and
`expired()` names the file that never came.

Mutation: in `_window_opens`, drop the `if absent and ...: return max(opens, at)` branch -- the
seven-hour-old held row is in `expired()`, not `live()`, and the first assertion reds. Drop the
`min(..., written + FILE_HOLD_LIMIT_SECONDS)` clamp and the last assertion reds: a late rewrite of
the held file revives the row (the real store did this to a 236 h row held on a directory).
"""
from __future__ import annotations

import datetime
import os
import time

from background import delivery_lane
from background import seat_continuation as sc


def test_a_file_held_row_outlives_its_window_and_is_drawable_once_the_file_appears(
        tmp_path, monkeypatch):
    monkeypatch.setattr(sc, "STORE", tmp_path / "continuations.json")
    now = time.time()
    written = now - 7 * 3600
    out = tmp_path / "grade.out"
    sc.hand_off("held", what=f"DO NOT DRAW BEFORE {out} EXISTS. Grade it.", why="w",
                done_means="d", now=written)
    lift = now + 2 * 3600
    # naive local on purpose: `delivery_lane._EMBARGO` reads the stamp as local time
    stamp = datetime.datetime.fromtimestamp(lift).strftime("%H:%M on %Y-%m-%d")  # noqa: DTZ006
    sc.hand_off("dated", what=f"DO NOT DRAW BEFORE {stamp}. Read it.", why="w",
                done_means="d", now=written)
    sc.hand_off("plain", what="Unrelated.", why="w", done_means="d", now=written)

    def live(at):
        return {i["id"] for i in sc.live(now=at)}

    def drawable(at):
        return {i["id"] for i in sc.live(now=at) if not delivery_lane._embargoed(i, at)}

    def expired(at):
        return {i["id"]: i["expiry_reason"] for i in sc.expired(now=at)}

    # Absent file, 7 h old: live but held. The dated row and the plain row behave as before.
    assert "held" in live(now), "a file-held row expired on its written clock with its file absent"
    assert "held" not in drawable(now), "a file hold no longer holds the draw"
    assert "dated" in live(now) and "dated" not in drawable(now), "the dated hold changed"
    assert expired(now).get("plain") == "window closed", "an unheld row no longer ages out"

    # The file appears: drawable, and the window runs from its mtime.
    out.write_text("done\n")
    os.utime(out, (now, now))
    assert "held" in drawable(now), "the row is not drawable once its file exists"
    assert "held" in expired(now + sc.STALE_AFTER_SECONDS + 60), (
        "a satisfied file hold now lives for ever")
    assert "dated" in drawable(lift + 60), "the dated row is not drawable after its stamp"

    # A file that never appears: past the outer limit the row expires and says which file.
    out.unlink()
    late = written + sc.FILE_HOLD_LIMIT_SECONDS + 60
    assert "held" in live(written + sc.FILE_HOLD_LIMIT_SECONDS - 60), "the hold ends early"
    assert expired(late).get("held") == f"held on {out}, never appeared", (
        "a file hold that never fired is not named as such in expired()")

    # A file rewritten long after the limit (a log, a directory) does not revive the row.
    out.write_text("rewritten\n")
    after = late + sc.STALE_AFTER_SECONDS + 3600
    os.utime(out, (after, after))
    assert "held" in expired(after + 60), "a late rewrite revived a row past its file-hold limit"
