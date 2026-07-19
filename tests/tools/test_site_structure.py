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


# --- SITE1_expert_doors mobile pass (SITE_CONSTITUTION.md door 8, cross-cutting) ---
# Structural guard so a future edit to one of these doors can't silently drop
# its phone-legible layout (R15: must be able to FAIL -- a page missing the
# block fails this test, proven by removing the block from any one file below).
SITE1_DOORS_WITH_MOBILE_PASS = [
    # (method-casebook retired 2026-07-20 -- redundant combined Method+Simplified surface)
    "company", "proof", "world", "method", "glossary", "tours",
]


def test_site1_expert_doors_have_mobile_pass():
    missing = []
    for door in SITE1_DOORS_WITH_MOBILE_PASS:
        text = (SITE / door / "index.html").read_text()
        if "@media (max-width: 640px)" not in text:
            missing.append(door)
    assert missing == [], f"SITE1 doors missing the mobile @media(max-width:640px) pass: {missing}"
