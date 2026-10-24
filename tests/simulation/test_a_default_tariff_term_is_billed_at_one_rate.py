"""A smart home is billed two rates on a ToU term it chose, and one rate on the default tariff.

Until 2026-10-24 `tou_desk.offers_tou` read the meter alone, so every term of a smart-metered home was
settled as a peak/off-peak pair, the default tariff included (items 5 and 6 of
`docs/staging/SEAT_FINDING_SVT_BILLS_ABOVE_THE_CAP_ARE_TWO_DEFECTS_NOT_A_GRADING_ARTEFACT_2026-10-23.md`).
A ToU pair is a contract the household chose, not a property of its meter
(`docs/market_research/a_tou_tariff_needs_the_households_choice_not_its_meter.md`).

The composition is `run_phase2b`'s: the door's offer, or `None`, handed to `run_hedged_term` as
`tou_rates`. One control over the whole partition: the same planted home, the same flat rate, the
same days, on two products.

Mutation, run when this was written: delete the `DEFAULT_TARIFF_TYPES` guard in `offers_tou` and the
`svt` leg settles at two rates (157.14 and 300.00), so this reds. Delete the meter read instead
(`return False`) and the `fixed` leg settles at one, so this reds.
"""

from __future__ import annotations

from company.interfaces.tou_offer import request_tou_offer
from simulation.hedged_settlement import run_hedged_term

SMART_HOME = {"metering": "NHH", "smart_meter": True}
DAYS = ("2021-03-01", "2021-03-02")
PRICES = [{"settlementDate": d, "settlementPeriod": p, "systemSellPrice": 80.0}
          for d in DAYS for p in range(1, 49)]


def _billed_rates(tariff_type: str) -> set[float]:
    offer = request_tou_offer(customer=SMART_HOME, tariff_type=tariff_type,
                              flat_unit_rate_gbp_per_mwh=200.0)
    records = run_hedged_term(
        "C1", DAYS[0], "2021-03-03", 200.0, 80.0, 0.5, 0.0, lambda _d: [0.2] * 48, PRICES,
        tou_rates=(None if offer is None
                   else (offer.peak_rate_gbp_per_mwh, offer.offpeak_rate_gbp_per_mwh)))
    assert len(records) == 96, "the planted term did not settle every period"
    return {round(r["unit_rate_gbp_per_mwh"], 6) for r in records}


def test_the_partition():
    chosen = _billed_rates("fixed")
    rolled = _billed_rates("svt")
    assert len(chosen) == 2, f"a smart home's chosen fix was not billed as a ToU pair: {chosen}"
    assert rolled == {200.0}, f"a smart home rolled onto the default was billed {rolled}"
