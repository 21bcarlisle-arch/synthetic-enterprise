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
import time

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


# ── AN EXPIRY AFTER A DRAW IS THE MECHANISM WORKING (2026-08-31) ─────────────────────────────────
# The seat executor's first unattended turn took `union-the-departure-routes-and-declare-the-
# denominator`, did it, and landed b8e6ba32d on origin. Hours later `--list` printed that id under
# "written and never taken; that is the drag, visible". The one surface built to say whether the
# handoff works was reporting its only success as its defining failure.
#
# `delivery_lane.DRAW_LEDGER_FILE` had recorded `first_drawn_at` for that id the whole time. This is
# not new information; it is a join nobody had made.

def test_an_expiry_after_a_draw_is_reported_as_done(tmp_path, monkeypatch):
    """MUTATION: drop the `drawn_at` join from `expired()` and this fires."""
    import json as _json

    from background import delivery_lane
    from background import seat_continuation as sc

    store = tmp_path / "continuations.json"
    ledger = tmp_path / "draws.json"
    monkeypatch.setattr(sc, "STORE", store)
    monkeypatch.setattr(delivery_lane, "DRAW_LEDGER_FILE", ledger)

    old = time.time() - sc.STALE_AFTER_SECONDS - 60
    sc.hand_off("taken-and-done", what="w", why="y", done_means="d", now=old)
    sc.hand_off("nobody-came", what="w", why="y", done_means="d", now=old)
    ledger.write_text(_json.dumps({"taken-and-done": {"first_drawn_at": old + 300,
                                                      "last_drawn_at": old + 300}}))

    by_id = {i["id"]: i for i in sc.expired()}
    assert by_id["taken-and-done"]["drawn_at"], "a drawn handoff must not read as never taken"
    assert by_id["nobody-came"]["drawn_at"] is None, (
        "an undrawn handoff must still report the drag -- that is the whole point of the surface"
    )


def test_an_unreadable_draw_ledger_reports_the_drag_rather_than_hiding_it(tmp_path, monkeypatch):
    """FAIL TOWARD THE UNCOMFORTABLE ANSWER. If the ledger cannot be read, the honest report is
    'nothing took this', not 'something probably did' -- the second would let a broken ledger
    quietly certify a mechanism that had stopped working."""
    from background import delivery_lane
    from background import seat_continuation as sc

    monkeypatch.setattr(sc, "STORE", tmp_path / "continuations.json")
    monkeypatch.setattr(delivery_lane, "DRAW_LEDGER_FILE", tmp_path / "does-not-exist.json")

    old = time.time() - sc.STALE_AFTER_SECONDS - 60
    sc.hand_off("cannot-tell", what="w", why="y", done_means="d", now=old)
    assert sc.expired()[0]["drawn_at"] is None


def test_the_live_list_is_untouched_by_the_join(tmp_path, monkeypatch):
    """Blast radius: `live()` answers a different question and must not grow a draw column.

    A continuation inside its window is offerable whether or not a tick has already looked at it;
    folding draw state into `live()` would stop re-offering work a tick started and abandoned.
    """
    from background import seat_continuation as sc

    monkeypatch.setattr(sc, "STORE", tmp_path / "continuations.json")
    sc.hand_off("fresh", what="w", why="y", done_means="d")
    assert [i["id"] for i in sc.live()] == ["fresh"]
    assert "drawn_at" not in sc.live()[0]


# ── A REFINEMENT UNDER A NEW ID LEFT THE REFUTED VERSION WINNING (2026-09-03) ────────────────────
# `hand_off` promised that a session refining its handoff "does not leave two versions competing".
# The guard is keyed to the ID STRING, so it only fires when the refinement reuses the id.
#
# On 2026-09-03 the seat wrote `land-the-live-world-undecomposed-floor-leg` ("the file already
# exists at <path>, the only thing standing between this and done is a git add"). Its artefact was
# then deleted by `ensure_worktree`'s `git clean -qfd` and the measurement relaunched, so the seat
# wrote the correction as a NEW id, `pick-up-the-relaunched-undecomposed-floor-leg`. Both stayed
# live, `live()` returns oldest first, and the 16:23 tick was handed the REFUTED one --
# deterministically, not by luck. It spent its orientation proving the cited file did not exist.
#
# So supersession is DECLARED. Nothing infers subject overlap: an inferred supersession would bury
# a live instruction, which is worse than the defect it fixes.

