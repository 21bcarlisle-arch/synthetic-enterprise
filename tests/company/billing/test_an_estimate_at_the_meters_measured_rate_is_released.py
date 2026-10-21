"""An estimate held on consumption scale, at a listed dwelling, at a daily rate the account's own meter
had already measured, is released (`pre_bill_validation.release_on_measured_rate`).

Defect this guards: PROS-2017-0336, a listed dwelling whose meter reads 2,500-5,000 kWh a month,
had every estimate held against the population ceiling. It went 14 months with no bill (SLC 21B.5
asks for one twice a year), then got one £5,067 catch-up. Rules and choices:
docs/market_research/unbilled_energy_and_revenue_assurance.md §4d. Evidence:
docs/staging/records/WORKER_PREREG_D48_THE_FIRST_RUN_CARRYING_THE_HELD_BILL_RELEASES_2026-10-21.md.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass

import pytest

from company.billing.monthly_bill_assembly import build_monthly_bills
from company.billing.pre_bill_validation import (
    ValidationOutcome,
    measured_daily_rates,
    release_on_measured_rate,
    validate_bill,
    validate_bills,
)


def _month(customer_id, month, kwh, basis, listed=True):
    """A 2023 resi electricity bill at 5% VAT that fails the ceiling on scale alone."""
    days = calendar.monthrange(2023, month)[1]
    commodity = round(kwh * 0.15, 2)
    standing = round(days * 0.30, 2)
    vat = round((commodity + standing) * 0.05, 2)
    return {
        "customer_id": customer_id, "segment": "resi", "commodity": "electricity",
        "period_start": f"2023-{month:02d}-01", "period_end": f"2023-{month:02d}-{days:02d}",
        "total_consumption_kwh": kwh, "commodity_amount_gbp": commodity,
        "non_commodity_amount_gbp": 0.0, "standing_charge_gbp": standing, "vat_gbp": vat,
        "total_amount_gbp": round(commodity + standing + vat, 2),
        "billing_basis": basis, "premise_council_tax_listed": listed,
    }


def _account(customer_id, read_kwh, estimate_kwh, listed=True, read_first=True):
    """January read (or not), then a February estimate."""
    january = _month(customer_id, 1, read_kwh, "actual" if read_first else "estimated", listed)
    return [january, _month(customer_id, 2, estimate_kwh, "estimated", listed)]


def test_every_leg_of_the_measured_rate_release_is_reachable():
    """The release exists to be taken rarely, so assert first that it CAN be taken, and that each
    refusal can too. A release that refused everything would pass every refusal below."""
    bills = (
        _account("UNDER", 6200.0, 5000.0)                     # 179/day under a measured 200/day
        + _account("OVER", 6200.0, 6500.0)                    # 232/day over a measured 200/day
        + _account("UNREAD", 6200.0, 5000.0, read_first=False)  # no read yet: nothing measured
        + _account("UNLISTED", 6200.0, 5000.0, listed=None)   # the mislabel half is unanswered
    )
    february = [b for b in bills if b["period_end"] == "2023-02-28"]
    assert all(validate_bill(b).held and validate_bill(b).consumption_scale_only for b in february)
    passing, held = validate_bills(bills)
    released = {b["customer_id"]: b["pre_bill_release"] for b in passing
                if b["period_end"] == "2023-02-28" and "pre_bill_release" in b}
    assert list(released) == ["UNDER"]
    assert released["UNDER"]["outcome"] == ValidationOutcome.RELEASED_ON_MEASURED_RATE.value
    assert released["UNDER"]["measured_kwh_per_day"] == pytest.approx(6200.0 / 31)
    assert sorted({r.customer_id for r in held if r.period_end == "2023-02-28"}) == [
        "OVER", "UNLISTED", "UNREAD"]


def test_only_a_read_before_the_bill_counts_as_measured():
    """A later read is something the supplier did not know when it billed. The March read measures
    14,000 kWh over 59 days, 237 a day, above the February estimate's 179: only its date refuses it."""
    bills = [_month("LATER", 2, 5000.0, "estimated"), _month("LATER", 3, 14000.0, "actual")]
    assert measured_daily_rates(bills)[0][1] > 5000.0 / 28
    assert release_on_measured_rate(bills[0], validate_bill(bills[0]), bills) is None


