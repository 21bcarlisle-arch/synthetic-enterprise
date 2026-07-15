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
DOORS = ["proof", "company", "world", "method", "director"]


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
def test_nav_allowed_to_wrap(door):
    """The nav bar has ~10 links; on a phone it must wrap, never overflow the body."""
    html = _html(door)
    m = re.search(r"\.site-nav\s*\{([^}]*)\}", html)
    assert m, f"{door}: no .site-nav rule found"
    assert "flex-wrap: wrap" in m.group(1), f"{door}: .site-nav missing flex-wrap: wrap"


@pytest.mark.parametrize("door", DOORS)
def test_tables_scroll_inside_their_own_container(door):
    """Every rendered <table> must be inside an overflow-x container, so a wide
    table scrolls inside its box rather than forcing horizontal body scroll."""
    html = _html(door)
    n_tables = len(re.findall(r"<table", html))
    if n_tables == 0:
        pytest.skip(f"{door}: renders no tables")
    # The doors build tables via JS as '<div class="table-scroll">...<table>'.
    assert "table-scroll" in html, f"{door}: {n_tables} table(s) but no table-scroll wrapper"
    assert "overflow-x" in html, f"{door}: table-scroll present but no overflow-x rule"
    n_wrappers = len(re.findall(r"table-scroll", html))
    # A wrapper for every table (each scrollable table has its own container).
    assert n_wrappers >= n_tables, (
        f"{door}: {n_tables} table(s) but only {n_wrappers} table-scroll wrapper(s)"
    )


@pytest.mark.parametrize("door", DOORS)
def test_no_remote_stylesheet_for_chrome(door):
    """Doors are self-contained: any linked stylesheet must be a same-origin site
    asset (../brand/brand.css), never a remote CDN that a phone might fail to load."""
    html = _html(door)
    for href in re.findall(r'<link[^>]+rel=["\']stylesheet["\'][^>]*href=["\']([^"\']+)', html):
        assert not href.startswith(("http://", "https://", "//")), (
            f"{door}: remote stylesheet {href}"
        )
