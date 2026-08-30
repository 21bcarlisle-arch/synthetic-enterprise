"""Mobile-responsive structural tests for the Expert Doors (SITE1_expert_doors).

These assert each door reads on a phone WITHOUT changing its data:
  * a width=device-width viewport is declared;
  * a `@media (max-width: 640px)` breakpoint exists (the mobile pass);
  * the primary nav is allowed to wrap (`flex-wrap: wrap`) rather than overflow;
  * every wide `<table>` lives inside an `overflow-x` scroll container, so a wide
    table scrolls inside its own box instead of forcing the whole body to scroll;
  * no self-contained door pulls a remote stylesheet for its layout chrome.

R15 (a control must be able to FAIL): each assertion targets a property that a
non-responsive door would genuinely lack — the method door shipped without
`flex-wrap` on its nav and without a mobile breakpoint, and both checks below fail
against that pre-pass source. Data-faithfulness after the CSS changes is covered
by the per-door render harnesses (test_company_door.py, test_world_door.py,
test_director_door.py, proof/test_*_panel.py), which execute each page's real JS
against the live JSON — CSS edits leave those rendered values untouched.
"""
import re
from pathlib import Path

import pytest

SITE = Path(__file__).resolve().parent
# DERIVED, 2026-08-20. This was a literal list of nine doors, and on that date every one of
# them was deleted -- the director ruled that the five tabs ARE the site and the rest either
# moved into a tab or went. A literal list would have taken 45 tests down with the pages.
#
# The SUBJECT survives the page list, and it is the more important half: "mobile is where I
# read this; treat it as the binding constraint" (director, 2026-08-19). So the doors are read
# from the built site, and a new tab is covered the day it ships rather than the day someone
# remembers to add it here.
def _pages():
    out = []
    for page in sorted(SITE.rglob("index.html")):
        rel = page.parent.relative_to(SITE).as_posix()
        out.append("." if rel == "." else rel)
    assert len(out) >= 5, (
        f"only {len(out)} built page(s) under {SITE} -- treating that as a broken scan rather "
        "than a shrunken site, since a short list makes every test below vacuous"
    )
    return out


DOORS = _pages()


def _html(door: str) -> str:
    return (SITE / door / "index.html").read_text(encoding="utf-8")


@pytest.mark.parametrize("door", DOORS)
def test_viewport_declared(door):
    html = _html(door)
    assert re.search(
        r'<meta[^>]+name=["\']viewport["\'][^>]+width=device-width', html
    ), f"{door}: no width=device-width viewport meta"


@pytest.mark.parametrize("door", DOORS)
def test_has_mobile_breakpoint(door):
    html = _html(door)
    assert re.search(r"@media\s*\([^)]*max-width:\s*640px", html), (
        f"{door}: no @media (max-width: 640px) mobile pass"
    )


@pytest.mark.parametrize("door", DOORS)
def test_no_page_defines_its_own_nav(door):
    """THE property that keeps the bar identical everywhere: brand.css is the only definition.

    REPLACES an assertion that every page carried `.site-nav { flex-wrap: wrap }` in its own
    <style>. That test was satisfied by exactly the arrangement the director reported as broken:
    eighteen pages each defining the nav, after the brand sheet, so no two agreed -- Home a 24px
    wordmark right-aligned, everyone else 15px left-aligned with an active pill, and "Harness"
    falling out of the band on some and not others. Per-page rules PASSING this test were the
    defect. Its premise was stale too ("~10 links"; there are five), and `flex-wrap: wrap` is no
    longer the mechanism: below 560px the bar is a deliberate two-row column, which is what
    "looks deliberate rather than wrapped" required.
    """
    html = _html(door)
    style = "\n".join(re.findall(r"<style>(.*?)</style>", html, re.S))
    own = re.findall(r"(?m)^\s*(\.site-nav|\.nav-link|\.nav-logo|\.doors)[^{}]*\{", style)
    assert not own, (
        f"{door} defines its own nav rules {sorted(set(own))} -- brand.css is the single "
        "definition, and a page-level override is what made the bar render differently per page"
    )


WRAPPER = '<div class="table-scroll">'
# The doors build tables by concatenating JS string literals, so a wrapper and the <table> it
# wraps are routinely split across a `' + '` join and a newline (capabilities/index.html:849).
# Removing the glue lets one adjacency rule read both the hand-written and the built shapes.
_JS_GLUE = re.compile(r"['\"]\s*\+\s*['\"]")


