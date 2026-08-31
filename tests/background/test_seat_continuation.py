"""The interactive seat's next piece must reach a tick, and must not outlive the tree it read.

Director, 2026-08-31: the seat cannot self-advance (measured: `surgical_land` cannot commit from a
worktree, so an isolated seat has no sanctioned door), so the class of work moves into the ticks
instead. `background/seat_continuation.py` is the handoff; `delivery_lane.next_item` reads it ahead
of the periodic seat's focus list.

WHAT EACH LEG NAMES AS ITS OWN DEFECT:

* the handoff never reaches the draw — the continuation is written and the tick never sees it,
  which is the whole drag restated with more machinery;
* a STALE continuation is offered — reasoning about a tree that has moved, arriving with the
  authority of a decision and none of its context. C3's measurement was taken on 465 renewal
  decisions and a landing cut the book to 144: the numbers survived and described nothing;
* an INCOMPLETE handoff is stored — a tick handed a topic writes a confident restatement of it;
* the store breaking takes the DRAW down — `delivery_lane.draw` documents that a lane which can
  throw takes every other lane with it, so a handoff store must cost the seat its continuation and
  never the machine its tick;
* an expired item is swept SILENTLY — a continuation nobody took is the drag itself, and it has to
  be visible or this module hides the thing it was built to remove.
"""
from __future__ import annotations

import json

import pytest

from background import delivery_lane, seat_continuation


@pytest.fixture
def store(tmp_path):
    return tmp_path / "continuation.json"


def _hand(store, work_id="next-piece", *, now=1_000_000.0, **over):
    fields = {
        "what": "union the two departure routes in measure_departure_level",
        "why": "the band control is green on a pre-C1b artefact",
        "done_means": "both routes in one reading on a declared denominator",
    }
    fields.update(over)
    return seat_continuation.hand_off(work_id, now=now, path=store, **fields)


def test_a_written_continuation_REACHES_the_draw_ahead_of_the_periodic_focus_list(
    store, monkeypatch, tmp_path
):
    """The whole point: a tick takes the seat's next piece without the director in the loop.

    MUTATION: remove the `seat_continuation.live()` loop from `delivery_lane.next_item` and this
    fires — the continuation is written, fresh, unclaimed, and never offered.
    """
    _hand(store, "the-next-piece")
    monkeypatch.setattr(seat_continuation, "STORE", store)
    # A periodic focus list that would otherwise win, so "ahead of" is what is being tested.
    monkeypatch.setattr(
        delivery_lane.direction_mod, "unreachable_focus",
        lambda *a, **k: [{"id": "older-periodic-item", "what": "something else", "why": "..."}],
    )
    item = delivery_lane.next_item(now=1_000_100.0, path=tmp_path / "claims.json")
    assert item is not None, "the seat's continuation never reached the draw"
    assert item["id"] == "the-next-piece", (
        f"the draw offered {item['id']!r} — the periodic re-derivation beat the live continuation, "
        "which is backwards: a continuation is minutes old and written with the whole context, a "
        "focus item is up to three hours old and re-derived from the tree"
    )


def test_a_STALE_continuation_is_NOT_offered(store, monkeypatch, tmp_path):
    """Reasoning about a tree that has moved must stop competing with fresher judgement.

    MUTATION: drop the cutoff from `live()` and this fires.
    """
    _hand(store, "written-long-ago", now=1_000_000.0)
    monkeypatch.setattr(seat_continuation, "STORE", store)
    monkeypatch.setattr(delivery_lane.direction_mod, "unreachable_focus", lambda *a, **k: [])

    later = 1_000_000.0 + seat_continuation.STALE_AFTER_SECONDS + 1
    assert seat_continuation.live(now=later, path=store) == []
    assert delivery_lane.next_item(now=later, path=tmp_path / "claims.json") is None, (
        "a continuation past its window was still handed to a tick"
    )
    assert [i["id"] for i in seat_continuation.expired(now=later, path=store)] == ["written-long-ago"]


def test_an_expired_continuation_is_REPORTED_and_not_silently_dropped(store):
    """A piece the seat judged worth doing and nothing took IS the drag. It must stay visible.

    MUTATION: make `expired()` return `[]`, or have `live()` delete what it filters, and this
    fires — the store would then look tidy in exactly the case that means it is not working.
    """
    _hand(store, "nobody-took-it", now=1_000_000.0)
    later = 1_000_000.0 + seat_continuation.STALE_AFTER_SECONDS + 1
    assert seat_continuation.expired(now=later, path=store), (
        "an expired continuation vanished instead of being reported"
    )
    assert json.loads(store.read_text()), "the record was deleted rather than aged out"


def test_an_INCOMPLETE_handoff_is_REFUSED_and_names_what_is_missing(store):
    """A tick handed a topic writes a restatement of it.

    MUTATION: drop the `missing` check from `hand_off` and this fires.
    """
    for empty in ("what", "why", "done_means"):
        with pytest.raises(ValueError) as exc:
            _hand(store, "incomplete", **{empty: "   "})
        assert empty in str(exc.value), "the refusal must name which field is missing"
    assert not store.exists() or json.loads(store.read_text()) == [], (
        "a refused handoff was stored anyway"
    )


def test_re_recording_the_same_id_REPLACES_it_rather_than_competing(store):
    """A session that refines what it is handing over must not leave two versions in the queue.

    MUTATION: append without filtering and this fires.
    """
    _hand(store, "same-id", what="first draft")
    _hand(store, "same-id", what="refined", now=1_000_500.0)
    items = json.loads(store.read_text())
    assert len(items) == 1
    assert items[0]["what"] == "refined"
    assert items[0]["written_at"] == 1_000_500.0, "the clock was not restamped on replacement"


def test_a_BROKEN_store_costs_the_seat_its_handoff_and_never_the_machine_its_tick(
    store, monkeypatch, tmp_path
):
    """`delivery_lane.draw` documents that a lane which can throw takes every other lane down.

    MUTATION: let `_load` raise on malformed JSON, or remove the `try/except` around the
    continuation loop in `next_item`, and this fires.
    """
    store.write_text("{ this is not json")
    monkeypatch.setattr(seat_continuation, "STORE", store)
    assert seat_continuation.live(path=store) == []

    monkeypatch.setattr(
        delivery_lane.direction_mod, "unreachable_focus",
        lambda *a, **k: [{"id": "periodic", "what": "w", "why": "y"}],
    )
    item = delivery_lane.next_item(now=1_000_100.0, path=tmp_path / "claims.json")
    assert item is not None and item["id"] == "periodic", (
        "an unreadable continuation store stopped the draw reaching the periodic focus list — "
        "the handoff must degrade to nothing, never to a broken lane"
    )


def test_a_CLAIMED_continuation_is_not_handed_out_twice(store, monkeypatch, tmp_path):
    """Two ticks on one piece is the duplication this whole lane exists to avoid.

    MUTATION: stop consulting `taken` before offering a continuation and this fires.
    """
    _hand(store, "claimed-already")
    monkeypatch.setattr(seat_continuation, "STORE", store)
    monkeypatch.setattr(delivery_lane.direction_mod, "unreachable_focus", lambda *a, **k: [])
    claims = tmp_path / "claims.json"

    first = delivery_lane.next_item(now=1_000_100.0, path=claims)
    assert first["id"] == "claimed-already"
    delivery_lane.claims_mod.claim("claimed-already", paths=[], path=claims, now=1_000_100.0)

    assert delivery_lane.next_item(now=1_000_200.0, path=claims) is None, (
        "the same continuation was offered to a second tick while the first still held it"
    )
