"""An actual read nets an estimate run to the meter, however small the run's error (class F).

Defect (209c3350ab and 9553d403b7 books): `CATCHUP_MATERIALITY_THRESHOLD_GBP` gated the correction,
so a run whose estimates were under £5 out was never billed or refunded. 2,747 of 6,452 corrections
were dropped, on 754 of 1,293 accounts; PROS-2016-0370's run was +£3.07 (+23 kWh over four
estimates) and its billed kWh never met settled kWh. A read-to-read bill charges closing read less
the last billed read, so it cannot drop energy (SLC 21B.1).
Finding: docs/staging/SEAT_FINDING_AN_ACTUAL_READ_UNDER_FIVE_POUNDS_OFF_THE_ESTIMATES_NEVER_CORRECTS_THEM_THE_REVENUE_ROWS_CLASS_E_2026-10-29.md;
knowledge: docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md section 9.
Harness as test_the_estimate_window_holds_only_what_the_meter_told_the_supplier.py (Sep read, Oct
unread, Nov read); October is estimated at 204.48 kWh whatever it truly used.
"""

from __future__ import annotations

import pytest

from tests.company.billing.test_the_estimate_window_holds_only_what_the_meter_told_the_supplier import (
    M,
    _Feed,
    _month,
)

OCT_ESTIMATE_KWH = 204.48
# 20p/kWh plus 5% VAT: 14.62 kWh unbilled is the +£3.07 run.
GROSS_GBP_PER_KWH = 0.21


class _ReadEveryMonth(_Feed):
    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        return self.final_read_for(customer_id, period_end, meter_type, true_kwh, consecutive)


def _bills(oct_true_kwh, feed=None):
    rows = _month("C1", 9, 230.0) + _month("C1", 10, oct_true_kwh) + _month("C1", 11, 700.0)
    return {b["period_end"][:7]: b for b in M.build_monthly_bills(rows, feed or _Feed())}


@pytest.mark.parametrize("error_gbp", [3.07, -1.57, 25.0])
def test_the_read_bills_the_runs_error_whatever_its_size(error_gbp):
    """MUTATION: restore the `is_material` gate and the two sub-£5 cases fail; the £25 case is the
    control that the branch is taken where it always was."""
    oct_true_kwh = OCT_ESTIMATE_KWH + error_gbp / GROSS_GBP_PER_KWH
    bills, read = _bills(oct_true_kwh), _bills(oct_true_kwh, _ReadEveryMonth())
    october, november = bills["2023-10"], bills["2023-11"]
    assert october["estimated_consumption_kwh"] == pytest.approx(OCT_ESTIMATE_KWH, abs=0.01)
    assert november.get("catchup_applied"), "the correction was dropped"
    assert november["catchup_raw_delta_gbp"] == pytest.approx(error_gbp, abs=0.02)
    # The money nets the run: the two bills charge what the same months cost when read monthly.
    assert (october["total_amount_gbp"] + november["total_amount_gbp"]
            == pytest.approx(read["2023-10"]["total_amount_gbp"] + read["2023-11"]["total_amount_gbp"],
                             abs=0.02))
    assert (october["vat_gbp"] + november["vat_gbp"]
            == pytest.approx(read["2023-10"]["vat_gbp"] + read["2023-11"]["vat_gbp"], abs=0.02))
    # The display flag survives, and says which side of £5 the correction fell.
    assert november["catchup_is_material"] is (abs(error_gbp) >= M.CATCHUP_MATERIALITY_THRESHOLD_GBP)


def test_a_run_estimated_exactly_adds_no_line():
    """A correction that rounds to 0.00 is not stamped as an event (the 2026-07-12 Expert-Hour
    finding the old gate answered), yet the register's true-up is still recorded."""
    november = _bills(OCT_ESTIMATE_KWH)["2023-11"]
    assert not november.get("catchup_applied")
    assert november["read_true_up_periods"] == 1
