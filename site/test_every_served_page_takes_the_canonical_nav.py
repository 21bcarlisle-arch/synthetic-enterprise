"""Every served page takes the canonical nav — including the ones a level down.

THE DEFECT, found by the director on 2026-08-24: `/knowledge/price-cap/` showed a nav reading
**Company · World · Knowledge · Proof · Glossary**. That is the pre-fold nav, and two of its
five links point at areas deleted on 2026-08-20 (`03dd8c49e` retired eleven pages). It was not
a cached copy: all eight Knowledge topic pages carried a hand-written nav and not one of them
had the `IA-NAV` marker.

WHY NOTHING CAUGHT IT — and this is the part worth keeping. Two populations, both wrong in the
same direction:

  * `ia_register.deployed_areas()` walks `site.iterdir()`, so its world is the ROOT plus each
    TOP-LEVEL directory. `/knowledge/price-cap/` is a level below that and simply is not in it.
    `_relative()` said so out loud — "only two depths exist on this surface" — and a third had
    existed since the Knowledge pages were written.
  * `tests/tools/test_nav_story_platform_method_rq.py` filters to pages that already contain
    `IA-NAV:START`. A page with a hand-written nav has no marker, so it was never a subject.

A control whose population is "the pages that already comply" cannot fail on the pages that do
not. That is the same shape as the freshness-banner control repaired on 2026-08-20 ("the
population is now derived from the pages themselves"), one directory deeper.

So the population here is EVERY `index.html` under `site/` that a reader can reach, derived by
walking the tree, and the test states the count it found — a population that silently shrinks
is the failure mode being guarded against.

R15 — each proven by reverting:
  * hand-edit any served page's nav back to the pre-fold one ->
    `test_every_served_page_carries_the_canonical_nav_block`.
  * point a nav entry at a deleted area -> `test_no_nav_link_points_at_a_deleted_area`.
  * render a sub-page's nav at depth 0 -> `test_a_sub_page_nav_resolves_from_where_it_sits`.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
NAV_MARKER = "IA-NAV:START"

#: Directories that hold no reader-facing page.
_SKIP = {"__pycache__", "assets", "brand", "data", "state", "snapshots", "shadow",
         "node_modules", "harness_out"}


def served_pages() -> list[Path]:
    """Every `index.html` a reader can reach, derived by walking the tree."""
    out = []
    for path in sorted(SITE.rglob("index.html")):
        rel = path.relative_to(SITE)
        if any(part in _SKIP for part in rel.parts):
            continue
        out.append(path)
    return out


def test_the_population_is_the_served_tree_and_it_is_not_empty():
    """A control whose population silently shrinks passes by having nothing to check. This is
    the one assertion that would notice."""
    pages = served_pages()
    assert len(pages) >= 12, (
        "only {} served pages found — the walk has stopped seeing the tree, and every "
        "assertion below is now vacuous".format(len(pages)))
    rels = {str(p.relative_to(SITE)) for p in pages}
    assert "knowledge/price-cap/index.html" in rels, (
        "the Knowledge topic pages are not in the population — this is exactly the blind spot "
        "that let eight pages keep a nav naming two deleted areas")


@pytest.mark.parametrize("page", served_pages(), ids=lambda p: str(p).split("site/")[-1])
def test_every_served_page_carries_the_canonical_nav_block(page: Path):
    html = page.read_text(encoding="utf-8")
    if "<nav" not in html:
        pytest.skip("page has no nav element at all — a separate defect, not this one")
    assert NAV_MARKER in html, (
        "{} carries a hand-written nav. The nav is DATA (site/ia_register.py) precisely so a "
        "page cannot drift its own copy, and this page drifted to the pre-fold one."
        .format(page.relative_to(SITE)))


@pytest.mark.parametrize("page", served_pages(), ids=lambda p: str(p).split("site/")[-1])
def test_no_nav_link_points_at_a_deleted_area(page: Path):
    """The failure a reader actually meets: a nav entry that 404s. Resolved against the tree,
    so a deleted directory reds this rather than being noticed by a visitor."""
    html = page.read_text(encoding="utf-8")
    block = re.search(r"IA-NAV:START.*?IA-NAV:END", html, re.S)
    if not block:
        pytest.skip("no canonical nav block — covered by the test above")
    for href in re.findall(r'<a href="([^"]+)"', block.group(0)):
        if href.startswith(("http", "#", "mailto:")):
            continue
        target = (page.parent / href).resolve()
        assert (target / "index.html").is_file() or target.is_file(), (
            "{} links to {!r}, which resolves to {} — no page there"
            .format(page.relative_to(SITE), href, target))


def test_a_sub_page_nav_resolves_from_where_it_sits():
    """The renderer must be able to address a page below an area. Before 2026-08-24 it could
    not, and that is why the eight pages were never rendered into."""
    import sys
    sys.path.insert(0, str(SITE))
    from ia_register import render_nav

    nav = render_nav("/knowledge/", depth=1)

    assert '<a href="../../" class="nav-link">Home</a>' in nav
    assert '<a href="../" class="nav-link active">Knowledge</a>' in nav
    assert '<a href="../../capabilities/"' in nav
    # depth 0 is the area's own index and must be unchanged
    top = render_nav("/knowledge/")
    assert '<a href="../" class="nav-link">Home</a>' in top
    assert '<a href="./" class="nav-link active">Knowledge</a>' in top
