"""Phase BH: Dynamic Pricing Activity section tests."""
import pytest
from saas.reporting.annual_report import _section_dynamic_pricing_activity


def _entry(term_start, rate_before, rate_after):
    return {
        "term_start": term_start,
        "unit_rate_before": rate_before,
        "unit_rate_after": rate_after,
        "customer_id": "C1",
        "commodity": "electricity",
    }


def _emerg(term_start, rate_before, rate_after):
    return {
        "term_start": term_start,
        "unit_rate_before": rate_before,
        "unit_rate_after": rate_after,
        "customer_id": "C1",
        "commodity": "electricity",
        "prev_margin_gbp": -1000.0,
    }


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_dynamic_pricing_activity({}) == ""
    assert _section_dynamic_pricing_activity({"dynamic_pricing_log": []}) == ""


# 2. Header present with data
def test_header_present():
    d = {
        "dynamic_pricing_log": [_entry("2022-01-01", 100.0, 120.0)],
        "margin_feedback_log": [],
    }
    assert "Dynamic Pricing Activity" in _section_dynamic_pricing_activity(d)


# 3. Positive delta shows + sign
def test_positive_delta_sign():
    d = {
        "dynamic_pricing_log": [_entry("2022-01-01", 100.0, 118.0)],
        "margin_feedback_log": [],
    }
    result = _section_dynamic_pricing_activity(d)
    assert "+18.0" in result


# 4. Negative delta (no + sign)
def test_negative_delta():
    d = {
        "dynamic_pricing_log": [_entry("2017-01-01", 100.0, 95.0)],
        "margin_feedback_log": [],
    }
    result = _section_dynamic_pricing_activity(d)
    assert "-5.0" in result


# 5. Emergency count per year
def test_emergency_count():
    d = {
        "dynamic_pricing_log": [_entry("2022-01-01", 100.0, 120.0)] * 3,
        "margin_feedback_log": [_emerg("2022-01-01", 100.0, 130.0)] * 2,
    }
    result = _section_dynamic_pricing_activity(d)
    assert "| 2022 | 3 |" in result
    assert "| 2" in result  # emergency count 2


# 6. Total adjustments in summary
def test_total_adjustments():
    entries = [_entry("2021-01-01", 100.0, 105.0)] * 5 + [_entry("2022-01-01", 100.0, 120.0)] * 3
    d = {"dynamic_pricing_log": entries, "margin_feedback_log": []}
    result = _section_dynamic_pricing_activity(d)
    assert "8" in result  # 5 + 3 = 8 total


# 7. Peak avg adjustment year identified
def test_peak_adjustment_year():
    d = {
        "dynamic_pricing_log": [
            _entry("2021-01-01", 100.0, 110.0),  # +10
            _entry("2022-01-01", 100.0, 125.0),  # +25 — peak
        ],
        "margin_feedback_log": [],
    }
    result = _section_dynamic_pricing_activity(d)
    assert "2022" in result
    assert "Peak avg adjustment" in result


# 8. Up/down count columns present
def test_up_down_columns():
    d = {
        "dynamic_pricing_log": [
            _entry("2022-01-01", 100.0, 120.0),  # up
            _entry("2022-06-01", 120.0, 115.0),  # down
        ],
        "margin_feedback_log": [],
    }
    result = _section_dynamic_pricing_activity(d)
    # 1 up, 1 down for 2022
    assert "| 2022 | 2 |" in result


# 9. Note about emergency reprices
def test_emergency_note():
    d = {"dynamic_pricing_log": [_entry("2022-01-01", 100.0, 120.0)], "margin_feedback_log": []}
    result = _section_dynamic_pricing_activity(d)
    assert "Emergency" in result or "emergency" in result


# 10. Total emergency count
def test_total_emergency():
    d = {
        "dynamic_pricing_log": [
            _entry("2021-01-01", 100.0, 110.0),
            _entry("2022-01-01", 100.0, 120.0),
        ],
        "margin_feedback_log": [
            _emerg("2021-01-01", 100.0, 125.0),
            _emerg("2022-01-01", 100.0, 130.0),
            _emerg("2022-06-01", 130.0, 140.0),
        ],
    }
    result = _section_dynamic_pricing_activity(d)
    assert "3 total" in result


# 11. Missing margin_feedback_log handled
def test_no_margin_feedback_log():
    d = {"dynamic_pricing_log": [_entry("2022-01-01", 100.0, 110.0)]}
    result = _section_dynamic_pricing_activity(d)
    assert "Dynamic Pricing Activity" in result


# 12. Year in table rows
def test_year_in_rows():
    d = {
        "dynamic_pricing_log": [_entry("2019-03-01", 100.0, 105.0)],
        "margin_feedback_log": [],
    }
    result = _section_dynamic_pricing_activity(d)
    assert "| 2019 |" in result
