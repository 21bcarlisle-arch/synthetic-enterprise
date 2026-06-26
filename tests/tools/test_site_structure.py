"""Phase 263 tests: four-section site structure -- nav bar, customers portal, project page."""
import json
from pathlib import Path

SITE = Path(__file__).resolve().parents[2] / "site"


def test_customers_index_exists():
    assert (SITE / "customers" / "index.html").exists()


def test_customers_index_has_login_form():
    text = (SITE / "customers" / "index.html").read_text()
    assert "doLogin" in text
    assert "acc" in text


def test_customers_index_has_site_nav():
    text = (SITE / "customers" / "index.html").read_text()
    assert "site-nav" in text or "nav-link" in text


def test_project_index_exists():
    assert (SITE / "project" / "index.html").exists()


def test_project_index_has_investor_kpis():
    text = (SITE / "project" / "index.html").read_text()
    assert "inv-kpis" in text or "investor" in text.lower()


def test_project_index_has_charts():
    text = (SITE / "project" / "index.html").read_text()
    assert "chart-tests" in text or 'id="ct"' in text


def test_customer_index_json_exists():
    assert (SITE / "data" / "customers" / "_index.json").exists()


def test_customer_json_accounts_present():
    index = json.loads((SITE / "data" / "customers" / "_index.json").read_text())
    assert "C1" in index
    assert "C_IC1" in index


def test_customer_json_c1_valid():
    d = json.loads((SITE / "data" / "customers" / "C1.json").read_text())
    assert d["account_id"] == "C1"
    assert d["segment"] in ("resi", "I&C", "SME")
    assert d["lifetime_revenue_gbp"] > 0


def test_phases_json_exists():
    assert (SITE / "data" / "phases.json").exists()


def test_phases_json_has_test_progression():
    d = json.loads((SITE / "data" / "phases.json").read_text())
    assert len(d["test_progression"]) > 10
    assert d["total_phases"] > 200


def test_main_dashboard_has_site_nav():
    text = (SITE / "index.html").read_text()
    assert "site-nav" in text


def test_generate_customer_data_module():
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
    from tools.generate_customer_data import generate
    assert callable(generate)
