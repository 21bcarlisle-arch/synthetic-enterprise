"""Controls for `simulation.run_cost`: one cost line per run, and a Monday flag when cost per settled
leg-year moves."""
import json
from datetime import datetime, timedelta, timezone

from simulation import run_cost


def _result(n_records: int, customers: int = 3) -> dict:
    return {"all_records": [{"customer_id": f"C{i % customers}"} for i in range(n_records)]}


def test_a_cost_line_divides_wall_and_peak_by_SETTLED_LEG_YEARS_and_counts_accounts():
    """Defect: the line divides by accounts or by records, so a longer window reads as a slower
    run. One record is one customer-leg-day, so leg-years are records / 365.25."""
    line = run_cost.cost_line(_result(730, customers=2), wall_s=200.0, report_end="2017-12-31")
    assert line["settled_leg_years"] == 2.0 and line["accounts"] == 2
    legs = 730 / 365.25
    assert line["s_per_leg_year"] == round(200.0 / legs, 3)
    assert abs(line["mb_per_leg_year"] - line["peak_self_mb"] / legs) < 0.1  # peak is shown to 0.1 MB


def test_record_appends_one_line_and_a_test_process_never_writes_the_live_log(tmp_path, monkeypatch):
    """Defect: a test run writes into the shared cost log and the Monday table reads test noise.
    Both sides: an explicit path writes; the live log is untouched from inside pytest."""
    target = tmp_path / "log.jsonl"
    run_cost.record(_result(365), wall_s=10.0, report_end=None, path=target)
    assert len(target.read_text().splitlines()) == 1

    live = tmp_path / "live.jsonl"
    monkeypatch.setattr(run_cost, "log_path", lambda: live)
    run_cost.record(_result(365), wall_s=10.0, report_end=None)
    assert not live.exists()


def test_the_monday_table_FLAGS_a_move_in_cost_per_leg_year_and_stays_quiet_when_steady(tmp_path):
    """Defect: a run gets slower per customer and nothing says so. THE FLAG MUST BE ABLE TO FIRE
    (a render that never flags passes every quiet week) and must not fire on a steady week."""
    now = datetime(2026, 10, 12, 4, tzinfo=timezone.utc)

    def write(rows):
        p = tmp_path / f"{len(rows)}-{rows[0]['s_per_leg_year']}.jsonl"
        p.write_text("\n".join(json.dumps(r) for r in rows))
        return p

    def row(days_ago, s):
        return {"at": (now - timedelta(days=days_ago)).isoformat(), "sha": "x", "accounts": 100,
                "settled_leg_years": 300, "wall_s": 300 * s, "peak_self_mb": 2000,
                "s_per_leg_year": s, "mb_per_leg_year": 6.0}

    moved = write([row(10, 1.0), row(9, 1.0), row(2, 2.0), row(1, 2.0)])
    assert "MOVED" in run_cost.render(7, moved, now)
    steady = write([row(10, 1.0), row(9, 1.0), row(2, 1.05), row(1, 1.0)])
    text = run_cost.render(7, steady, now)
    assert "MOVED" not in text and "s_per_leg_year: median" in text


def test_an_empty_week_says_so_rather_than_rendering_an_empty_table(tmp_path):
    assert "NO RUNS RECORDED" in run_cost.render(7, tmp_path / "absent.jsonl")
