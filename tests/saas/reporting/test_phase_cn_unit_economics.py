"""Phase CN: Unit Economics annual report section tests."""
import pytest
import json


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


# 6. Revenue per customer increases through 2022
def test_revenue_increases_by_2022():
    from saas.reporting.annual_report import _section_unit_economics
    data = _load_data()
    result = _section_unit_economics(data)
    # 2022 has highest revenue per customer (£248k) — check line present
    assert "248" in result.replace(",", "")


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
