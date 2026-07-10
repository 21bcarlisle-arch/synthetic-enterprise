"""Tests for tools/generate_dashboard_data.py::extract_arrears_case_load() --
Operations tab KPI expansion candidate (c), 2026-07-10 (PRIORITIES.md)."""
import json

import pytest

from tools.generate_dashboard_data import extract_arrears_case_load


def _data():
    return {
        "years": {
            "2020": {"active_customer_ids": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10"]},
            "2021": {"active_customer_ids": ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "C9", "C10"]},
        },
    }


def _write_ledger(tmp_path, customers):
    ledger_dir = tmp_path / "site" / "state"
    ledger_dir.mkdir(parents=True)
    (ledger_dir / "billing_ledger.json").write_text(json.dumps({"customers": customers}))


def test_no_ledger_file_returns_zero_cases(tmp_path, monkeypatch):
    import tools.generate_dashboard_data as gdd
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    result = gdd.extract_arrears_case_load(_data())
    for row in result["annual"]:
        assert row["case_count"] == 0
        assert row["status"] == "green"


def test_counts_distinct_customers_with_arrears_that_year(tmp_path, monkeypatch):
    import tools.generate_dashboard_data as gdd
    _write_ledger(tmp_path, {
        "C1": {"arrears_history": [{"opened_date": "2020-03-01"}, {"opened_date": "2020-06-01"}]},
        "C2": {"arrears_history": [{"opened_date": "2020-04-01"}]},
    })
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    result = gdd.extract_arrears_case_load(_data())
    row_2020 = next(r for r in result["annual"] if r["year"] == 2020)
    assert row_2020["case_count"] == 2  # C1 counted once despite 2 cases


def test_non_crisis_year_green_below_8_pct(tmp_path, monkeypatch):
    import tools.generate_dashboard_data as gdd
    _write_ledger(tmp_path, {"C1": {"arrears_history": [{"opened_date": "2020-03-01"}]}})
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    result = gdd.extract_arrears_case_load(_data())
    row_2020 = next(r for r in result["annual"] if r["year"] == 2020)
    assert row_2020["arrears_rate_pct"] == 10.0
    assert row_2020["status"] == "amber"  # 10% is above the 8% non-crisis green threshold


def test_crisis_year_has_wider_green_band(tmp_path, monkeypatch):
    """2021 is a crisis year -- green threshold is 12%, not 8%."""
    import tools.generate_dashboard_data as gdd
    _write_ledger(tmp_path, {"C1": {"arrears_history": [{"opened_date": "2021-03-01"}]}})
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    result = gdd.extract_arrears_case_load(_data())
    row_2021 = next(r for r in result["annual"] if r["year"] == 2021)
    assert row_2021["is_crisis"] is True
    assert row_2021["status"] == "green"  # 10% < 12% crisis-year threshold


def test_red_status_above_amber_threshold(tmp_path, monkeypatch):
    import tools.generate_dashboard_data as gdd
    _write_ledger(tmp_path, {
        f"C{i}": {"arrears_history": [{"opened_date": "2020-03-01"}]} for i in range(1, 9)
    })
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    result = gdd.extract_arrears_case_load(_data())
    row_2020 = next(r for r in result["annual"] if r["year"] == 2020)
    assert row_2020["arrears_rate_pct"] == 80.0
    assert row_2020["status"] == "red"


def test_case_outside_year_range_not_counted(tmp_path, monkeypatch):
    import tools.generate_dashboard_data as gdd
    _write_ledger(tmp_path, {"C1": {"arrears_history": [{"opened_date": "2019-03-01"}]}})
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    result = gdd.extract_arrears_case_load(_data())
    row_2020 = next(r for r in result["annual"] if r["year"] == 2020)
    assert row_2020["case_count"] == 0


def test_zero_active_customers_gives_unknown_status(tmp_path, monkeypatch):
    import tools.generate_dashboard_data as gdd
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    data = {"years": {"2020": {"active_customer_ids": []}}}
    result = gdd.extract_arrears_case_load(data)
    row = result["annual"][0]
    assert row["arrears_rate_pct"] is None
    assert row["status"] == "unknown"


def test_malformed_ledger_json_does_not_crash(tmp_path, monkeypatch):
    import tools.generate_dashboard_data as gdd
    ledger_dir = tmp_path / "site" / "state"
    ledger_dir.mkdir(parents=True)
    (ledger_dir / "billing_ledger.json").write_text("not valid json")
    monkeypatch.setattr(gdd, "PROJECT", tmp_path)
    result = gdd.extract_arrears_case_load(_data())
    assert result["annual"][0]["case_count"] == 0
