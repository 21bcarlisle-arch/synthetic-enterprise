"""A void stub's estimate on an Economy 7 meter prints Day and Night, not one Anytime register.

The bb58608b91 book: two occupier accounts (OCC-23ee23cb44e4, OCC-7e06d09fc108) opened on a PC2
meter with a 7-day stub billed to the owner. `as_void_row` zeroes the band kWh (89220b9ddc), so the
stub went through `_estimate_records_at_tariff_rate`, which priced the estimate flat and wrote no
band. The bill printed Anytime, the meter's Day and Night opened at 0 on the next bill, and the
stubs were 6 of the 9 non-renewal breaches that refused the publish (E7 two registers 2, ToU bands
sum 2, estimate after actual 2).

Mutation: drop the band write in `_estimate_records_at_tariff_rate` -> the E7 tests red (no
registers). Price every band at the row's opening rate -> the daily split's Night is no cheaper
than its Day, and reds. The single-rate test is the other side of the partition: a void stub with no band
keys still prints no registers.
"""
from datetime import date, timedelta

import pytest

from company.billing.monthly_bill_assembly import _estimate_records_at_tariff_rate
from saas.bill_generator import generate_bill
from sim.customer_state_layer import as_void_row
from simulation.settlement_daily import fold_to_days
from simulation.svt_product import stamp_hmt_epg_receipt

_DAY_RATE, _NIGHT_RATE = 236.773, 111.283  # GBP/MWh, the contracted pair on OCC-23ee23cb44e4
_NIGHT_PERIODS = range(1, 15)


def _e7_void_week(first_day: str, two_rate: bool = True, daily: bool = False) -> list[dict]:
    """A week of settled rows on an Economy 7 term, voided as the world voids them: half-hourly,
    or folded to the daily rows the world's book holds, each carrying both bands."""
    start = date.fromisoformat(first_day)
    rows = []
    for d in range(7):
        for period in range(1, 49):
            band = "night" if period in _NIGHT_PERIODS else "day"
            rate = (_NIGHT_RATE if band == "night" else _DAY_RATE) if two_rate else 180.0
            kwh = 0.4
            row = {
                "customer_id": "OCC-E7",
                "settlement_date": (start + timedelta(days=d)).isoformat(),
                "settlement_period": period,
                "consumption_kwh": kwh,
                "revenue_gbp": kwh / 1000 * rate + 0.005,
                "standing_charge_gbp": 0.005,
                "wholesale_cost_gbp": 0.01,
                "unit_rate_gbp_per_mwh": rate,
            }
            if two_rate:
                row["tou_%s_kwh" % band] = kwh
                row["tou_%s_unit_charge_gbp" % band] = kwh / 1000 * rate
            rows.append(row)
    if daily:
        rows = fold_to_days(rows)
    for row in rows:
        as_void_row(row, "electricity")
    return stamp_hmt_epg_receipt(rows, fuel="electricity")


@pytest.mark.parametrize("first_day", ["2022-01-25", "2023-01-25"])  # outside and inside the EPG
def test_the_stub_prints_day_and_night_summing_to_the_estimate(first_day):
    rows = _e7_void_week(first_day)
    bill = generate_bill("OCC-E7", _estimate_records_at_tariff_rate(rows, 95.5, "electricity"), "svt")

    assert bill.get("tou_registers_withheld") is None
    registers = bill.get("registers") or []
    assert [r["label"] for r in registers] == ["Day", "Night"]
    assert sum(r["consumption_kwh"] for r in registers) == pytest.approx(95.5)


@pytest.mark.parametrize("daily", [False, True])
def test_the_per_register_estimate_sets_the_split(daily):
    rows = _e7_void_week("2022-01-25", daily=daily)
    by_register = {"day": 40.0, "night": 55.5}
    bill = generate_bill("OCC-E7", _estimate_records_at_tariff_rate(
        rows, 95.5, "electricity", by_register), "svt")

    kwh = {r["label"]: r["consumption_kwh"] for r in bill["registers"]}
    assert kwh == pytest.approx({"Day": 40.0, "Night": 55.5})
    # Each register at its own band's rate: Day's energy costs the contracted gap more per kWh than
    # Night's (12.5p here). Priced at one rate the two are equal to float noise, which a bare `<` passed.
    rate = {r["label"]: r["commodity_amount_gbp"] / r["consumption_kwh"] for r in bill["registers"]}
    assert rate["Day"] - rate["Night"] == pytest.approx((_DAY_RATE - _NIGHT_RATE) / 1000)


def test_a_daily_row_without_a_per_register_estimate_invents_no_split():
    """Both bands on one row and no register estimate: no split is established, so none is printed."""
    rows = _e7_void_week("2022-01-25", daily=True)
    bill = generate_bill("OCC-E7", _estimate_records_at_tariff_rate(rows, 95.5, "electricity"), "svt")

    assert bill.get("registers") is None
    assert bill["total_consumption_kwh"] == pytest.approx(95.5)


def test_a_single_rate_void_stub_still_prints_no_registers():
    rows = _e7_void_week("2022-01-25", two_rate=False)
    bill = generate_bill("OCC-E7", _estimate_records_at_tariff_rate(
        rows, 95.5, "electricity", {"day": 40.0, "night": 55.5}), "svt")

    assert bill.get("registers") is None
    assert bill["total_consumption_kwh"] == pytest.approx(95.5)
