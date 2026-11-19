"""The run's walk counter and final-month nets reach a harness file beside the run output.

Defect this catches: the run builds `settlements_behind_the_walk`, `later_settlements` and
`final_month_nets` in phase 2b, and no file ever held them, because the run output is a `saas/`
whitelist and these are world truth. The D5 pre-registration's "the next book names the walk"
could not happen on any book (17 Nov, 18f201c5bf).
"""

import fnmatch
import inspect
import json
from pathlib import Path

import background.live_payment_triad as lpt
import simulation.run_phase2b as run_phase2b
import tools.run_annual_report as rar

THREE = {"settlements_behind_the_walk", "later_settlements", "final_month_nets"}
PREPAY = "prepayment_supply_events"


def test_every_key_the_run_builds_is_written_and_none_is_named_missing(tmp_path):
    assert set(rar.WORLD_WALK_TRUTH_KEYS) == THREE | {PREPAY}
    raw = {"phase2b": {k: {"sentinel": k} for k in THREE | {PREPAY}} | {"total_net": 1.0}}
    run_output = tmp_path / "run_output_abc123_20261117T000000Z.json"
    written = json.loads(rar.write_world_walk_truth(raw, run_output).read_text())
    assert all(written[k] == {"sentinel": k} for k in THREE | {PREPAY}) and written["missing"] == []
    assert "total_net" not in written and written["run_output"] == run_output.name


def test_a_key_the_run_did_not_build_is_named_not_written_empty(tmp_path):
    raw = {"phase2b": {"later_settlements": {"delivered": 3}}}
    written = json.loads(rar.write_world_walk_truth(
        raw, tmp_path / "run_output_x_y.json").read_text())
    assert written["missing"] == ["settlements_behind_the_walk", "final_month_nets", PREPAY]
    assert "final_month_nets" not in written


def test_the_companion_sits_beside_the_run_and_no_run_glob_reads_it(tmp_path):
    run_output = tmp_path / "run_output_abc123_20261117T000000Z.json"
    path = rar.world_walk_truth_path(run_output)
    assert path.parent == run_output.parent and path.name != run_output.name
    assert path.name == "world_walk_truth_abc123_20261117T000000Z.json"
    assert not fnmatch.fnmatch(path.name, "run_output_*.json")


def test_the_run_builds_all_three_and_main_writes_them_from_the_raw_run():
    source = inspect.getsource(run_phase2b)
    assert all(f'"{k}": _payment_triad.{k}()' in source for k in THREE)
    assert f'"{PREPAY}": _method_dynamics.summarise_supply_events(' in source
    assert "write_world_walk_truth(raw_output, args.save_json)" in inspect.getsource(rar.main)


def test_every_crossing_behind_the_walk_is_carried_not_only_twenty():
    triad = lpt.LivePaymentTriad()
    triad._behind_the_walk = [
        {"account_id": f"A{i}", "leg": f"A{i}", "settled_on": "2023-08-15", "amount_gbp": 1.0,
         "walked_through": "2023-08-15", "walked_by": "record_period"} for i in range(25)]
    behind = triad.settlements_behind_the_walk()
    assert behind["count"] == 25 and len(behind["examples"]) == 20
    assert [r["account_id"] for r in behind["rows"]] == [f"A{i}" for i in range(25)]
    assert json.loads(json.dumps(behind)) == behind
    assert Path(rar.world_walk_truth_path(Path("run_output_a_b.json"))).suffix == ".json"
