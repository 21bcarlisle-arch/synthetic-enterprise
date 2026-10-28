"""A household's settlement of a failed bill repays THAT bill's leg, not its account's first leg.

Defect the control names: `world_payment_truth.build` keyed each crossed settlement by billing
account and gave it to the account's first leg, electricity. On a dual-fuel account a settled gas
bill became electricity credit that nobody had paid, the gas bill stayed owed to the write-off at
close, and the reg 6D refund paid the phantom credit out (5e3e9966a5: no gas leg held a
settlement, 523 sat on electricity; the five refunds of the 2026-10-27 cold-read finding).

The partition is asserted reachable first: settlements cross on both fuels' legs, and on months
where only one fuel failed, so a build that drops every settlement cannot pass.
"""
from __future__ import annotations

from datetime import date

import simulation.world_payment_truth as wpt
from background.live_payment_triad import LivePaymentTriad


def _dual_fuel_truth(households: int = 40) -> dict[str, dict]:
    triad = LivePaymentTriad()
    for m in range(1, 13):
        for i in range(households):
            for fuel, leg in (("electricity", f"RESI{i:05d}"), ("gas", f"RESI{i:05d}g")):
                triad.record_period(customer_id=leg, due_date=date(2020, m, 28), amount_gbp=120.0,
                                    income_stress_value="high", segment="resi", fuel=fuel,
                                    household_legs=2)
    triad.collections_journeys(date(2022, 12, 31))
    return wpt.build(triad, date(2022, 12, 31))


def test_each_settlement_repays_a_bill_its_own_leg_failed():
    truth = _dual_fuel_truth()
    settled = [(leg, rp["bill_month"]) for leg, t in truth.items() for rp in t["repayments"]
               if rp["kind"] == "settlement"]
    assert any(leg.endswith("g") for leg, _ in settled), "no gas leg was ever repaid a settlement"
    assert any(not leg.endswith("g") for leg, _ in settled), "no electricity leg was repaid either"
    one_fuel_failed = [
        (leg, m) for leg, m in settled
        if (truth.get(leg[:-1] if leg.endswith("g") else leg + "g", {}).get("outcomes", {})
            .get(m, {}).get("result")) != "failed"]
    assert one_fuel_failed, "no settlement fell in a month only one fuel failed: the partition is not reached"

    wrong = [(leg, m) for leg, m in settled if truth[leg]["outcomes"].get(m, {}).get("result") != "failed"]
    assert wrong == [], (
        f"{len(wrong)} settlement(s) repay a month their own leg paid, e.g. {wrong[:3]}: "
        "another leg's settlement booked here as credit nobody paid")
