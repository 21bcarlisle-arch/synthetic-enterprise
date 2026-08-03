"""MINOR-9: sitemap.xml 404'd while robots.txt invited normal indexing.

Expert-Hour finding (docs/design/maturity_map.yaml :: SITE1_expert_doors
expert_hour.findings):

  MINOR-9 "all evidentiary content is JS-only with no <noscript> fallback ...
          sitemap.xml 404s while robots.txt invites normal indexing, so a non-JS
          crawler indexes 'Loading...' as the content of the evidence pages."

The <noscript> half is tested at the door (site/proof/test_site1_proof_citations.py,
which asserts the served markup AND that every endpoint the fallback advertises
actually exists). This file covers the site-wide half: the sitemap must exist, be
valid, list the canonical doors, and -- the part that makes it more than a
formality -- every URL it advertises must correspond to a page that ACTUALLY
EXISTS in the repo. A sitemap pointing a crawler at a 404 is the same defect class
as MAJOR-7's dead citations, aimed at a machine instead of a person.

R15: each control is proven to fire on its own named defect, on a SCRATCH copy of
the document -- never by mutating the real file. Absence-style assertions (the
exclusion rules) carry a non-emptiness floor first, because an empty or truncated
sitemap would satisfy them vacuously -- the classic FAIL-OPEN shape.

ANTI-PIN: no URL count and no lastmod is asserted; the sitemap is hand-authored and
deliberately publishes no lastmod (a stale unfalsifiable date would breach R14's
spirit), so nothing here can wedge on regenerated data.
"""
from __future__ import annotations

import re
import xml.etree.ElementTree as ET
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[2]
SITE = PROJECT / "site"
SITEMAP = SITE / "sitemap.xml"
ROBOTS = SITE / "robots.txt"
REDIRECTS = SITE / "_redirects"

NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"
CANONICAL_HOST = "https://poesys.net"

# Directories kept in-repo for reference but 301'd away by site/_redirects -- listing
# any of them in the sitemap would advertise a dead-end URL to a crawler.
REDIRECTED_LEGACY = ("/method/", "/simplified/", "/project/", "/tours/", "/wip-flow/",
                     "/platform/", "/method-casebook/", "/supplier/", "/sim/")
# Off-nav / internal surfaces that must never be advertised.
NEVER_ADVERTISED = ("/director/", "/shadow/")


def _locs(text: str) -> list[str]:
    root = ET.fromstring(text)
    return [el.text for el in root.iter(NS + "loc")]


@pytest.fixture(scope="module")
def sitemap_text() -> str:
    # FAIL-SILENT/FAIL-OPEN floor: a missing sitemap is a FAILED check, and every
    # exclusion assertion below would otherwise pass on an empty document.
    assert SITEMAP.is_file(), "site/sitemap.xml does not exist -- MINOR-9 is not closed"
    text = SITEMAP.read_text()
    assert _locs(text), "sitemap.xml parses but lists no <loc> -- exclusion checks would be vacuous"
    return text


# ===========================================================================
# The sitemap exists, parses, and covers the canonical door set
# ===========================================================================
def test_sitemap_is_valid_xml_and_lists_the_canonical_doors(sitemap_text):
    locs = _locs(sitemap_text)
    for door in (CANONICAL_HOST + "/", CANONICAL_HOST + "/proof/",
                 CANONICAL_HOST + "/company/", CANONICAL_HOST + "/world/"):
        assert door in locs, f"canonical door {door!r} missing from sitemap.xml"


def test_every_advertised_url_is_a_page_that_actually_exists(sitemap_text):
    """The control that makes the sitemap more than a formality: advertising a URL
    that 404s is MAJOR-7's defect class pointed at a crawler."""
    missing = []
    for loc in _locs(sitemap_text):
        assert loc.startswith(CANONICAL_HOST), f"non-canonical host in sitemap: {loc}"
        rel = loc[len(CANONICAL_HOST):].strip("/")
        page = SITE / "index.html" if not rel else SITE / rel / "index.html"
        if not page.is_file():
            missing.append(loc)
    assert missing == [], f"sitemap advertises URL(s) with no page in the repo: {missing}"


def test_the_existence_check_fires_on_an_advertised_ghost_page(sitemap_text):
    """R15: prove the control above can FAIL, on a SCRATCH copy of the document."""
    ghost = CANONICAL_HOST + "/no-such-door/"
    mutated = sitemap_text.replace("</urlset>", f"  <url><loc>{ghost}</loc></url>\n</urlset>")
    missing = []
    for loc in _locs(mutated):
        rel = loc[len(CANONICAL_HOST):].strip("/")
        page = SITE / "index.html" if not rel else SITE / rel / "index.html"
        if not page.is_file():
            missing.append(loc)
    assert missing == [ghost], f"the ghost-page control did not fire: {missing}"


# ===========================================================================
# Exclusions: redirected legacy doors and off-nav surfaces
# ===========================================================================
def test_sitemap_excludes_redirected_legacy_doors_and_offnav_surfaces(sitemap_text):
    joined = " ".join(_locs(sitemap_text))
    for killed in REDIRECTED_LEGACY:
        assert killed not in joined, f"redirected legacy door {killed!r} must not be advertised"
    for private in NEVER_ADVERTISED:
        assert private not in joined, f"{private!r} is off-nav/internal, must not be advertised"


def test_the_exclusion_control_fires_on_a_reintroduced_legacy_door(sitemap_text):
    """R15: the exclusion rule must be able to fail."""
    mutated = sitemap_text.replace(
        "</urlset>", f"  <url><loc>{CANONICAL_HOST}/method/</loc></url>\n</urlset>")
    joined = " ".join(_locs(mutated))
    assert "/method/" in joined
    with pytest.raises(AssertionError):
        for killed in REDIRECTED_LEGACY:
            assert killed not in joined