def unwrapped_tables(html):
    """Return the source offset of every `<table` NOT opened immediately inside a WRAPPER.

    COUNTING IS THE DEFECT THIS REPLACES, not a stylistic choice. The previous assertion was
    `len(findall("table-scroll")) >= len(findall("<table"))`, and `table-scroll` matches things
    that are not wrappers: every door's own `.table-scroll { overflow-x: auto }` rule, and in
    site/capabilities/index.html a comment naming the class as well. So the real assertion was
    `real_wrappers + 1 >= n_tables` on two doors and `real_wrappers + 2 >= n_tables` on the
    third -- one unwrapped table always passed, and two passed on capabilities. A count also
    cannot tell a table wrapped twice from two tables wrapped once.

    Adjacency is the property the reader actually gets: a table scrolls inside its own box iff
    the element opened around it is the overflow-x container. It has no fail-open slack because
    each `<table` is judged on its own, and the CSS rule and the comment can never satisfy it.
    """
    flat = _JS_GLUE.sub("", html)
    return [
        m.start()
        for m in re.finditer(r"<table[\s>]", flat)
        if not flat[: m.start()].rstrip().endswith(WRAPPER)
    ]


@pytest.mark.parametrize("door", DOORS)
def test_tables_scroll_inside_their_own_container(door):
    """Every rendered <table> must open immediately inside an overflow-x container, so a wide
    table scrolls inside its box rather than forcing horizontal body scroll."""
    html = _html(door)
    n_tables = len(re.findall(r"<table[\s>]", html))
    if n_tables == 0:
        pytest.skip(f"{door}: renders no tables")
    assert "overflow-x" in html, f"{door}: {n_tables} table(s) but no overflow-x rule"
    loose = unwrapped_tables(html)
    lines = [html.count("\n", 0, off) + 1 for off in loose]
    assert not loose, (
        f"{door}: {len(loose)} of {n_tables} table(s) not opened inside {WRAPPER} "
        f"(near source line(s) {lines}) -- a wide table there scrolls the whole body"
    )


def test_the_table_scroll_check_can_fail():
    """R15: the mutation the replaced control could not see -- ONE unwrapped table.

    Each fixture is the previous assertion's blind spot expressed literally. The first two
    carry the exact `table-scroll` occurrences that made it pass (the CSS rule, and the comment
    that pushed capabilities' slack to two) while wrapping nothing at all. If any of these
    stops failing, the count has come back.
    """
    css = ".table-scroll { overflow-x: auto; }"
    comment = "// `table-scroll` rather than an inline overflow-x:auto"

    # 1 table, 1 `table-scroll` hit that is the CSS rule -> the old check passed this.
    assert unwrapped_tables(f"<style>{css}</style><table><tr><td>x</td></tr></table>")
    # capabilities' shape: the comment bought a second table's worth of slack.
    assert (
        len(unwrapped_tables(f"<style>{css}</style>{comment}<table></table><table></table>")) == 2
    )
    # One wrapped, one bare -- the single-violation case the old check was built to miss.
    one_bare = f"<style>{css}</style>{WRAPPER}<table></table></div><table></table>"
    assert len(unwrapped_tables(one_bare)) == 1
    # A wrapper that wraps something else does not cover a later bare table.
    assert unwrapped_tables(f"{WRAPPER}<div>x</div></div><table></table>")
    # And the honest shapes stay green, including across the JS `' + '` join.
    assert unwrapped_tables(f"<style>{css}</style>{WRAPPER}<table></table></div>") == []
    assert unwrapped_tables("'" + WRAPPER + "'\n      + '<table style=\"x\">'") == []


@pytest.mark.parametrize("door", DOORS)
def test_no_remote_stylesheet_for_chrome(door):
    """Doors are self-contained: any linked stylesheet must be a same-origin site
    asset (../brand/brand.css), never a remote CDN that a phone might fail to load."""
    html = _html(door)
    for href in re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)', html):
        assert not href.startswith(("http://", "https://", "//")), (
            f"{door}: remote stylesheet {href}"
        )


def test_the_brand_sheet_carries_the_phone_layout():
    """The other half: one definition is only useful if it is the RIGHT one. Below 560px the
    five doors plus the wordmark cannot share a 360px row, so the bar becomes two deliberate
    rows rather than overflowing."""
    css = (SITE / "brand" / "brand.css").read_text(encoding="utf-8")
    assert "@media (max-width: 560px)" in css, "the phone layout is gone from the brand sheet"
    tail = css.split("@media (max-width: 560px)", 1)[1]
    assert "flex-direction: column" in tail, "the phone bar is no longer the two-row design"
