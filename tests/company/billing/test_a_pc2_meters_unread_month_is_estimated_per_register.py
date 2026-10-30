"""A PC2 (Economy 7) meter's unread month is estimated per register on PC2's published shape.

Defect this guards (docs/staging/SEAT_FINDING_A_PC2_METERS_UNREAD_MONTH_IS_ESTIMATED_PER_REGISTER_2026-10-30.md):
a storage home's estimate was its total over a PC1-shaped weight. That spreads winter night heat
into a summer month: on this file's home it estimates August at +22%. The estimate was then split
into Day and Night in the unread month's own settled ratio, a split no read gave the company.
Knowledge: docs/market_research/a_storage_heated_homes_default_tariff_is_two_rate.md.

The home here uses 7,000 kWh a year, 60% of it at night (Nottingham's 53-66%, page G4). Each
register follows PC2's monthly shape from January to July. In August, which goes unread, it doubles
its Night use. A per-register estimate on PC2's shape is therefore exact for Day and for PC2's Night,
and it cannot know about the doubling.

R15, each mutation applied in place and reverted:
  * `economy_7 = False` in `build_monthly_bills`: the PC2 test fails at the total.
  * `register_ratios=None` at the scale: the PC2 test fails at the Night register.
  * `estimate_unread_register_kwh` uses each register's weight as `profile_weight("electricity", ...)`:
    the PC2 test fails at the total.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import date

import pytest

import company.billing.monthly_bill_assembly as M
from company.billing.unread_month_estimate import (
    PC2_MONTHLY_REGISTER_SHARE,
    estimate_unread_register_kwh,
)

NIGHT_OF_YEAR = sum(PC2_MONTHLY_REGISTER_SHARE["night"])
RATE = {"day": 300.0, "night": 140.0}


def _use(month: int, register: str) -> float:
    share = 0.6 / NIGHT_OF_YEAR if register == "night" else 0.4 / (1 - NIGHT_OF_YEAR)
    kwh = 7000 * PC2_MONTHLY_REGISTER_SHARE[register][month - 1] * share
    return kwh * 2 if (month, register) == (8, "night") else kwh


def _records():
    out = []
    for month in range(1, 9):
        days = calendar.monthrange(2023, month)[1]
        for day in range(1, days + 1):
            for period, register in ((2, "night"), (20, "day")):
                kwh = _use(month, register) / days
                out.append({
                    "customer_id": "S1",
                    "settlement_date": f"2023-{month:02d}-{day:02d}",
                    "settlement_period": period,
                    "consumption_kwh": kwh,
                    "unit_rate_gbp_per_mwh": RATE[register],
                    "revenue_gbp": kwh / 1000 * RATE[register] + 0.25,
                    "standing_charge_gbp": 0.25,
                    "wholesale_cost_gbp": 0.0,
                    "margin_gbp": 0.0,
                    f"tou_{register}_kwh": kwh,
                    f"tou_{register}_unit_charge_gbp": kwh / 1000 * RATE[register],
                })
    return out


@dataclass
class _Read:
    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int


class _AugustUnread:
    def meter_type_for(self, customer):
        return "traditional"

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        if period_end[5:7] == "08":
            return _Read("estimated", None, consecutive + 1)
        return _Read("actual", None, 0)

    def final_read_for(self, *_args):
        return _Read("actual", None, 0)


def _august(monkeypatch, profile_class: int) -> dict:
    monkeypatch.setattr(M, "get_customer", lambda _cid: {
        "commodity": "electricity", "registered_profile_class": profile_class, "eac_kwh": 7000})
    bills = M.build_monthly_bills(_records(), _AugustUnread())
    return next(b for b in bills if b["period_end"].startswith("2023-08"))


def _register(bill: dict, band: str) -> float:
    return next(r["consumption_kwh"] for r in bill["registers"] if r["band"] == band)


def test_a_pc2_meters_unread_month_is_its_registers_on_pc2s_shape(monkeypatch):
    pc2, pc1 = _august(monkeypatch, 2), _august(monkeypatch, 1)
    # Both meters reach the estimate branch, so the difference below is the shape, not a guard.
    assert pc2["billing_basis"] == pc1["billing_basis"] == "estimated"

    day, pc2_night = _use(8, "day"), _use(8, "night") / 2
    assert pc2["estimated_consumption_kwh"] == pytest.approx(day + pc2_night, abs=0.05)
    # The split is the estimate's: Night is PC2's August, not the doubled use no read reported.
    assert _register(pc2, "night") == pytest.approx(pc2_night, rel=1e-6)
    assert _register(pc2, "day") == pytest.approx(day, rel=1e-6)

    # The same home on PC1 is still the total on PC1's shape, which over-estimates its summer.
    assert pc1["estimated_consumption_kwh"] > 1.15 * pc2["estimated_consumption_kwh"]


def test_a_register_read_at_nothing_estimates_nothing_and_a_meter_read_at_nothing_no_estimate():
    window = [(date(2023, 5, 1), date(2023, 5, 31), {"day": 300.0, "night": 0.0})]
    estimate = estimate_unread_register_kwh(window, date(2023, 6, 1), date(2023, 6, 30))
    assert estimate["night"] == 0.0 and estimate["day"] > 0
    nothing = [(date(2023, 5, 1), date(2023, 5, 31), {"day": 0.0, "night": 0.0})]
    assert estimate_unread_register_kwh(nothing, date(2023, 6, 1), date(2023, 6, 30)) is None
