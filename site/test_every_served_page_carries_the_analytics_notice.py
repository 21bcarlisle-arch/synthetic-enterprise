"""Every served page tells the reader that Cloudflare Web Analytics counts its views.

THE DEFECT this guards: the director ruled on 26 Oct (ruling item 2) to keep Cloudflare Web
Analytics *with* a footer notice on every page linking to /privacy/. The beacon is injected at
the edge into EVERY HTML response, so a page without the notice is a page whose reader is
counted without being told. Pages are hand-edited by several lanes and two generators write
whole pages, so the notice can be lost by any of them.

The population is every `.html` file a reader can be served, derived by walking `site/`, not
the list `tools/render_site_nav.footer_pages()` keeps: a control whose population is the
renderer's own list cannot notice a page the renderer misses.

R15, each proven by reverting:
  * delete the SITE-FOOTER block from any served page ->
    `test_every_served_page_carries_the_notice_and_its_privacy_link`.
  * drop `render_footer` from `tools/model_on_a_page_sheets.render_page` ->
    `test_the_generated_model_sheets_carry_the_notice`.
  * point the link at a path that is not /privacy/ -> the link-resolution leg.
"""
from __future__ import annotations

import posixpath
import re
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
NOTICE = ("Poesys counts page views with Cloudflare Web Analytics. It sets no cookies and does "
          "not track you across sites.")
_SKIP = {"__pycache__", "assets", "brand", "data", "state", "snapshots", "shadow",
         "node_modules", "harness_out"}
_LINK = re.compile(re.escape(NOTICE) + r'\s*<a href="([^"]+)"[^>]*>Privacy</a>')


def served_html() -> list[Path]:
    return [p for p in sorted(SITE.rglob("*.html"))
            if not any(part in _SKIP for part in p.relative_to(SITE).parts)]


def test_the_population_is_the_served_tree():
    rels = {str(p.relative_to(SITE)) for p in served_html()}
    assert len(rels) >= 60, f"only {len(rels)} served pages found; the walk has gone blind"
    for must in ("index.html", "404.html", "privacy/index.html",
                 "knowledge/price-cap/index.html", "model/map/index.html"):
        assert must in rels, must


@pytest.mark.parametrize("page", served_html(), ids=lambda p: str(p.relative_to(SITE)))
def test_every_served_page_carries_the_notice_and_its_privacy_link(page: Path):
    html = page.read_text(encoding="utf-8")
    m = _LINK.search(html)
    assert m, (f"{page.relative_to(SITE)} does not carry the analytics notice linked to "
               f"Privacy; run `python3 -m tools.render_site_nav --write`")
    href = m.group(1)
    rel_dir = posixpath.dirname(str(page.relative_to(SITE)).replace("\\", "/"))
    target = href.lstrip("/") if href.startswith("/") else posixpath.normpath(
        posixpath.join(rel_dir, href))
    assert (SITE / target / "index.html").is_file() and Path(target).parts[-1] == "privacy", (
        f"{page.relative_to(SITE)}: the notice links {href!r}, which is not the privacy page")


def test_the_generated_model_sheets_carry_the_notice():
    from tools import model_on_a_page_sheets as sheets
    pages = {p: b for p, b in sheets.build().items() if p.suffix == ".html"}
    assert pages, "the sheet generator built no pages; this leg would be vacuous"
    for path, body in pages.items():
        assert NOTICE in body, f"{path}: the generator drops the analytics notice on regeneration"
