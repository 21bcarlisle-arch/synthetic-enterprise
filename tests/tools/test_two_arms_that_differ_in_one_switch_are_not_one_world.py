"""Two arm artefacts that differ in one `SE_*` switch are not one world, and do not pair.

Fires on: a switch dropped from the stamp, the pairing rule ignoring the switches, or either
caller (`decompose_floor`, the page's `_seed_spreads`) not asking it.

1002b and 1002c shared departure digest `cf823b185f8ca51c` and ran different worlds through
`SE_SERVED_SEGMENTS`. The digest was the only thing any pairing asked.

R15 -- the mutations, each run and reverted (2026-10-04):
  * drop `SE_SERVED_SEGMENTS` from `behaviour_switches`' name set -> the closure leg reds.
  * compare only the switch NAMES in `world_stamps_pair`, not their values -> the partition reds
    on the one-switch pair.
  * remove the switch leg from `decompose_floor` / `_seed_spreads` -> the caller legs red.
"""
from __future__ import annotations

import tools.generate_value_arms_data as gva
import tools.run_value_cycle_ab as ab

_DIGEST = "cf823b185f8ca51c"


def _stamp(**switches):
    values = {"SE_DEBT_OBJECTION": None, "SE_SERVED_SEGMENTS": None}
    values.update(switches)
    return {"digest": _DIGEST, "unavailable_because": None,
            "behaviour_switches": {"values": values, "digest": None, "unavailable_because": None}}


def test_the_stamp_names_the_switches_the_run_reads_from_its_import_closure():
    block = ab.behaviour_switches()
    assert block["unavailable_because"] is None, block
    for name in ("SE_SERVED_SEGMENTS", "SE_DEBT_OBJECTION"):
        assert name in block["values"], "the stamp does not name {}".format(name)
    stamped = ab.world_identity()
    assert stamped["behaviour_switches"]["values"] == block["values"]
    assert stamped["code_commit"] == ab.PRODUCING_COMMIT


def test_the_value_recorded_is_this_process_environment_and_unset_is_none():
    closure = {"tools/run_value_cycle_ab.py"}
    on = ab.behaviour_switches(closure, environ={"SE_SERVED_SEGMENTS": "renewal"})
    off = ab.behaviour_switches(closure, environ={})
    assert on["values"]["SE_SERVED_SEGMENTS"] == "renewal"
    assert off["values"]["SE_SERVED_SEGMENTS"] is None
    assert on["digest"] != off["digest"]


def test_one_switch_refuses_the_pair_and_identical_stamps_pair():
    same = ab.world_stamps_pair(_stamp(SE_SERVED_SEGMENTS="a"), _stamp(SE_SERVED_SEGMENTS="a"))
    one = ab.world_stamps_pair(_stamp(SE_SERVED_SEGMENTS="a"), _stamp(SE_SERVED_SEGMENTS="b"))
    one_sided = ab.world_stamps_pair(_stamp(), {"digest": _DIGEST})
    legacy = ab.world_stamps_pair({"digest": _DIGEST}, {"digest": _DIGEST})
    # The rule can both admit and refuse, over the whole partition.
    assert same is None and legacy is None
    assert one and "SE_SERVED_SEGMENTS" in one, one
    assert one_sided, "a stamped run paired with an unstamped one"
    unread = ab.world_stamps_pair(_stamp(), {"digest": _DIGEST, "behaviour_switches": {
        "values": {"SE_SERVED_SEGMENTS": None}}})
    assert unread and "SE_DEBT_OBJECTION" in unread, "a switch one side never read was a match"


def _leg(mode, values, stamp):
    return {"redraw_scope": {"mode": mode}, "world_identity": stamp,
            "seeds": [{"seed": s, "selection_gbp": v}
                      for s, v in zip((11111, 22222, 33333), values)]}


def test_decompose_floor_refuses_legs_one_switch_apart():
    def run(except_stamp):
        return ab.decompose_floor(
            _leg("all", [1.0, 5.0, 9.0], _stamp(SE_SERVED_SEGMENTS="a")),
            _leg("only", [1.0, 3.0, 6.0], _stamp(SE_SERVED_SEGMENTS="a")),
            _leg("except", [2.0, 4.0, 7.0], except_stamp),
            {"level_vs_selection": {"selection_gbp": 4.0},
             "world_identity": _stamp(SE_SERVED_SEGMENTS="a")})
    refused = run(_stamp(SE_SERVED_SEGMENTS="b"))
    admitted = run(_stamp(SE_SERVED_SEGMENTS="a"))
    assert refused["available"] is False and "SE_SERVED_SEGMENTS" in refused["why_not"], refused
    assert "SE_SERVED_SEGMENTS" not in str(admitted.get("why_not")), admitted


def test_the_page_does_not_bound_a_figure_with_a_floor_one_switch_apart():
    floor = {"generated_at": "2026-10-02T12:00:00Z", "world_identity": _stamp(SE_SERVED_SEGMENTS="a"),
             "seeds": []}
    point = {"generated_at": "2026-10-02T10:00:00Z", "world_identity": _stamp(SE_SERVED_SEGMENTS="b")}
    refused = gva._seed_spreads(floor, point)
    assert refused["available"] is False and "SE_SERVED_SEGMENTS" in refused["reason"], refused
    matched = gva._seed_spreads(floor, dict(point, world_identity=_stamp(SE_SERVED_SEGMENTS="a")))
    assert "SE_SERVED_SEGMENTS" not in str(matched.get("reason")), matched
