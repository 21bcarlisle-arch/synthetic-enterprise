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
