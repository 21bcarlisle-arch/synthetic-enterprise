"""Tests for Phase QO shadow-side design system (PRIORITIES.md P1):
kpi-card/kpi-grid and rag-chip give the shadow mirror the same component
vocabulary as the customer portal's design system (company/portal/templates/
base.html), plus population_anchoring.json (Phase PQ/PR/PS) surfaced as
rag-chips on the Sim tab for the first time."""
from tools.generate_shadow_html import build_index, build_sim, CSS, _population_anchoring_rag


def _dash():
    return {
        "portfolio": {
            "net_margin_gbp": 100.0, "gross_margin_gbp": 200.0, "enterprise_value_gbp": 300.0,
            "treasury_start_gbp": 10.0, "treasury_end_gbp": 20.0, "bills_total": 5,
            "churn_count": 1, "retention_offers": 2, "retention_retained": 2,
            "cost_to_serve_gbp": 3.0,
        },
        "insights": {"executive_summary": "", "insights": []},
        "build": {"current_phase": "QO", "test_count": 1, "company_modules": 1},
        "financial": {"annual": []},
        "meta": {"git_commit": "abc1234"},
    }


def test_css_defines_kpi_and_rag_chip_components():
    assert ".kpi-card" in CSS
    assert ".kpi-grid" in CSS
    assert ".rag-chip" in CSS
    assert ".rag-green" in CSS and ".rag-amber" in CSS and ".rag-red" in CSS


def test_build_index_renders_headline_metrics_as_kpi_cards():
    html = build_index(_dash(), "ts")
    assert "kpi-card" in html
    assert "kpi-grid" in html
    assert "&pound;100" in html


def test_population_anchoring_rag_empty_when_no_data():
    assert _population_anchoring_rag({}) == ""
    assert _population_anchoring_rag(None) == ""


def test_population_anchoring_rag_renders_overall_chip():
    pa = {
        "overall_rag": "RED",
        "long_run_comparison": {"ratio": 0.47, "rag": "GREEN"},
        "bad_debt_vs_benchmark": [{"year": 2020, "bad_debt_pct": 0.5, "rag": "GREEN"}],
    }
    html = _population_anchoring_rag(pa)
    assert "rag-chip rag-red" in html
    assert "RED" in html
    assert "rag-chip rag-green" in html


def test_build_sim_includes_population_anchoring_section_when_provided():
    sim_data = {"annual": [], "monthly": [], "peak_records": [], "metadata": {}}
    pa = {"overall_rag": "AMBER", "bad_debt_vs_benchmark": [{"year": 2021, "bad_debt_pct": 1.0, "rag": "AMBER"}]}
    html = build_sim(sim_data, "ts", population_anchoring=pa)
    assert "Population Anchoring" in html
    assert "rag-chip rag-amber" in html


def test_build_sim_omits_population_anchoring_section_when_absent():
    sim_data = {"annual": [], "monthly": [], "peak_records": [], "metadata": {}}
    html = build_sim(sim_data, "ts")
    assert "Population Anchoring vs Real UK Market Benchmarks" not in html

