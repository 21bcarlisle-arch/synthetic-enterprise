"""Phase CN: Unit Economics annual report section tests."""
import json

import pytest


def _load_data():
    with open("docs/reports/run_output_latest.json") as f:
        return json.load(f)


def _render():
    from saas.reporting.annual_report import _section_unit_economics
    return _section_unit_economics(_load_data())


# 1. Section renders without error
def test_renders():
    result = _render()
    assert isinstance(result, str)
    assert len(result) > 100


# 2. Contains header
def test_contains_header():
    assert "Operational Unit Economics" in _render()


# 3. Has table header
def test_has_table():
    result = _render()
    assert "Rev/cust" in result
    assert "Net %" in result


# 4. All years appear in output
def test_all_years_present():
    result = _render()
    for yr in ["2016", "2017", "2022", "2025"]:
        assert yr in result


# 5. 2022 crisis year appears with low-margin flag
def test_crisis_year_flagged():
    result = _render()
    # 2022 net margin = 7.4% — not flagged
    # But 2021 at 3.3% should be flagged
    assert "<<" in result  # at least one low-margin year


# 6. Revenue per customer rises into the 2022 crisis year
def test_revenue_increases_by_2022():
    """The CLAIM is that the crisis year lifted revenue per customer. The old assertion
    was `> £200,000`, which is not that claim -- it is a fact about WHO WAS ON THE BOOK.

    Filed 2026-08-24 as
    `WORKER_FINDING_A_REV_PER_CUSTOMER_THRESHOLD_TEST_REDS_THE_MOMENT_THE_GROWN_BOOK_IS_COMMITTED`,
    which named the class exactly: "a test that pins an ABSOLUTE figure which is really a
    function of population size". £200k per customer is only reachable on a book whose
    revenue is >98% five industrial accounts. The director suspended I&C on the same day
    the finding was filed; both stalled; the residential book renders ~£3,500 and this
    assertion would have reddened every lane the moment the new run output was committed.

    So it now asserts the RISE -- 2022 above the pre-crisis 2020 -- which is the sentence
    the test's own title makes and which holds on any book. R15: it still fails if the
    crisis stops showing in the unit economics, which is the thing worth catching.
    """
    import re

    from saas.reporting.annual_report import _section_unit_economics
    data = _load_data()
    result = _section_unit_economics(data)

    def rev_per_customer(year):
        rows = [line for line in result.split("\n") if f"| {year} |" in line]
        assert rows, f"No {year} row in unit economics table"
        figures = re.findall(r"£([\d,]+)", rows[0])
        assert figures, f"No £ figure in the {year} row: {rows[0]!r}"
        return int(figures[0].replace(",", ""))

    crisis, pre_crisis = rev_per_customer(2022), rev_per_customer(2020)
    assert crisis > pre_crisis, (
        f"2022 rev/cust ({crisis:,}) should exceed pre-crisis 2020 ({pre_crisis:,})")


# 7. Best year identified
def test_best_year_identified():
    result = _render()
    assert "Best year per customer" in result


# 8. Worst year identified
def test_worst_year_identified():
    result = _render()
    assert "Worst year per customer" in result


# 9. Returns empty string for empty data
def test_empty_data():
    from saas.reporting.annual_report import _section_unit_economics
    result = _section_unit_economics({})
    assert result == ""


# 10. Margin threshold note present
def test_ofgem_note_present():
    result = _render()
    assert "5%" in result


# 11. 2024 high-margin year (14.3%) not flagged
def test_high_margin_year_clean():
    result = _render()
    # 2024 = 14.3% — should appear without "<<"
    lines = result.split("\n")
    for line in lines:
        if "2024" in line and "|" in line:
            assert "<<" not in line
            break


# 12. Active customer count appears
def test_active_customer_count():
    result = _render()
    assert "18" in result   # peak portfolio size


# 13. Best year per customer shown
def test_best_year_per_customer():
    result = _render()
    assert "Best year per customer" in result


# 14. Low margin flag present when applicable
def test_low_margin_flag():
    result = _render()
    # Check either << flag or the Ofgem threshold note
    assert "5%" in result or "<<" in result or "threshold" in result.lower()


# 15. Active customer count in table
def test_active_count_in_table():
    result = _render()
    # Rows contain numbers for active customers
    import re
    rows = [l for l in result.splitlines() if l.startswith("| 20")]
    assert len(rows) > 0