def test_no_advertised_url_is_itself_a_redirect_source(sitemap_text):
    """Independent oracle: derive the redirect sources from site/_redirects itself
    rather than from the hardcoded list above, so a NEW redirect added later cannot
    silently leave a stale sitemap entry behind."""
    assert REDIRECTS.is_file(), "site/_redirects missing -- cannot cross-check"
    sources = set()
    for line in REDIRECTS.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[0].startswith("/"):
            sources.add(parts[0].rstrip("*").rstrip("/") or "/")
    assert len(sources) > 3, f"parsed only {len(sources)} redirect sources -- oracle is empty"
    clashes = []
    for loc in _locs(sitemap_text):
        rel = "/" + loc[len(CANONICAL_HOST):].strip("/")
        if rel != "/" and rel in sources:
            clashes.append(loc)
    assert clashes == [], f"sitemap advertises URL(s) that site/_redirects 301s away: {clashes}"


# ===========================================================================
# The OTHER direction: a public door that exists must be advertised
# ===========================================================================
def _redirect_sources() -> set[str]:
    """Redirect sources parsed from site/_redirects (independent oracle)."""
    assert REDIRECTS.is_file(), "site/_redirects missing -- cannot cross-check"
    sources = set()
    for line in REDIRECTS.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) >= 2 and parts[0].startswith("/"):
            sources.add(parts[0].rstrip("*").rstrip("/") or "/")
    assert len(sources) > 3, f"parsed only {len(sources)} redirect sources -- oracle is empty"
    return sources


def _public_doors_on_disk() -> set[str]:
    """Every door directory that actually ships a page, minus the two documented
    exclusion classes. DERIVED from the repo, never hand-typed -- that is the whole
    point: a hand-typed list would need editing by the same change that adds a door,
    which is precisely the edit that gets forgotten."""
    redirected = _redirect_sources()
    doors = set()
    for page in SITE.glob("*/index.html"):
        rel = "/" + page.parent.name + "/"
        if rel.rstrip("/") in redirected or rel in REDIRECTED_LEGACY or rel in NEVER_ADVERTISED:
            continue
        doors.add(rel)
    assert doors, "no public doors discovered on disk -- this control would be vacuous"
    return doors


def test_every_public_door_on_disk_is_advertised(sitemap_text):
    """The missing half of the sitemap contract, and a real fail-open closed.

    Every control above checks that what IS advertised is legitimate. NOTHING checked
    that a legitimate door is advertised AT ALL -- so a new public door could ship,
    be linked from the front door, serve 200, and never appear in the sitemap.

    That is not merely an SEO nit here, because `site/live_pixel_verify.py` DERIVES
    its door list from this sitemap (`canonical_doors()`). An unlisted door is
    therefore never live-pixel-verified by a default run: the R11 control silently
    skips it while reporting "N/N doors verified". Found live on 2026-08-03 --
    /evidence/ (linked six times from the front-door diagram, serving 200) was absent
    from this file and thus outside the verifier's coverage entirely.
    """
    advertised = {loc[len(CANONICAL_HOST):] for loc in _locs(sitemap_text)}
    unlisted = sorted(_public_doors_on_disk() - advertised)
    assert unlisted == [], (
        f"public door(s) exist on disk but are not advertised: {unlisted}. "
        "An unlisted door is also invisible to site/live_pixel_verify.py, which derives "
        "its door list from this sitemap -- so it is never verified against the live surface."
    )


def test_the_unlisted_door_control_fires_on_a_dropped_entry(sitemap_text):
    """R15: prove the control above can FAIL, on a SCRATCH copy of the document.

    Drops a door that genuinely exists on disk and asserts the check reports exactly
    that door -- a control that passes on a mutilated sitemap would be theatre.
    """
    victim = sorted(_public_doors_on_disk())[0]
    mutated = sitemap_text.replace(
        f"  <url><loc>{CANONICAL_HOST}{victim}</loc></url>\n", "")
    assert mutated != sitemap_text, f"mutation did not apply for {victim}"
    advertised = {loc[len(CANONICAL_HOST):] for loc in _locs(mutated)}
    assert sorted(_public_doors_on_disk() - advertised) == [victim]


# ===========================================================================
# robots.txt points at the real sitemap, and its crawler policy is untouched
# ===========================================================================
def test_robots_points_at_the_sitemap():
    text = ROBOTS.read_text()
    m = re.search(r"^Sitemap:\s*(\S+)\s*$", text, re.M)
    assert m, "robots.txt has no Sitemap: directive -- MINOR-9 is not closed"
    assert m.group(1) == CANONICAL_HOST + "/sitemap.xml", m.group(1)
    # And that URL must resolve to the file this test suite just validated.
    assert SITEMAP.is_file()


def test_the_existing_crawler_policy_is_not_weakened_by_the_fix():
    """The MINOR-9 fix adds one directive; it must not have relaxed the
    DIRECTOR_ANSWERS_ENTITY_CRAWLERS AI-training blocks."""
    text = ROBOTS.read_text()
    for bot in ("GPTBot", "ClaudeBot", "Google-Extended", "CCBot",
                "Applebot-Extended", "PerplexityBot", "Bytespider"):
        block = re.search(r"User-agent:\s*" + re.escape(bot) + r"\s*\nDisallow:\s*/", text)
        assert block, f"AI-training block for {bot} is missing or weakened"
    assert re.search(r"User-agent:\s*\*\s*\nAllow:\s*/", text), "normal-search Allow lost"
