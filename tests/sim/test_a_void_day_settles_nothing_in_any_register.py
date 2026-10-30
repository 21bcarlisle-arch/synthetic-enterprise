"""A void day at a two-rate meter settles nothing in any register, not only in its total.

Defect this guards (docs/staging/SEAT_FINDING_THE_E7_AND_PC2_BUILDS_LEAVE_EIGHT_ROWS_BREACHED_ON_PROFILE_CLASS_2_HOMES_2026-10-30.md,
point 5): `as_void_row` zeroed `consumption_kwh` and kept the occupied day's `tou_day_kwh` and
`tou_night_kwh`. The bands then held 82 kWh against a 95 kWh bill, the bill withheld its registers,
and OCC-23ee23cb44e4's and OCC-7e06d09fc108's first two bills printed one Anytime register on an
Economy 7 meter. Mutation: drop the band loop in `as_void_row` and this test reds.
"""

from __future__ import annotations

from sim.customer_state_layer import as_void_row


def test_a_void_rows_bands_are_zero_and_its_standing_charge_stays():
    rec = {"settlement_date": "2022-02-01", "consumption_kwh": 11.58, "revenue_gbp": 2.76,
           "tou_day_kwh": 9.84, "tou_night_kwh": 1.74,
           "tou_day_unit_charge_gbp": 2.33, "tou_night_unit_charge_gbp": 0.19,
           "standing_charge_gbp": 0.0, "capital_cost_gbp": 0.0}
    as_void_row(rec, "electricity")
    bands = {k: v for k, v in rec.items() if k.startswith("tou_")}
    assert len(bands) == 4 and set(bands.values()) == {0.0}, bands
    assert rec["consumption_kwh"] == 0.0
    # The standing charge is the owner's and is still settled: the row is a void, not a deletion.
    assert rec["standing_charge_gbp"] > 0 and rec["revenue_gbp"] == rec["standing_charge_gbp"]
