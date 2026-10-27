"""The BUILD draw follows the director's priority order, not only the dials.

DIRECTOR_CANON_THE_PRIORITY_ORDER_2026-10-05: "Verify the draw follows this order, not just the
dials. On 4 September a re-ranking changed the weights and the work did not move." And: "In-flight
work finishes first." The defect these name: at equal dials, a step-6 or step-7 atom is drawn as
often as a step-2 one, because the dial-weighted coin cannot see the order.
"""

from __future__ import annotations

import json
import random
import time

import pytest

from background import supervisor

_ORDER = """\
steps:
  2: {name: billing, atoms: [S2_billing]}
  6: {name: forward simulation, atoms: [S6_forward]}
  7: {name: nps, atoms: [S7_nps]}
"""


def _atom(aid: str, dial: int = 50) -> str:
    # One shared file_scope, so the draw grants only the primary and the test reads it alone.
    return (f"- id: {aid}\n  lane: X\n  dial_inherited: {dial}\n  level_current: 0\n"
            f"  level_target: 2\n  loop_stage: build\n  file_scope: [shared.py]\n")


@pytest.fixture
def world(tmp_path, monkeypatch):
    monkeypatch.setattr(supervisor, "MATURITY_MAP_PATH", tmp_path / "maturity_map.yaml")
    monkeypatch.setattr(supervisor, "ATOM_STALL_STATE_FILE", tmp_path / ".atom_stall_tracker.json")
    monkeypatch.setattr(supervisor, "BUILD_IN_PROGRESS_FILE", tmp_path / ".build_in_progress.json")
    monkeypatch.setattr(supervisor, "PRIORITY_ORDER_PATH", tmp_path / "priority_order.yaml")
    # The draw's OTHER guards read the live tree (gap ledger, pass ceiling, git worktrees, the
    # seat's direction record). They are not the subject, so they pass the set through untouched.
    monkeypatch.setattr(supervisor, "_coupled_load_gap_ledger", lambda: {})
    monkeypatch.setattr(supervisor, "_coupled_world_l3_blocked", lambda a, atoms, g: (False, ""))
    monkeypatch.setattr(supervisor, "_exclude_saturated_from_core_draw", lambda c: c)
    monkeypatch.setattr(supervisor, "_prefer_unmerged_free", lambda c, lane="BUILD": c)
    monkeypatch.setattr(supervisor._direction, "focus_weights", lambda c, w: w)
    (tmp_path / "priority_order.yaml").write_text(_ORDER)
    return tmp_path


def _primaries(atoms_yaml: str, seeds: int = 200) -> set[str]:
    supervisor.MATURITY_MAP_PATH.write_text(atoms_yaml)
    return {supervisor._maturity_map_draw_concurrent(rng=random.Random(s))[0]["id"]
            for s in range(seeds)}


def test_at_equal_dials_a_step_2_atom_outranks_step_6_and_step_7(world):
    assert _primaries(_atom("S6_forward") + _atom("S2_billing") + _atom("S7_nps")) == {"S2_billing"}


def test_the_order_can_be_left_and_in_flight_work_is_not_pre_empted(world):
    """The partition in one control: the order bites, it falls away when no ordered atom is a
    candidate, and an atom already under way keeps its turn beside the earlier step."""
    three = _atom("S6_forward") + _atom("S2_billing") + _atom("S7_nps")
    ordered = _primaries(three)
    unordered = _primaries(_atom("U1_unmapped") + _atom("U2_unmapped"))
    supervisor.ATOM_STALL_STATE_FILE.write_text(json.dumps({"S6_forward": {
        "last_drawn_at": time.time() - 60, "stalled": False, "consecutive_unchanged": 0}}))
    in_flight = _primaries(three)
    assert ordered == {"S2_billing"}
    assert unordered == {"U1_unmapped", "U2_unmapped"}
    assert in_flight == {"S2_billing", "S6_forward"}


def test_a_stalled_atom_is_not_in_flight(world):
    supervisor.ATOM_STALL_STATE_FILE.write_text(json.dumps({"S6_forward": {
        "last_drawn_at": time.time() - 60, "stalled": True, "consecutive_unchanged": 5}}))
    assert _primaries(_atom("S6_forward") + _atom("S2_billing")) == {"S2_billing"}


