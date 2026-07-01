"""Phase BR: Worst Settlement Period section tests."""
import pytest
from saas.reporting.annual_report import _section_worst_settlement_periods


def _yr(date, sp, cid, loss):
    return {"worst_period": {"settlement_date": date, "settlement_period": sp,
                              "customer_id": cid, "net_margin_gbp": loss}}


def _data(*year_tuples):
    return {"years": {str(2016 + i): _yr(*t) for i, t in enumerate(year_tuples)}}


# 1. Empty returns empty
def test_empty_returns_empty():
    assert _section_worst_settlement_periods({}) == ""
    assert _section_worst_settlement_periods({"years": {}}) == ""


# 2. Header present
def test_header_present():
    d = _data(("2022-12-31", 1, "C_IC3g", -2969.97))
    assert "Worst Half-Hourly Settlement Period" in _section_worst_settlement_periods(d)


# 3. Year row present
def test_year_row():
    d = _data(("2022-12-31", 1, "C_IC3g", -2969.97))
    result = _section_worst_settlement_periods(d)
    assert "| 2016 |" in result


# 4. Customer ID in row
def test_customer_id():
    d = _data(("2022-12-31", 1, "C_IC3g", -2969.97))
    result = _section_worst_settlement_periods(d)
    assert "C_IC3g" in result


# 5. Negative loss shown with minus
def test_negative_loss_format():
    d = _data(("2022-12-31", 1, "C_IC3g", -2969.97))
    result = _section_worst_settlement_periods(d)
    assert "-£2,970" in result or "-£2,969" in result


# 6. Single worst period flagged
def test_worst_period_flagged():
    d = _data(
        ("2022-12-31", 1, "C_IC3g", -2969.97),
        ("2023-12-31", 1, "C_IC3g", -3474.99),
    )
    result = _section_worst_settlement_periods(d)
    assert "Single worst period" in result and "2017" in result


# 7. SP column correct
def test_sp_column():
    d = _data(("2022-12-31", 1, "C_IC3g", -2969.97))
    result = _section_worst_settlement_periods(d)
    assert "| 1 |" in result


# 8. Date column correct
def test_date_column():
    d = _data(("2022-12-31", 1, "C_IC3g", -2969.97))
    result = _section_worst_settlement_periods(d)
    assert "2022-12-31" in result


# 9. SP note present
def test_sp_note_present():
    d = _data(("2022-12-31", 1, "C_IC3g", -2969.97))
    result = _section_worst_settlement_periods(d)
    assert "SP =" in result or "settlement period" in result


# 10. Multiple years sorted
def test_years_sorted():
    d = _data(
        ("2016-11-08", 40, "C6", -0.36),
        ("2022-12-31", 1, "C_IC3g", -2969.97),
    )
    result = _section_worst_settlement_periods(d)
    pos_2016 = result.find("| 2016 |")
    pos_2017 = result.find("| 2017 |")
    assert pos_2016 < pos_2017


# 11. Positive loss in table row shows without minus
def test_positive_loss_no_minus():
    d = _data(("2016-11-08", 40, "C6", 100.5))
    result = _section_worst_settlement_periods(d)
    # table row should have £100 without minus sign in column
    lines = [l for l in result.split("\n") if "| 2016 |" in l]
    assert lines and "-£100" not in lines[0]


# 12. Missing worst_period year skipped
def test_missing_worst_period_skipped():
    data = {"years": {"2016": {}, "2017": _yr("2017-01-01", 12, "C1", -50.0)}}
    result = _section_worst_settlement_periods(data)
    assert "| 2017 |" in result
    assert "| 2016 |" not in result


# 13. Single worst period shown in summary
def test_single_worst_period_summary():
    d = {"years": {"2022": {"worst_period": {
        "settlement_date": "2022-12-01", "settlement_period": 36,
        "customer_id": "C1", "net_margin_gbp": -450.0
    }}}}
    result = _section_worst_settlement_periods(d)
    assert "Single worst period" in result or "worst period" in result.lower()


# 14. Negative margin shown as loss
def test_negative_margin_formatted():
    d = {"years": {"2022": {"worst_period": {
        "settlement_date": "2022-12-01", "settlement_period": 36,
        "customer_id": "C1", "net_margin_gbp": -750.0
    }}}}
    result = _section_worst_settlement_periods(d)
    assert "-£750" in result or "750" in result


# 15. Years without worst_period skipped gracefully
def test_missing_worst_period_year_skipped():
    d = {"years": {
        "2021": {},
        "2022": {"worst_period": {"settlement_date": "2022-10-01",
                                   "settlement_period": 20, "customer_id": "C2",
                                   "net_margin_gbp": -300.0}},
    }}
    result = _section_worst_settlement_periods(d)
    assert "| 2022 |" in result
    assert "| 2021 |" not in result
