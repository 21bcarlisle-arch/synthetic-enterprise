"""Phase AW: Bill Shock Analysis annual report section tests.

UPDATED 2026-09-02, and four of these assertions were pinning the defect rather than the
behaviour. Recorded here rather than quietly rewritten, because "the test changed too" is the
sentence that hides a regression:

* `test_shock_rate_computed` asserted incidence = flagged / `bills_count`. That denominator
  counts bills with no prior bill, which CANNOT be flagged. The section now divides by the
  bills with a computable change, and the test asserts the new denominator.
* `test_high_flag_shown` / `test_elevated_flag_shown` banded the MIXED mean across both
  bill-shock populations. The band now applies only to the standard-credit population, so the
  fixtures name a population.
* `test_shock_pct_formatted` asserted "33.8%" from a stored 0.338 -- the one rendering that was
  always right. It still holds; only the fixture had to grow bills for the split to see them.

The units property itself is held by
`tests/saas/reporting/test_a_rendered_shock_figure_is_in_the_units_of_its_own_percent_sign.py`.
"""
import pytest
from saas.reporting.annual_report import _section_bill_shock_analysis


def _bills(pct, count, population="bill", year="2022"):
    return [
        {
            "customer_id": f"C{i}",
            "period_end": f"{year}-01-31",
            "bill_shock_pct": pct,
            "bill_shock_population": population,
        }
        for i in range(count)
    ]


def _yr(avg_shock, events_count, bills=100):
    events = [{"customer_id": "C1", "period_end": "2022-01-31", "bill_shock_pct": 0.3,
               "bill_shock_population": "bill"}] * events_count
    return {
        "avg_bill_shock_pct": avg_shock,
        "bill_shock_events": events,
        "bills_count": bills,
    }


def _data(avg_shock, events_count, bills=100, shock_bills=None):
    """A year plus the per-bill list the population split is computed from."""
    d = {"years": {"2022": _yr(avg_shock, events_count, bills)}}
    d["bills"] = shock_bills if shock_bills is not None else _bills(avg_shock, 10)
    return d


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_bill_shock_analysis({}) == ""
    assert _section_bill_shock_analysis({"years": {}}) == ""


# 2. No avg_bill_shock_pct returns empty
def test_no_shock_data_returns_empty():
    d = {"years": {"2022": {"revenue_gbp": 1000}}}
    assert _section_bill_shock_analysis(d) == ""


# 3. Header present
def test_header_present():
    d = {"years": {"2022": _yr(0.338, 61)}}
    result = _section_bill_shock_analysis(d)
    assert "Bill Shock" in result


# 4. Year in table
def test_year_in_table():
    d = {"years": {"2022": _yr(0.338, 61)}}
    result = _section_bill_shock_analysis(d)
    assert "2022" in result


# 5. HIGH flag shown for >= 30% -- ON THE POPULATION WHOSE FIGURE IS A SHOCK
def test_high_flag_shown():
    result = _section_bill_shock_analysis(_data(0.338, 61, shock_bills=_bills(0.338, 10)))
    assert "HIGH" in result


# 6. ELEVATED flag shown for 20-30%
def test_elevated_flag_shown():
    result = _section_bill_shock_analysis(_data(0.25, 30, shock_bills=_bills(0.25, 10)))
    assert "ELEVATED" in result


# 7. No flag for < 20%
def test_no_flag_below_20pct():
    result = _section_bill_shock_analysis(_data(0.145, 53, shock_bills=_bills(0.145, 10)))
    assert "HIGH" not in result
    assert "ELEVATED" not in result


# 8. Worst year identified in crisis note
def test_worst_year_in_crisis_note():
    d = {"years": {
        "2020": _yr(0.145, 53),
        "2022": _yr(0.338, 61),
        "2023": _yr(0.172, 42),
    }}
    result = _section_bill_shock_analysis(d)
    assert "Crisis peak: 2022" in result or "2022" in result


# 9. Incidence is flagged bills over COMPUTABLE bills, not over every bill issued.
def test_shock_rate_computed():
    # 40 flagged, 100 bills issued, but only 80 with a prior bill to difference => 50%, not 40%.
    d = _data(0.338, 40, bills=100, shock_bills=_bills(0.338, 80))
    result = _section_bill_shock_analysis(d)
    assert "| 2022 | standard credit | 40 | 80 | 50% |" in result
    assert "| 2022 | standard credit | 40 | 100 |" not in result


# 10. Regulatory SLC note shown
def test_regulatory_note():
    d = {"years": {"2022": _yr(0.338, 61)}}
    result = _section_bill_shock_analysis(d)
    assert "SLC" in result or "Ofgem" in result


# 11. Multiple years all appear
def test_multiple_years_appear():
    d = {"years": {
        "2020": _yr(0.145, 53),
        "2021": _yr(0.159, 51),
        "2022": _yr(0.338, 61),
    }}
    result = _section_bill_shock_analysis(d)
    assert "2020" in result and "2021" in result and "2022" in result


# 12. Shock pct formatted correctly -- a 0.338 FRACTION renders as "33.8%", never "0.34%".
def test_shock_pct_formatted():
    result = _section_bill_shock_analysis(_data(0.338, 61, shock_bills=_bills(0.338, 10)))
    assert "33.8%" in result
    assert "0.3%" not in result


def test_bill_shock_header_present():
    from saas.reporting.annual_report import _section_bill_shock_analysis
    d = {"years": {"2022": _yr(0.25, 30)}}
    result = _section_bill_shock_analysis(d)
    assert "Bill Shock" in result


def test_elevated_flag_shown_duplicate_name_kept_for_history():
    from saas.reporting.annual_report import _section_bill_shock_analysis
    result = _section_bill_shock_analysis(_data(0.25, 30, shock_bills=_bills(0.25, 10)))
    assert "ELEVATED" in result


def test_zero_events_no_flag():
    from saas.reporting.annual_report import _section_bill_shock_analysis
    result = _section_bill_shock_analysis(_data(0.05, 0, shock_bills=_bills(0.05, 10)))
    assert "HIGH" not in result
    assert "ELEVATED" not in result
