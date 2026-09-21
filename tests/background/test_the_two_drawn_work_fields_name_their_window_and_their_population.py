"""The brief's two drawn-work readings are a different window AND a different population.

THE DEFECT, read off the live orientation of 2026-09-21. `build_brief` carried a key called
`focus_drawn_never_landed`, built from `_drawn_never_landed(now)`, which reads the claims ledger
over `delivery_lane.DRAWN_WITHOUT_LANDING_HORIZON_SECONDS` and returns EVERY Lane 0 item handed
out in that horizon -- nothing in the path filters it to the focus. Inches away sat
`previous_focus_drawn`, fed `focus_drawn_since(since)`: the previous focus alone, over the stretch.
Two windows, two populations, neither field stating which, and both read side by side by the one
reader they exist for. For four stretches they agreed only because the evidence happened not to
contain a contradiction. That stretch it finally did: the field NAMED for focus held exactly one
row, `name-the-35-remaining-bare-keyerror-refusals-on-raise-on-missing-registers`, an ordinary
draw that was never in focus at all, while `previous_focus_drawn` correctly reported all three
focus items drawn.

WHY A NAME IS A LOAD-BEARING CLAIM HERE. The reader of this brief is a bounded session that will
not open `delivery_lane.py`. `focus_` in the key was the only statement it had about the
population, and it was false; the absence of any window statement was read as "the stretch",
because every other key in the brief is.

THE PARTITION IS THE POINT, and it is why this is one control and not four. A brief that stated
ONE window twice, or named ONE population twice, passes every per-field assertion anyone would
write -- "the never-landed block says what it covers", "the steer verdict says what it covers" --
while the two fields remain indistinguishable, which is the entire defect. So both windows are
pulled out of ONE rendered prompt and required to exist, to be two, and to be the two the code
actually measured over.

MUTATIONS (each must fire):
  (a) rename the key back to `focus_drawn_never_landed` -- the naming and population legs go red;
  (b) drop the `MEASURED OVER` clause from either prompt block -- the window leg finds one, not
      two;
  (c) give both blocks the same window text -- the window leg finds two equal strings;
  (d) filter `_drawn_never_landed` to the focus (make the name true the wrong way round) -- the
      UNSTUBBED leg goes red. It is a separate test on purpose: the brief-level legs stub that
      function to get two known populations, and a stub is exactly the thing a filter inside the
      function hides behind. The first draft of this file claimed (d) and could not see it.
  (e) drop `window=` at the `focus_was_drawn` call site -- the steer verdict falls back to
      `AN UNSTATED WINDOW` and the stated-window leg goes red;
  (f) hand-type the horizon in the prompt instead of reading the constant -- the horizon leg goes
      red as soon as the constant moves, which is the only time it matters.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

from background import delivery_lane as dl
from background import delivery_seat as ds

#: An ordinary Lane 0 draw that was NEVER in focus. The whole finding is that this row is a legal
#: member of one field and structurally impossible in the other.
NEVER_IN_FOCUS = "an-ordinary-draw-that-was-never-in-focus"
#: ...and a focus item that WAS drawn, so the steer verdict is a pass while the block above still
#: has a row. The two readings disagreeing is the normal case, not the fault.
IN_FOCUS = "a-focus-item-the-draw-took"

#: Every `MEASURED OVER <what>` clause the prompt states, one per drawn-work block.
_WINDOW_CLAUSE = re.compile(r"MEASURED OVER (.*?)(?:\n|$)")


def _brief(monkeypatch, *, missed_rows):
    """A real `build_brief`, with only the two drawn-work feeders stubbed.

    Everything else -- the git reads, the map, the staging root -- runs for real, because a key
    wired to a fixture proves the fixture. The two feeders are stubbed because the point of the
    control is what the brief does with two DIFFERENT populations, and the live ledger is not
    obliged to contain one.
    """
    monkeypatch.setattr(ds, "_drawn_never_landed", lambda now: list(missed_rows))
    monkeypatch.setattr(ds, "focus_drawn_since", lambda since: [IN_FOCUS])
    monkeypatch.setattr(ds, "last_orientation", lambda: {"focus": [IN_FOCUS], "map_levels": {}})
    return ds.build_brief(datetime.now(timezone.utc))


def test_BOTH_drawn_work_fields_state_their_window_and_the_two_windows_are_DIFFERENT(monkeypatch):
    """One prompt, both blocks, one statement over the partition."""
    brief = _brief(monkeypatch, missed_rows=[
        {"id": NEVER_IN_FOCUS, "drawn_at": 0.0, "hours_since_draw": 5.0}])
    stated = _WINDOW_CLAUSE.findall(ds._prompt(brief))

    assert len(stated) == 2, (
        "the brief has two drawn-work readings and {} of them says what it was measured over -- "
        "an unstated window is read as the stretch, because every other key here is: {}".format(
            len(stated), stated))
    assert len(set(stated)) == 2, (
        "both drawn-work blocks state the SAME window, so the reader still cannot tell a day of "
        "the draw ledger from this stretch: {}".format(stated))

    ledger_window, = [s for s in stated if "DRAW LEDGER" in s]
    steer_window, = [s for s in stated if "DRAW LEDGER" not in s]
    assert "{}h".format(round(dl.DRAWN_WITHOUT_LANDING_HORIZON_SECONDS / 3600.0, 1)) \
        in ledger_window, (
        "the never-landed block states a horizon that is not the one it was measured over: "
        "{}".format(ledger_window))
    assert brief["previous_focus_drawn"]["window"] in steer_window, (
        "the steer verdict's prompt sentence and its own `window` key disagree: {!r} vs {!r}"
        .format(steer_window, brief["previous_focus_drawn"]["window"]))
    assert "UNSTATED" not in steer_window, (
        "the call site stopped passing `window=`, so the verdict reports its own window as "
        "unknown: {}".format(steer_window))


def test_AND_THE_EMPTY_BRANCH_states_the_same_window_rather_than_going_quiet(monkeypatch):
    """Silence is the branch that runs most often. A window stated only when there are rows is a
    window the reader never learns on the stretches that look fine."""
    brief = _brief(monkeypatch, missed_rows=[])
    stated = _WINDOW_CLAUSE.findall(ds._prompt(brief))

    assert len(stated) == 2 and len(set(stated)) == 2, stated
    assert "NO DRAWN LANE 0 ITEM" in ds._prompt(brief)


def test_THE_KEY_NAMES_THE_POPULATION_IT_HOLDS_and_the_two_populations_differ(monkeypatch):
    """The name is the only statement of population the reader gets, and it was false."""
    brief = _brief(monkeypatch, missed_rows=[
        {"id": NEVER_IN_FOCUS, "drawn_at": 0.0, "hours_since_draw": 5.0}])

    assert "focus_drawn_never_landed" not in brief, (
        "the key is named for the focus again and it still holds every Lane 0 draw in the horizon")
    assert not [k for k in brief if k.startswith("focus_") and "never_landed" in k], list(brief)

    populations = {
        "lane_0_drawn_never_landed": {r["id"] for r in brief["lane_0_drawn_never_landed"]},
        "previous_focus_drawn": set(brief["previous_focus_drawn"]["focus"]),
    }
    assert populations["lane_0_drawn_never_landed"] == {NEVER_IN_FOCUS}, (
        "the never-landed field dropped a drawn item that was never in focus, so it now IS a "
        "focus field and the bottleneck it exists to show is invisible again: {}".format(
            populations))
    assert populations["previous_focus_drawn"] == {IN_FOCUS}, populations
    assert not populations["lane_0_drawn_never_landed"] & populations["previous_focus_drawn"], (
        "the fixture no longer distinguishes the two populations, so neither leg above can fail")

    # ...and the disagreement the pair is allowed to have: the steer bit AND an item landed
    # nothing. Asserted so a future repair cannot make them agree by construction, which would
    # make the whole control unfalsifiable.
    assert brief["previous_focus_drawn"]["steered"] is True
    assert brief["lane_0_drawn_never_landed"], "both readings must be non-empty here"


def test_AND_THE_UNSTUBBED_READER_IS_NOT_FILTERED_BY_THE_FOCUS_EITHER(tmp_path, monkeypatch):
    """The leg the three above cannot carry, and the reason it is written separately.

    They stub `_drawn_never_landed` to hand the brief two known populations -- which is what makes
    them a control on the BRIEF, and exactly what makes them blind to a focus filter INSIDE the
    function they stubbed. A mutation that added one passed all three silently. So this leg drives
    the real reader against a real ledger, with a live focus that does not contain the drawn id:
    the name now says `lane_0`, and the value has to keep being every Lane 0 draw.

    MUTATION (must fire): filter `_drawn_never_landed`'s return to `direction.current_focus()`.
    """
    from background import direction as direction_mod
    from background import seat_work_in_hand as claims_mod

    now = datetime(2026, 9, 21, 12, 0, tzinfo=timezone.utc)
    drawn_at = now.timestamp() - 3 * 3600
    store = tmp_path / "claims.json"
    store.write_text("{}", encoding="utf-8")
    dl._ledger_path(store).write_text(
        '{{"{}": {{"first_drawn_at": {d}, "last_drawn_at": {d}}}}}'.format(
            NEVER_IN_FOCUS, d=drawn_at), encoding="utf-8")
    monkeypatch.setattr(claims_mod, "guard_live_ledger_write", lambda *a, **k: None)
    monkeypatch.setattr(dl, "CLAIMS_FILE", store)
    monkeypatch.setattr(direction_mod, "current_focus", lambda *a, **k: (IN_FOCUS,))

    got = [r["id"] for r in ds._drawn_never_landed(now)]

    assert got == [NEVER_IN_FOCUS], (
        "the never-landed reader dropped a Lane 0 item because it was not in the focus, so the "
        "key is a focus key again under a lane name -- and the bottleneck it exists to show, work "
        "drawn outside the steer and never landed, is invisible: {}".format(got))
