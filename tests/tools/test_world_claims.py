"""The population knowledge pages' claims hold on the drawn world, and the check can fail.

The defect this names: a page said ~75% of the book was dual fuel and the world drew 1% for three
months, because nothing compared one with the other (director steer, 2026-10-19, item 2). Each test
below states which way it would go red.
"""
from __future__ import annotations

import shutil

import pytest

from tools import world_claims as wc


@pytest.fixture(scope="module")
def book():
    return wc.drawn_book()


def test_every_population_page_carries_a_claim():
    """A page listed in PAGES with no `world-claims` block would check nothing and read as checked."""
    have = {c["page"] for c in wc.claims()}
    assert set(wc.PAGES) <= have, sorted(set(wc.PAGES) - have)


def test_every_claim_on_every_page_holds_on_the_drawn_book(book):
    results = wc.check(book)
    assert results
    assert not wc.failures(results), "\n".join(wc.failures(results))


def test_the_check_reaches_all_three_verdicts(book):
    """Assert the GAP and UNCHECKABLE branches CAN be taken before trusting a green.

    One control over the whole partition. A check that held every claim whatever the book would
    pass the test above."""
    rows = wc.claims()
    real = rows[0]
    impossible = {**real, "id": "impossible", "band": [2.0, 3.0]}
    unwritten = {**real, "id": "unwritten", "measure": "no_such_measure"}
    malformed = {**real, "id": "malformed", "band": [0.5]}
    verdicts = {r["id"]: r["verdict"] for r in wc.check(book, [real, impossible, unwritten, malformed])}
    assert verdicts == {real["id"]: "holds", "impossible": "GAP",
                        "unwritten": "UNCHECKABLE", "malformed": "UNCHECKABLE"}, verdicts


def test_the_page_is_the_one_home_of_the_band(tmp_path, book):
    """Editing the band ON THE PAGE turns the check red. A band copied into code would not move."""
    page = wc.PAGES[0]
    for p in wc.PAGES:
        (tmp_path / p).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(wc.PROJECT / p, tmp_path / p)
    text = (tmp_path / page).read_text(encoding="utf-8")
    assert "band: [0.70, 0.85]" in text
    (tmp_path / page).write_text(text.replace("band: [0.70, 0.85]", "band: [0.01, 0.05]"),
                                 encoding="utf-8")
    moved = {r["id"]: r["verdict"] for r in wc.check(book, wc.claims(tmp_path))}
    assert moved["dual_share_of_homes"] == "GAP", moved


def test_a_wrong_payment_draw_is_refused():
    """The payment page's claim refuses a book with no direct debit, the shape of a draw that lost
    its payment-method weights."""
    rows = [c for c in wc.claims() if c["measure"] == "direct_debit_share_of_accounts"]
    assert rows
    book = [({"customer_id": f"C{i}", "commodity": "electricity", "payment_method": "other"}, None)
            for i in range(100)]
    assert {r["verdict"] for r in wc.check(book, rows)} == {"GAP"}


def test_the_table_names_a_red_claim_first(book):
    rows = wc.claims()
    rows = rows + [{**rows[0], "id": "impossible", "band": [2.0, 3.0]}]
    table = wc.render(wc.check(book, rows)).splitlines()
    assert table[2].startswith("| `impossible` |") and "**GAP**" in table[2], table


@pytest.mark.parametrize("route", ["trickle", "campaign"])
def test_each_other_route_into_the_book_fails_only_its_named_gaps(route):
    """The founders are not the only way a home arrives. Each route is measured on its own, and
    the claims it fails must be exactly the ones `KNOWN_ROUTE_GAPS` names: a new gap reds, and so
    does a fixed one that is still listed."""
    results = wc.check(wc.drawn_book(route=route))
    assert {r["verdict"] for r in results} <= {"holds", "GAP"}, wc.failures(results)
    known = {cid for (r, cid) in wc.KNOWN_ROUTE_GAPS if r == route}
    assert wc.route_gaps(route, results) == known, wc.failures(results)


def test_every_route_is_a_route_drawn_book_can_assemble():
    assert set(wc.ROUTES) == {"founders", "trickle", "campaign"}
    assert {r for (r, _) in wc.KNOWN_ROUTE_GAPS} <= set(wc.ROUTES)
    with pytest.raises(ValueError):
        wc.drawn_book(seeds=wc.SEEDS[:1], route="no_such_route")
