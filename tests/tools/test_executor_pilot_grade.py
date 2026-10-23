"""The P2 pilot's grader reads each turn's verdict, arm and outcome the way the rule means them.

Defects each test names:
- a LANDED NOTHING followed by a FINISHED for the same turn reading as landed (the executor writes
  both when paths moved under other lanes but no landing was bound);
- an arm decision joined to an EARLIER run of the same work id;
- a verdict that can only say one thing (the partition control);
- the A/A placebo arming turns by a different rule from the live pilot.
"""
from tools import executor_pilot_grade as g

LOG = """\
- [2026-10-23 08:00 UTC] RUNNING alpha in /var/tmp/se-seat-executor on aaa
- [2026-10-23 08:30 UTC] FINISHED alpha: rc=0 -- 3 of 3 bound path(s) moved on the shared tree, including x
- [2026-10-23 09:00 UTC] RUNNING beta in /var/tmp/se-seat-executor on bbb
- [2026-10-23 09:40 UTC] LANDED NOTHING: beta, bound paths unchanged since bbb (rc=1) -- no landing
- [2026-10-23 09:40 UTC] FINISHED beta: rc=1 -- 2 of 2 bound path(s) moved on the shared tree, including y
- [2026-10-23 10:00 UTC] RUNNING gamma in /var/tmp/se-seat-executor on ccc
- [2026-10-23 10:20 UTC] FINISHED gamma: rc=0 -- 0 of 2 bound path(s) moved on the shared tree
- [2026-10-23 11:00 UTC] RUNNING alpha in /var/tmp/se-seat-executor on ddd
"""


def test_a_landed_nothing_inside_the_turn_outranks_its_finished_line():
    turns = g.executor_turns(LOG)
    assert [(t["work_id"], t["landed"]) for t in turns] == [
        ("alpha", True), ("beta", False), ("gamma", False), ("alpha", None)]


def test_an_arm_decision_joins_the_run_after_it_not_an_earlier_run_of_the_same_id():
    turns = g.executor_turns(LOG)
    late = g._stamp("2026-10-23 10:59")
    joined = g.join([{"ts": late, "work_id": "alpha", "arm": "sonnet"}], turns)
    assert joined[0]["landed"] is None and joined[0]["start"] == g._stamp("2026-10-23 11:00")


def _arm(n, landed, usd, rework):
    return {"n": n, "landed_share": landed, "usd_per_landed": usd, "rework_share": rework}


def test_every_verdict_on_the_partition_can_be_reached():
    calls = {
        g.verdict(_arm(5, .6, 1, 0), _arm(30, .6, 4, 0)).get("call"),          # not ready
        g.verdict(_arm(20, .6, 2, .1), _arm(20, .65, 4, .1))["call"],         # all three hold
        g.verdict(_arm(20, .6, 3.5, .1), _arm(20, .65, 4, .1))["call"],       # not 25% cheaper
        g.verdict(_arm(20, .6, 2, None), _arm(20, .65, 4, .1))["call"],       # rework unmeasured
    }
    assert calls == {None, "SWITCH ON", "REVERT"}
    assert g.verdict(_arm(19, .6, 1, 0), _arm(30, .6, 4, 0))["ready"] is False
    assert g.verdict(_arm(20, .49, 1, 0), _arm(20, .6, 4, 0))["landed_within_10_points"] is False
    assert g.verdict(_arm(20, .6, 1, .2), _arm(20, .6, 4, .1))["rework_no_higher"] is False


def test_the_placebo_arms_a_work_id_exactly_as_the_live_pilot_would(tmp_path):
    from background.model_tier import executor_arm
    cfg = tmp_path / "pilot.yaml"
    cfg.write_text('enabled: true\nstarts: "2026-10-23"\nends: "2026-11-06"\none_in: 4\n')
    ids = [f"item-{i}" for i in range(40)]
    log = "".join(f"- [2026-10-23 08:{i:02d} UTC] RUNNING {w} in /x on a\n" for i, w in enumerate(ids))
    placebo = {r["work_id"]: r["arm"] for r in g.placebo_rows(log, "2026-10-23", 4)}
    live = {w: executor_arm("plain drawn item", w, config=cfg, today="2026-10-24").arm for w in ids}
    assert placebo == live and {"sonnet", "control"} <= set(live.values())
