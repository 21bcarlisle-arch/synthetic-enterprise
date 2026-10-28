"""The Energy Price Guarantee the supplier received is its share on the SETTLED volume, not on the kWh
an estimated bill charged.

Defect this guards (residual R2 of docs/staging/SEAT_FINDING_THE_SECOND_COLD_READS_ROWS_FIND_A_LATE_
DIRECT_DEBIT_AN_UNSHOWN_PRICE_GUARANTEE_AND_ESTIMATES_TOO_CLOSE_TO_THE_MONTH_2026-10-28.md). An
estimated bill in Oct 2022 - Jun 2023 books the Treasury's share on its estimated kWh
(`hmt_epg_receipt_gbp`, the household's discount), and the catch-up at the next actual read corrects
the household's energy but never that share. On the 1a02c46116 book the 17 EPG-window accounts
outside INV_BILLED_EX_VAT_RECONCILES_TO_REVENUE's band all fall inside it once the share is taken
on settled kWh. The scheme paid on settlement data and reconciled after it ended
(docs/market_research/default_tariff_cap_and_epg_on_the_bill.md, "How the supplier was paid").

The bills come from `build_monthly_bills` with a scripted feed: actual reads in January and April,
estimates in February and March at January's kWh, above what was used.

Mutations, each reds this file:
  * `build_monthly_bills` stops stamping `epg_support_gbp` -> the key is missing.
  * it stamps the bill's own `hmt_epg_receipt_gbp` instead of the settled rows' -> the estimates'
    support exceeds what the rows received.
  * `make_epg_receipt_event` reads `hmt_epg_receipt_gbp` again -> ledger revenue exceeds settlement.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass

import pytest

from company.billing.monthly_bill_assembly import build_monthly_bills
from saas.ledger import build_ledger, derive_pnl

USE = {1: 500.0, 2: 300.0, 3: 280.0, 4: 260.0}
CAP_GBP_PER_MWH, RECEIPT_GBP_PER_MWH = 400.0, 200.0


@pytest.fixture(autouse=True)
def _the_estimate_is_the_last_actual(monkeypatch):
    monkeypatch.setattr("company.billing.monthly_bill_assembly.estimate_unread_kwh",
                        lambda _c, trailing, *_p: trailing[-1][2])
    monkeypatch.setattr("company.billing.monthly_bill_assembly.MIN_ADVANCE_DAYS", 0)


def _records():
    out = []
    for month, kwh in USE.items():
        days = calendar.monthrange(2023, month)[1]
        per_day = kwh / days
        out.extend({
            "customer_id": "C2",
            "settlement_date": f"2023-{month:02d}-{d:02d}",
            "settlement_period": 1,
            "consumption_kwh": per_day,
            "unit_rate_gbp_per_mwh": CAP_GBP_PER_MWH,
            "revenue_gbp": per_day / 1000 * CAP_GBP_PER_MWH + 0.5,
            "standing_charge_gbp": 0.5,
            "wholesale_cost_gbp": 0.0,
            "margin_gbp": 0.0,
            "hmt_epg_receipt_gbp_per_mwh": RECEIPT_GBP_PER_MWH,
            "hmt_epg_receipt_gbp": per_day / 1000 * RECEIPT_GBP_PER_MWH,
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


def _bills():
    return sorted(build_monthly_bills(_records(), _Feed()), key=lambda b: b["period_start"])


def test_each_bill_carries_the_support_on_its_months_settled_volume():
    bills = _bills()
    estimates = [b for b in bills if b["billing_basis"] == "estimated"]
    # Both sides of the partition are reachable: two estimates, two actual bills.
    assert len(estimates) == 2 and len(bills) == 4
    for b in bills:
        settled = USE[int(b["period_start"][5:7])] / 1000 * RECEIPT_GBP_PER_MWH
        assert b["epg_support_gbp"] == pytest.approx(settled, abs=1e-6), b["period_start"]
    # The estimates' discount was on kWh nobody used; the support is not.
    for b in estimates:
        assert b["hmt_epg_receipt_gbp"] > b["epg_support_gbp"] + 1.0


def test_the_ledger_books_the_support_the_scheme_paid_so_revenue_is_what_settled():
    records, bills = _records(), _bills()
    pnl = derive_pnl(build_ledger(records, bills))
    assert pnl["epg_receipt_gbp"] == pytest.approx(
        sum(USE.values()) / 1000 * RECEIPT_GBP_PER_MWH, abs=1e-6)
