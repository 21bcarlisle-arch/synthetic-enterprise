"""R15 for the published-surface reachability control (`tools/site_reachability.py`).

THE CONTROL'S OWN NAMED DEFECT, from the document that asked for it
(DIRECTOR_OBSERVATION_PUBLISHED_SURFACE_NAV_AND_STAMPS_2026-08-12, item 1): nine knowledge
pages existed, rendered and passed their tests; eight had no route in from anywhere a
reader could start, and the defect was found by the director looking at the live site. His
ask: "If a control could make 'a published page with no route in' fail at build time rather
than be found by the director looking at the site, that is worth more than the fix.
Whatever you build must be deliberately breakable and shown to go red."

So every control here is proven to FIRE on its own named defect, and — the half that makes
it more than theatre — proven NOT to fire on the healthy shape, so it is not a test that is
simply always red. The three R15 killer patterns are each targeted:

  TAUTOLOGY   — `test_a_route_only_a_script_can_build_is_not_a_route` and
                `test_a_page_reachable_only_from_an_EXCLUDED_page_is_still_an_orphan`:
                reachability is derived from real markup links out of pages a reader can
                actually get to, never from the page's own claim to be published.
  FAIL-OPEN   — the four `REFUSES` tests: a missing front door, a population under the
                floor, and a front door that reaches nothing all RAISE rather than report
                a clean site. An empty or moved `site/` must never read as "no orphans".
  FAIL-SILENT — `test_a_STALE_EXCLUSION_is_itself_a_failure`: the one hand-authored list in
                the module cannot rot into an allowlist for pages that no longer exist.

EVERY MUTATION RUNS ON A SCRATCH COPY of a synthetic site, never on `site/` — the discipline
`test_site1_proof_crawlability.py` already sets in this repo, and the reason the real
surface cannot be damaged by a test run. `test_the_live_site_...` is the one test that reads
the real tree, and it only READS.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from tools import site_reachability as sr

PROJECT = Path(__file__).resolve().parents[2]
LIVE_SITE = PROJECT / "site"


# --------------------------------------------------------------------------------------
# A synthetic site, so the mutations describe a shape rather than today's page list.
# --------------------------------------------------------------------------------------

def _page(title: str, links: list[str] = (), script_links: list[str] = ()) -> str:
    """One page. `script_links` go inside a <script>, which must NOT count as routes."""
    anchors = "\n".join(f'<a href="{h}">{h}</a>' for h in links)
    js = "".join(f"out += '<a href=\"{h}\">x</a>';" for h in script_links)
    script = f"<script>var out='';{js}</script>" if script_links else ""
    return f"<!DOCTYPE html><html><head><title>{title}</title></head><body>{anchors}{script}</body></html>"


@pytest.fixture()
def scratch(tmp_path: Path, monkeypatch) -> Path:
    """A healthy site: front door routes to every page that is expected to be routed.

    Deliberately >= MIN_PAGES so the non-emptiness floor is satisfied and the tests below
    exercise the ORPHAN logic rather than the refusal logic (which has its own tests).

    STRUCTURAL_EXCLUSIONS IS EMPTIED FOR THE SCRATCH SITE, and the emptying is the honest
    choice rather than a convenience: those entries name real files under `site/`, so
    against a fixture they would ALL read as stale and every scratch assertion would be
    about the live exclusion list instead of about the shape under test. The live list
    keeps its own guard — `test_every_STRUCTURAL_EXCLUSION_names_a_page_that_exists` runs
    it against the real tree, so emptying it here removes no coverage. Tests that need an
    exclusion add one explicitly with `monkeypatch.setitem`, so what is excluded in any
    scratch test is visible in that test.
    """
    monkeypatch.setattr(sr, "STRUCTURAL_EXCLUSIONS", {})
    root = tmp_path / "site"
    (root / "knowledge").mkdir(parents=True)
    doors = ["world", "company", "proof", "glossary", "now", "evidence", "privacy", "customers"]
    (root / "index.html").write_text(_page("home", [f"./{d}/" for d in doors] + ["./knowledge/"]))
    for d in doors:
        (root / d).mkdir()
        (root / d / "index.html").write_text(_page(d, ["../"]))
    (root / "knowledge" / "index.html").write_text(_page("knowledge", ["../", "./topic-a/"]))
    (root / "knowledge" / "topic-a").mkdir()
    (root / "knowledge" / "topic-a" / "index.html").write_text(_page("topic-a", ["../"]))
    return root


def test_the_scratch_fixture_is_HEALTHY_so_a_red_below_means_the_mutation(scratch: Path):
    """NOT-ALWAYS-RED. Without this every assertion below could pass on a broken control."""
    assert sr.check(scratch) == []
    assert sr.orphans(scratch) == []


# --------------------------------------------------------------------------------------
# The named defect: a page with no route in.
# --------------------------------------------------------------------------------------

def test_a_NEW_PAGE_WITH_NO_ROUTE_IN_is_caught(scratch: Path):
    """THE defect the director found, in the form it would arrive: someone adds a page."""
    (scratch / "knowledge" / "topic-b").mkdir()
    (scratch / "knowledge" / "topic-b" / "index.html").write_text(_page("topic-b", ["../"]))

    assert sr.orphans(scratch) == ["knowledge/topic-b/index.html"]
    assert any("NO ROUTE IN" in f for f in sr.check(scratch))


def test_LINKING_THE_NEW_PAGE_RELEASES_IT(scratch: Path):
    """The release direction. A control whose failure cannot be cleared teaches nothing."""
    (scratch / "knowledge" / "topic-b").mkdir()
    (scratch / "knowledge" / "topic-b" / "index.html").write_text(_page("topic-b", ["../"]))
    assert sr.orphans(scratch) == ["knowledge/topic-b/index.html"]

    index = scratch / "knowledge" / "index.html"
    index.write_text(_page("knowledge", ["../", "./topic-a/", "./topic-b/"]))

    assert sr.orphans(scratch) == []


def test_THE_WHOLE_SECTION_STRANDS_when_its_only_route_in_is_cut(scratch: Path):
    """The live shape exactly: the section index exists, nothing links to the section.

    This is why the fix was one route and not eight — and why the control reports both
    pages rather than only the index a reader would have landed on.
    """
    doors = ["world", "company", "proof", "glossary", "now", "evidence", "privacy", "customers"]
    (scratch / "index.html").write_text(_page("home", [f"./{d}/" for d in doors]))

    assert sr.orphans(scratch) == [
        "knowledge/index.html",
        "knowledge/topic-a/index.html",
    ]


def test_a_page_reachable_only_from_an_EXCLUDED_page_is_still_an_orphan(scratch: Path, monkeypatch):
    """TAUTOLOGY GUARD. An excluded page is not a reader's starting point, so it cannot
    hand a route to anything else. Were exclusions to propagate reachability, an orphan
    could be 'published' by linking it from the 404 page."""
    monkeypatch.setitem(sr.STRUCTURAL_EXCLUSIONS, "attic.html", "test fixture: excluded")
    (scratch / "attic.html").write_text(_page("attic", ["./secret/"]))
    (scratch / "secret").mkdir()
    (scratch / "secret" / "index.html").write_text(_page("secret", ["../"]))

    assert sr.orphans(scratch) == ["secret/index.html"]


def test_a_route_only_a_SCRIPT_can_build_is_not_a_route(scratch: Path):
    """CONSERVATISM, and the bug found while writing this module.

    A link a reader can only follow if JS runs is not a route in for a crawler or for a
    reader whose JS failed. Counting it would OVERSTATE reachability, and an overstated
    reachability is a MISSED orphan — fail-open in the only direction that matters here.
    """
    (scratch / "js-only").mkdir()
    (scratch / "js-only" / "index.html").write_text(_page("js-only", ["../"]))
    doors = ["world", "company", "proof", "glossary", "now", "evidence", "privacy", "customers"]
    (scratch / "index.html").write_text(
        _page("home", [f"./{d}/" for d in doors] + ["./knowledge/"], script_links=["./js-only/"])
    )

    assert sr.orphans(scratch) == ["js-only/index.html"]


# --------------------------------------------------------------------------------------
# The exclusions are DERIVED. Each source is proven live, not hardcoded.
# --------------------------------------------------------------------------------------

def test_a_REDIRECTED_AWAY_directory_is_excluded_and_says_why(scratch: Path):
    """`_redirects` is the author's own declaration that a directory is retired."""
    (scratch / "legacy").mkdir()
    (scratch / "legacy" / "index.html").write_text(_page("legacy", ["../"]))
    assert sr.orphans(scratch) == ["legacy/index.html"]

    (scratch / "_redirects").write_text("/legacy /proof/ 301\n/legacy/* /proof/ 301\n")

    assert sr.orphans(scratch) == []
    assert "_redirects" in sr.excluded("legacy/index.html", sr.redirect_sources(scratch))


