"""Tests for tools/generate_sim_data.py pure aggregation helpers."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from tools.generate_sim_data import _monthly_aggregation, _annual_aggregation, _peak_records


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
