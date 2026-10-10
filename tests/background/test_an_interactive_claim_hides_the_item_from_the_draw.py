"""The interactive session's `--claim` door, and that what it writes is what the draw skips.

The defect: `delivery_lane.next_item` skipped ids held in `.seat_work_in_hand.json`, but nothing
outside the executor could write one, so a session building a direction item stayed drawable until
it had created a file the name match could see. Home-mover retention was drawn that way, 2026-10-10.
"""
from __future__ import annotations

import json

import pytest

from background import delivery_lane as L
from background import seat_work_in_hand as S

LIVE = "home-mover-retention-as-a-supplier-lever"


@pytest.fixture
def store(tmp_path, monkeypatch):
    p = tmp_path / ".seat_work_in_hand.json"
    monkeypatch.setattr(S, "CLAIMS_FILE", p)
    monkeypatch.setattr(S, "live_direction_ids", lambda now=None: {LIVE})
    return p


def _held(p):
    return json.loads(p.read_text()) if p.exists() else {}


def test_the_door_accepts_a_live_id_and_refuses_a_typo_without_writing(store):
    """Both branches, one control: a door that refuses everything passes a refusal-only test."""
    assert S.main(["--claim", LIVE + "-typo"]) == 1
    assert _held(store) == {}, "a refused claim must write nothing"
    assert S.main(["--claim", LIVE, "--note", "building it in /var/tmp/se-mover"]) == 0
    assert set(_held(store)) == {LIVE}
    assert S.main(["--claim", "no-row-work", "--any-id"]) == 0
    assert set(_held(store)) == {LIVE, "no-row-work"}


def test_what_the_door_writes_is_what_the_draw_treats_as_taken(store, tmp_path):
    S.main(["--claim", LIVE])
    taken = L.held_in_other_stores(tmp_path / "lane.json",
                                   stores=[(store, float(S.STALE_AFTER_SECONDS))])
    assert LIVE in taken


def test_release_says_whether_anything_was_held(store):
    S.main(["--claim", LIVE])
    assert S.main(["--release", LIVE]) == 0
    assert _held(store) == {}
    assert S.main(["--release", LIVE]) == 1
