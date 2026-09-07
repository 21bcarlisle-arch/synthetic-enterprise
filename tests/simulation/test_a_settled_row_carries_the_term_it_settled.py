"""Every settlement writer stamps the term it settled, and the fold carries it.

THE DEFECT THIS EXISTS FOR (2026-09-07, measured). Four settlement writers built a record and
not one of them wrote the term start it was handed, though every one takes it as an argument.
`simulation/settlement_daily.CARRIED_FIELDS` had listed `"term_start"` since it was written, so
the daily fold was ready to carry a field nothing produced.

What it cost: `company/crm/customer_profitability.estimate_prior_term_net_margin` groups the
settled book by `term_start` to find the most recent completed term. With the field absent,
`prior_term_starts` was empty and the function returned `None` before summing a single margin --
on 78 of 78 calls, both fuels. `compute_profitability_uplift` therefore returned 0.0, which is
ALSO its answer for "this account is profitable", so the supplier's own policy of repricing
net-negative accounts was unreachable across the whole book and no run output could say so. 296
renewals cleared every eligibility gate and all 296 got `None`. Working:
docs/staging/SEAT_RESULT_THE_ID_REPAIR_IS_LIVE_AND_BOUGHT_NOTHING_BECAUSE_NO_SETTLED_ROW_CARRIES_A_TERM_START_2026-09-07.md

KEYED TO THE PROPERTY, not to today's writers: the emitters are DISCOVERED from the modules
rather than listed, so a fifth `run_*_term` added tomorrow is checked here the day it lands
instead of quietly emitting rows that cannot say which term produced them. That is the same
completeness shape as
`tests/company/pricing/test_value_arm_in_the_renewal_chain.py::test_every_commodity_writer_3_reprices_can_reach_the_book_it_settled_itself`,
which guards the id on the reading end while this guards the field on the writing end.
"""

import inspect

import pytest

from simulation import gas_settlement, hedged_settlement
from simulation.settlement_daily import CARRIED_FIELDS, fold_to_days

TERM_START = "2022-01-01"
TERM_END = "2022-01-04"
_DAYS = ["2022-01-01", "2022-01-02", "2022-01-03"]


def _elec_prices(price=60.0):
    return [
        {"settlementDate": d, "settlementPeriod": p, "systemSellPrice": price}
        for d in _DAYS for p in range(1, 49)
    ]


def _gas_prices(price=40.0):
    return [{"settlementDate": d, "systemSellPrice": price} for d in _DAYS]


def _shape_fn(date_str):
    return [1.0] * 48


# Each entry drives one emitter with the term bounds above and nothing else varying. The value
# is a zero-argument callable so a writer that raises fails as this test, named, rather than at
# collection.
EMITTERS = {
    "run_hedged_term": lambda: hedged_settlement.run_hedged_term(
        customer_id="C1",
        term_start_date=TERM_START,
        term_end_date=TERM_END,
        fixed_tariff_rate_gbp_per_mwh=150.0,
        hedge_price_gbp_per_mwh=80.0,
        hedge_fraction=0.5,
        monthly_cost_of_capital_gbp=10.0,
        consumption_shape=_shape_fn,
        system_price_records=_elec_prices(),
    ),
    "run_deemed_term": lambda: hedged_settlement.run_deemed_term(
        customer_id="C1",
        term_start_date=TERM_START,
        term_end_date=TERM_END,
        deemed_premium=0.20,
        consumption_shape=_shape_fn,
        system_price_records=_elec_prices(),
    ),
    "run_flex_term": lambda: hedged_settlement.run_flex_term(
        customer_id="C_IC1",
        term_start_date=TERM_START,
        term_end_date=TERM_END,
        flex_markup_per_mwh=2.0,
        consumption_shape=_shape_fn,
        system_price_records=_elec_prices(),
        segment="I&C",
    ),
    "run_gas_term": lambda: gas_settlement.run_gas_term(
        "C1g", TERM_START, TERM_END,
        12000, 60.0, 0.5, 40.0, 10.0, _gas_prices(),
    ),
}


def _discovered_emitters():
    """Every `run_*_term` the two settlement modules define themselves."""
    found = set()
    for module in (hedged_settlement, gas_settlement):
        for name, fn in inspect.getmembers(module, inspect.isfunction):
            if fn.__module__ == module.__name__ and name.startswith("run_") and name.endswith("_term"):
                found.add(name)
    return found


def test_the_emitter_table_covers_every_settlement_writer():
    """The completeness leg: a new writer arrives covered, or this goes red.

    Without it the test below is only ever as good as the day it was written -- the exact shape
    that let the field be missing from four writers at once.
    """
    discovered = _discovered_emitters()
    assert discovered, (
        "no `run_*_term` emitter was discovered in either settlement module -- the discovery "
        "rule has drifted from how the writers are named, and this control is now vacuous"
    )
    uncovered = discovered - set(EMITTERS)
    assert not uncovered, (
        f"settlement writer(s) {sorted(uncovered)} emit rows and this control does not drive "
        f"them -- add them to EMITTERS rather than letting a writer stamp nothing"
    )


@pytest.mark.parametrize("name", sorted(EMITTERS))
def test_every_settled_row_carries_the_term_that_produced_it(name):
    records = EMITTERS[name]()

    # THE FIXTURE REALLY SETTLED SOMETHING. A writer returning [] passes every assertion below
    # vacuously, and "no rows" is exactly what a broken fixture looks like.
    assert records, (
        f"{name} settled no rows for {TERM_START}..{TERM_END}, so this control proves nothing "
        f"about what it stamps -- fix the fixture, do not weaken the assertion"
    )

    missing = [r for r in records if r.get("term_start") != TERM_START]
    assert not missing, (
        f"{name}: {len(missing)} of {len(records)} settled rows do not carry "
        f"term_start=={TERM_START!r} (first: {missing[0].get('term_start')!r}). A row that "
        f"cannot say which term produced it is invisible to "
        f"`estimate_prior_term_net_margin`, which groups the book by exactly this field."
    )


@pytest.mark.parametrize("name", sorted(EMITTERS))
def test_the_daily_fold_carries_the_term_through_to_the_book(name):
    """The writing end is not enough: writer 3 reads the FOLDED book, not the raw records.

    `all_records.extend(fold_to_days(settled_this_term))` (`simulation/run_phase2b.py`) is the
    one place the book is fed, so a field stamped per-period and dropped by the fold would be
    just as invisible while every assertion above stayed green.
    """
    assert "term_start" in CARRIED_FIELDS, (
        "the fold no longer declares term_start a carried field, so it will be SUMMED or "
        "last-wins rather than carried -- writer 3 reads the folded book"
    )
    days = fold_to_days(EMITTERS[name]())
    assert days, f"{name}: the fold produced no days from a term that settled rows"
    assert all(d.get("term_start") == TERM_START for d in days), (
        f"{name}: the daily fold lost term_start between the writer and the book "
        f"`estimate_prior_term_net_margin` reads"
    )
