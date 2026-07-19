"""Regression tests for NAV_STORY_PLATFORM_METHOD.md item 6/7 (Phase RQ):
Method nav link added site-wide, Project tab slims down (Company sub-tab ->
Method, Capabilities sub-tab -> Platform), Platform gains the Capabilities
register. Follows the established node-unavailable static-guard pattern
(tests/tools/test_billing_tab_fix.py) since node is gated behind an
unapprovable permission prompt in this environment."""
import re
from pathlib import Path as _P

PROJECT = _P(__file__).resolve().parents[2]

# NOTE (2026-07-19, v4 site retirement): site/platform/ retired (the old SIM/Supplier/Platform
# split the ratified brief section 6 kills; its content re-homes into The Method). Removed from
# this list and the platform-specific assertions below dropped. supplier/sim also slated to retire.
SITE_PAGES_WITH_NAV = [
    "site/index.html",
    "site/customers/index.html", "site/project/index.html",
    "site/method/index.html",
]


def _read(rel):
    return (PROJECT / rel).read_text()


def test_every_site_page_links_to_method():
    for rel in SITE_PAGES_WITH_NAV:
        html = _read(rel)
        assert 'method/' in html, rel + " missing a Method nav link"


def test_method_page_exists_and_is_well_formed():
    html = _read("site/method/index.html")
    assert "<title>Poesys -- Method</title>" in html
    m = re.search(r"<script>(.*)</script>", html, re.S)
    assert m, "method page has no script body"
    body = m.group(1)
    assert body.count("{") == body.count("}")
    assert body.count("(") == body.count(")")
    assert body.count("[") == body.count("]")


def test_method_page_fetches_method_json():
    html = _read("site/method/index.html")
    assert 'fetch("../data/method.json' in html


def test_method_page_renders_all_sections():
    html = _read("site/method/index.html")
    for fn in ["renderRoles", "renderRules", "renderLoop", "renderRetro", "renderBuild"]:
        assert "function " + fn in html, fn + " missing from method page"


def test_project_tab_company_and_capabilities_removed():
    html = _read("site/project/index.html")
    assert 'data-tab="company"' not in html
    assert 'data-tab="capabilities"' not in html
    assert 'id="tab-company"' not in html
    assert 'id="tab-capabilities"' not in html
    assert "function renderCapabilities" not in html
    assert "CAPS" not in html


def test_project_tab_still_has_timeline_system_regulatory_overview():
    html = _read("site/project/index.html")
    for tab in ["overview", "timeline", "system", "regulatory"]:
        assert 'data-tab="' + tab + '"' in html, tab + " tab missing from Project"


def test_project_overview_points_to_method():
    html = _read("site/project/index.html")
    assert '../method/' in html
    # (v4 retirement) the old '../platform/' link is removed -- platform re-homes into Method.
    assert '../platform/' not in html


def test_home_page_method_card_links_not_placeholder():
    html = _read("site/index.html")
    assert "coming next" not in html.lower()
    assert 'href="./method/"' in html
