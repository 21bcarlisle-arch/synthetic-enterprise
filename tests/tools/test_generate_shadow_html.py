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


# --- DIRECTOR_ANSWERS_ENTITY_CRAWLERS.md (2026-07-12): copyright footer ---


def test_build_index_has_copyright_footer():
    html = build_index(_dash(), "2026-07-04T12:00:00Z")
    assert "Poesys Platforms. All rights reserved." in html
    assert "Poesys Platforms Ltd" not in html  # not incorporated yet -- no "Ltd" suffix


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


def test_2021_22_crisis_supplier_failure_count_is_single_sourced():
    """COLD_EYES_PROTOCOL same-page/cross-page reconciliation class (the
    "11-vs-13" class): a CRO cold-walk found the same external fact (UK
    suppliers that failed in the 2021-22 crisis) stated FIVE different ways
    across site/index.html, site/sim/, site/project/ (twice), and
    site/timeline/ -- "29", "28", "30+", "roughly 30", "around 30". No
    anchored citation exists in ASSUMPTIONS.md for an exact figure, so this
    guards consistency of the hedged phrasing ("around 30") rather than
    asserting a specific unanchored digit."""
    import re
    from pathlib import Path
    repo_root = Path(__file__).resolve().parents[2]
    pages = [
        repo_root / "site" / "index.html",
        repo_root / "site" / "data" / "proof.json",  # (v4) sim/ retired -> Proof (data-driven, section-12) carries the fact
        repo_root / "site" / "project" / "index.html",
        repo_root / "site" / "world" / "index.html",  # (v4) timeline retired -> world carries the fact
    ]
    bad_pattern = re.compile(r"\b(29|28|30\+)\b.{0,20}(real )?(UK )?suppliers?")
    for page in pages:
        text = page.read_text()
        assert not bad_pattern.search(text), f"{page} uses an inconsistent supplier-failure count"
    # (v4) count the CONSISTENT hedged phrasing "around 30 ... suppliers" the control guards --
    # robust to each door's verb ("failed"/"to exit"/"ended ~30 suppliers") since consistency of
    # the hedge, not a specific verb, is the point.
    mentions_fact = [p for p in pages if re.search(r"around 30[^<]{0,40}suppliers?", p.read_text())]
    assert len(mentions_fact) >= 3  # sanity: this must actually be checking real mentions


def test_every_static_site_page_has_the_copyright_footer():
    """DIRECTOR_ANSWERS_ENTITY_CRAWLERS.md: 'Footer site-wide' -- structural
    guard so a future page addition can't silently omit it."""
    import glob
    from pathlib import Path
    repo_root = Path(__file__).resolve().parents[2]
    pages = sorted(glob.glob(str(repo_root / "site" / "*.html"))) + sorted(
        glob.glob(str(repo_root / "site" / "*" / "index.html"))
    )
    pages = [p for p in pages if "/shadow/" not in p]
    assert len(pages) >= 10  # sanity: this must actually be scanning real pages
    missing = [p for p in pages if "Poesys Platforms" not in Path(p).read_text()]
    assert missing == [], f"pages missing the copyright footer: {missing}"
