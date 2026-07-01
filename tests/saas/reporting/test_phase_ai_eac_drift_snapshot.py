"""Phase AI tests: EAC Drift Snapshot section in annual report."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "../../.."))

from saas.reporting.annual_report import _section_eac_drift_snapshot


def _make_data(demand_estimation_log=None):
    return {"demand_estimation_log": demand_estimation_log or []}


def _entry(cid, term_start, company_eac, true_eac=None, source="prior_billing"):
    return {
        "customer_id": cid,
        "term_start": term_start,
        "company_eac_kwh": company_eac,
        "true_eac_kwh": true_eac or company_eac,
        "error_pct": 0.0,
        "source": source,
    }


# 1. Silent when no demand_estimation_log
def test_empty_log_returns_empty():
    result = _section_eac_drift_snapshot(_make_data())
    assert result == ""


# 2. Silent when demand_estimation_log is missing
def test_missing_key_returns_empty():
    result = _section_eac_drift_snapshot({})
    assert result == ""


# 3. Returns section header when data exists
def test_returns_header_when_data_exists():
    data = _make_data([
        _entry("C1", "2016-12-31", 3000),
        _entry("C1", "2017-12-31", 3100),
    ])
    result = _section_eac_drift_snapshot(data)
    assert "EAC Drift Snapshot" in result


# 4. Drift computation: single customer increasing
def test_significant_increase_detected():
    data = _make_data([
        _entry("C1", "2016-12-31", 3000),
        _entry("C1", "2021-12-31", 11000),  # +267% — EV acquisition
    ])
    result = _section_eac_drift_snapshot(data)
    assert "+267%" in result or "+266%" in result  # rounding
    assert "EV" in result


# 5. Significant decrease flagged as likely solar
def test_significant_decrease_flagged_as_solar():
    data = _make_data([
        _entry("C4", "2017-10-01", 5000),
        _entry("C4", "2024-09-29", 3500),  # -30%
    ])
    result = _section_eac_drift_snapshot(data)
    assert "solar" in result or "efficiency" in result


# 6. Stable customers included in stable count
def test_stable_customers_counted():
    data = _make_data([
        _entry("C1", "2016-12-31", 3000),
        _entry("C1", "2021-12-31", 3050),   # +1.7% — stable
        _entry("C2", "2017-04-01", 5000),
        _entry("C2", "2022-03-31", 5100),   # +2% — stable
    ])
    result = _section_eac_drift_snapshot(data)
    assert "2 stable" in result


# 7. Notable drift customers appear in the table
def test_notable_drift_in_table():
    data = _make_data([
        _entry("C1", "2016-12-31", 3000),
        _entry("C1", "2021-12-31", 10000),   # +233% — very notable
    ])
    result = _section_eac_drift_snapshot(data)
    assert "C1" in result
    assert "3,000" in result
    assert "10,000" in result


# 8. Multiple customers: most significant drift sorted first
def test_sorting_by_drift_magnitude():
    data = _make_data([
        _entry("C1", "2016-12-31", 3000),
        _entry("C1", "2021-12-31", 3090),    # +3% — stable, not in table
        _entry("C2", "2016-12-31", 5000),
        _entry("C2", "2021-12-31", 9000),    # +80% — in table
    ])
    result = _section_eac_drift_snapshot(data)
    assert "C2" in result
    assert "C1" not in result.split("##")[1].split("|")[0]  # C1 not in table rows


# 9. Portfolio demand trend shows increasing/decreasing counts
def test_portfolio_trend_line():
    data = _make_data([
        _entry("C1", "2016-12-31", 3000),
        _entry("C1", "2021-12-31", 4000),   # +33%
        _entry("C4", "2017-10-01", 5000),
        _entry("C4", "2024-09-29", 4000),   # -20%
    ])
    result = _section_eac_drift_snapshot(data)
    assert "Portfolio demand trend" in result
    assert "1 customers increasing" in result
    assert "1 decreasing" in result


# 10. Single-renewal customers (only one entry) show zero drift
def test_single_renewal_stable():
    data = _make_data([
        _entry("C_IC1", "2018-01-31", 2000000),
    ])
    result = _section_eac_drift_snapshot(data)
    assert "EAC Drift Snapshot" in result
    # 0 significant, 0 moderate, 1 stable
    assert "0 significant" in result
    assert "1 stable" in result


def test_section_returns_string_type():
    result = _section_eac_drift_snapshot(_make_data())
    assert isinstance(result, str)


def test_section_returns_string_with_data():
    data = _make_data([_entry("C1", "2016-12-31", 3000), _entry("C1", "2021-12-31", 4000)])
    result = _section_eac_drift_snapshot(data)
    assert isinstance(result, str)


def test_stable_count_is_1_for_minimal_drift():
    data = _make_data([
        _entry("C1", "2016-12-31", 3000),
        _entry("C1", "2021-12-31", 3050),
    ])
    result = _section_eac_drift_snapshot(data)
    assert "1 stable" in result