def test_DELETING_THE_REDIRECT_RULE_makes_the_page_an_orphan_again(scratch: Path):
    """The derivation is LIVE. If the exclusion were copied into this module by hand, the
    page would stay excluded after the declaration that justified it was withdrawn."""
    (scratch / "legacy").mkdir()
    (scratch / "legacy" / "index.html").write_text(_page("legacy", ["../"]))
    (scratch / "_redirects").write_text("/legacy /proof/ 301\n")
    assert sr.orphans(scratch) == []

    (scratch / "_redirects").write_text("# the rule was withdrawn\n")

    assert sr.orphans(scratch) == ["legacy/index.html"]


def test_an_ABSENT_redirects_file_excludes_NOTHING(scratch: Path):
    """FAIL-OPEN guard on the derivation itself: a missing declaration must narrow the
    exclusion set to empty, never widen it to everything."""
    assert sr.redirect_sources(scratch) == set()
    assert not (scratch / "_redirects").exists()

    (scratch / "orphan.html").write_text(_page("orphan"))

    assert sr.orphans(scratch) == ["orphan.html"]


def test_the_WWW_CANONICALISATION_rule_is_not_read_as_a_page_path(scratch: Path):
    """`_redirects` also carries absolute-URL rules. Parsing `https://www.poesys.net/*` as
    a path prefix would be harmless by luck here and dangerous in general."""
    (scratch / "_redirects").write_text(
        "https://www.poesys.net/* https://poesys.net/:splat 301\n/favicon.ico /favicon.svg 301\n"
    )
    (scratch / "orphan.html").write_text(_page("orphan"))

    assert sr.orphans(scratch) == ["orphan.html"]


