"""Phase BK: Financial Ratios section tests."""
import pytest
from saas.reporting.annual_report import _section_financial_ratios


def _ma(yr, rev, gm, nm, bd=0.0):
    return {str(yr): {"income_statement": {
        "revenue_gbp": rev, "gross_margin_gbp": gm,
        "net_margin_gbp": nm, "bad_debt_gbp": bd,
    }}}


def _yrs(yr, n_cust):
    return {str(yr): {"active_customer_ids": ["C{}".format(i) for i in range(n_cust)]}}


def _data(ma_entries, yr_entries):
    ma = {}
    yrs = {}
    for e in ma_entries:
        ma.update(e)
    for e in yr_entries:
        yrs.update(e)
    return {"management_accounts": ma, "years": yrs}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_financial_ratios({}) == ""
    assert _section_financial_ratios({"management_accounts": {}}) == ""


# 2. Header present
def test_header_present():
    d = _data([_ma(2022, 1_000_000, 400_000, 200_000)], [_yrs(2022, 10)])
    assert "Financial Ratios" in _section_financial_ratios(d)


# 3. EBIT% computed correctly
def test_ebit_pct():
    # rev=1M, nm=300k -> EBIT=30%
    d = _data([_ma(2022, 1_000_000, 400_000, 300_000)], [_yrs(2022, 10)])
    result = _section_financial_ratios(d)
    assert "30.0%" in result


# 4. Revenue per customer
def test_revenue_per_customer():
    # rev=500k, 5 customers -> £100k each
    d = _data([_ma(2022, 500_000, 200_000, 100_000)], [_yrs(2022, 5)])
    result = _section_financial_ratios(d)
    assert "£100,000" in result


# 5. GM per customer
def test_gm_per_customer():
    # gm=200k, 4 customers -> £50k
    d = _data([_ma(2022, 400_000, 200_000, 100_000)], [_yrs(2022, 4)])
    result = _section_financial_ratios(d)
    assert "£50,000" in result


# 6. Bad debt rate
def test_bad_debt_rate():
    # bd=10k, rev=1M -> 1.00%
    d = _data([_ma(2022, 1_000_000, 400_000, 200_000, 10_000)], [_yrs(2022, 10)])
    result = _section_financial_ratios(d)
    assert "1.00%" in result


# 7. Best EBIT year identified
def test_best_ebit_year():
    d = _data(
        [_ma(2021, 500_000, 250_000, 100_000), _ma(2022, 500_000, 250_000, 250_000)],
        [_yrs(2021, 5), _yrs(2022, 5)]
    )
    result = _section_financial_ratios(d)
    assert "Best EBIT%: 2022" in result


# 8. Worst EBIT year identified
def test_worst_ebit_year():
    d = _data(
        [_ma(2021, 500_000, 250_000, 100_000), _ma(2022, 500_000, 250_000, 250_000)],
        [_yrs(2021, 5), _yrs(2022, 5)]
    )
    result = _section_financial_ratios(d)
    assert "Worst EBIT%: 2021" in result


# 9. Peak revenue per customer year
def test_peak_revenue_per_customer():
    # 2022: 1M/5=200k per customer (higher)
    # 2021: 500k/5=100k
    d = _data(
        [_ma(2021, 500_000, 200_000, 100_000), _ma(2022, 1_000_000, 400_000, 200_000)],
        [_yrs(2021, 5), _yrs(2022, 5)]
    )
    result = _section_financial_ratios(d)
    assert "Peak revenue/customer: 2022" in result


# 10. Note about I&C mix
def test_note_present():
    d = _data([_ma(2022, 1_000_000, 400_000, 200_000)], [_yrs(2022, 10)])
    result = _section_financial_ratios(d)
    assert "Note:" in result or "I&C" in result


# 11. Customer count in table
def test_customer_count_in_table():
    d = _data([_ma(2022, 1_000_000, 400_000, 200_000)], [_yrs(2022, 14)])
    result = _section_financial_ratios(d)
    assert "| 14 |" in result


# 12. Zero revenue handled (no div-by-zero)
def test_zero_revenue_no_crash():
    d = _data([_ma(2022, 0, 0, 0, 0)], [_yrs(2022, 10)])
    result = _section_financial_ratios(d)
    assert "0.0%" in result  # EBIT% = 0%
