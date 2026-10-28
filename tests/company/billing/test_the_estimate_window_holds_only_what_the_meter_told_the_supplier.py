"""R3 (2026-10-28): after an estimated month, an actual read tells the supplier the register's advance
since the LAST actual read, never the month's own settlement kWh. The estimate window used to take
that month's settlement kWh, which no read gave the supplier. On the 1a02c46116 book that set the
estimate on 2,754 of 31,588 estimated bills (493 accounts), wherever no actual read lay 182 or more
days back to annualise.

Finding: docs/staging/SEAT_FINDING_THE_SECOND_COLD_READS_ROWS_FIND_A_LATE_DIRECT_DEBIT_AN_UNSHOWN_PRICE_GUARANTEE_AND_ESTIMATES_TOO_CLOSE_TO_THE_MONTH_2026-10-28.md
(R3); pre-registration: docs/staging/records/SEAT_PREREGISTRATION_R3_THE_PRINTED_ACTUAL_REGISTER_AND_THE_ESTIMATE_WINDOW_2026-10-28.md.
"""

from __future__ import annotations

import calendar
import datetime as dt
from dataclasses import dataclass

import pytest

from company.billing import monthly_bill_assembly as M
from company.billing import unread_month_estimate as U

D = dt.date
DEC = (D(2023, 12, 1), D(2023, 12, 31))


@dataclass
class _Read:
    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int


class _Feed:
    """Sep read, Oct unread, Nov read, Dec unread: a read that closes an estimated run."""

    def meter_type_for(self, customer):
        return "traditional"

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        if period_end[:7] in ("2023-09", "2023-11"):
            return _Read("actual", None, 0)
        return _Read("estimated", None, consecutive + 1)

    def final_read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        return _Read("actual", None, 0)


def _month(cid, month, kwh):
    days = calendar.monthrange(2023, month)[1]
    return [{"customer_id": cid, "settlement_date": f"2023-{month:02d}-{d:02d}",
             "settlement_period": 1, "consumption_kwh": kwh / days,
             "unit_rate_gbp_per_mwh": 200.0, "revenue_gbp": kwh / days / 1000 * 200.0 + 0.5,
             "standing_charge_gbp": 0.5, "wholesale_cost_gbp": 0.0, "margin_gbp": 0.0}
            for d in range(1, days + 1)]


def _december(oct_kwh, nov_kwh, **kw):
    rows = (_month("C1", 9, 230.0) + _month("C1", 10, oct_kwh) + _month("C1", 11, nov_kwh)
            + _month("C1", 12, 1000.0))
    bills = M.build_monthly_bills(rows, _Feed(), **kw)
    return next(b for b in bills if b["period_end"].startswith("2023-12"))["estimated_consumption_kwh"]


@pytest.mark.parametrize("annualised", [False, True])
def test_two_worlds_with_the_same_reads_are_estimated_alike(annualised):
    """Defect caught: the window holds November's settlement kWh. The two worlds' meters read the
    same on 30 Sep and 30 Nov (1,120 kWh between them); only how that splits across Oct and Nov
    differs, which no read shows, so the December estimate must not move. Three months of reads
    is under the 182-day advance, so the switch's on leg falls back to the window too."""
    late = _december(420.0, 700.0, annualised_advance_estimate=annualised)
    early = _december(700.0, 420.0, annualised_advance_estimate=annualised)
    assert late == pytest.approx(early, abs=0.01), (late, early)


def test_the_window_entry_spans_the_last_actual_read_to_this_one():
    """The value, not only the invariance: the entry after the run is 1 Oct to 30 Nov at the
    register's 1,120 kWh advance. The branch is asserted takeable first: the month-only window
    the defect built must give a different December, or the test above proves nothing."""
    sep = (D(2023, 9, 1), D(2023, 9, 30), 230.0)
    read = [sep, (D(2023, 10, 1), D(2023, 11, 30), 1120.0)]
    month_only = [sep, (D(2023, 11, 1), D(2023, 11, 30), 700.0)]
    honest = U.estimate_unread_kwh("electricity", read, *DEC)
    assert abs(honest - U.estimate_unread_kwh("electricity", month_only, *DEC)) > 1.0
    assert _december(420.0, 700.0) == pytest.approx(honest, abs=0.01)