def test_a_META_REFRESH_page_is_a_signpost_and_not_a_destination(scratch: Path):
    """Derived from the page's OWN markup — the same declaration the browser obeys."""
    (scratch / "moved").mkdir()
    (scratch / "moved" / "index.html").write_text(
        '<html><head><meta http-equiv="refresh" content="0; url=../world/">'
        '</head><body><a href="../world/">moved</a></body></html>'
    )

    assert "moved/index.html" in sr.redirect_pages(scratch)
    assert sr.orphans(scratch) == []


def test_REMOVING_THE_REFRESH_META_makes_it_an_orphan_again(scratch: Path):
    """The derivation is live, not a name-based excuse."""
    (scratch / "moved").mkdir()
    (scratch / "moved" / "index.html").write_text(
        '<html><head><meta http-equiv="refresh" content="0; url=../world/"></head><body></body></html>'
    )
    assert sr.orphans(scratch) == []

    (scratch / "moved" / "index.html").write_text(_page("no longer a signpost"))

    assert sr.orphans(scratch) == ["moved/index.html"]


def test_an_UNWRITTEN_page_is_COUNTED_but_NOT_EXCUSED_from_the_orphan_rule(scratch: Path):
    """THE ANTI-LAUNDERING TEST, and the one this module got wrong on the first pass.

    A page byte-identical to the stub template is reported as unwritten AND, if nothing
    routes to it, is still an orphan. Were `unwritten` an exclusion, an unfinished section
    could be stranded indefinitely behind a green verdict — the control deciding a content
    question in whichever direction made its own answer clean.
    """
    # The template moved OUT of the published tree on 2026-08-20 -- it was being deployed, so
    # the site served a stub at its own URL and every page-scanning control carried an
    # exemption for it. Written where the module now looks, relative to the site root.
    template = (scratch / sr.STUB_TEMPLATE).resolve()
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text(_page("stub template"))
    (scratch / "knowledge" / "topic-b").mkdir()
    (scratch / "knowledge" / "topic-b" / "index.html").write_text(_page("stub template"))

    assert sr.unwritten_pages(scratch) == {"knowledge/topic-b/index.html"}
    assert "knowledge/topic-b/index.html" in sr.orphans(scratch)


def test_ROUTING_an_unwritten_page_clears_the_orphan_and_KEEPS_the_count(scratch: Path):
    """Both halves of the treatment: routing answers the reachability question and leaves
    the content debt still visible, so a routed stub cannot read as a written page."""
    # The template moved OUT of the published tree on 2026-08-20 -- it was being deployed, so
    # the site served a stub at its own URL and every page-scanning control carried an
    # exemption for it. Written where the module now looks, relative to the site root.
    template = (scratch / sr.STUB_TEMPLATE).resolve()
    template.parent.mkdir(parents=True, exist_ok=True)
    template.write_text(_page("stub template"))
    (scratch / "knowledge" / "topic-b").mkdir()
    (scratch / "knowledge" / "topic-b" / "index.html").write_text(_page("stub template"))
    (scratch / "knowledge" / "index.html").write_text(
        _page("knowledge", ["../", "./topic-a/", "./topic-b/"])
    )

    assert sr.orphans(scratch) == []
    assert sr.unwritten_pages(scratch) == {"knowledge/topic-b/index.html"}


# --------------------------------------------------------------------------------------
# FAIL-CLOSED. Every degenerate input raises instead of reporting a clean site.
# --------------------------------------------------------------------------------------

def test_REFUSES_when_the_front_door_is_missing(scratch: Path):
    (scratch / "index.html").unlink()

    with pytest.raises(sr.ReachabilityError, match="entry point"):
        sr.orphans(scratch)


