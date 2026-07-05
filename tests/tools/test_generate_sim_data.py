"""Tests for tools/generate_sim_data.py pure aggregation helpers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

import json

from tools.generate_sim_data import (
    _monthly_aggregation, _annual_aggregation, _peak_records,
    _negative_price_hours_by_year, _daily_aggregation,
    generate,
)
import tools.generate_sim_data as generate_sim_data_module


def _ssp_rec(date, period, ssp):
    return {"settlementDate": date, "settlementPeriod": period, "systemSellPrice": ssp}


def test_monthly_aggregation_empty_records():
    result = _monthly_aggregation([])
    assert result == []


def test_monthly_aggregation_out_of_range_excluded():
    records = [_ssp_rec("2015-12-01", 1, 50.0)]  # before SIM_START
    result = _monthly_aggregation(records)
    assert result == []


def test_monthly_aggregation_single_record():
    records = [_ssp_rec("2022-06-01", 1, 100.0)]
    result = _monthly_aggregation(records)
    assert len(result) == 1
    assert result[0]["month"] == "2022-06"
    assert result[0]["mean"] == 100.0


def test_monthly_aggregation_keys():
    records = [_ssp_rec("2022-06-01", 1, 100.0)]
    r = _monthly_aggregation(records)[0]
    for key in ("month", "mean", "p95", "p5", "max", "min", "period_count", "is_crisis"):
        assert key in r


def test_monthly_aggregation_crisis_flag():
    records = [_ssp_rec("2022-06-01", 1, 100.0)]
    r = _monthly_aggregation(records)[0]
    assert r["is_crisis"] is True


def test_monthly_aggregation_non_crisis_flag():
    records = [_ssp_rec("2018-06-01", 1, 50.0)]
    r = _monthly_aggregation(records)[0]
    assert r["is_crisis"] is False


def test_annual_aggregation_empty():
    assert _annual_aggregation([]) == []


def test_annual_aggregation_groups_by_year():
    monthly = [
        {"month": "2022-01", "mean": 100.0, "max": 120.0, "min": 80.0, "p95": 115.0},
        {"month": "2022-06", "mean": 60.0, "max": 75.0, "min": 50.0, "p95": 70.0},
        {"month": "2021-12", "mean": 80.0, "max": 90.0, "min": 70.0, "p95": 85.0},
    ]
    result = _annual_aggregation(monthly)
    years = [r["year"] for r in result]
    assert "2021" in years
    assert "2022" in years


def test_annual_aggregation_keys():
    monthly = [{"month": "2022-01", "mean": 100.0, "max": 120.0, "min": 80.0, "p95": 115.0}]
    r = _annual_aggregation(monthly)[0]
    for key in ("year", "mean", "p95", "max", "min", "month_count"):
        assert key in r


def test_peak_records_returns_top_n():
    records = [_ssp_rec("2022-06-01", i, float(i * 10)) for i in range(1, 21)]
    result = _peak_records(records, n=5)
    assert len(result) == 5
    assert result[0]["ssp"] == 200.0


def test_peak_records_out_of_range_excluded():
    records = [_ssp_rec("2015-01-01", 1, 9999.0)]  # before SIM_START
    result = _peak_records(records, n=5)
    assert result == []


def test_peak_records_keys():
    records = [_ssp_rec("2022-06-01", 1, 100.0)]
    r = _peak_records(records, n=1)[0]
    for key in ("date", "period", "ssp"):
        assert key in r

import pytest as _pytest2

def test_annual_aggregation_single_month():
    monthly = [{"month": "2022-03", "mean": 90.0, "max": 110.0, "min": 70.0, "p95": 105.0}]
    result = _annual_aggregation(monthly)
    assert len(result) == 1
    assert result[0]["year"] == "2022"


def test_peak_records_sorted_desc():
    records = [_ssp_rec("2022-06-01", i, float(i)) for i in range(1, 10)]
    result = _peak_records(records, n=3)
    ssps = [r["ssp"] for r in result]
    assert ssps == sorted(ssps, reverse=True)


def test_monthly_aggregation_two_periods_same_month():
    records = [_ssp_rec("2022-06-01", 1, 100.0), _ssp_rec("2022-06-01", 2, 200.0)]
    result = _monthly_aggregation(records)
    assert len(result) == 1
    assert result[0]["period_count"] == 2
    assert result[0]["mean"] == _pytest2.approx(150.0)


def test_negative_price_hours_counts_only_negative():
    records = [
        _ssp_rec("2022-01-01", 1, -10.0),
        _ssp_rec("2022-01-01", 2, 50.0),
        _ssp_rec("2022-01-02", 1, -5.0),
    ]
    result = _negative_price_hours_by_year(records)
    assert result["2022"] == 1.0  # two negative periods * 0.5h


def test_negative_price_hours_out_of_range_excluded():
    records = [_ssp_rec("2015-01-01", 1, -10.0)]
    result = _negative_price_hours_by_year(records)
    assert result == {}


def test_negative_price_hours_empty():
    assert _negative_price_hours_by_year([]) == {}


def test_annual_aggregation_carries_negative_price_hours():
    monthly = [{"month": "2022-01", "mean": 100.0, "max": 120.0, "min": 80.0, "p95": 115.0}]
    result = _annual_aggregation(monthly, {"2022": 12.5})
    assert result[0]["negative_price_hours"] == 12.5


def test_annual_aggregation_defaults_negative_price_hours_to_zero():
    monthly = [{"month": "2022-01", "mean": 100.0, "max": 120.0, "min": 80.0, "p95": 115.0}]
    result = _annual_aggregation(monthly)
    assert result[0]["negative_price_hours"] == 0


def test_daily_aggregation_keys():
    records = [_ssp_rec("2022-06-01", 1, 100.0), _ssp_rec("2022-06-01", 2, 200.0)]
    result = _daily_aggregation(records)
    assert "2022-06-01" in result
    for key in ("mean", "max", "min", "short_pct"):
        assert key in result["2022-06-01"]
    assert result["2022-06-01"]["mean"] == 150.0


def _ssp_niv_rec(date, period, ssp, niv):
    return {
        "settlementDate": date, "settlementPeriod": period,
        "systemSellPrice": ssp, "netImbalanceVolume": niv,
    }


def test_daily_aggregation_short_pct_computed_from_niv():
    records = [
        _ssp_niv_rec("2022-12-01", 1, 100.0, -50.0),
        _ssp_niv_rec("2022-12-01", 2, 100.0, -50.0),
        _ssp_niv_rec("2022-12-01", 3, 100.0, 20.0),
        _ssp_niv_rec("2022-12-01", 4, 100.0, 20.0),
    ]
    result = _daily_aggregation(records)
    assert result["2022-12-01"]["short_pct"] == 50.0


def test_daily_aggregation_short_pct_none_when_no_niv():
    records = [_ssp_rec("2022-06-01", 1, 100.0)]
    result = _daily_aggregation(records)
    assert result["2022-06-01"]["short_pct"] is None


def test_daily_aggregation_out_of_range_excluded():
    records = [_ssp_rec("2015-01-01", 1, 100.0)]
    assert _daily_aggregation(records) == {}


def test_daily_aggregation_empty():
    assert _daily_aggregation([]) == {}


def test_generate_embeds_git_hash_and_phase(tmp_path, monkeypatch):
    """SIM_TAB_OVERHAUL.md item 5: the live SIM tab needs a freshness stamp
    (git commit + phase), not just a timestamp, matching what shadow pages
    already carry (tools/generate_shadow_html.py's _page())."""
    cache = tmp_path / "elexon_ssp_full.json"
    cache.write_text(json.dumps([
        {"settlementDate": "2022-06-01", "settlementPeriod": 1, "systemSellPrice": 100.0},
    ]))
    build_info = tmp_path / "build_info.json"
    build_info.write_text(json.dumps({"phase": "RB"}))
    output = tmp_path / "sim_data.json"

    monkeypatch.setattr(generate_sim_data_module, "SSP_CACHE", cache)
    monkeypatch.setattr(generate_sim_data_module, "OUTPUT_PATH", output)
    monkeypatch.setattr(generate_sim_data_module, "BUILD_INFO_PATH", build_info)

    generate(git_hash="abc1234")

    payload = json.loads(output.read_text())
    assert payload["metadata"]["git_hash"] == "abc1234"
    assert payload["metadata"]["phase"] == "RB"


def test_generate_defaults_unknown_without_build_info(tmp_path, monkeypatch):
    cache = tmp_path / "elexon_ssp_full.json"
    cache.write_text(json.dumps([
        {"settlementDate": "2022-06-01", "settlementPeriod": 1, "systemSellPrice": 100.0},
    ]))
    output = tmp_path / "sim_data.json"

    monkeypatch.setattr(generate_sim_data_module, "SSP_CACHE", cache)
    monkeypatch.setattr(generate_sim_data_module, "OUTPUT_PATH", output)
    monkeypatch.setattr(generate_sim_data_module, "BUILD_INFO_PATH", tmp_path / "nonexistent.json")

    generate()

    payload = json.loads(output.read_text())
    assert payload["metadata"]["git_hash"] == "unknown"
    assert payload["metadata"]["phase"] == "unknown"
