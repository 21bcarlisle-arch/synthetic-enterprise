#!/usr/bin/env python3
"""Render every page's nav from the one IA register (`site/ia_register.py`).

    python3 -m tools.render_site_nav --check    # exit 1 if any page is out of date
    python3 -m tools.render_site_nav --write    # bring every page into line

WHY A TOOL AND NOT A HAND EDIT
------------------------------
Sixteen areas carry twelve distinct nav shapes. Every later step of the website
structure programme (SITE5..SITE11) moves a tab, and each one would otherwise be
sixteen hand edits -- sixteen chances to strand a page, in a migration whose whole
non-negotiable is that no intermediate state routes a reader at a page that is not
there (brief §9.2). After this, a tab move is one line in CANONICAL_NAV and one run of
this tool.

WHAT IT DOES NOT TOUCH
----------------------
The nav LOGO, the `<nav>` element's own class, and every byte outside the marked
region. Two grammars exist on this surface -- the home page's bare `nav.doors` inside
`header.site-nav`, and everyone else's `nav.site-nav` with `.nav-link` -- and this
renders both rather than forcing one, because collapsing them is a CSS change on the
front door and Step 0 is deliberately not that.

`/shadow/` is exempt (a generated mirror at a second root; see NAV_EXEMPT).
`/evidence/` carries no nav at all and is GENERATED half-hourly by
`tools/generate_evidence_data.py` -- hand-editing it is overwritten within the hour, so
its nav is rendered by that generator, from this same register.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "site"))

import ia_register as reg  # noqa: E402

# The first site-level nav on a page. `project/index.html` carries a SECOND <nav>
# (its in-page tab bar) which is not site nav; matching on these two classes and
# taking only the first occurrence leaves it alone.
_NAV_BLOCK = re.compile(r'(<nav class="(?:site-nav|doors)"[^>]*>)(.*?)(</nav>)', re.S)
_LOGO = re.compile(r'\s*<a\b[^>]*class="[^"]*nav-logo[^"]*"[^>]*>.*?</a>', re.S)
_MARKED = re.compile(
    re.escape(reg.NAV_START) + r".*?" + re.escape(reg.NAV_END), re.S
)


def _indent_of(inner: str, default: str = "  ") -> str:
    """The indentation the page already uses for its nav links, so a rendered nav
    reads like the file it lands in rather than like a generator's output."""
    m = re.search(r"\n([ \t]+)<a\b", inner)
    return m.group(1) if m else default


def render_page(html: str, area: str, depth: int = 0) -> str:
    """The page with its nav region rendered from the register. Idempotent. `depth` is levels
    below `area` (1 for a Knowledge topic page), passed through to `ia_register.render_nav`."""
    m = _NAV_BLOCK.search(html)
    if not m:
        raise ValueError(f"{area}: no site-level <nav> block found")
    open_tag, inner, close_tag = m.group(1), m.group(2), m.group(3)
    indent = _indent_of(inner)
    block = reg.render_nav(area, indent=indent, depth=depth)

    if _MARKED.search(inner):
        new_inner = _MARKED.sub(lambda _: block, inner, count=1)
    else:
        # First pass: keep the logo anchor (not a route -- see ia_register), drop the
        # hand-maintained link list, and put the marked region in its place.
        logo = _LOGO.match(inner) or _LOGO.search(inner)
        keep = logo.group(0).strip() if logo else ""
        head = f"\n{indent}{keep}" if keep else ""
        new_inner = f"{head}\n{indent}{block}\n"
    return html[: m.start()] + open_tag + new_inner + close_tag + html[m.end():]


def pages(site: Path = reg.SITE) -> list[tuple[str, Path]]:
    """(area, index.html) for every area whose nav this tool owns."""
    out = []
    for area in reg.deployed_areas(site):
        if area in reg.NAV_EXEMPT or area in reg.GENERATED_NAV:
            continue
        path = site / "index.html" if area == "/" else site / area.strip("/") / "index.html"
        if not path.is_file():
            continue
        out.append((area, path))
    return out


def sub_pages(site: Path = reg.SITE) -> list[tuple[str, int, str, Path]]:
    """(area, depth, url, path) for every page BELOW an area's index that already carries the
    marked nav block -- the Knowledge topic pages, /harness/module-graph/ -- plus an exempt
    area's own index (/privacy/), which carries the nav but is not a tab.

    Before 2026-10-22 `pages()` was the whole population, so these pages were rendered once by
    hand and then drifted: the "How it's built" rename reached five pages and left 35 naming
    "Harness" in the old order. Only pages with the marker are taken: a page with no marked
    block is the canonical-nav test's to refuse, not this tool's to rewrite."""
    out = []
    for path in sorted(site.rglob("index.html")):
        parts = path.relative_to(site).parts[:-1]
        if not parts or (len(parts) == 1 and f"/{parts[0]}/" not in reg.NAV_EXEMPT):
            continue  # an area's own index: pages() owns it
        area = f"/{parts[0]}/"
        if area in reg.GENERATED_NAV:
            continue
        html = path.read_text(encoding="utf-8")
        if reg.NAV_START not in html:
            continue
        out.append((area, len(parts) - 1, "/" + "/".join(parts) + "/", path))
    return out


def population(site: Path = reg.SITE) -> list[tuple[str, int, str, Path]]:
    """(area, depth, url, path) for every page whose nav this tool renders."""
    return [(a, 0, a, p) for a, p in pages(site)] + sub_pages(site)


def stale(site: Path = reg.SITE) -> list[str]:
    """Pages (by URL) whose committed nav is not what the register renders."""
    bad = []
    for area, depth, url, path in population(site):
        html = path.read_text(encoding="utf-8")
        if render_page(html, area, depth) != html:
            bad.append(url)
    return bad


def write(site: Path = reg.SITE) -> list[str]:
    changed = []
    for area, depth, url, path in population(site):
        html = path.read_text(encoding="utf-8")
        new = render_page(html, area, depth)
        if new != html:
            path.write_text(new, encoding="utf-8")
            changed.append(url)
    return changed


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--write", action="store_true", help="rewrite pages in place")
    ap.add_argument("--check", action="store_true", help="report drift, change nothing")
    args = ap.parse_args(argv)
    if args.write:
        changed = write()
        print(f"rendered {len(changed)} page(s): {', '.join(changed) or 'none'}")
        return 0
    bad = stale()
    for area in bad:
        print(f"STALE {area} -- nav does not match site/ia_register.py")
    print(f"{len(bad)} page(s) out of date")
    return 1 if bad else 0


if __name__ == "__main__":
    raise SystemExit(main())
