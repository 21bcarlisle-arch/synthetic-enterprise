"""W2_36 <-> D48 runner: it writes its own row and nothing else.

The 2026-11-08 draft of this runner carried an UNMEASURED_PAIRS block that wrote `gap: null`
rows for W2_30 and W1_14. Those keys belong to `tools/couple_d48_billing_gap.py`, which landed
measured rows for them in aca12f3a5, and a rerun of the draft would have overwritten them.
"""
from __future__ import annotations

import json

import pytest

import tools.couple_w2_36_d48 as pair

W2_30 = "W2_30_per_household_half_hourly_electricity_and_seasonal_gas_shape"
W1_14 = "W1_14_weather_cells_for_household_heat_load"


def _book():
    """Two accounts. A: an estimate over-bills by 10 kWh and an actual read trues it up.
    B: an estimate is still open, 5 kWh under true use."""
    bills, reads = [], []

    def bill(cid, end, kwh, basis, true_up=None, true_kwh=None):
        bills.append({"customer_id": cid, "period_end": end, "total_consumption_kwh": kwh,
                      "billing_basis": basis, "read_true_up_kwh": true_up,
                      "commodity": "electricity"})
        reads.append({"customer_id": cid, "true_consumption_kwh": true_kwh})

    bill("A", "2020-01-31", 110.0, "estimated", true_kwh=100.0)
    bill("A", "2020-02-29", 100.0, "actual", true_up=-10.0, true_kwh=100.0)
    bill("B", "2020-01-31", 100.0, "actual", true_kwh=100.0)
    bill("B", "2020-02-29", 95.0, "estimated", true_kwh=100.0)
    return {"bills": bills, "meter_read_log": reads, "producing_commit": {"commit": "test"}}


def test_the_measure_can_see_both_a_closed_and_an_open_estimate():
    rows, truth, belief, noskill, s = pair.account_errors(_book())
    # A's read tells the company exactly what its estimate over-billed; B's open run it cannot see.
    assert list(truth) == pytest.approx([10.0, -5.0])
    assert list(belief) == pytest.approx([10.0, 0.0])
    assert s == pytest.approx(10.0 / 110.0)


def test_a_rerun_leaves_the_w2_30_and_w1_14_rows_byte_equal(tmp_path):
    book = tmp_path / "book.json"
    book.write_text(json.dumps(_book()))
    ledger = tmp_path / "ledger.json"
    others = {W2_30: {"twin_atom_id": "D48", "gap": 0.386}, W1_14: {"twin_atom_id": "D48", "gap": None}}
    ledger.write_text(json.dumps(others, indent=2, sort_keys=True))
    before = {k: json.dumps(v, sort_keys=True) for k, v in others.items()}

    for _ in range(2):
        pair.main(["--book", str(book), "--write-ledger", "--ledger", str(ledger)])

    after = json.loads(ledger.read_text())
    assert pair.WORLD_ATOM_ID in after, "the runner must write its own row, or this test proves nothing"
    assert {k: json.dumps(after[k], sort_keys=True) for k in others} == before
    assert set(after) == set(others) | {pair.WORLD_ATOM_ID}
