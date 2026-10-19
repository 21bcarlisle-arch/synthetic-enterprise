"""The drawn opening book bears the published GB fuel split, at the director's founder count.

The defect this names: for three months the founder book was 1% dual fuel, because each drawn
account took its fuel from an unanchored coin. Nothing compared the book with the published record
while the founder count grew from 13 to 400 (director steer, 2026-10-17).

The bands are NOT written here. They are the `world-claims` block in §5b of
`docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md`,
read and measured by `tools/world_claims.py` (director steer, 2026-10-19, item 4: one home per
fact). This file keeps the fuel page's own two questions: the book bears the page, and the page's
claims refuse the book the 17 Oct defect drew. `tests/tools/test_world_claims.py` holds the
mechanism's controls across every page.

It runs at the production founder count, so raising the count re-asks the question.
"""
from __future__ import annotations

import collections

from tools import world_claims as wc

PAGE = "docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md"
SEEDS = wc.SEEDS


def _page_claims():
    rows = [c for c in wc.claims() if c["page"] == PAGE]
    assert rows, f"{PAGE} carries no world-claims block"
    return rows


class _Home:
    def __init__(self, commodity):
        self.commodity = commodity


def test_the_check_refuses_the_book_it_was_written_against():
    """The control CAN fail, on the 17 Oct book: 250 electricity-only and 107 gas-only accounts on
    gas homes, 25 electricity on electric homes, no dual home."""
    gas, elec = _Home("gas"), _Home("electricity")
    pairs = ([({"customer_id": f"E{i}", "commodity": "electricity"}, gas) for i in range(250)]
             + [({"customer_id": f"G{i}", "commodity": "gas"}, gas) for i in range(107)]
             + [({"customer_id": f"N{i}", "commodity": "electricity"}, elec) for i in range(25)])
    red = {r["id"] for r in wc.check(pairs, _page_claims()) if r["verdict"] == "GAP"}
    assert {"dual_share_of_homes", "gas_only_share_of_homes"} <= red, red


def test_the_drawn_founders_bear_the_published_fuel_split():
    results = wc.check(wc.drawn_book(), _page_claims())
    assert not wc.failures(results), wc.failures(results)


def test_a_dual_home_is_one_household_on_one_premise(monkeypatch):
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    from simulation import live_population as lp

    by_home = collections.defaultdict(list)
    for record, premise in lp._drawn_founder_pairs(SEEDS[0]):
        by_home[record["customer_id"].rstrip("g")].append((record, premise))
    duals = [legs for legs in by_home.values() if len(legs) == 2]
    assert duals
    for (elec, p1), (gas, p2) in duals:
        assert gas["customer_id"] == elec["customer_id"] + "g"
        assert p1 is p2 and p1.commodity == "gas"
        assert gas["aq_kwh"] > 0 and gas["acquisition_date"] == elec["acquisition_date"]
