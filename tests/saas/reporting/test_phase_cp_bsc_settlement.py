"""Phase CP: BSC Settlement Exposure report section tests."""
import json
import pytest


def _load_data():
    with open("docs/reports/run_output_latest.json") as f:
        return json.load(f)


def _render():
    from saas.reporting.annual_report import _section_bsc_settlement_exposure
    return _section_bsc_settlement_exposure(_load_data())


# 1. Section renders without error
def test_renders():
    result = _render()
    assert isinstance(result, str)
    assert len(result) > 100


# 2. Contains header
def test_header():
    assert "BSC Settlement" in _render()


# 3. Table has correct columns
def test_table_columns():
    result = _render()
    assert "BSC Credit Required" in result
    assert "Peak Daily" in result
    assert "% of Revenue" in result


# 4. All years appear
def test_all_years():
    result = _render()
    for yr in ["2016", "2017", "2022", "2025"]:
        assert yr in result


# 5. The reported peak is the ACTUAL peak in the data it was given
def test_peak_credit_matches_the_data():
    """WAS `test_2022_peak_credit`, pinning "2022" and "10," against the live run output.

    It went red on 2026-08-26 when the director's I&C suspension took the industrial volume
    off the book: BSC credit cover tracks portfolio size, so the peak moved from 2022 (~£10k)
    to 2025 (£401). Nothing malfunctioned -- the test was asserting a fact about a book the
    company no longer has, which is a change-detector on a DIAGNOSTIC output (R12), not a
    check of the section.

    What is worth pinning is that the rendered sentence agrees with the table above it. The
    expected peak is RE-DERIVED here from the same run data rather than read back from the
    renderer -- independence, or this would pass against a section that reported any year at
    all (R15 TAUTOLOGY).
    """
    data = _load_data()
    years = data["years"]
    expected_year = max(years, key=lambda y: years[y].get("bsc_credit_required_gbp", 0))
    expected_gbp = years[expected_year]["bsc_credit_required_gbp"]
    result = _render()
    assert "**Peak BSC credit requirement:** {} at £{:,.0f}".format(
        expected_year, expected_gbp) in result


def test_the_peak_sentence_only_blames_the_price_surge_when_the_peak_IS_the_surge():
    """The partner for the fix in `_section_bsc_settlement_exposure`.

    The sentence used to carry "(portfolio growth and 2021-22 price surge)" for whatever year
    came out on top, so the published report read "2025 at £401 (portfolio growth and 2021-22
    price surge)" -- a cause three years before its effect. The clause is now conditional on
    the peak year actually being 2021 or 2022.
    """
    result = _render()
    peak_line = [ln for ln in result.splitlines() if "Peak BSC credit requirement" in ln][0]
    years = _load_data()["years"]
    peak_year = max(years, key=lambda y: years[y].get("bsc_credit_required_gbp", 0))
    if str(peak_year) in ("2021", "2022"):
        assert "price surge" in peak_line
    else:
        assert "price surge" not in peak_line, (
            "the report is blaming the 2021-22 surge for a {} peak: {}".format(
                peak_year, peak_line))


# 6. 2025 flagged as << (0.51% > 0.40% threshold)
def test_high_ratio_flagged():
    result = _render()
    # 2025: 0.51% ratio should be flagged
    assert "<<" in result


# 7. Peak year identified in summary
def test_peak_year_identified():
    result = _render()
    assert "Peak BSC credit" in result
    assert "2022" in result   # 2022 = highest at £10,210


# 8. Elexon reference present
def test_elexon_reference():
    result = _render()
    assert "Elexon" in result or "BSC" in result


# 9. Empty data returns empty string
def test_empty_data():
    from saas.reporting.annual_report import _section_bsc_settlement_exposure
    assert _section_bsc_settlement_exposure({}) == ""


# 10. Credit increases through portfolio growth
def test_credit_grows_with_portfolio():
    from saas.reporting.annual_report import _section_bsc_settlement_exposure
    data = _load_data()
    years = data.get("years", {})
    credit_2016 = years["2016"].get("bsc_credit_required_gbp", 0)
    credit_2022 = years["2022"].get("bsc_credit_required_gbp", 0)
    assert credit_2022 > credit_2016


# 11. Peak daily is less than credit required
def test_peak_daily_less_than_credit():
    data = _load_data()
    years = data.get("years", {})
    for yr in years.values():
        bsc = yr.get("bsc_credit_required_gbp", 0)
        peak = yr.get("bsc_peak_daily_gbp", 0)
        if bsc > 0:
            assert peak < bsc


# 12. 2017 credit appears (~£559-560)
def test_2017_credit_appears():
    result = _render()
    # Small float variations mean value is ~559-560; check 2017 row exists with £5xx
    assert "2017" in result and "£5" in result


# 13. Peak BSC year noted
def test_peak_bsc_credit_noted():
    result = _render()
    assert "Peak BSC credit" in result


# 14. Above 0.4% flag in table when applicable
def test_flag_note_present():
    result = _render()
    assert "<<" in result or "BSC credit above" in result or "elevated" in result.lower()


# 15. Year rows present in output
def test_year_rows_present():
    result = _render()
    import re
    rows = [l for l in result.splitlines() if l.startswith("| 20")]
    assert len(rows) > 0
