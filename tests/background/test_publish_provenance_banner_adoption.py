"""R15 for the banner-adoption rule (`background.publish_provenance.banner_adoption_violations`).

WHAT WENT WRONG, AND WHY THIS FILE IS SEPARATE FROM ITS SIBLING
---------------------------------------------------------------
`WORKER_FINDING_THE_FRESHNESS_BANNER_REACHES_NO_PAGE_AND_ITS_CONTROL_ASKS_FIVE_DELETED_DOORS`
(2026-08-21). The rule used to be five hand-typed names -- company, proof, world, now, project --
asserted directly in `test_publish_provenance.py`. `03dd8c49e` deleted all five on the director's
ruling, so the check raised `FileNotFoundError` and its red said MISSING PAGE while the property
was in fact violated: after the consolidation the banner was on no page at all. A control that is
red for the wrong reason is not a loud control, it is an ABSENT one.

It is its own file for two reasons, both mechanical rather than tidy:

  * `tools/pre_commit_test_gate.py::SITE_SURFACE_TESTS` names this file, so **any** staged
    `site/**.html` now runs it. The old rule sat in a file nothing routinely selected -- the
    finding's own diagnosis of why the wrongness survived a day -- and naming the 15-test sibling
    on every page edit would have been a tax nobody kept.
  * `tests_for()`'s suffix glob (`test_<stem>_*.py`) still selects it from
    `background/publish_provenance.py`, so both edges that can break the rule reach it.

THE MEASUREMENT THAT JUSTIFIES THE REWRITE, not an assertion about it: run the derived rule over
the tree the five names were RIGHT about (`03dd8c49e^`) and it finds **24** live-data pages, of
which exactly those five carried the banner and **19 did not**. The hand-typed list was not merely
stale after the ruling -- it was green on a tree where four fifths of the population was
uncovered, including the front door. That is `test_the_typed_five_were_blind_to_nineteen_pages`.
"""
from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

import pytest

from background import publish_provenance as prov

RULING = "03dd8c49e"  # "The five tabs are the site now" -- the commit that retired the five doors
TYPED_FIVE = ("company", "now", "project", "proof", "world")


# ── fixtures: a minimal site we can mutate ────────────────────────────────────
def _page(body: str) -> str:
    return f"<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n{body}\n</head>\n<body></body>\n</html>\n"


BANNER_TAG = '<script src="{hop}assets/freshness-banner.js" defer></script>'
LIVE_READ = '<script>fetch("{hop}data/dashboard.json").then(function(r){{return r.json();}});</script>'


@pytest.fixture
def site(tmp_path: Path) -> Path:
    """One live-data page, correctly banner-ed, one depth down. The CLEAN baseline every
    mutation below departs from by exactly one edit."""
    root = tmp_path / "site"
    (root / "assets").mkdir(parents=True)
    (root / "assets" / "freshness-banner.js").write_text("/* the layer */", encoding="utf-8")
    (root / "data").mkdir()
    door = root / "capabilities"
    door.mkdir()
    door.joinpath("index.html").write_text(
        _page(BANNER_TAG.format(hop="../") + "\n" + LIVE_READ.format(hop="../")), encoding="utf-8")
    return root


# The shipped register describes the shipped site, so every fixture below passes an EMPTY one --
# otherwise each mutation test would also report the real snapshot exemption as missing from the
# fixture, and each assertion would be satisfied by that instead of by its own mutation.
NO_EXEMPT: dict = {}


def test_the_baseline_fixture_is_clean(site: Path):
    """THE NULL CONTROL for every mutation below. If the untouched fixture already reported a
    violation, each mutation test would pass on the fixture's own defect and prove nothing about
    the mutation it names."""
    assert prov.banner_adoption_violations(site, NO_EXEMPT) == []
    assert prov.live_data_pages(site, NO_EXEMPT) == ("capabilities/index.html",)


