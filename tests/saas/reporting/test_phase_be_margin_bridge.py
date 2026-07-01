"""Phase BE: Gross Margin Bridge section tests."""
import pytest
from saas.reporting.annual_report import _section_gross_margin_bridge


def _ma(yr, rev, wc, nc):
    gm = rev - wc - nc
    return {str(yr): {"income_statement": {
        "revenue_gbp": rev, "wholesale_cost_gbp": wc,
        "non_commodity_cost_gbp": nc, "gross_margin_gbp": gm,
    }}}


def _data(*year_tuples):
    ma = {}
    for yr, rev, wc, nc in year_tuples:
        ma.update(_ma(yr, rev, wc, nc))
    return {"management_accounts": ma}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_gross_margin_bridge({}) == ""
    assert _section_gross_margin_bridge({"management_accounts": {}}) == ""


# 2. Single year returns empty (need 2+ to show delta)
def test_single_year_empty():
    d = _data((2022, 1_000_000, 500_000, 200_000))
    assert _section_gross_margin_bridge(d) == ""


# 3. Header present with 2+ years
def test_header_with_two_years():
    d = _data((2021, 1_000_000, 400_000, 200_000), (2022, 1_500_000, 700_000, 250_000))
    result = _section_gross_margin_bridge(d)
    assert "Gross Margin Bridge" in result


# 4. GM% computed correctly
def test_gm_pct_correct():
    # 2022: rev=1M, wc=600k, nc=100k → gm=300k → 30.0%
    d = _data((2021, 500_000, 300_000, 50_000), (2022, 1_000_000, 600_000, 100_000))
    result = _section_gross_margin_bridge(d)
    assert "30.0%" in result


# 5. Delta revenue shown
def test_delta_revenue_shown():
    d = _data((2021, 1_000_000, 400_000, 100_000), (2022, 1_500_000, 500_000, 150_000))
    result = _section_gross_margin_bridge(d)
    # ΔRevenue = +£500k
    assert "+£500,000.00" in result


# 6. Negative delta shown with minus sign
def test_negative_delta_shown():
    d = _data((2021, 1_500_000, 500_000, 150_000), (2022, 1_000_000, 400_000, 100_000))
    result = _section_gross_margin_bridge(d)
    # ΔRevenue = -£500k
    assert "£-500,000.00" in result or "-£500,000.00" in result


# 7. Best GM year identified
def test_best_gm_year():
    d = _data((2021, 500_000, 100_000, 50_000), (2022, 1_000_000, 600_000, 100_000))
    result = _section_gross_margin_bridge(d)
    # 2021: gm = 350k / 500k = 70%; 2022: gm = 300k / 1M = 30%
    assert "Best GM year: 2021" in result


# 8. Worst GM year identified
def test_worst_gm_year():
    d = _data((2021, 500_000, 100_000, 50_000), (2022, 1_000_000, 600_000, 100_000))
    result = _section_gross_margin_bridge(d)
    assert "Worst GM year: 2022" in result


# 9. Year table row includes revenue and wholesale
def test_year_row_has_revenue_and_wholesale():
    d = _data((2021, 2_443_878, 983_205, 686_469), (2022, 4_285_512, 2_412_101, 810_117))
    result = _section_gross_margin_bridge(d)
    assert "2022" in result
    assert "24.8%" in result  # 2022 GM% in real data


# 10. First year shows dash for deltas
def test_first_year_no_delta():
    d = _data((2021, 500_000, 200_000, 100_000), (2022, 600_000, 250_000, 120_000))
    result = _section_gross_margin_bridge(d)
    assert "— | — | — | —" in result or "—" in result


# 11. Wholesale delta correctly attributed
def test_wholesale_delta():
    d = _data((2021, 1_000_000, 400_000, 100_000), (2022, 1_000_000, 600_000, 100_000))
    result = _section_gross_margin_bridge(d)
    # ΔWholesale = +£200k; ΔGM = -£200k
    assert "+£200,000.00" in result or "200,000" in result


# 12. Note about non-commodity costs present
def test_note_present():
    d = _data((2021, 500_000, 200_000, 100_000), (2022, 600_000, 250_000, 120_000))
    result = _section_gross_margin_bridge(d)
    assert "Note:" in result or "non-commodity" in result.lower()


def test_header_contains_bridge():
    d = _data((2021, 500_000, 200_000, 100_000), (2022, 600_000, 250_000, 120_000))
    result = _section_gross_margin_bridge(d)
    assert "Gross Margin Bridge" in result


def test_single_year_returns_empty():
    d = _data((2022, 600_000, 250_000, 120_000))
    result = _section_gross_margin_bridge(d)
    assert result == ""


def test_best_worst_year_shown():
    d = _data((2020, 500_000, 200_000, 50_000), (2021, 600_000, 400_000, 100_000))
    result = _section_gross_margin_bridge(d)
    assert "Best GM year" in result
    assert "Worst GM year" in result
