"""An item was drawn, the work was FINISHED, and it never left the working tree.

THE DEFECT, measured on the live draw ledger 2026-09-07. Two Lane 0 items were handed out --
`the-lane-0-chain-counter-reads-1-across-four-consecutive-continuation-draws` at 04:11 and
`six-dd-level-collection-controls-are-red-at-head-and-are-still-red-at-this-orientation` at 04:41
-- and both were done: correct, tested, and sitting uncommitted in the shared tree while four
orientations came and went. `record_draw` had written each of them a `first_drawn_at` and
`_remember_landing` never wrote either a `last_landing_at`, so the ledger held the entire finding
hours before anybody noticed and NOTHING READ IT. `sweep_stale` did its job and returned both
claims to the pool, silently, which is the only thing that happens to a window that closes empty.

WHY NO OTHER SURFACE COULD HAVE SAID IT. `commits` cannot show work that was never committed.
`atoms_drawn` / `drawn_since` say the item WAS handed out, which reads as the lane working.
`focus_was_drawn` grades whether the steer bit, and it did -- the steer reached three items that
stretch and delivered one. Every reading available to the orientation was consistent with a
healthy lane, because the bottleneck had moved from "never drawn" to "drawn and never landed" and
no key in the brief was keyed to the second one.

MUTATIONS (each must fire, and which test catches it):
  (a) drop the `stamp - drawn < CLAIM_STALE_SECONDS` clause (report items still inside their
      window) -- `..._AN_ITEM_STILL_INSIDE_ITS_WINDOW_IS_NOT_MISSED` goes red;
  (b) key the landing test to `last_landing_at` being NULL rather than to the draw --
      `..._A_LANDING_THAT_PREDATES_THE_REDRAW_IS_NOT_A_LANDING` goes red;
  (c) drop the horizon (report the whole 400-row ledger) -- `..._THE_HORIZON_IS_A_DAY` goes red;
  (d) report every row regardless (never break) -- the partition control goes red on its landed
      and in-window legs;
  (e) delete the `is_material` clause -- `..._A_MISSED_LANDING_IS_MATERIAL` goes red;
  (f) move the prompt's sentence below `json.dumps(brief)[:60_000]` -- `..._SURVIVES_THE_PROMPT_
      TRUNCATION` goes red;
  (g) revert `build_brief` to not carry the key at all -- `..._THE_BRIEF_CARRIES_IT` goes red.

THE PARTITION CONTROL IS FIRST, AND IT IS ONE STATEMENT OVER THREE OUTCOMES. A reader that
reported NOTHING would pass "the landed one is absent" and "the in-window one is absent" -- two
thirds of the obvious suite -- while the mechanism was dead. So the three legs are asserted
together against one ledger, which is the shape this project keeps having to relearn.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone

from background import delivery_lane as dl
from background import delivery_seat as ds

#: 2026-09-07 04:11:26 and 04:41:27 Europe/London -- the two real draws, read from
#: `docs/observability/.delivery_lane_claims.draws.json` as it stood that morning.
CHAIN_COUNTER_DRAWN_AT = 1788750686.9329503
DD_CONTROLS_DRAWN_AT = 1788752487.427198
#: 2026-09-07 06:00:00 Europe/London. Chosen because it falls BETWEEN the two windows closing
#: (05:51 and 06:21), which is what makes the leg below a discriminator rather than a count.
SIX_AM = 1788757200.0


def _ledger(tmp_path, rows: dict):
    store = tmp_path / "claims.json"
    store.write_text("{}", encoding="utf-8")
    dl._ledger_path(store).write_text(json.dumps(rows), encoding="utf-8")
    return store


def test_THE_PARTITION_a_closed_empty_window_is_reported_and_a_landed_or_live_one_is_not(tmp_path):
    """One ledger, three outcomes, one assertion: the reader must SEPARATE them.

    A mechanism that returned everything, or nothing, satisfies two of the three legs on its own.
    """
    now = 1_000_000.0
    store = _ledger(tmp_path, {
        "landed-inside-its-window": {
            "first_drawn_at": now - 3 * 3600, "last_drawn_at": now - 3 * 3600,
            "last_landing_at": now - 2 * 3600, "last_landing_paths": ["a.py"]},
        "still-inside-its-window": {
            "first_drawn_at": now - 600, "last_drawn_at": now - 600},
        "window-closed-with-nothing-landed": {
            "first_drawn_at": now - 3 * 3600, "last_drawn_at": now - 3 * 3600},
    })
    got = [r["id"] for r in dl.drawn_without_landing(now=now, path=store)]
    assert got == ["window-closed-with-nothing-landed"], got


def test_AN_ITEM_STILL_INSIDE_ITS_WINDOW_IS_NOT_MISSED_it_is_being_worked(tmp_path):
    """The clock, not the emptiness, is what makes it a miss.

    Asserted as a MOVE across the boundary rather than as an absence, so a reader that reports
    nothing at all cannot pass it: the same row is silent one second before `CLAIM_STALE_SECONDS`
    and reported one second after.
    """
    drawn = 1_000_000.0
    store = _ledger(tmp_path, {"one": {"first_drawn_at": drawn, "last_drawn_at": drawn}})
    just_inside = drawn + dl.CLAIM_STALE_SECONDS - 1
    assert dl.drawn_without_landing(now=just_inside, path=store) == []
    just_outside = drawn + dl.CLAIM_STALE_SECONDS + 1
    assert [r["id"] for r in dl.drawn_without_landing(now=just_outside, path=store)] == ["one"]


def test_A_LANDING_THAT_PREDATES_THE_REDRAW_IS_NOT_A_LANDING_for_the_second_window(tmp_path):
    """`last_landing_at` populated says nothing about the LAST draw.

    An id drawn, landed, and drawn again carries a landing instant that a null test reads as
    healthy -- and the second window is exactly as empty as a first one would have been. Both
    orders are asserted from one ledger so the test cannot pass by reporting every row.
    """
    now = 1_000_000.0
    store = _ledger(tmp_path, {
        "redrawn-after-landing": {
            "first_drawn_at": now - 10 * 3600, "last_drawn_at": now - 3 * 3600,
            "last_landing_at": now - 5 * 3600, "last_landing_paths": ["a.py"]},
        "landed-after-its-last-draw": {
            "first_drawn_at": now - 10 * 3600, "last_drawn_at": now - 5 * 3600,
            "last_landing_at": now - 3 * 3600, "last_landing_paths": ["b.py"]},
    })
    got = [r["id"] for r in dl.drawn_without_landing(now=now, path=store)]
    assert got == ["redrawn-after-landing"], got


def test_THE_HORIZON_IS_A_DAY_so_the_surface_does_not_open_with_the_whole_ledger(tmp_path):
    """Bounded, and the bound is stated where it can be read.

    The ledger remembers 400 draws over several weeks. A reader with no horizon opens with dozens
    of ancient never-landed ids, which is a surface the orientation learns to skip -- the failure
    mode this leg exists to avoid, and indistinguishable from a working one by a green suite.
    """
    now = 1_000_000.0
    horizon = dl.DRAWN_WITHOUT_LANDING_HORIZON_SECONDS
    store = _ledger(tmp_path, {
        "inside-the-horizon": {"first_drawn_at": now - horizon + 3600,
                               "last_drawn_at": now - horizon + 3600},
        "older-than-the-horizon": {"first_drawn_at": now - horizon - 3600,
                                   "last_drawn_at": now - horizon - 3600},
    })
    got = [r["id"] for r in dl.drawn_without_landing(now=now, path=store)]
    assert got == ["inside-the-horizon"], got
    assert horizon > 3 * 3600, "a stretch-length horizon would drop the fact by the next orientation"


def test_THE_2026_09_07_LEDGER_would_have_named_the_chain_counter_at_the_next_orientation(tmp_path):
    """The real instants, replayed: this is what nothing was reading.

    Keyed to the two RECORDED draws rather than to today's ledger, so it still means something
    once those rows are evicted. At 06:00 the 04:11 window had closed and the 04:41 one had not,
    which is also the second, independent witness that the clock leg is reached.
    """
    store = _ledger(tmp_path, {
        "the-lane-0-chain-counter-reads-1-across-four-consecutive-continuation-draws": {
            "first_drawn_at": CHAIN_COUNTER_DRAWN_AT, "last_drawn_at": CHAIN_COUNTER_DRAWN_AT},
        "six-dd-level-collection-controls-are-red-at-head-and-are-still-red-at-this-orientation": {
            "first_drawn_at": DD_CONTROLS_DRAWN_AT, "last_drawn_at": DD_CONTROLS_DRAWN_AT},
    })
    got = [r["id"] for r in dl.drawn_without_landing(now=SIX_AM, path=store)]
    assert got == [
        "the-lane-0-chain-counter-reads-1-across-four-consecutive-continuation-draws"], got
    # ...and both, once the second window has closed too.
    both = [r["id"] for r in dl.drawn_without_landing(now=SIX_AM + 3600, path=store)]
    assert len(both) == 2, both


def test_AN_UNREADABLE_LEDGER_reads_as_nothing_missed_and_never_raises(tmp_path):
    """The fail-open direction, and it is deliberate: this feeds a brief with twenty other keys."""
    store = tmp_path / "claims.json"
    store.write_text("{}", encoding="utf-8")
    dl._ledger_path(store).write_text("{ this is not json", encoding="utf-8")
    assert dl.drawn_without_landing(now=1_000_000.0, path=store) == []


# ---- the orientation legs: the fact has to REACH the seat, not just exist -----

def test_A_MISSED_LANDING_IS_MATERIAL_and_the_reason_names_the_item():
    """Whole partition again: a stretch with the same brief and an EMPTY list must be immaterial,
    or the clause is satisfied by `is_material` returning True for everything."""
    quiet = {
        "substantive_count": 0, "shape": {}, "divergence": {},
        "levels_recorded": {}, "levels_moved": {}, "director_inputs": [],
        "findings": {"blocking": []}, "live_direction_age_hours": 1.0,
        "focus_drawn_never_landed": [],
    }
    material, why = ds.is_material(quiet)
    assert material is False, why

    missed = dict(quiet, focus_drawn_never_landed=[
        {"id": "the-lane-0-chain-counter-reads-1-across-four-consecutive-continuation-draws",
         "drawn_at": CHAIN_COUNTER_DRAWN_AT, "hours_since_draw": 1.8}])
    material, why = ds.is_material(missed)
    assert material is True
    assert "the-lane-0-chain-counter" in why, why


def test_IT_SURVIVES_THE_PROMPT_TRUNCATION_because_the_json_is_capped_at_60k():
    """The brief is dumped `[:60_000]`. A fact that only lives inside that cap is a fact a long
    stretch deletes, which is why three other inputs already sit above it."""
    rows = [{"id": "drawn-and-never-landed-{}".format(i), "drawn_at": 0.0,
             "hours_since_draw": 5.0} for i in range(2)]
    brief = {"focus_drawn_never_landed": rows, "previous_wrong": [],
             "divergence": {"says": "measured"}, "shape": {"rendered": "x", "available": True},
             # big enough that anything below the dump is cut
             "commits": [{"subject": "x" * 200} for _ in range(500)]}
    text = ds._prompt(brief)
    head = text[:text.index(json.dumps(brief, indent=1)[:200])]
    assert "drawn-and-never-landed-0" in head, "the ids must be ABOVE the truncated json"
    assert "git status" in head, "the seat must be told the work may already be on disk"

    empty = ds._prompt(dict(brief, focus_drawn_never_landed=[]))
    assert "NO DRAWN LANE 0 ITEM" in empty, "silence must be stated, not inferred from an absence"


def test_THE_BRIEF_CARRIES_IT_and_early_enough_that_the_cap_cannot_reach_it():
    """Read from the real store, so a key wired to nothing cannot pass."""
    brief = ds.build_brief(datetime.now(timezone.utc))
    assert "focus_drawn_never_landed" in brief
    assert isinstance(brief["focus_drawn_never_landed"], list)
    keys = list(brief)
    assert keys.index("focus_drawn_never_landed") < keys.index("commits"), keys
