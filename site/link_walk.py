#!/usr/bin/env python3
"""R11 internal link-walk -- DIAGNOSTIC (not yet a publish gate).

Director ruling 2026-07-23 (WORDS->DIAGRAM->EVIDENCE / SITE_MODEL_SPINE):
  "one canonical page per URL; legacy pages redirect; zero old-format leaks.
   Add an R11 link-walk to the publish gate: every internal link on every
   published page resolves to a canonical current page, or the publish fails."

This module crawls every internal *page-navigation* href across the built site
and classifies each destination:

  DEAD       -- target resolves to no file on disk (a broken link)
  REDIRECTED -- target path matches a SOURCE in site/_redirects, i.e. a legacy
                URL that 301s elsewhere; a link pointing here is "backward"/
                non-canonical -- it should point at the redirect TARGET directly
  OK         -- resolves to an existing, non-redirected (canonical) page

Scope note -- this is the COMPLEMENT of test_evidence_links_resolve.py, which
already covers ../data/*.json and ../state/*.json evidence links. This walker
deliberately EXCLUDES those (json data/state refs), external http(s) links,
pure #fragment anchors, and JS-template dynamic hrefs ('+esc(...)) -- it walks
only static page-to-page navigation, which the evidence-link control does not.

WHY DIAGNOSTIC, NOT GATE (yet): the SITE_V5 IA is mid-cutover -- /method,
/simplified, /project, /tours are simultaneously (a) live nav doors the front
door still links AND required reachable by test_nav_story_platform_method_rq,
and (b) redirect SOURCES in _redirects. Until the WORDS->DIAGRAM->EVIDENCE IA
reorg settles which doors are canonical (director-pixel-gated, ruling #3),
wiring these REDIRECTED findings into the publish gate would re-wedge the gate
that was just cleared. So this runs as a report now; it flips to a gating
test_ (added to BOTH the publish-gate content set AND the site-lane pre-commit
set, per the parked class fix) once the canonical door set is decided.

Run:  python3 site/link_walk.py            # human report, exit 1 on findings
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

SITE = Path(__file__).resolve().parent

# A page-navigation href, opened by a quote. We then filter out the kinds that
# are not internal static page links (see classify()).
_HREF = re.compile(r'href=(["\'])([^"\']+)\1')

# JS-template dynamic hrefs -- rendered client-side from data, not static links.
_DYNAMIC = re.compile(r"""['"]?\s*\+\s*|["']\s*$|^\s*['"]?\s*\+""")


def _pages(site: Path = SITE) -> list[Path]:
    return sorted(site.glob("*/index.html")) + [site / "index.html"]


def _redirect_sources(site: Path = SITE) -> set[str]:
    """URL path prefixes that appear as a SOURCE in site/_redirects.

    Returns normalised path prefixes (leading slash, no trailing slash, splat
    and scheme stripped) -- e.g. '/method', '/simplified'. A link whose path
    equals one of these (or sits under it) is pointing at a legacy redirect."""
    src: set[str] = set()
    rf = site / "_redirects"
    if not rf.exists():
        return src
    for line in rf.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = line.split()
        if len(parts) < 2:
            continue
        source = parts[0]
        if "://" in source:  # absolute www->root style, not an internal path
            continue
        source = source.rstrip("*").rstrip("/")
        if source:
            src.add(source)
    return src


def _is_internal_page_link(href: str) -> bool:
    href = href.strip()
    if not href or href.startswith("#"):
        return False
    if href.startswith(("http://", "https://", "mailto:", "tel:")):
        return False
    if _DYNAMIC.search(href):  # JS-concatenated dynamic href
        return False
    if "'+" in href or "+'" in href or '"+' in href or '+"' in href:
        return False
    # data/state JSON evidence links are covered by test_evidence_links_resolve.
    path = href.split("?", 1)[0].split("#", 1)[0]
    if path.endswith(".json"):
        return False
    # asset files (css/svg/png/ico) are not page nav; existence-checked separately
    if re.search(r"\.(css|svg|png|ico|js|webmanifest|txt|xml)$", path):
        return False
    return True


def _url_path(page: Path, href: str, site: Path = SITE) -> str:
    """The site-absolute URL path a link points to, e.g. '/method/'."""
    path = href.split("?", 1)[0].split("#", 1)[0]
    if path.startswith("/"):
        resolved = (site / path.lstrip("/")).resolve()
    else:
        resolved = (page.parent / path).resolve()
    try:
        rel = resolved.relative_to(site)
    except ValueError:
        return path  # escaped the site tree -- keep raw for the report
    url = "/" + str(rel)
    if url == "/.":
        url = "/"
    return url


def _resolves_on_disk(page: Path, href: str, site: Path = SITE) -> bool:
    path = href.split("?", 1)[0].split("#", 1)[0]
    if path.startswith("/"):
        base = (site / path.lstrip("/")).resolve()
    else:
        base = (page.parent / path).resolve()
    if base.is_file():
        return True
    if (base / "index.html").is_file():
        return True
    # bare "/" or "./" -> site root index
    if base == site and (site / "index.html").is_file():
        return True
    return False


def classify(site: Path = SITE) -> dict[str, list[tuple[str, str, str]]]:
    """Return {'DEAD': [...], 'REDIRECTED': [...]} of (page, href, url_path)."""
    redirect_sources = _redirect_sources(site)
    findings: dict[str, list[tuple[str, str, str]]] = {"DEAD": [], "REDIRECTED": []}
    for page in _pages(site):
        html = page.read_text(encoding="utf-8")
        page_id = str(page.relative_to(site))
        seen: set[str] = set()
        for m in _HREF.finditer(html):
            href = m.group(2)
            if href in seen or not _is_internal_page_link(href):
                continue
            seen.add(href)
            url = _url_path(page, href, site)
            url_key = "/" + url.strip("/").split("/")[0] if url != "/" else "/"
            if not _resolves_on_disk(page, href, site):
                findings["DEAD"].append((page_id, href, url))
            elif url_key in redirect_sources or url.rstrip("/") in redirect_sources:
                findings["REDIRECTED"].append((page_id, href, url))
    return findings


def main() -> int:
    findings = classify()
    dead, redir = findings["DEAD"], findings["REDIRECTED"]
    print("=== R11 internal link-walk (DIAGNOSTIC) ===")
    print(f"redirect sources: {sorted(_redirect_sources())}\n")
    print(f"DEAD links (target missing on disk): {len(dead)}")
    for page_id, href, url in dead:
        print(f"  [DEAD]  {page_id:28s} href={href!r:30s} -> {url}")
    print(f"\nREDIRECTED links (point at a legacy redirect source): {len(redir)}")
    for page_id, href, url in redir:
        print(f"  [REDIR] {page_id:28s} href={href!r:30s} -> {url}")
    total = len(dead) + len(redir)
    print(f"\nTOTAL non-canonical/dead internal links: {total}")
    return 1 if total else 0


if __name__ == "__main__":
    sys.exit(main())
