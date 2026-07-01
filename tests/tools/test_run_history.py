"""Phase 262 tests: run_history guard in append_run_history + extract_run_history."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.generate_insights import generate_insights, append_run_history

_DATA = {
    "_ledger_headline": {"net_margin_gbp": 5_000_000, "gross_margin_gbp": 6_000_000,
                         "total_revenue_gbp": 10_000_000},
    "_trading_headline": {"hedge_fraction": 0.75, "total_volume_mwh": 50_000,
                          "cost_vs_spot_gbp": -200_000},
    "_risk_headline": {"var_95_gbp": 500_000, "bill_shocks": 10},
    "_customers_headline": {"active_electricity": 500, "churn_rate_pct": 3.5,
                            "avg_credit_score": 720},
    "per_customer_lifetime": {},
    "years": {2022: {"hedge_effectiveness": {"actual_cost_gbp": 10000, "naked_cost_gbp": 12000}},2023: {"hedge_effectiveness": {"actual_cost_gbp": 9000, "naked_cost_gbp": 11000}}},
}


def test_append_run_history_skips_fake_hash(tmp_path):
    hp = tmp_path / "hist.json"
    ins = generate_insights(_DATA, "testhash")
    append_run_history(ins, hp)
    history = json.loads(hp.read_text()) if hp.exists() else []
    assert history == []


def test_append_run_history_skips_negative_margin(tmp_path):
    hp = tmp_path / "hist.json"
    bad = dict(_DATA)
    bad["_ledger_headline"] = {"net_margin_gbp": -8317, "gross_margin_gbp": 0,
                                "total_revenue_gbp": 0}
    ins = generate_insights(bad, "f534735abc123456")
    append_run_history(ins, hp)
    history = json.loads(hp.read_text()) if hp.exists() else []
    assert len(history) == 0


def test_append_run_history_writes_real_hash(tmp_path):
    hp = tmp_path / "hist.json"
    ins = generate_insights(_DATA, "a1b2c3d")
    append_run_history(ins, hp)
    history = json.loads(hp.read_text())
    assert len(history) == 1
    assert history[0]["git_hash"] == "a1b2c3d"
    assert history[0]["net_margin_gbp"] > 0


def test_extract_run_history_returns_last_n(tmp_path):
    from tools.generate_dashboard_data import extract_run_history
    hp = tmp_path / "hist.json"
    entries = [
        {"git_hash": "aaa" + format(i, "04d"), "net_margin_gbp": i * 1000,
         "generated_at": "2026-01-01"}
        for i in range(1, 16)
    ]
    hp.write_text(json.dumps(entries))
    result = extract_run_history(hp, max_entries=10)
    assert len(result) == 10
    assert result[-1]["git_hash"].endswith("0015")


def test_extract_run_history_returns_empty_on_missing(tmp_path):
    from tools.generate_dashboard_data import extract_run_history
    result = extract_run_history(tmp_path / "nonexistent.json")
    assert result == []


def test_dashboard_includes_run_history_key(tmp_path):
    from tools.generate_dashboard_data import extract_run_history
    hp = tmp_path / "hist.json"
    hp.write_text(json.dumps([{
        "git_hash": "a1b2c3d4",
        "net_margin_gbp": 6_000_000,
        "generated_at": "2026-06-26T12:00:00",
        "executive_summary": "Steady state.",
    }]))
    result = extract_run_history(hp)
    assert len(result) == 1
    assert result[0]["git_hash"] == "a1b2c3d4"


from tools.generate_insights import _fmt_gbp, _fmt_pct, _committee_count


def test_fmt_gbp_positive():
    assert _fmt_gbp(1000.0) == "£1,000"


def test_fmt_gbp_negative():
    assert _fmt_gbp(-500.0) == "-£500"


def test_fmt_gbp_zero():
    assert _fmt_gbp(0.0) == "£0"


def test_fmt_gbp_million():
    assert _fmt_gbp(1_234_567.0) == "£1,234,567"


def test_fmt_pct_default_one_decimal():
    assert _fmt_pct(3.5) == "3.5%"


def test_fmt_pct_zero_decimals():
    assert _fmt_pct(7.0, 0) == "7%"


def test_fmt_pct_two_decimals():
    assert _fmt_pct(1.234, 2) == "1.23%"


def test_committee_count_missing_year():
    assert _committee_count({}, "2022") == 0


def test_committee_count_int_value():
    years = {"2022": {"committee_wake_ups": 5}}
    assert _committee_count(years, "2022") == 5


def test_committee_count_list_value():
    years = {"2022": {"committee_wake_ups": ["a", "b", "c"]}}
    assert _committee_count(years, "2022") == 3
