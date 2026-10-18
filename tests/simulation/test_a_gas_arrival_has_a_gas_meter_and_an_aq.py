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


def _unfiltered(seed, **weights):
    return draw_population(seed, draw_region=True, assign_cohorts=True,
                           premise_stock_fn=lambda year: lp._trickle_stock(year, seed),
                           seasonal_dates=True, **weights)


def _on_electric(raw):
    return [sc for sc in raw if sc.commodity == "gas"
            and getattr(sc.premise, "commodity", "gas") != "gas"]


def test_the_rule_can_fire_and_every_gas_arrival_left_has_a_meter_and_an_aq():
    """Since 2026-10-17 the arrival takes its home's fuel, so the meter rule holds at the draw.
    A forced fuel still breaks it, which is what keeps the empty list below from being vacuous."""
    assert _on_electric(_unfiltered(SEED, commodity_weights={"gas": 1.0})), (
        "a forced gas draw at seed 61101 no longer lands on an electric home")
    assert not _on_electric(_unfiltered(SEED))
    gas = [d for sc in lp._drawn_trickle(SEED) for d in lp._trickle_records(sc)
           if d["commodity"] == "gas"]
    assert gas and all(isinstance(d.get("aq_kwh"), float) for d in gas)


def test_the_default_books_trickle_is_untouched():
    raw = _unfiltered(lp._DEFAULT_BASE_SEED)
    assert [sc.customer_id for sc in lp._drawn_trickle(lp._DEFAULT_BASE_SEED)] == [
        sc.customer_id for sc in raw]
    assert all(lp._trickle_dict(sc) == sc.to_customer_dict() for sc in raw)
