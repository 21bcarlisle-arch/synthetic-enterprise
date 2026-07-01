import pytest
from datetime import date
from company.billing.annual_statement import AnnualStatement, AnnualStatementBook


@pytest.fixture
def book():
    return AnnualStatementBook()


def test_generate_basic(book):
    stmt = book.generate(
        "C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed 1yr", "fixed"
    )
    assert stmt.customer_id == "C1"
    assert stmt.year == 2022
    assert stmt.consumption_kwh == 3500.0
    assert stmt.total_cost_gbp == 1200.0


def test_generate_no_prev_year(book):
    stmt = book.generate("C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed 1yr", "fixed")
    assert stmt.prev_year_consumption_kwh is None
    assert stmt.consumption_change_pct is None


def test_consumption_change_pct(book):
    stmt = book.generate(
        "C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed 1yr", "fixed",
        prev_year_consumption_kwh=3000.0
    )
    assert stmt.consumption_change_pct == pytest.approx(16.7, abs=0.2)


def test_consumption_decrease(book):
    stmt = book.generate(
        "C1", 2022, 2800.0, 1000.0, 34.0, 28.5, "Fixed 1yr", "fixed",
        prev_year_consumption_kwh=3500.0
    )
    assert stmt.consumption_change_pct is not None
    assert stmt.consumption_change_pct < 0


def test_estimated_saving_positive(book):
    # Market avg £1300, customer pays £1200 -> saving £100
    stmt = book.generate(
        "C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed 1yr", "fixed",
        market_avg_cost_gbp=1300.0
    )
    assert stmt.estimated_saving_gbp == 100.0


def test_estimated_saving_negative(book):
    # Market avg £1000, customer pays £1200 -> saving -£200 (customer paying more)
    stmt = book.generate(
        "C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "SVT", "variable",
        market_avg_cost_gbp=1000.0
    )
    assert stmt.estimated_saving_gbp == -200.0


def test_no_market_avg_means_no_saving(book):
    stmt = book.generate("C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed 1yr", "fixed")
    assert stmt.market_avg_cost_gbp is None
    assert stmt.estimated_saving_gbp is None


def test_get_statement(book):
    book.generate("C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed 1yr", "fixed")
    stmt = book.get("C1", 2022)
    assert stmt is not None
    assert stmt.customer_id == "C1"


def test_get_missing_returns_none(book):
    assert book.get("NOBODY", 2022) is None


def test_overdue_returns_missing_customers(book):
    book.generate("C1", 2021, 3500.0, 1200.0, 34.0, 28.5, "Fixed 1yr", "fixed")
    overdue = book.overdue(date(2022, 6, 1), ["C1", "C2"])
    assert "C2" in overdue
    assert "C1" not in overdue


def test_summary(book):
    book.generate("C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed 1yr", "fixed")
    book.generate("C2", 2022, 2800.0, 900.0, 30.0, 28.5, "Fixed 1yr", "fixed")
    s = book.summary(2022)
    assert s["total_issued"] == 2
    assert s["avg_consumption_kwh"] == pytest.approx(3150.0, abs=1.0)
    assert s["avg_cost_gbp"] == pytest.approx(1050.0, abs=1.0)


def test_summary_empty_year(book):
    s = book.summary(2020)
    assert s["total_issued"] == 0
    assert s["avg_consumption_kwh"] == 0.0


# --- Phase LN depth tests ---

def test_effective_unit_rate_stored(book):
    stmt = book.generate("C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed 1yr", "fixed")
    assert stmt.effective_unit_rate_ppm == pytest.approx(34.0)


def test_sc_ppd_stored(book):
    stmt = book.generate("C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed 1yr", "fixed")
    assert stmt.sc_ppd == pytest.approx(28.5)


def test_tariff_name_stored(book):
    stmt = book.generate("C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed 1yr", "fixed")
    assert stmt.tariff_name == "Fixed 1yr"


def test_tariff_type_stored(book):
    stmt = book.generate("C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed 1yr", "variable")
    assert stmt.tariff_type == "variable"


def test_prev_year_kwh_stored(book):
    stmt = book.generate(
        "C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed 1yr", "fixed",
        prev_year_consumption_kwh=3200.0
    )
    assert stmt.prev_year_consumption_kwh == pytest.approx(3200.0)


def test_market_avg_stored(book):
    stmt = book.generate(
        "C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed 1yr", "fixed",
        market_avg_cost_gbp=1350.0
    )
    assert stmt.market_avg_cost_gbp == pytest.approx(1350.0)


def test_generate_returns_statement(book):
    result = book.generate("C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed 1yr", "fixed")
    assert isinstance(result, AnnualStatement)


def test_statements_for_customer(book):
    book.generate("C1", 2021, 3200.0, 1100.0, 33.0, 28.0, "Fixed", "fixed")
    book.generate("C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed", "fixed")
    book.generate("C2", 2022, 4000.0, 1400.0, 35.0, 30.0, "SVT", "variable")
    stmts = book.statements_for_customer("C1")
    assert len(stmts) == 2


def test_issued_for_year(book):
    book.generate("C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed", "fixed")
    book.generate("C2", 2022, 4000.0, 1400.0, 35.0, 30.0, "SVT", "variable")
    issued = book.issued_for_year(2022)
    assert set(issued) == {"C1", "C2"}


def test_summary_keys(book):
    book.generate("C1", 2022, 3500.0, 1200.0, 34.0, 28.5, "Fixed", "fixed")
    s = book.summary(2022)
    for k in ("year", "total_issued", "avg_consumption_kwh", "avg_cost_gbp"):
        assert k in s
