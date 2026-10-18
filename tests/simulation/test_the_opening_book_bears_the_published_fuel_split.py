"""The drawn opening book bears the published GB fuel split, at the director's founder count.

The defect this names: for three months the founder book was 1% dual fuel, because each drawn
account took its fuel from an unanchored coin. Nothing compared the book with the published record
while the founder count grew from 13 to 400 (director steer, 2026-10-17). The bands are the
published household shares from
`docs/market_research/how_a_gb_domestic_book_splits_by_fuel_and_how_a_two_fuel_home_switches.md`,
widened by 3 sd of sampling noise over eight seeds pooled (~1,780 homes), not this draw's own
constants. So the control reads the property, and moving a constant inside its range leaves it
green. Pooled because fewer homes cannot tell 85% gas homes from the 90% the old heating draw
produced (measured: 85.5% against 90.4% over these eight seeds).

It runs at the production founder count, so raising the count re-asks the question.
"""
from __future__ import annotations

import collections

#: Share of homes buying both fuels from us. Floor: the whole market, 72% of households (CMA/GfK
#: 2014 ¶41), pulled down by the ex-incumbents' legacy single-fuel tails. Ceiling: a challenger
#: built by switching, Utility Warehouse 80% and First Utility over 90% of customers dual (CMA EMI
#: App. 2.2), at 84-86% gas homes. Band 70%-85% after 3 sd (~2 points) of sampling noise.
DUAL_SHARE_BAND = (0.70, 0.85)
#: Homes with a gas meter: 84% (DESNZ 2024) to 86% (EHS AT3.5), ± 3 sd (2.5 points).
GAS_HOME_SHARE_BAND = (0.815, 0.885)
#: A gas-only account is a split home's gas leg: 4m of 31m supplier customers (13%, CMA PF ¶9).
GAS_ONLY_SHARE_CEILING = 0.15

SEEDS = (20260724, 61101, 61102, 61103, 61104, 61105, 61106, 61107)


def fuel_composition(pairs) -> dict:
    """Shares of HOMES, from `(record, premise)` pairs; a home is its id with the gas `g` dropped."""
    homes = collections.defaultdict(list)
    for record, premise in pairs:
        homes[record["customer_id"].rstrip("g")].append((record["commodity"], premise))
    n = len(homes)
    dual = sum(1 for legs in homes.values() if sorted(f for f, _ in legs) == ["electricity", "gas"])
    gas_only = sum(1 for legs in homes.values() if [f for f, _ in legs] == ["gas"])
    gas_home = sum(1 for legs in homes.values()
                   if getattr(legs[0][1], "commodity", None) == "gas")
    return {"homes": n, "dual": dual / n, "gas_only": gas_only / n, "gas_home": gas_home / n}


def refusals(c: dict) -> list:
    """Each way the composition departs from the published record, named; empty when it bears it."""
    out = []
    if not DUAL_SHARE_BAND[0] <= c["dual"] <= DUAL_SHARE_BAND[1]:
        out.append(f"dual share {c['dual']:.0%} outside published {DUAL_SHARE_BAND}")
    if not GAS_HOME_SHARE_BAND[0] <= c["gas_home"] <= GAS_HOME_SHARE_BAND[1]:
        out.append(f"gas-home share {c['gas_home']:.0%} outside published {GAS_HOME_SHARE_BAND}")
    if c["gas_only"] > GAS_ONLY_SHARE_CEILING:
        out.append(f"gas-only share {c['gas_only']:.0%} above published ceiling")
    return out


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
    found = refusals(fuel_composition(pairs))
    assert any("dual share" in r for r in found) and any("gas-only" in r for r in found), found


def test_the_drawn_founders_bear_the_published_fuel_split(monkeypatch):
    monkeypatch.setenv("SE_DRAW_POPULATION", "1")
    from simulation import live_population as lp

    pooled = []
    for seed in SEEDS:
        pairs = lp._drawn_founder_pairs(seed)
        assert len(pairs) == lp.founder_accounts() - lp._founder_roster_size()
        pooled += [({**r, "customer_id": f"{seed}:{r['customer_id']}"}, p) for r, p in pairs]
    c = fuel_composition(pooled)
    assert not refusals(c), (c, refusals(c))


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
