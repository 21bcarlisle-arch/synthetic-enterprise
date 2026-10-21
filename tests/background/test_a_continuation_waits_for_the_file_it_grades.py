"""A GRADE CONTINUATION WAITS FOR THE FILE IT GRADES, NOT FOR A GUESS ABOUT WHEN IT WILL EXIST.

Four times in two days (2026-10-20/21) a grade continuation was handed to a tick before its arms
finished: each carried `DO NOT DRAW BEFORE <time>`, and a time is a guess about a run's length. The
file the grade reads is the premise itself, so the item can say so:

    DO NOT DRAW BEFORE /var/tmp/se-pcs-arms-out/flat.rc EXISTS

The property: while the path is absent the item is skipped (and the lane keeps delivering); once it
exists the item is offered; with a time as well, both must be met; a quoted mention holds nothing.
"""
from __future__ import annotations

import datetime
import time

import pytest

from background import delivery_lane, delivery_seat, seat_continuation


@pytest.fixture
def now() -> float:
    return float(int(time.time() // 60) * 60)


def _hand_off(item_id: str, what: str, now: float) -> None:
    seat_continuation.hand_off(item_id, what=what, why="w", done_means="d", now=now)


def test_the_same_continuation_is_held_without_its_file_and_offered_with_it(
        tmp_path, monkeypatch, now):
    """The whole partition over ONE item: held branch, offered branch, and the lane never empty."""
    monkeypatch.setattr(delivery_lane, "CLAIMS_FILE", tmp_path / "claims.json")
    monkeypatch.setattr(seat_continuation, "STORE", tmp_path / "continuations.json")
    monkeypatch.setattr(delivery_lane.direction_mod, "unreachable_focus", lambda _atoms: [])
    rc = tmp_path / "arms" / "flat.rc"
    later = datetime.datetime.fromtimestamp(now + 3600).strftime("%H:%M on %Y-%m-%d")
    _hand_off("grade-the-arms", f"DO NOT DRAW BEFORE {rc} EXISTS. Grade the three arms.", now)
    _hand_off("grade-both-ways",
              f"DO NOT DRAW BEFORE {rc} EXISTS and DO NOT DRAW BEFORE {later}. Grade.", now)
    _hand_off("a-sibling", "Unrelated work behind it.", now)
    _hand_off("describes-the-grammar",
              f"Add the form `DO NOT DRAW BEFORE {tmp_path}/never EXISTS` to the draw.", now)
    claims = tmp_path / "claims.json"

    def offered(at: float) -> set[str]:
        return {i["id"] for i in seat_continuation.live(now=at)
                if not delivery_lane._embargoed(i, at)}

    held = delivery_lane.next_item(now=now, path=claims)
    assert held is not None and held["id"] == "a-sibling", (
        "absent file: the waiting grade was handed out, or the lane fell silent behind it")
    assert offered(now) == {"a-sibling", "describes-the-grammar"}, (
        "a backticked mention of the grammar is a description, not an instruction")

    rc.parent.mkdir()
    rc.write_text("0\n")
    released = delivery_lane.next_item(now=now, path=claims)
    assert released is not None and released["id"] == "grade-the-arms", (
        "the file exists and the item is still withheld -- a wait became a refusal")
    assert "grade-both-ways" not in offered(now), "the path was met but the time was not"
    assert "grade-both-ways" in offered(now + 7200), "both met and the item is still held"


def test_the_brief_queue_line_names_the_path_it_waits_for(tmp_path, monkeypatch, now):
    monkeypatch.setattr(seat_continuation, "STORE", tmp_path / "continuations.json")
    rc = tmp_path / "flat.rc"
    _hand_off("grade-the-arms", f"DO NOT DRAW BEFORE {rc} EXISTS. Grade.", now)
    at = datetime.datetime.fromtimestamp(now + 60, datetime.timezone.utc)
    rendered = delivery_seat._render_continuation_queue(
        delivery_seat._continuation_queue(at, at))
    assert f"HELD until {rc} exists" in rendered
    rc.write_text("0\n")
    assert "HELD until" not in delivery_seat._render_continuation_queue(
        delivery_seat._continuation_queue(at, at))