# ── the shipped assertion ─────────────────────────────────────────────────────
def test_the_shipped_site_has_no_live_data_page_that_cannot_say_how_old_it_is():
    """The property in the director's words (DIRECTOR_RULING_PUBLISH_DECOUPLING, property 3):
    a visitor can always tell WHAT they are seeing and HOW current it is."""
    violations = prov.banner_adoption_violations()
    assert violations == [], "\n".join(violations)


def test_the_shipped_population_is_not_empty_and_is_every_page_that_reads_a_feed():
    """Guards the shipped assertion above against passing vacuously -- zero pages checked is the
    way this control fails without failing."""
    pages = prov.live_data_pages()
    assert len(pages) >= 4, pages
    assert "index.html" in pages, "the front door reads dashboard.json and is in the population"


# ── MUTATION 1: the defect the finding is about ───────────────────────────────
def test_a_live_data_page_without_the_banner_is_reported(site: Path):
    """The named defect: a page renders live figures and states nothing about their age."""
    page = site / "capabilities" / "index.html"
    page.write_text(page.read_text(encoding="utf-8").replace(
        BANNER_TAG.format(hop="../"), ""), encoding="utf-8")
    violations = prov.banner_adoption_violations(site, NO_EXEMPT)
    assert any("capabilities/index.html" in v and "loads no freshness banner" in v
               for v in violations), violations


# ── MUTATION 2: presence is not the property ──────────────────────────────────
def test_a_banner_reference_with_the_wrong_hop_count_is_reported(site: Path):
    """A SUBSTRING-PRESENCE control would pass here, and the page would 404 the layer silently --
    which the layer's own docstring names as its cardinal failure mode. The src is resolved."""
    page = site / "capabilities" / "index.html"
    page.write_text(page.read_text(encoding="utf-8").replace(
        'src="../assets/', 'src="../../assets/'), encoding="utf-8")
    violations = prov.banner_adoption_violations(site, NO_EXEMPT)
    assert any("does not exist" in v for v in violations), violations


def test_a_root_absolute_banner_reference_is_accepted(site: Path):
    """The counter-mutation: resolving an absolute src against the PAGE's directory reports every
    one of the five retired doors as broken. Both conventions are legal; the doc root is the site
    root. Without this the control would be red on a tree where the property held."""
    page = site / "capabilities" / "index.html"
    page.write_text(page.read_text(encoding="utf-8").replace(
        'src="../assets/', 'src="/assets/'), encoding="utf-8")
    assert prov.banner_adoption_violations(site, NO_EXEMPT) == []


# ── MUTATION 3: the rule must not fire on everything ──────────────────────────
def test_a_page_that_renders_no_live_figure_is_not_in_the_population(site: Path):
    """A rule that demanded a banner on every page would be green on this site for a reason that
    has nothing to do with freshness. /privacy/ and /404/ render nothing live and owe nothing."""
    (site / "privacy").mkdir()
    (site / "privacy" / "index.html").write_text(_page("<title>Privacy</title>"), encoding="utf-8")
    assert "privacy/index.html" not in prov.live_data_pages(site, NO_EXEMPT)
    assert prov.banner_adoption_violations(site, NO_EXEMPT) == []


def test_an_evidence_link_to_a_json_file_is_not_a_rendered_figure(site: Path):
    """The discrimination that keeps the rule off a correct page: linking to `data/x.json` so a
    reader can open it is not a freshness claim. Only a script-side READ is."""
    (site / "method").mkdir()
    (site / "method" / "index.html").write_text(
        _page('<a href="../data/capabilities.json">capabilities.json</a>'), encoding="utf-8")
    assert "method/index.html" not in prov.live_data_pages(site, NO_EXEMPT)


