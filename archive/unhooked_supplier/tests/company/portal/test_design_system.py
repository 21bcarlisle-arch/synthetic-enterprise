"""Phase QO: Website Integrity Part B -- design system across portal + shadow.

PRIORITIES.md P1 remaining scope: one coherent design system (consistent nav,
typography, spacing, palette, KPI cards, RAG chips) across the customer portal
and the four shadow sections. base.html centralizes tokens/components for the
portal; every one of the 19 portal templates now extends it.
"""
from pathlib import Path

from starlette.testclient import TestClient

from company.portal.app import app

client = TestClient(app, raise_server_exceptions=True)

TEMPLATES = Path("company/portal/templates")

CUSTOMER_PAGES = [
    "dashboard.html", "billing.html", "bills.html", "consumption.html",
    "statement.html", "tariff_compare.html", "direct_debit.html", "contact.html",
    "smart_meter.html", "payment_confirm.html", "tariff_switch_confirm.html",
]
ADMIN_PAGES = [
    "admin.html", "admin_complaints.html", "admin_collections.html",
    "admin_renewals.html", "admin_retention.html", "admin_vulnerability.html",
    "regulatory.html", "trading.html",
]

EXTENDS_MARKER = '{% extends "base.html" %}'


def test_base_template_exists():
    assert (TEMPLATES / "base.html").exists()


def test_base_template_defines_design_tokens():
    html = (TEMPLATES / "base.html").read_text()
    for token in ("--navy", "--blue", "--green", "--red", "--amber", "--grey", "--surface"):
        assert token in html


def test_base_template_defines_shared_components():
    html = (TEMPLATES / "base.html").read_text()
    for cls in (".kpi-card", ".kpi-grid", ".rag-chip", ".rag-green", ".rag-amber",
                ".rag-red", ".banner", ".btn", "nav.site-nav"):
        assert cls in html


def test_all_customer_and_admin_pages_extend_base():
    for name in CUSTOMER_PAGES + ADMIN_PAGES:
        html = (TEMPLATES / name).read_text()
        assert EXTENDS_MARKER in html, name


def test_login_extends_base():
    html = (TEMPLATES / "login.html").read_text()
    assert EXTENDS_MARKER in html


def test_customer_pages_use_shared_nav_class():
    for name in CUSTOMER_PAGES:
        html = (TEMPLATES / name).read_text()
        assert "site-nav" in html, name


def test_admin_pages_link_back_to_admin_overview():
    for name in ADMIN_PAGES:
        html = (TEMPLATES / name).read_text()
        assert 'href="/admin"' in html, name


def test_dashboard_renders_with_design_system_classes():
    r = client.get("/account/C1")
    assert r.status_code == 200
    assert "site-nav" in r.text
    assert "kpi-card" in r.text or "No invoices" in r.text


def test_regulatory_rag_chip_renders_for_compliance_status():
    r = client.get("/regulatory")
    assert r.status_code == 200
    assert "rag-chip" in r.text
    assert any(s in r.text for s in ("COMPLIANT", "AT_RISK", "BREACH"))


def test_admin_retention_uses_rag_chip_for_risk_tiers():
    r = client.get("/admin/retention")
    assert r.status_code == 200
    assert "rag-chip" in r.text
    assert "rag-red" in r.text or "rag-amber" in r.text or "rag-green" in r.text


def test_active_nav_link_marked_per_page():
    r = client.get("/admin/collections")
    assert r.status_code == 200
    assert 'href="/admin/collections" class="active"' in r.text


def test_all_templates_have_no_stray_inline_style_blocks():
    for name in CUSTOMER_PAGES + ADMIN_PAGES + ["login.html"]:
        html = (TEMPLATES / name).read_text()
        assert "<style>" not in html, name + " still has an inline style block"
