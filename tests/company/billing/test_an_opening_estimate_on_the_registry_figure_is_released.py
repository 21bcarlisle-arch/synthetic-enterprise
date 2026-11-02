"""An estimate held on consumption scale, at a listed dwelling, before the account's first read and no
higher than the registry figure it was handed, is released (`release_on_measured_rate`, §4f).

Defect this guards: SYN-2016-582, an electrically heated listed dwelling (EAC 22,909.7 kWh), had its
four opening estimates (Dec 2016 to Mar 2017, 1,869 to 2,633 kWh a month) held against the population
ceiling. With no read yet, nothing could release them, and they reached the customer as one £1,220.95
catch-up at the 31 Jul 2017 read (08f267b666 book; SEAT_FINDING_THREE_SMALL_EXCEPTIONS_..._2026-10-29.md
§3). Rules and choices: docs/market_research/unbilled_energy_and_revenue_assurance.md §4f.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass

import pytest

from company.billing.monthly_bill_assembly import build_monthly_bills
from company.billing.pre_bill_validation import (
    ValidationOutcome,
    release_on_measured_rate,
    validate_bill,
    validate_bills,
)

EAC = 22909.7  # SYN-2016-582's registry figure


def _bill(customer_id, start, end, kwh, basis="estimated", listed=True, registry=EAC):
    """A resi electricity bill at 5% VAT that fails the ceiling on scale alone."""
    days = (int(end[8:]) - int(start[8:])) + 1
    commodity = round(kwh * 0.15, 2)
    standing = round(days * 0.30, 2)
    vat = round((commodity + standing) * 0.05, 2)
    bill = {
        "customer_id": customer_id, "segment": "resi", "commodity": "electricity",
        "period_start": start, "period_end": end,
        "total_consumption_kwh": kwh, "commodity_amount_gbp": commodity,
        "non_commodity_amount_gbp": 0.0, "standing_charge_gbp": standing, "vat_gbp": vat,
        "total_amount_gbp": round(commodity + standing + vat, 2),
        "billing_basis": basis, "premise_council_tax_listed": listed,
    }
    if registry is not None:
        bill["registry_annual_kwh"] = registry
    return bill


def test_every_leg_of_the_registry_release_is_reachable():
    """Assert the release CAN be taken before asserting what each refusal does: a release that
    refused everything would pass every refusal below. January's 2,633.2 kWh is the printed
    estimate, and the registry figure's share of those 31 days to the tenth."""
    jan = ("2017-01-01", "2017-01-31")
    bills = [
        _bill("AT", *jan, 2633.2),                         # the registry figure's own share
        _bill("OVER", *jan, 2800.0),                       # above it: wrong in scale for this meter
        _bill("STUB", "2017-01-25", "2017-01-31", 2633.2),  # a month's energy on a seven-day stub
        _bill("NOFIGURE", *jan, 2633.2, registry=None),    # the TDCV stand-in, no measurement behind it
        _bill("UNLISTED", *jan, 2633.2, listed=None),      # the mislabel half is unanswered
    ]
    assert all(validate_bill(b).held and validate_bill(b).consumption_scale_only for b in bills)
    passing, held = validate_bills(bills)
    released = {b["customer_id"]: b["pre_bill_release"] for b in passing}
    assert list(released) == ["AT"]
    assert released["AT"]["outcome"] == ValidationOutcome.RELEASED_ON_REGISTRY_FIGURE.value
    assert released["AT"]["registry_share_kwh"] == pytest.approx(2633.2, abs=0.05)
    assert sorted(r.customer_id for r in held) == ["NOFIGURE", "OVER", "STUB", "UNLISTED"]


def test_after_a_read_the_measured_rate_decides_not_the_registry():
    """Once the meter has a read, §4d governs: an estimate at the registry figure but above every rate
    the meter measured stays held."""
    read = _bill("READ", "2017-01-01", "2017-01-31", 1000.0, basis="actual")
    feb = _bill("READ", "2017-02-01", "2017-02-28", 2403.2)
    assert release_on_measured_rate(feb, validate_bill(feb), [read, feb]) is None
    assert release_on_measured_rate(feb, validate_bill(feb), [feb]) is not None


# --- The billing run stamps the figure, and the catch-up and the issuance door agree -------------
# If they disagreed, a released opening estimate would be reconciled as billed nothing at the first
# read and so billed twice. The scripted read feed follows
# test_an_estimate_at_the_meters_measured_rate_is_released.py.

USE = {"C1": {1: 2600.0, 2: 2350.0, 3: 2500.0}, "C2": {1: 2600.0, 2: 2350.0, 3: 2500.0}}


@pytest.fixture
def _an_electrically_heated_registration(monkeypatch):
    def registration(customer_id):
        return {"customer_id": customer_id, "segment": "resi", "commodity": "electricity",
                "contract_type": "fixed_1yr", "eac_kwh": EAC}
    monkeypatch.setattr("company.billing.monthly_bill_assembly.get_customer", registration)


def _records():
    out = []
    for cid, months in USE.items():
        for month, kwh in months.items():
            days = calendar.monthrange(2017, month)[1]
            out.extend({
                "customer_id": cid, "settlement_date": f"2017-{month:02d}-{d:02d}",
                "settlement_period": 1, "consumption_kwh": kwh / days,
                "unit_rate_gbp_per_mwh": 150.0, "revenue_gbp": (kwh / days / 1000) * 150.0 + 0.3,
                "standing_charge_gbp": 0.3, "wholesale_cost_gbp": 0.0, "margin_gbp": 0.0,
            } for d in range(1, days + 1))
    return out


@dataclass
class _Read:
    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int


class _Feed:
    """No read until March: January and February are opening estimates."""

    def meter_type_for(self, customer):
        return "traditional"

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        if period_end[5:7] in ("01", "02"):
            return _Read("estimated", None, consecutive + 1)
        return _Read("actual", None, 0)

    def final_read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        return _Read("actual", None, 0)


@pytest.mark.usefixtures("_an_electrically_heated_registration")
def test_the_opening_estimates_issue_and_the_first_read_reconciles_them_as_sent():
    bills = build_monthly_bills(
        _records(), _Feed(),
        premise_listing_feed=lambda customer: True if customer["customer_id"] == "C1" else None)
    _issued, held = validate_bills(bills)
    held_keys = {(r.customer_id, r.period_end) for r in held}
    for cid in USE:
        mine = sorted((b for b in bills if b["customer_id"] == cid), key=lambda b: b["period_end"])
        estimates = [b for b in mine if b["billing_basis"] == "estimated"]
        assert len(estimates) == 2
        assert all(b["registry_annual_kwh"] == EAC for b in estimates)
        # Over the population ceiling, so the release is what issues them, not a pass.
        assert all(validate_bill(b).held for b in estimates)
        held_here = sum((cid, b["period_end"]) in held_keys for b in estimates)
        assert held_here == (0 if cid == "C1" else 2), cid
        catchup = mine[-1]
        assert catchup["catchup_unbilled_periods"] == held_here, (
            f"{cid}: the catch-up and the issuance door disagree on which estimates were sent")