# ── MUTATION 4: the call shape must not be the detector ───────────────────────
def test_a_feed_read_through_a_wrapper_is_still_in_the_population(site: Path):
    """FAIL-OPEN THIS CLOSES, taken from the real page rather than invented: `site/company/
    index.html` at `03dd8c49e^` read all five of its feeds through
    `function jget(url){ return fetch(url+"?t="+Date.now()); }` and names no URL inside a
    `fetch(` at all. A detector keyed on one call shape is one refactor from blind."""
    (site / "company").mkdir()
    (site / "company" / "index.html").write_text(_page(
        '<script>function jget(u){return fetch(u+"?t="+Date.now()).then(function(r){'
        'return r.json();});}\njget("../data/company.json").then(render);</script>'),
        encoding="utf-8")
    assert "company/index.html" in prov.live_data_pages(site, NO_EXEMPT)
    assert any("company/index.html" in v for v in prov.banner_adoption_violations(site, NO_EXEMPT))


# ── MUTATION 5: the vacuity floor ─────────────────────────────────────────────
def test_a_site_with_no_live_data_page_fails_rather_than_passing(tmp_path: Path):
    """THE FAILURE THIS CONTROL WOULD OTHERWISE HAVE. Pointed at the wrong tree, or broken in its
    own derivation, it finds nothing and certifies the site clean. Zero subjects is a violation."""
    empty = tmp_path / "site"
    empty.mkdir()
    violations = prov.banner_adoption_violations(empty, NO_EXEMPT)
    assert any("no live-data page" in v for v in violations), violations


# ── MUTATION 6: the exemption register cannot become a hole ───────────────────
def test_an_exemption_naming_an_absent_page_is_reported(site: Path):
    violations = prov.banner_adoption_violations(
        site, {"snapshots/gone.html": "a page that is not here"})
    assert any("not a page on this site" in v for v in violations), violations


def test_an_exemption_naming_a_page_that_renders_nothing_live_is_reported(site: Path):
    """An exemption that was never needed reads exactly like one that is -- so it fails, and the
    register can only ever hold pages the rule would otherwise have caught."""
    (site / "static.html").write_text(_page("<title>Static</title>"), encoding="utf-8")
    violations = prov.banner_adoption_violations(
        site, {"static.html": "claims credit for nothing"})
    assert any("renders no live figure" in v for v in violations), violations


def test_the_shipped_exemption_register_holds_only_frozen_archives():
    """The one live entry, asserted as one: a dated snapshot whose URL is its own timestamp. If
    this list grows, the growth is the thing to look at."""
    assert set(prov.BANNER_EXEMPT) == {"snapshots/DASHBOARD_20260623_120151.html"}


# ── the historical discrimination, on bytes any clone can rebuild ─────────────
@pytest.mark.skipif(shutil.which("git") is None, reason="git not available")
def test_the_typed_five_were_blind_to_nineteen_pages(tmp_path: Path):
    """MEASURED AGAINST THE RETIRED SUBJECT, not against a live 200 no tree can reproduce.

    `git archive 03dd8c49e^` is the tree the five hand-typed names were right about. Over it the
    DERIVED rule finds 24 live-data pages: the five carry the banner, nineteen do not. So the old
    control was green on a tree where the property was violated on four fifths of its own
    population -- the front door among them. That is what makes this a rewrite rather than a
    re-pointing, and it is the falsifier for the claim: if the derived rule agreed with the typed
    list on that tree, the rewrite would have bought nothing.
    """
    old = tmp_path / "old"
    old.mkdir()
    proc = subprocess.run(["git", "archive", f"{RULING}^", "site"],
                          cwd=Path(__file__).resolve().parents[2], capture_output=True)
    if proc.returncode != 0:  # shallow clone without that history
        pytest.skip(f"{RULING}^ not in this clone")
    subprocess.run(["tar", "-x", "-C", str(old), "--strip-components=1"],
                   input=proc.stdout, check=True)

    pages = prov.live_data_pages(old)
    violations = prov.banner_adoption_violations(old)
    assert len(pages) == 24, pages
    covered = {p for p in pages if not any(p in v for v in violations)}
    assert covered == {f"{d}/index.html" for d in TYPED_FIVE}, covered
    assert len(violations) == 19, violations
    assert "index.html" in {v.split()[0] for v in violations}, (
        "the front door read dashboard.json and carried no banner, while the typed list "
        "documented it as exempt for rendering no live figure")