def test_within_a_step_the_dials_still_choose(world):
    (world / "priority_order.yaml").write_text(
        "steps:\n  2: {atoms: [S2_heavy, S2_light]}\n  6: {atoms: [S6_forward]}\n")
    supervisor.MATURITY_MAP_PATH.write_text(
        _atom("S2_heavy", 90) + _atom("S2_light", 10) + _atom("S6_forward", 100))
    drawn = [supervisor._maturity_map_draw_concurrent(rng=random.Random(s))[0]["id"]
             for s in range(400)]
    assert set(drawn) == {"S2_heavy", "S2_light"}
    assert drawn.count("S2_heavy") > 3 * drawn.count("S2_light")


def test_a_missing_order_leaves_the_dials_alone(world):
    (world / "priority_order.yaml").unlink()
    assert _primaries(_atom("S6_forward") + _atom("S2_billing")) == {"S2_billing", "S6_forward"}


# THE CORRECTNESS STRETCH (director, 2026-10-26 18:30, "Ok do it"): "No new feature work is drawn
# until the steps below are done ... Work already landing may finish."

_STRETCH = ("correctness_stretch: {ruling: THE_RULING.md, ahead_of_steps: [6, 7]%s}\n" + _ORDER)


def _disjoint(aid: str) -> str:
    return _atom(aid).replace("[shared.py]", f"[{aid}.py]")


def test_a_held_step_atom_is_refused_and_drawable_once_the_exit_is_recorded(world):
    """The partition in one control: refused with the stretch present (as primary AND as a
    concurrent pick), drawn once `exit_met` is recorded, and an in-flight one keeps its turn.

    MUTATION (must fire): skip `correctness_stretch_refusals` in the draw -> S6 is a concurrent
    pick.
    MUTATION (must fire): ignore `exit_met` -> S6 is never drawable again."""
    order = world / "priority_order.yaml"
    supervisor.MATURITY_MAP_PATH.write_text(_disjoint("S6_forward") + _disjoint("S2_billing"))

    order.write_text(_STRETCH % "")
    held = {a["id"] for s in range(50)
            for a in supervisor._maturity_map_draw_concurrent(rng=random.Random(s))}
    supervisor.MATURITY_MAP_PATH.write_text(_atom("S6_forward"))
    alone = supervisor._maturity_map_draw_concurrent(rng=random.Random(0))

    order.write_text(_STRETCH % ", exit_met: READING.md")
    lifted = _primaries(_atom("S6_forward"))

    order.write_text(_STRETCH % "")
    supervisor.ATOM_STALL_STATE_FILE.write_text(json.dumps({"S6_forward": {
        "last_drawn_at": time.time() - 60, "stalled": False, "consecutive_unchanged": 0}}))
    in_flight = _primaries(_atom("S6_forward"))

    assert held == {"S2_billing"}
    assert alone == []
    assert lifted == {"S6_forward"}
    assert in_flight == {"S6_forward"}


def test_the_refusal_names_the_ruling(world):
    (world / "priority_order.yaml").write_text(_STRETCH % "")
    why = supervisor.correctness_stretch_refusals()
    assert set(why) == {"S6_forward", "S7_nps"}
    assert "THE_RULING.md" in why["S6_forward"] and "step 6" in why["S6_forward"]


def test_the_live_stretch_is_read_as_written():
    """Keyed to the property, not today's answer: while the live file carries a stretch, the
    reader either refuses its held steps' atoms or sees its exit recorded -- never a silent
    fail-open on a shape it cannot parse."""
    import yaml
    live = yaml.safe_load(supervisor.PRIORITY_ORDER_PATH.read_text(encoding="utf-8")) or {}
    stretch = live.get("correctness_stretch")
    if not stretch:
        pytest.skip("no correctness stretch in the live priority order")
    steps = set(stretch.get("ahead_of_steps") or [])
    held = {aid for k, v in (live.get("steps") or {}).items() if int(k) in steps
            for aid in (v or {}).get("atoms") or []}
    assert stretch.get("exit_met") or set(supervisor.correctness_stretch_refusals()) == held
