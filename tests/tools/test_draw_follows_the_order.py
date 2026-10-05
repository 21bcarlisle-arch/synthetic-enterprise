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


def test_the_supervisors_own_log_lines_never_reach_this_tools_output(monkeypatch, capsys):
    """`--json` is read by machines; one stray gate line ahead of it made the first live run
    unparseable. MUTATION (must fire): drop the stdout redirect around the supervisor call."""
    import sys
    import types

    def _draw(rng=None, exclude_stalled=False):
        print("- [gate] COUPLED_TRIAD gate: excluding X from BUILD draw")
        rng.choices([{"id": "a2"}], weights=[1.0], k=1)
        return []

    import background

    fake = types.SimpleNamespace(_maturity_map_draw_concurrent=_draw)
    # BOTH HOMES OF THE NAME: `from background import supervisor` reads the package attribute
    # when an earlier test already imported it, and sys.modules only otherwise. Patching one
    # made this test order-dependent (green alone, red in the gate's run).
    monkeypatch.setitem(sys.modules, "background.supervisor", fake)
    monkeypatch.setattr(background, "supervisor", fake, raising=False)
    cands, pool, weights = d.live_draw()
    assert [c["id"] for c in cands] == [c["id"] for c in pool] == ["a2"] and weights == [1.0]
    assert capsys.readouterr().out == ""


def test_a_whole_tree_in_a_file_scope_cannot_claim_a_commit_for_a_step():
    """C30 listed `tests` and `simulation`, so every test commit counted as step-5 work.
    MUTATION (must fire): return True from `names_a_subject`."""
    assert d.names_a_subject("tools/draw_follows_the_order.py")
    assert not d.names_a_subject("tests")
