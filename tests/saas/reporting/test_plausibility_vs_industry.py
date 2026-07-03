"""Harness Hardening: Plausibility vs Industry section tests."""
import pytest
from saas.reporting.annual_report import _section_plausibility_vs_industry


def _data(yr, rev, gm, nm, bd=0.0, churned=0, n_cust=10):
    """Build minimal data dict for one year."""
    cust_ids = ["C{}".format(i) for i in range(n_cust)]
    events = [{"event_type": "churned", "event_date": "{}-06-01".format(yr)}
              for _ in range(churned)]
    return {
        "management_accounts": {
            str(yr): {"income_statement": {
                "revenue_gbp": rev,
                "gross_margin_gbp": gm,
                "net_margin_gbp": nm,
                "bad_debt_gbp": bd,
            }}
        },
        "years": {str(yr): {"active_customer_ids": cust_ids}},
        "customer_events": events,
    }


# 1. Empty returns empty string
def test_empty_data_returns_empty():
    assert _section_plausibility_vs_industry({}) == ""
    assert _section_plausibility_vs_industry({"management_accounts": {}}) == ""


# 2. Header present in output
def test_header_present():
    d = _data(2022, 1_000_000, 150_000, 30_000)
    result = _section_plausibility_vs_industry(d)
    assert "Plausibility vs Industry" in result


# 3. Green net margin within range shows OK
def test_green_net_margin():
    # nm = 30k / 1M = 3.0% -> green (-5 to +8%)
    d = _data(2022, 1_000_000, 150_000, 30_000)
    result = _section_plausibility_vs_industry(d)
    assert "OK3.0%" in result or "OK" in result


# 4. Red net margin (heavily negative) shows !
def test_red_net_margin_negative():
    # nm = -300k / 1M = -30.0% -> red (outside amber -20%)
    d = _data(2022, 1_000_000, 150_000, -300_000)
    result = _section_plausibility_vs_industry(d)
    assert "!" in result
    assert "RED" in result or "review required" in result.lower()


# 5. Amber net margin shows ~
def test_amber_net_margin():
    # nm = -120k / 1M = -12% -> amber (-20% to +20%)
    d = _data(2022, 1_000_000, 150_000, -120_000)
    result = _section_plausibility_vs_industry(d)
    assert "~" in result
    assert "AMBER" in result or "monitor" in result.lower()


# 6. Bad debt rate computed correctly
def test_bad_debt_rate():
    # bd = 20k / 1M = 2.0% -> green
    d = _data(2022, 1_000_000, 150_000, 30_000, bd=20_000)
    result = _section_plausibility_vs_industry(d)
    assert "2.00%" in result


# 7. High bad debt triggers red
def test_high_bad_debt_red():
    # bd = 120k / 1M = 12% -> red (>10% amber ceiling)
    d = _data(2022, 1_000_000, 150_000, 30_000, bd=120_000)
    result = _section_plausibility_vs_industry(d)
    assert "!" in result


# 8. Churn rate computed from events / customers
def test_churn_rate_computed():
    # 2 churned / 10 customers = 20% -> green (3-35%)
    d = _data(2022, 1_000_000, 150_000, 30_000, churned=2, n_cust=10)
    result = _section_plausibility_vs_industry(d)
    assert "20%" in result


# 9. Benchmark ranges shown in footer
def test_benchmark_ranges_shown():
    d = _data(2022, 1_000_000, 150_000, 30_000)
    result = _section_plausibility_vs_industry(d)
    assert "Benchmark ranges" in result


# 10. Zero revenue year skipped (no div by zero)
def test_zero_revenue_skipped():
    d = {
        "management_accounts": {"2022": {"income_statement": {
            "revenue_gbp": 0.0, "gross_margin_gbp": 0.0,
            "net_margin_gbp": 0.0, "bad_debt_gbp": 0.0,
        }}},
        "years": {"2022": {"active_customer_ids": ["C1"]}},
        "customer_events": [],
    }
    result = _section_plausibility_vs_industry(d)
    assert result == ""


# 11. All green shows "within industry norms"
def test_all_green_message():
    # nm=3%, gm=15%, bd=1%, churn=20% -> all green
    d = _data(2022, 1_000_000, 150_000, 30_000, bd=10_000, churned=2, n_cust=10)
    result = _section_plausibility_vs_industry(d)
    assert "within industry norms" in result


# 12. Year shown in table row
def test_year_in_table():
    d = _data(2023, 1_000_000, 150_000, 30_000)
    result = _section_plausibility_vs_industry(d)
    assert "2023" in result


# 13. Multiple years all rendered
def test_multiple_years():
    d = {
        "management_accounts": {
            "2021": {"income_statement": {"revenue_gbp": 1e6, "gross_margin_gbp": 100_000, "net_margin_gbp": 20_000, "bad_debt_gbp": 5_000}},
            "2022": {"income_statement": {"revenue_gbp": 1e6, "gross_margin_gbp": 80_000,  "net_margin_gbp": -50_000, "bad_debt_gbp": 5_000}},
        },
        "years": {
            "2021": {"active_customer_ids": ["C1", "C2"]},
            "2022": {"active_customer_ids": ["C1", "C2"]},
        },
        "customer_events": [],
    }
    result = _section_plausibility_vs_industry(d)
    assert "2021" in result and "2022" in result


# 14. Gross margin rate computed and shown
def test_gross_margin_pct():
    # gm = 200k / 1M = 20% -> green (borderline)
    d = _data(2022, 1_000_000, 200_000, 30_000)
    result = _section_plausibility_vs_industry(d)
    assert "20.0%" in result


# 15. Red year listed in RED flag message
def test_red_year_named():
    # nm = -300k / 1M = -30% -> red
    d = _data(2022, 1_000_000, 100_000, -300_000)
    result = _section_plausibility_vs_industry(d)
    assert "2022" in result and "review required" in result.lower()
