"""Phase 267 tests: Year filter on Financial, Trading, Customers tabs."""
from pathlib import Path

SITE = Path(__file__).resolve().parents[2] / "site"


def _html():
    return (SITE / "index.html").read_text()


def test_year_btns_helper_present():
    """yearBtnsHtml() helper generates year buttons for reuse across tabs."""
    html = _html()
    assert "function yearBtnsHtml" in html


def test_financial_tab_uses_year_btns():
    """renderFinancial injects year selector and filters annual data."""
    html = _html()
    idx = html.index("function renderFinancial")
    idx_next = html.index("function render", idx + 1)
    fn = html[idx:idx_next]
    assert "yearBtnsHtml()" in fn
    assert "YEAR_FILTER" in fn
    assert "faAll.filter" in fn


def test_trading_tab_uses_year_btns():
    """renderTrading injects year selector and filters spot/hedge data."""
    html = _html()
    idx = html.index("function renderTrading")
    idx_next = html.index("function render", idx + 1)
    fn = html[idx:idx_next]
    assert "yearBtnsHtml()" in fn
    assert "YEAR_FILTER" in fn


def test_customers_tab_uses_year_btns():
    """renderCustomers injects year selector and filters events/retention."""
    html = _html()
    idx = html.index("function renderCustomers")
    idx_next = html.index("function render", idx + 1)
    fn = html[idx:idx_next]
    assert "yearBtnsHtml()" in fn
    assert "YEAR_FILTER" in fn


def test_trading_spot_monthly_year_filtered():
    """Spot monthly data filtered to selected year via startsWith."""
    html = _html()
    idx = html.index("function renderTrading")
    idx_next = html.index("function render", idx + 1)
    fn = html[idx:idx_next]
    assert "startsWith" in fn
    assert "smAll.filter" in fn


def test_customers_events_year_filtered():
    """Customer events and retention filtered to selected year."""
    html = _html()
    idx = html.index("function renderCustomers")
    idx_next = html.index("function render", idx + 1)
    fn = html[idx:idx_next]
    assert "startsWith" in fn
    assert "_sortedEvents.filter" in fn


def test_select_year_clears_tab_cache():
    """selectYear clears rendered cache for financial/trading/customers and re-renders."""
    html = _html()
    assert "delete rendered" in html
    # All three filterable tabs are covered
    idx = html.index("function selectYear")
    idx_next = html.index("function render", idx + 1)
    fn = html[idx:idx_next]
    assert "'financial'" in fn
    assert "'trading'" in fn
    assert "'customers'" in fn


def test_mkchart_destroys_existing_instance():
    """mkChart destroys any existing Chart.js instance to allow tab re-render."""
    html = _html()
    assert "Chart.getChart" in html
    assert ".destroy()" in html
