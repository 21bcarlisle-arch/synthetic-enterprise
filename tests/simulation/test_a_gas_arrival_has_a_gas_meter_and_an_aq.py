"""A drawn arrival on gas follows the founders' two rules: no gas meter, no gas account; no
published AQ, no account. And the arrival that IS a gas account carries its AQ.

The defect: the trickle was the one way into the book without them. At EP17 seed 61101 it put a
gas account on an electric home and a gas account with no `aq_kwh`, and `run_phase2b` raised a
KeyError at import on 8 of the 12 authorised seeds.
"""
from __future__ import annotations

import simulation.live_population as lp
from simulation.population_draw import draw_population

SEED = 61101


def _unfiltered(seed):
    return draw_population(seed, draw_region=True, assign_cohorts=True,
                           premise_stock_fn=lambda year: lp._trickle_stock(year, seed),
                           seasonal_dates=True)


def test_the_rule_can_fire_and_every_gas_arrival_left_has_a_meter_and_an_aq():
    raw = _unfiltered(SEED)
    on_electric = [sc for sc in raw if sc.commodity == "gas"
                   and getattr(sc.premise, "commodity", "gas") != "gas"]
    assert on_electric, "seed 61101 no longer draws a gas arrival on an electric home"
    kept = lp._drawn_trickle(SEED)
    assert {sc.customer_id for sc in on_electric}.isdisjoint(sc.customer_id for sc in kept)
    gas = [lp._trickle_dict(sc) for sc in kept if sc.commodity == "gas"]
    assert gas and all(isinstance(d.get("aq_kwh"), float) for d in gas)


def test_the_default_books_trickle_is_untouched():
    raw = _unfiltered(lp._DEFAULT_BASE_SEED)
    assert [sc.customer_id for sc in lp._drawn_trickle(lp._DEFAULT_BASE_SEED)] == [
        sc.customer_id for sc in raw]
    assert all(lp._trickle_dict(sc) == sc.to_customer_dict() for sc in raw)
