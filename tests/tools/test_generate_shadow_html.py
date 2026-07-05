"""Tests for freshness stamps on site/shadow/ pages (Phase QF, Part C of the
website-integrity fix): every page footer must name the git commit + phase it
was generated from, not just a bare timestamp, so a stale surface is
identifiable without cross-referencing another page."""
from tools.generate_shadow_html import (
    build_index, build_customers, build_supplier, build_sim, build_project,
)


def _dash(git_commit="abc1234", phase="QF"):
    return {
        "meta": {"git_commit": git_commit},
        "build": {"current_phase": phase, "test_count": 12345, "company_modules": 400},
        "portfolio": {
            "net_margin_gbp": 100.0, "gross_margin_gbp": 200.0, "enterprise_value_gbp": 300.0,
            "treasury_start_gbp": 10.0, "treasury_end_gbp": 20.0, "bills_total": 5,
            "churn_count": 1, "retention_offers": 1, "retention_retained": 1,
            "cost_to_serve_gbp": 1.0,
        },
        "insights": {"executive_summary": "test summary", "insights": []},
        "financial": {"annual": [], "ledger": {}, "segment_annual": []},
        "customers": {"lifetime": {}, "events": [], "retention": []},
        "run_history": [],
    }


def test_build_index_footer_has_freshness_stamp():
    html = build_index(_dash(), "2026-07-04T12:00:00Z")
    assert "Run abc1234" in html
    assert "Phase QF" in html


def test_build_customers_footer_has_freshness_stamp():
    html = build_customers(_dash(), {"customers": {}}, "2026-07-04T12:00:00Z")
    assert "Run abc1234" in html
    assert "Phase QF" in html


def test_build_supplier_footer_has_freshness_stamp():
    html = build_supplier(_dash(), "2026-07-04T12:00:00Z")
    assert "Run abc1234" in html
    assert "Phase QF" in html


def test_build_sim_footer_has_freshness_stamp():
    sim_data = {"annual": [], "monthly": [], "peak_records": [], "metadata": {}}
    html = build_sim(sim_data, "2026-07-04T12:00:00Z", "abc1234", "QF")
    assert "Run abc1234" in html
    assert "Phase QF" in html


def test_build_project_footer_has_freshness_stamp():
    html = build_project(_dash(), "some latest.md text", "2026-07-04T12:00:00Z")
    assert "Run abc1234" in html
    assert "Phase QF" in html


def test_footer_shows_unknown_when_meta_missing():
    """Absence of meta must not crash generation -- it should degrade to '?'."""
    html = build_index({
        "portfolio": {}, "insights": {}, "financial": {"annual": []},
    }, "ts")
    assert "Run ?" in html
    assert "Phase ?" in html


def test_shadow_page_uses_v4_light_design_system():
    """WEBSITE_AS_SHOWCASE.md Part 0 (Phase RE): the shadow mirror must share
    site/sim/index.html's light v4 tokens (:root custom properties, site-nav),
    not its own dark "advisor-verification" palette -- Rich's directive was
    that the public-facing site/ surface carries one consistent design
    language. Guards against reverting to the old dark theme."""
    html = build_index(_dash(), "2026-07-04T12:00:00Z")
    assert "--bg:#f9f9f7" in html
    assert "site-nav" in html
    assert "#1a1a1a" not in html
    assert "#2a2a4a" not in html
