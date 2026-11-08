"""A CONTINUATION EMBARGOED PAST ITS OWN SIX HOURS IS STILL THERE WHEN THE EMBARGO LIFTS.

`read-the-monday-status-line-against-the-gate` (written 23:53 Sat 7 Nov) can only be done after the
04:00 Mon publish. Unstamped, it was drawn 28 hours early; stamped, it would have aged out of the
six-hour window 22 hours before its stamp lifted. So the window opens at the later of when the item
was written and its dated embargo.

Mutation: revert `_window_opens` to `written_at` alone -- the embargoed item is gone at `lift`.
"""
from __future__ import annotations

import datetime
import time

from background import delivery_lane, seat_continuation


def test_an_embargoed_item_outlives_its_written_window_and_an_unstamped_one_does_not(
        tmp_path, monkeypatch):
    monkeypatch.setattr(seat_continuation, "STORE", tmp_path / "continuations.json")
    now = float(int(time.time() // 60) * 60)
    lift = now + 28 * 3600
    stamp = datetime.datetime.fromtimestamp(lift).strftime("%H:%M on %Y-%m-%d")
    seat_continuation.hand_off("read-monday", what=f"DO NOT DRAW BEFORE {stamp}. Read the line.",
                               why="w", done_means="d", now=now)
    seat_continuation.hand_off("today", what="Unrelated.", why="w", done_means="d", now=now)
    window = seat_continuation.STALE_AFTER_SECONDS

    def offered(at: float) -> set[str]:
        return {i["id"] for i in seat_continuation.live(now=at)
                if not delivery_lane._embargoed(i, at)}

    def expired(at: float) -> set[str]:
        return {i["id"] for i in seat_continuation.expired(now=at)}

    # Every branch is reachable: offered, held, aged out -- for each item.
    assert offered(now) == {"today"}, "the embargo did not hold, or the sibling was not offered"
    assert "today" in expired(now + window + 60), "an unstamped item no longer ages out"
    assert "read-monday" not in expired(now + window + 60), (
        "the embargoed item aged out on its written clock, before its embargo lifted")
    assert offered(lift + 60) == {"read-monday"}, (
        "the embargoed item aged out before its embargo lifted -- it can never be drawn")
    assert "read-monday" in expired(lift + window + 60), "an embargoed item now lives for ever"
