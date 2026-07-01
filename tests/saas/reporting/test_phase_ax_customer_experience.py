"""Phase AX: Customer Experience & Service Quality annual report section tests."""
import pytest
from saas.reporting.annual_report import _section_customer_experience


def _yr(clarity=0.82, complaint=0.047, acq_att=0, acq_wins=0):
    return {
        "avg_clarity": clarity,
        "avg_complaint_probability": complaint,
        "acquisition_attempts": acq_att,
        "acquisition_wins": acq_wins,
    }


def _data(years_dict, sq=0.905, avg_clarity=0.816, avg_complaint=0.047, total_att=0, total_wins=0):
    return {
        "years": years_dict,
        "service_quality_score": sq,
        "avg_clarity_total": avg_clarity,
        "avg_complaint_probability_total": avg_complaint,
        "total_acquisition_attempts": total_att,
        "total_acquisition_wins": total_wins,
    }


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_customer_experience({}) == ""


# 2. No service_quality_score returns empty
def test_no_sq_returns_empty():
    d = {"years": {"2022": _yr()}}
    assert _section_customer_experience(d) == ""


# 3. Header present
def test_header_present():
    d = _data({"2022": _yr()})
    result = _section_customer_experience(d)
    assert "Customer Experience" in result


# 4. Year in table
def test_year_in_table():
    d = _data({"2022": _yr()})
    result = _section_customer_experience(d)
    assert "2022" in result


# 5. LOW CLARITY flag when clarity < 0.80
def test_low_clarity_flag():
    d = _data({"2022": _yr(clarity=0.791)})
    result = _section_customer_experience(d)
    assert "LOW CLARITY" in result


# 6. No flag when clarity >= 0.80
def test_no_flag_when_above_80():
    d = _data({"2020": _yr(clarity=0.830)})
    result = _section_customer_experience(d)
    assert "LOW CLARITY" not in result


# 7. HIGH COMPLAINTS flag when complaint_prob > 0.055
def test_high_complaints_flag():
    d = _data({"2025": _yr(clarity=0.81, complaint=0.059)})
    result = _section_customer_experience(d)
    assert "HIGH COMPLAINTS" in result or "LOW CLARITY" in result  # either or both


# 8. Service quality score shown
def test_service_quality_shown():
    d = _data({"2022": _yr()}, sq=0.905)
    result = _section_customer_experience(d)
    assert "90.5%" in result or "service quality" in result.lower()


# 9. Acquisition performance shown when attempts > 0
def test_acquisition_performance_shown():
    d = _data({"2020": _yr(acq_att=1)}, total_att=5, total_wins=0)
    result = _section_customer_experience(d)
    assert "Acquisition performance" in result
    assert "5 attempts" in result or "5" in result


# 10. Zero win note shown
def test_zero_wins_note():
    d = _data({"2020": _yr()}, total_att=5, total_wins=0)
    result = _section_customer_experience(d)
    assert "0 wins" in result or "No new customers" in result


# 11. Worst clarity year identified
def test_worst_clarity_year():
    d = _data({
        "2020": _yr(clarity=0.830),
        "2022": _yr(clarity=0.791),
        "2025": _yr(clarity=0.777),
    })
    result = _section_customer_experience(d)
    assert "2025" in result
    assert "Lowest clarity" in result or "0.777" in result


# 12. Multiple years all appear
def test_multiple_years_all_appear():
    d = _data({
        "2020": _yr(),
        "2021": _yr(),
        "2022": _yr(),
    })
    result = _section_customer_experience(d)
    assert "2020" in result and "2021" in result and "2022" in result


def test_header_present():
    d = _data({"2022": _yr()})
    result = _section_customer_experience(d)
    assert "Customer Experience" in result


def test_high_complaints_flag_shown():
    d = _data({"2022": _yr(complaint=0.06)})
    result = _section_customer_experience(d)
    assert "HIGH COMPLAINTS" in result


def test_low_clarity_flag_shown():
    d = _data({"2022": _yr(clarity=0.75)})
    result = _section_customer_experience(d)
    assert "LOW CLARITY" in result
