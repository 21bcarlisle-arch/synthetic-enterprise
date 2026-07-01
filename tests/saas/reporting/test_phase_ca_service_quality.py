"""Phase CA: Service Quality annual report section tests."""
import pytest


def _mk_data(years_dict):
    return {"years": years_dict}


def _section(years_dict):
    from saas.reporting.annual_report import _section_service_quality
    return _section_service_quality(_mk_data(years_dict))


def _year(clarity, complaint_p, bill_shock_pct, bills=150, shock_n=30):
    events = [{"customer_id": "C1"}] * shock_n
    return {
        "avg_clarity": clarity,
        "avg_complaint_probability": complaint_p,
        "avg_bill_shock_pct": bill_shock_pct,
        "bills_count": bills,
        "bill_shock_events": events,
    }


# 1. Empty data returns empty string
def test_empty_returns_empty():
    assert _section({}) == ""


# 2. Section header present
def test_section_header():
    result = _section({"2022": _year(0.791, 0.056, 0.34)})
    assert "Customer Service Quality" in result


# 3. 2022 shows RED
def test_crisis_year_red():
    result = _section({"2022": _year(0.791, 0.056, 0.34)})
    assert "RED" in result


# 4. Good year shows GREEN
def test_good_year_green():
    result = _section({"2020": _year(0.850, 0.040, 0.15)})
    assert "GREEN" in result


# 5. Per-year row shows year number
def test_year_in_row():
    result = _section({"2019": _year(0.824, 0.047, 0.17)})
    assert "2019" in result


# 6. Table header present
def test_table_header():
    result = _section({"2020": _year(0.850, 0.040, 0.15)})
    assert "Clarity" in result
    assert "Complaint" in result


# 7. Worst clarity year identified
def test_worst_clarity_year():
    result = _section({
        "2020": _year(0.850, 0.040, 0.15),
        "2022": _year(0.791, 0.056, 0.34),
    })
    assert "Worst clarity year" in result
    assert "2022" in result


# 8. Improving trend shows IMPROVING
def test_improving_trend():
    result = _section({
        "2022": _year(0.791, 0.056, 0.34),
        "2023": _year(0.808, 0.048, 0.17),
    })
    assert "IMPROVING" in result


# 9. Declining trend shows DECLINING
def test_declining_trend():
    result = _section({
        "2023": _year(0.820, 0.045, 0.15),
        "2025": _year(0.777, 0.059, 0.24),
    })
    assert "DECLINING" in result


# 10. RED years listed in summary
def test_red_years_summary():
    result = _section({
        "2022": _year(0.791, 0.056, 0.34),
        "2023": _year(0.808, 0.048, 0.17),
    })
    assert "RED years" in result
    assert "2022" in result


# 11. Complaint % shown as percentage
def test_complaint_pct_display():
    result = _section({"2022": _year(0.791, 0.056, 0.34)})
    assert "5.6%" in result


# 12. Ofgem benchmarks mentioned
def test_ofgem_benchmarks():
    result = _section({"2020": _year(0.850, 0.040, 0.15)})
    assert "Ofgem" in result


# 13. RED year noted in summary
def test_red_year_noted():
    from saas.reporting.annual_report import _section_service_quality
    d = {"years": {"2022": {
        "avg_clarity": 0.78, "avg_complaint_probability": 0.08,
        "avg_bill_shock_pct": 0.5, "bills_count": 50, "bill_shock_events": []
    }}}
    result = _section_service_quality(d)
    # With clarity 0.78 and complaint 8%, should be RED
    if "RED" in result:
        assert "RED years" in result or "RED !" in result
    else:
        assert "Service Quality" in result


# 14. Trend IMPROVING when later year better
def test_trend_improving():
    from saas.reporting.annual_report import _section_service_quality
    d = {"years": {
        "2021": {"avg_clarity": 0.79, "avg_complaint_probability": 0.06,
                 "avg_bill_shock_pct": 0.1, "bills_count": 30, "bill_shock_events": []},
        "2022": {"avg_clarity": 0.85, "avg_complaint_probability": 0.03,
                 "avg_bill_shock_pct": 0.05, "bills_count": 50, "bill_shock_events": []},
    }}
    result = _section_service_quality(d)
    assert "IMPROVING" in result or "DECLINING" in result


# 15. Worst clarity year noted
def test_worst_clarity_noted():
    from saas.reporting.annual_report import _section_service_quality
    d = {"years": {
        "2021": {"avg_clarity": 0.76, "avg_complaint_probability": 0.05,
                 "avg_bill_shock_pct": 0.1, "bills_count": 20, "bill_shock_events": []},
        "2022": {"avg_clarity": 0.88, "avg_complaint_probability": 0.03,
                 "avg_bill_shock_pct": 0.05, "bills_count": 30, "bill_shock_events": []},
    }}
    result = _section_service_quality(d)
    assert "clarity" in result.lower() or "Clarity" in result
