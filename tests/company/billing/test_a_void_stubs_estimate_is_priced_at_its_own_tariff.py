"""A void stub's estimate is charged at the account's own tariff, not at the 0p of an empty home.

Defect this guards (D46, BLOCKING finding
docs/staging/WORKER_FINDING_NINE_CUSTOMER_YEARS_BILL_LESS_THAN_THEIR_GROSS_MARGIN_AT_ORIGIN_2026-10-14.md):
`build_monthly_bills` priced an estimate by scaling the true settled rows, and only when true kWh was
above 0. A B7 void row holds 0 kWh, so the company printed its registry-EAC estimate and charged the
true bill, the standing charge alone. 60 OCC invoices on the 2248e3baf ledger did, and whether an
estimate was charged turned on a fact only the world holds. Knowledge:
docs/market_research/back_billing_and_liability.md §14.

The bills come from the company's own `build_monthly_bills` with a scripted read feed: December 2022
is a void opening stub read as estimated, January an actual read. The opening estimate is replaced by
a fixed 55 kWh, because this file grades the price, not the estimate.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass

import pytest

from company.billing.monthly_bill_assembly import build_monthly_bills

STUB_KWH = 55.0
RATE = 250.0
SC = 0.5
JAN_KWH = 300.0
# V1's void rows carry their tariff rate; V0's carry none, so it keeps the old fallback.
RATES = {"V1": RATE, "V0": None}


@pytest.fixture(autouse=True)
def _the_opening_estimate_is_fixed(monkeypatch):
    monkeypatch.setattr(
        "company.billing.monthly_bill_assembly.opening_estimate_kwh", lambda *_a: STUB_KWH)
    monkeypatch.setattr(
        "company.billing.monthly_bill_assembly.get_customer",
        lambda cid: {"segment": "resi", "commodity": "electricity"})


def _records():
    out = []
    for cid, rate in RATES.items():
        # The void stub: 24-31 December, 0 kWh, the owner's standing charge, the rate untouched
        # (`as_void_row` zeroes volumes, not the rate).
        out.extend({
            "customer_id": cid, "settlement_date": f"2022-12-{d:02d}", "settlement_period": 1,
            "consumption_kwh": 0.0, "unit_rate_gbp_per_mwh": rate,
            "revenue_gbp": SC, "standing_charge_gbp": SC, "void_owner_charge_gbp": SC,
            "wholesale_cost_gbp": 0.0, "margin_gbp": SC,
        } for d in range(24, 32))
        days = calendar.monthrange(2023, 1)[1]
        out.extend({
            "customer_id": cid, "settlement_date": f"2023-01-{d:02d}", "settlement_period": 1,
            "consumption_kwh": JAN_KWH / days, "unit_rate_gbp_per_mwh": RATE,
            "revenue_gbp": JAN_KWH / days / 1000 * RATE + SC, "standing_charge_gbp": SC,
            "wholesale_cost_gbp": 0.0, "margin_gbp": 0.0,
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
        if period_end.startswith("2022-12"):
            return _Read("estimated", None, consecutive + 1)
        return _Read("actual", None, 0)

    def final_read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        return _Read("actual", None, 0)


def _stub_and_read(cid):
    bills = sorted((b for b in build_monthly_bills(_records(), _Feed()) if b["customer_id"] == cid),
                   key=lambda b: b["period_end"])
    assert [b["billing_basis"] for b in bills] == ["estimated", "actual"]
    return bills


def test_a_void_stubs_estimate_is_charged_at_the_rows_tariff_and_a_row_without_one_keeps_the_true_bill():
    priced_stub, _ = _stub_and_read("V1")
    fallback_stub, _ = _stub_and_read("V0")
    standing = 8 * SC

    # Both branches are reachable: V1 is priced, V0 is not.
    assert priced_stub["total_consumption_kwh"] == pytest.approx(STUB_KWH)
    assert fallback_stub["total_consumption_kwh"] == pytest.approx(0.0)

    # V1 charges the estimate at its own rate on top of the unchanged standing charge, with VAT.
    vat = priced_stub["vat_gbp"] / (priced_stub["total_amount_gbp"] - priced_stub["vat_gbp"])
    expected = (STUB_KWH / 1000 * RATE + standing) * (1 + vat)
    assert priced_stub["total_amount_gbp"] == pytest.approx(expected, abs=0.01), (
        "a void stub's estimate was charged at 0p: the price turned on the world's 0 kWh")
    assert priced_stub["standing_charge_gbp"] == pytest.approx(standing)

    # V0 has no rate to name, so it bills what was used and says so.
    assert fallback_stub["total_amount_gbp"] == pytest.approx(
        fallback_stub["true_total_amount_gbp"], abs=0.01)


def test_the_next_actual_read_credits_the_void_estimate_back_in_full():
    stub, read = _stub_and_read("V1")
    charged_for_nothing = stub["total_amount_gbp"] - stub["true_total_amount_gbp"]
    assert charged_for_nothing > 1.0
    assert read["catchup_raw_delta_gbp"] == pytest.approx(-charged_for_nothing, abs=0.01)
