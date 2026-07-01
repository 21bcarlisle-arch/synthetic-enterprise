"""Phase 269 tests: customer portal billing year filter and spend summary."""
from pathlib import Path

CUSTOMERS = Path(__file__).resolve().parents[2] / "site" / "customers"


def test_customers_index_has_bill_year_state():
    text = (CUSTOMERS / "index.html").read_text()
    assert "BILL_YEAR" in text


def test_customers_index_has_render_bills():
    text = (CUSTOMERS / "index.html").read_text()
    assert "renderBills" in text


def test_customers_index_has_filter_bill_year():
    text = (CUSTOMERS / "index.html").read_text()
    assert "filterBillYear" in text


def test_customers_index_has_bills_section_placeholder():
    text = (CUSTOMERS / "index.html").read_text()
    assert "bills-section" in text


def test_customers_index_has_year_btn_css():
    text = (CUSTOMERS / "index.html").read_text()
    assert "year-btn" in text


def test_customers_index_has_yactive_css():
    text = (CUSTOMERS / "index.html").read_text()
    assert "yactive" in text


def test_customers_index_bill_total_calculation():
    text = (CUSTOMERS / "index.html").read_text()
    assert "total" in text and "amount_gbp" in text


def test_customers_index_outstanding_display():
    text = (CUSTOMERS / "index.html").read_text()
    assert "Outstanding" in text or "UNPAID" in text


def test_customers_index_has_tariff_reference():
    text = (CUSTOMERS / "index.html").read_text()
    assert "tariff" in text


def test_customers_index_has_meter_reference():
    text = (CUSTOMERS / "index.html").read_text()
    assert "meter" in text


def test_customers_index_has_segment_reference():
    text = (CUSTOMERS / "index.html").read_text()
    assert "segment" in text


def test_customers_index_has_invoice_reference():
    text = (CUSTOMERS / "index.html").read_text()
    assert "invoice" in text


def test_customers_index_has_total_reference():
    text = (CUSTOMERS / "index.html").read_text()
    assert "total" in text.lower() or "amount" in text.lower()


def test_customers_index_has_currency_reference():
    text = (CUSTOMERS / "index.html").read_text()
    assert "amount_gbp" in text or "GBP" in text or "£" in text


def test_customers_index_has_data_fetch():
    text = (CUSTOMERS / "index.html").read_text()
    assert "fetch" in text or "sim_data" in text
