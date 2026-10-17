"""A held estimate was never sent, so the catch-up at the next actual read reconciles it as £0 billed.

Defect this guards (BLOCKING finding, 2026-10-14,
docs/staging/WORKER_FINDING_NINE_CUSTOMER_YEARS_BILL_LESS_THAN_THEIR_GROSS_MARGIN_AT_ORIGIN_2026-10-14.md):
`validate_bills` holds bills AFTER assembly, while the catch-up was formed DURING assembly as if every
estimate had been billed. A held period was credited for an estimate nobody received, and seven of the
book's customer-years billed less than their own gross margin. Licence reading:
docs/market_research/back_billing_and_liability.md §12.

The bills come from the company's own `build_monthly_bills` with a scripted read feed. The estimator
is replaced by "the last actual read's kWh", because this file grades the reconciliation, not the
estimate. The hold itself is the real `validate_bill`: a domestic account billed at 6,000 kWh a month
fails the consumption-scale checks, and one at 300 kWh does not.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass

import pytest

from company.billing.monthly_bill_assembly import build_monthly_bills
from company.billing.pre_bill_validation import validate_bills

# kWh in each month of 2023: an actual read in January, estimates in February and March, an
# actual read in April that resolves them.
# C1 is billed at a scale a domestic account fails on; C2 is an ordinary home. Both are resi.
USE = {
    "C1": {1: 6000.0, 2: 5000.0, 3: 5200.0, 4: 4800.0},
    "C2": {1: 300.0, 2: 420.0, 3: 380.0, 4: 300.0},
}


@pytest.fixture(autouse=True)
def _the_estimate_is_the_last_actual(monkeypatch):
    def last_actual(_commodity, trailing, *_period):
        return trailing[-1][2]
    monkeypatch.setattr("company.billing.monthly_bill_assembly.estimate_unread_kwh", last_actual)


def _records():
    out = []
    for cid, months in USE.items():
        for month, kwh in months.items():
            days = calendar.monthrange(2023, month)[1]
            out.extend({
                "customer_id": cid,
                "settlement_date": f"2023-{month:02d}-{d:02d}",
                "settlement_period": 1,
                "consumption_kwh": kwh / days,
                "unit_rate_gbp_per_mwh": 200.0,
                "revenue_gbp": (kwh / days / 1000) * 200.0 + 0.5,
                "standing_charge_gbp": 0.5,
                "wholesale_cost_gbp": 0.0,
                "margin_gbp": 0.0,
            } for d in range(1, days + 1))
    return out


@dataclass
class _Read:
    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int


class _Feed:
    def meter_type_for(self, customer):
        return "traditional"

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        if period_end[5:7] in ("02", "03"):
            return _Read("estimated", None, consecutive + 1)
        return _Read("actual", None, 0)

    def final_read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        return _Read("actual", None, 0)


def _by_account():
    bills = build_monthly_bills(_records(), _Feed())
    _issued, held = validate_bills(bills)
    held_keys = {(r.customer_id, r.period_end) for r in held}
    out = {}
    for cid in USE:
        mine = sorted((b for b in bills if b["customer_id"] == cid), key=lambda b: b["period_end"])
        estimates = [b for b in mine if b["billing_basis"] == "estimated"]
        catchup = next(b for b in mine if b["period_end"].startswith("2023-04"))
        out[cid] = (estimates, catchup, held_keys)
    return out


def test_a_held_estimate_is_reconciled_as_billed_nothing_and_a_sent_one_as_what_was_sent():
    accounts = _by_account()
    big_estimates, big_catchup, held_keys = accounts["C1"]
    small_estimates, small_catchup, _ = accounts["C2"]

    # Both branches are reachable: BIG's estimates are held downstream, SMALL's are issued.
    assert len(big_estimates) == 2 and len(small_estimates) == 2
    assert all((b["customer_id"], b["period_end"]) in held_keys for b in big_estimates)
    assert not any((b["customer_id"], b["period_end"]) in held_keys for b in small_estimates)

    # Held: nothing was sent, so the whole true charge is owed at the read.
    big_true = round(sum(b["true_total_amount_gbp"] for b in big_estimates), 2)
    assert big_catchup["catchup_raw_delta_gbp"] == pytest.approx(big_true, abs=0.01), (
        "a held estimate was netted off the catch-up as if it had been billed")
    assert big_catchup["catchup_unbilled_periods"] == 2

    # Issued: the catch-up is true minus what was sent, exactly as before.
    small_delta = round(sum(b["true_total_amount_gbp"] - b["total_amount_gbp"]
                            for b in small_estimates), 2)
    assert small_catchup["catchup_raw_delta_gbp"] == pytest.approx(small_delta, abs=0.01)
    assert small_catchup["catchup_unbilled_periods"] == 0