def test_a_refinement_under_a_NEW_id_RETIRES_the_refuted_one_rather_than_LOSING_to_it(
    store, monkeypatch, tmp_path
):
    """The refuted entry must not be offered, and oldest-first means it does not merely tie.

    MUTATION: drop the `_superseded_ids` filter from `live()` and this fires — the refuted entry
    comes back and, being older, is returned FIRST and drawn by the tick.
    """
    _hand(store, "land-the-artefact", what="the file already exists; just git add it")
    _hand(store, "pick-up-the-relaunch", what="the artefact was deleted; the re-run is in flight",
          now=1_000_500.0, supersedes=["land-the-artefact"])

    ids = [i["id"] for i in seat_continuation.live(now=1_000_600.0, path=store)]
    assert "land-the-artefact" not in ids, (
        "the refuted instruction is still offerable; a tick will be told to git add a file that "
        "no longer exists"
    )
    assert ids == ["pick-up-the-relaunch"]

    # And the draw itself, because `live()` being right is not the property that matters.
    monkeypatch.setattr(seat_continuation, "STORE", store)
    monkeypatch.setattr(delivery_lane.direction_mod, "unreachable_focus", lambda *a, **k: [])
    item = delivery_lane.next_item(now=1_000_600.0, path=tmp_path / "claims.json")
    assert item is not None and item["id"] == "pick-up-the-relaunch", (
        f"the tick was handed {item and item['id']!r} — the correction must reach the draw, not "
        "the instruction it corrected"
    )


def test_a_RETIRED_entry_is_REPORTED_and_not_silently_filtered(store):
    """A record dropped from every surface is indistinguishable from a lost write.

    A superseded entry inside its window is in neither `live()` nor `expired()`. If it printed
    nowhere, this module would hide a retirement exactly as it once hid a success.

    MUTATION: make `superseded()` return `[]`, or drop its loop in `main()`, and this fires.
    """
    _hand(store, "refuted")
    _hand(store, "correction", now=1_000_500.0, supersedes=["refuted"])

    assert [i["id"] for i in seat_continuation.live(now=1_000_600.0, path=store)] == ["correction"]
    assert [i["id"] for i in seat_continuation.expired(now=1_000_600.0, path=store)] == []

    retired = seat_continuation.superseded(path=store)
    assert [i["id"] for i in retired] == ["refuted"], (
        "a retired continuation appears on no surface at all — a supersession now reads exactly "
        "like the store having lost a write"
    )
    assert retired[0]["superseded_by"] == ["correction"], (
        "the retirement does not name what retired it, so a reader cannot check the judgement"
    )


def test_an_EXPIRED_correction_does_not_RESURRECT_the_instruction_it_retired(store):
    """Supersession is a fact about the SUBJECT, not about the clock.

    The realistic path: `seat_executor` promotes focus items to continuations automatically, so a
    retired id can be RE-STAMPED fresh by a derivation that never knew it was refuted. If the
    retirement were keyed to the correction still being live, the refuted instruction would return
    the moment its correction aged out — and it would return as the OLDEST live entry, i.e. first.

    MUTATION: filter `_superseded_ids` to entries inside the window and this fires.
    """
    _hand(store, "correction", now=1_000_000.0, supersedes=["refuted"])
    # The auto-promoter re-derives the refuted item from the tree and stamps it fresh, hours later.
    _hand(store, "refuted", now=1_000_000.0 + 7 * 3600)
    now = 1_000_000.0 + 7 * 3600 + 60

    assert seat_continuation.live(now=now, path=store) == [], (
        "a refuted instruction came back to life because its correction aged out — the retirement "
        "must outlive the entry that recorded it"
    )
    assert [i["id"] for i in seat_continuation.expired(now=now, path=store)] == ["correction"], (
        "the correction should age out as an ordinary continuation; only the RETIRED entry is "
        "excluded from the drag report"
    )


def test_an_entry_naming_ITSELF_is_still_offered(store):
    """A self-reference must be ignored, not honoured.

    Otherwise a single mistyped id erases the seat's own judgement and `superseded()` reports the
    entry as retired by itself, which explains nothing to the reader.

    MUTATION: remove the `dead != item.get("id")` guard from `_superseded_ids` and this fires.
    """
    _hand(store, "only-item", supersedes=["only-item"])
    assert [i["id"] for i in seat_continuation.live(now=1_000_100.0, path=store)] == ["only-item"], (
        "an entry naming its own id deleted itself from the queue"
    )
    assert seat_continuation.superseded(path=store) == []


def test_a_handoff_with_no_supersedes_stores_NO_such_key(store):
    """Blast radius: the store is read by `delivery_lane` and printed to the director.

    MUTATION: always write `supersedes` and this fires — every historical entry grows an empty
    field and the diff on a live observability ledger stops being readable.
    """
    item = _hand(store, "plain")
    assert "supersedes" not in item
    assert "supersedes" not in json.loads(store.read_text())[0]
