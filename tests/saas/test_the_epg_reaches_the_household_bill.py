"""A default-tariff bill in the Energy Price Guarantee charges the household the EPG, and the supplier
still books the cap.

Cause B of `docs/staging/SEAT_FINDING_SVT_BILLS_ABOVE_THE_CAP_ARE_TWO_DEFECTS_NOT_A_GRADING_ARTEFACT_
2026-10-23.md`: settlement bills `revenue_gbp`, the supplier's receipt at the Ofgem level, so the
household's invoice carried HM Treasury's half. Pre-registration:
`docs/staging/records/SEAT_PREREGISTRATION_THE_EPG_REACHES_THE_HOUSEHOLD_BILL_2026-10-24.md`.

Mutations, each reds this file:
  * `generate_bill` drops the `commodity_amount_gbp -= hmt_epg_receipt_gbp` line -> the EPG bill
    fails the household ceiling.
  * `derive_pnl` drops `+ epg_receipt` from revenue -> supplier revenue falls short of settlement.
  * `stamp_hmt_epg_receipt` stamps every record (drops `if receipt:`) -> a September row carries a
    0.0 receipt. The September BILL is still identical under this mutation (a 0.0 carve is a no-op),
    so the partition asserts on the rows, which every settled day of the run would otherwise grow.
  * `_estimated_settlement_records` stops scaling the receipt -> the estimate's household rate is
    no longer the true bill's.
  * `_estimate_records_at_tariff_rate` drops its receipt line, or `stamp_hmt_epg_receipt` stops
    writing `hmt_epg_receipt_gbp_per_mwh` -> a void stub's estimate is over its ceiling by exactly
    cap minus EPG (33.47p in Jan 2023, `OCC-eb8498f3f8aa` on the `88cdf35e48` run).
"""
from datetime import date, timedelta

from company.billing.monthly_bill_assembly import (
    _estimate_records_at_tariff_rate,
    _estimated_settlement_records,
)
from company.compliance.domain_invariants import default_tariff_invoice_excess_p_per_kwh
from saas.bill_generator import generate_bill
from saas.ledger import build_ledger, derive_pnl
from sim.customer_state_layer import as_void_row
from simulation.svt_product import _ex_vat, stamp_hmt_epg_receipt
from simulation.svt_rates import get_svt_elec_rate_gbp_per_mwh

_STANDING_GBP_PER_DAY = 0.5


def _svt_month(first_day: str, kwh_per_day: float = 10.0) -> list[dict]:
    """A month of daily settled rows on an SVT term struck at the cap, ex-VAT, as settlement writes."""
    rate = _ex_vat(get_svt_elec_rate_gbp_per_mwh(first_day))
    start = date.fromisoformat(first_day)
    return [
        {
            "customer_id": "SYN-EPG",
            "settlement_date": (start + timedelta(days=i)).isoformat(),
            "settlement_period": 48,
            "consumption_kwh": kwh_per_day,
            "revenue_gbp": kwh_per_day / 1000 * rate + _STANDING_GBP_PER_DAY,
            "standing_charge_gbp": _STANDING_GBP_PER_DAY,
            "wholesale_cost_gbp": 1.0,
            "unit_rate_gbp_per_mwh": rate,
        }
        for i in range(28)
    ]


def _excess(bill: dict) -> float | None:
    return default_tariff_invoice_excess_p_per_kwh({
        "amount_gbp": bill["total_amount_gbp"], "vat_gbp": bill["vat_gbp"],
        "consumption_kwh": bill["total_consumption_kwh"],
        "commodity_amount_gbp": bill["commodity_amount_gbp"],
        "non_commodity_amount_gbp": bill["non_commodity_amount_gbp"],
        "period_start": bill["period_start"], "commodity": "electricity",
    }, "svt")


def test_the_partition():
    """Both sides are reachable: a bill inside the EPG carries a receipt, one outside carries none."""
    inside = generate_bill("SYN-EPG", stamp_hmt_epg_receipt(_svt_month("2023-01-01"), fuel="electricity"), "svt")
    outside_rows = _svt_month("2022-09-01")
    unstamped = generate_bill("SYN-EPG", [dict(r) for r in outside_rows], "svt")
    stamped_outside = stamp_hmt_epg_receipt(outside_rows, fuel="electricity")
    assert not any("hmt_epg_receipt_gbp" in r for r in stamped_outside)
    outside = generate_bill("SYN-EPG", stamped_outside, "svt")

    assert inside.get("hmt_epg_receipt_gbp", 0.0) > 0 and "hmt_epg_receipt_gbp" not in outside
    # Outside the EPG nothing on the bill moves at all.
    assert outside == unstamped


def test_the_household_is_billed_within_its_ceiling_during_the_epg():
    rows = _svt_month("2023-01-01")
    before = generate_bill("SYN-EPG", [dict(r) for r in rows], "svt")
    after = generate_bill("SYN-EPG", stamp_hmt_epg_receipt(rows, fuel="electricity"), "svt")

    # The defect, reproduced: the unstamped bill charges the household the Ofgem level.
    assert _excess(before) > 30.0
    assert _excess(after) == 0.0


def test_the_supplier_still_books_what_settlement_received():
    rows = stamp_hmt_epg_receipt(_svt_month("2023-01-01"), fuel="electricity")
    bill = generate_bill("SYN-EPG", rows, "svt")
    pnl = derive_pnl(build_ledger(rows, [bill]))

    settled = sum(r["revenue_gbp"] for r in rows)
    assert abs(pnl["revenue_gbp"] - settled) < 1e-6
    assert abs(pnl["epg_receipt_gbp"] - bill["hmt_epg_receipt_gbp"]) < 1e-9


def test_an_estimate_charges_the_household_the_same_rate_as_the_true_bill():
    rows = stamp_hmt_epg_receipt(_svt_month("2023-01-01"), fuel="electricity")
    true_bill = generate_bill("SYN-EPG", rows, "svt")
    estimate = generate_bill("SYN-EPG", _estimated_settlement_records(rows, 0.6, "electricity"), "svt")

    assert abs(estimate["average_unit_rate_gbp_per_mwh"] - true_bill["average_unit_rate_gbp_per_mwh"]) < 1e-6
    assert abs(estimate["hmt_epg_receipt_gbp"] - 0.6 * true_bill["hmt_epg_receipt_gbp"]) < 1e-6


def test_a_void_stub_estimated_at_the_tariff_rate_charges_the_household_the_epg():
    """A void row has 0 kWh, so its own receipt is 0.0, and the company estimates it at the row's rate."""
    rows = _svt_month("2023-01-01")
    for r in rows:
        as_void_row(r, "electricity")
    stamp_hmt_epg_receipt(rows, fuel="electricity")
    assert all(r["hmt_epg_receipt_gbp"] == 0.0 for r in rows)

    estimate = generate_bill(
        "OCC-EPG", _estimate_records_at_tariff_rate(rows, 193.28, "electricity"), "svt")

    assert estimate["hmt_epg_receipt_gbp"] > 0
    assert _excess(estimate) == 0.0
