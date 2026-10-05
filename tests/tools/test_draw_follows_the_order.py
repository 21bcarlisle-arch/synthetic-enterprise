"""The draw is graded against the director's order, not only against the dials. Defect it names:
on 2026-09-04 a re-ranking changed the weights and the work did not move, and nothing measured it."""

from tools import draw_follows_the_order as d

ORDER = {"since": "2026-10-05", "steps": {
    2: {"atoms": ["a2"]}, 3: {"atoms": ["a3"]}, 5: {"atoms": ["a5", "a5b"]}}}
ATOMS = {
    "a2": {"id": "a2", "level_current": 0, "level_target": 3, "loop_stage": "build"},
    "a3": {"id": "a3", "level_current": 0, "level_target": 3, "loop_stage": "build"},
    "a5": {"id": "a5", "level_current": 0, "level_target": 3, "loop_stage": "idle",
           "block_reason": "sequencing"},
    "a5b": {"id": "a5b", "level_current": 3, "level_target": 3, "loop_stage": "build"},
}


def test_both_kinds_of_violation_are_reachable_and_a_held_order_reads_clean():
    """The partition first, so a grader that never fires cannot pass: an inverted draw and an
    undrawable step are each named, and an order that holds has no violation at all.

    MUTATION (must fire): compare shares with `<` instead of `>`, or skip the drawable check."""
    steps = d.step_of(ORDER)
    held = d.live_shares([{"id": "a2"}, {"id": "a3"}], [3.0, 1.0], steps)
    inverted = d.live_shares([{"id": "a2"}, {"id": "a3"}], [1.0, 3.0], steps)

    assert d.violations(held, ORDER, ATOMS, {"a2", "a3", "a5"}) == []
    assert d.violations(inverted, ORDER, ATOMS, {"a2", "a3", "a5"}) == [
        "step 3 holds 75% of the draw, more than step 2's 25%"]
    [undrawable] = d.violations(held, ORDER, ATOMS, {"a2", "a3"})
    assert undrawable.startswith("step 5 has no drawable atom")
    assert "a5 is idle (sequencing)" in undrawable and "a5b is at target" in undrawable


def test_work_outside_every_step_is_counted_as_step_zero_not_dropped():
    shares = d.live_shares([{"id": "a2"}, {"id": "harness"}], [1.0, 1.0], d.step_of(ORDER))
    assert shares == {2: 0.5, 0: 0.5}


def test_the_weekly_step_carries_the_order_check(monkeypatch):
    """A check nothing runs is not a check. MUTATION (must fire): drop the section from Monday."""
    from datetime import date

    from background import weekly_rhythm

    monkeypatch.setattr(d, "render", lambda: "ORDER-CHECKED-HERE")
    body = weekly_rhythm._step_body(weekly_rhythm.MONDAY_STEP, date(2026, 10, 12), [])
    assert "## Does the work follow the priority order" in body and "ORDER-CHECKED-HERE" in body