def test_the_measured_rate_counts_the_catch_up_of_the_run_before_the_read():
    """A read after two estimates measures the register's advance over all three months."""
    run = [_month("RUN", 1, 3000.0, "estimated"), _month("RUN", 2, 3000.0, "estimated"),
           dict(_month("RUN", 3, 3000.0, "actual"), read_true_up_billed_kwh=6000.0,
                read_true_up_kwh=2000.0)]
    assert measured_daily_rates(run) == [("2023-03-31", pytest.approx(11000.0 / 90))]


# --- The catch-up and the issuance door decide the same release ---------------------------------
# If they disagreed, a released estimate would be reconciled as billed nothing at the next read and
# so billed twice. The scripted read feed and estimator follow
# test_a_held_estimate_is_reconciled_as_billed_nothing.py.

# C1 is listed and C2 is not answered. The ids are the supply book's, so the billing run resolves them.
USE = {"C1": {1: 6200.0, 2: 5000.0, 3: 5200.0, 4: 4800.0},
       "C2": {1: 6200.0, 2: 5000.0, 3: 5200.0, 4: 4800.0}}


@pytest.fixture
def _the_estimate_is_nine_tenths_of_the_last_actual(monkeypatch):
    def estimate(_commodity, trailing, *_period):
        return 0.9 * trailing[-1][2]
    monkeypatch.setattr("company.billing.monthly_bill_assembly.estimate_unread_kwh", estimate)


def _records():
    out = []
    for cid, months in USE.items():
        for month, kwh in months.items():
            days = calendar.monthrange(2023, month)[1]
            out.extend({
                "customer_id": cid, "settlement_date": f"2023-{month:02d}-{d:02d}",
                "settlement_period": 1, "consumption_kwh": kwh / days,
                "unit_rate_gbp_per_mwh": 200.0, "revenue_gbp": (kwh / days / 1000) * 200.0 + 0.5,
                "standing_charge_gbp": 0.5, "wholesale_cost_gbp": 0.0, "margin_gbp": 0.0,
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


@pytest.mark.usefixtures("_the_estimate_is_nine_tenths_of_the_last_actual")
def test_the_catch_up_reconciles_a_released_estimate_as_sent_and_a_held_one_as_not():
    bills = build_monthly_bills(
        _records(), _Feed(),
        premise_listing_feed=lambda customer: True if customer["customer_id"] == "C1" else None)
    _issued, held = validate_bills(bills)
    held_keys = {(r.customer_id, r.period_end) for r in held}
    for cid in USE:
        mine = sorted((b for b in bills if b["customer_id"] == cid), key=lambda b: b["period_end"])
        estimates = [b for b in mine if b["billing_basis"] == "estimated"]
        catchup = next(b for b in mine if b["period_end"].startswith("2023-04"))
        held_here = sum((cid, b["period_end"]) in held_keys for b in estimates)
        # Both branches are reachable: every listed estimate releases, every unanswered one holds.
        assert len(estimates) == 2
        assert held_here == (0 if cid == "C1" else 2), cid
        # The catch-up counts as unbilled exactly the periods the issuance door holds.
        assert catchup["catchup_unbilled_periods"] == held_here, (
            f"{cid}: the catch-up and the issuance door disagree on which estimates were sent")
        sent = sum(b["total_amount_gbp"] for b in estimates
                   if (cid, b["period_end"]) not in held_keys)
        true = sum(b["true_total_amount_gbp"] for b in estimates)
        assert catchup["catchup_raw_delta_gbp"] == pytest.approx(true - sent, abs=0.01)