def test_REFUSES_a_population_under_the_floor(tmp_path: Path):
    """A moved or renamed site directory must not read as a healthy one."""
    root = tmp_path / "site"
    root.mkdir()
    (root / "index.html").write_text(_page("home"))

    with pytest.raises(sr.ReachabilityError, match="floor"):
        sr.orphans(root)


def test_REFUSES_when_the_front_door_reaches_NOTHING(scratch: Path):
    """A markup/parser failure would otherwise be reported as ~everything orphaned — a
    true failure for an entirely wrong reason, sending the reader to the pages instead of
    to the parse."""
    (scratch / "index.html").write_text("<html><body>no anchors at all</body></html>")

    with pytest.raises(sr.ReachabilityError, match="reaches no other page"):
        sr.orphans(scratch)


def test_a_STALE_EXCLUSION_is_itself_a_failure(scratch: Path, monkeypatch):
    """FAIL-SILENT guard. The one hand-authored list here must not outlive its pages, or it
    becomes an allowlist for whatever later takes that filename."""
    monkeypatch.setitem(sr.STRUCTURAL_EXCLUSIONS, "gone.html", "test fixture: never existed")

    assert sr.stale_exclusions(scratch) == ["gone.html"]
    assert any("STALE EXCLUSION" in f for f in sr.check(scratch))


# --------------------------------------------------------------------------------------
# The live surface.
# --------------------------------------------------------------------------------------

def test_every_STRUCTURAL_EXCLUSION_names_a_page_that_exists():
    """The rot guard, run against the real site rather than a fixture."""
    assert sr.stale_exclusions(LIVE_SITE) == []


def test_the_LIVE_KNOWLEDGE_SECTION_is_reachable_from_the_front_door():
    """Item 1, pinned to the surface the director actually named.

    The generic control above would go green again if the knowledge section were deleted;
    this one asserts the section EXISTS and every one of its pages is routed, which is what
    "the Knowledge section has no route in" asked for.
    """
    population = sr.page_population(LIVE_SITE)
    reachable, _ = sr.crawl(LIVE_SITE, population)
    knowledge = {p for p in population if p.startswith("knowledge/")}
    assert len(knowledge) >= 9, f"knowledge section floor: only {len(knowledge)} page(s)"
    assert "knowledge/index.html" in reachable, "the section index is not reachable"

    # The authoring template is excluded by name and the moved-page signpost by its own
    # markup; both are legitimately unrouted, so the section's claim is about the rest.
    signposts = sr.redirect_pages(LIVE_SITE)
    retired = sr.redirect_sources(LIVE_SITE)
    stranded = sorted(
        p for p in knowledge - reachable - signposts
        if sr.excluded(p, retired) is None
    )
    assert not stranded, f"knowledge pages with no route in: {stranded}"


def test_the_UNWRITTEN_COUNT_is_a_RATCHET_that_can_only_shrink():
    """Content debt, held visible. 7 stub-identical knowledge pages measured 2026-08-12;
    this fails if an eighth is deployed, and is tightened as they are written."""
    unwritten = sr.unwritten_pages(LIVE_SITE)
    assert len(unwritten) <= 7, f"a new unwritten page was deployed: {sorted(unwritten)}"
    assert all(p.startswith("knowledge/") for p in unwritten), sorted(unwritten)


def test_the_LIVE_SITE_has_no_published_page_without_a_route_in():
    """THE control. Whole-tree, so a brand-new orphan page fails here and not on the
    director's screen. Reads the real site; writes nothing."""
    assert sr.check(LIVE_SITE) == []


def test_every_SITEMAP_url_is_actually_reachable_from_the_front_door():
    """The sitemap's own promise, enforced: "the front door plus every surface reachable
    from it". A sitemap advertising a page a reader cannot navigate to is item 1 aimed at a
    machine instead of at a person."""
    import re as _re

    sitemap = (LIVE_SITE / "sitemap.xml").read_text()
    locs = _re.findall(r"<loc>([^<]+)</loc>", sitemap)
    assert len(locs) >= 5, f"sitemap floor: only {len(locs)} url(s), refusing a vacuous pass"

    population = sr.page_population(LIVE_SITE)
    reachable, _ = sr.crawl(LIVE_SITE, population)
    unreachable = []
    for loc in locs:
        path = loc.split("poesys.net", 1)[-1].lstrip("/")
        page = f"{path}{sr.ENTRY}" if path in ("", *(f"{d}/" for d in ())) or path.endswith("/") or path == "" else path
        page = page or sr.ENTRY
        if page not in reachable:
            unreachable.append(loc)
    assert not unreachable, f"sitemap advertises unreachable page(s): {unreachable}"
