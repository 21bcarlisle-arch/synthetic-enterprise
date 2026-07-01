"""Phase BM: Price Cap Headroom section tests."""
import pytest
from saas.reporting.annual_report import _section_price_cap_headroom


def _r(cid, term_start, vs_svt_pct):
    return {"customer_id": cid, "term_start": term_start, "rate_vs_svt_pct": vs_svt_pct}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_price_cap_headroom({}) == ""
    assert _section_price_cap_headroom({"churn_basis_risk": []}) == ""


# 2. Header present
def test_header_present():
    d = {"churn_basis_risk": [_r("C1", "2022-01-01", -10.0)]}
    assert "Price Cap Headroom" in _section_price_cap_headroom(d)


# 3. Negative avg shows below cap
def test_negative_avg_below_cap():
    d = {"churn_basis_risk": [_r("C1", "2022-01-01", -10.0), _r("C2", "2022-01-01", -20.0)]}
    result = _section_price_cap_headroom(d)
    assert "-15.0%" in result


# 4. Positive avg shows above cap
def test_positive_avg_above_cap():
    d = {"churn_basis_risk": [_r("C1", "2021-01-01", 15.0), _r("C2", "2021-01-01", 5.0)]}
    result = _section_price_cap_headroom(d)
    assert "+10.0%" in result


# 5. Above-cap count per year
def test_above_cap_count():
    d = {"churn_basis_risk": [
        _r("C1", "2022-01-01", 20.0),  # above
        _r("C2", "2022-01-01", -5.0),  # below
        _r("C3", "2022-01-01", 10.0),  # above
    ]}
    result = _section_price_cap_headroom(d)
    assert "2/3" in result  # 2 above cap out of 3


# 6. Best headroom year shown
def test_best_headroom_year():
    d = {"churn_basis_risk": [
        _r("C1", "2021-01-01", 10.0),   # above cap
        _r("C1", "2024-01-01", -30.0),  # below cap (better headroom)
    ]}
    result = _section_price_cap_headroom(d)
    assert "Best headroom year: 2024" in result


# 7. Largest above-SVT year shown
def test_largest_above_svt():
    d = {"churn_basis_risk": [
        _r("C1", "2021-01-01", 50.0),  # max above-SVT year
        _r("C1", "2022-01-01", 10.0),
    ]}
    result = _section_price_cap_headroom(d)
    assert "2021" in result
    assert "above" in result.lower() or "SVT" in result


# 8. Note about I&C exemption
def test_ic_note():
    d = {"churn_basis_risk": [_r("C1", "2022-01-01", -10.0)]}
    result = _section_price_cap_headroom(d)
    assert "I&C" in result or "exempt" in result.lower()


# 9. Year row in table
def test_year_in_table():
    d = {"churn_basis_risk": [_r("C1", "2019-06-30", -18.0)]}
    result = _section_price_cap_headroom(d)
    assert "| 2019 |" in result


# 10. Terms missing rate_vs_svt handled
def test_missing_rate_vs_svt_handled():
    d = {"churn_basis_risk": [
        {"customer_id": "C1", "term_start": "2022-01-01"},  # no rate_vs_svt
        _r("C2", "2022-01-01", -10.0),
    ]}
    result = _section_price_cap_headroom(d)
    assert "Price Cap Headroom" in result  # should not crash


# 11. Min and max shown in row
def test_min_max_in_row():
    d = {"churn_basis_risk": [
        _r("C1", "2022-01-01", -30.0),
        _r("C2", "2022-01-01", 20.0),
    ]}
    result = _section_price_cap_headroom(d)
    assert "-30.0%" in result
    assert "20.0%" in result


# 12. SVT regulatory note present
def test_svt_regulatory_note():
    d = {"churn_basis_risk": [_r("C1", "2022-01-01", -10.0)]}
    result = _section_price_cap_headroom(d)
    assert "SVT" in result and "Ofgem" in result


# 13. Best headroom year label shown
def test_best_headroom_label_shown():
    d = {"churn_basis_risk": [_r("C1", "2022-01-01", -25.0), _r("C1", "2023-01-01", -5.0)]}
    result = _section_price_cap_headroom(d)
    assert "Best headroom year" in result


# 14. Observation count in row
def test_observation_count_in_row():
    d = {"churn_basis_risk": [
        _r("C1", "2022-01-01", -10.0),
        _r("C2", "2022-06-01", -12.0),
        _r("C3", "2022-09-01", -8.0),
    ]}
    result = _section_price_cap_headroom(d)
    assert "| 3 |" in result or "| 2022 | 3 |" in result


# 15. Largest above-SVT year label shown
def test_largest_above_svt_label_shown():
    d = {"churn_basis_risk": [_r("C1", "2022-01-01", 15.0), _r("C1", "2023-01-01", -5.0)]}
    result = _section_price_cap_headroom(d)
    assert "above-SVT" in result or "Largest" in result
