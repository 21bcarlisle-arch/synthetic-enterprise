"""The SLC 21B.4 register writes a row when a run of estimates reaches a year, and not before.

Defect this guards (2026-10-16,
docs/staging/WORKER_FINDING_C7_AND_286_OTHER_RUNS_OVER_TWELVE_MONTHS_NONE_BILLED_PAST_THE_BAR_AND_NOTHING_ASKS_FOR_A_READ_2026-10-16.md):
nothing in the company read `consecutive_estimated_count`, so 355 runs of a year or more without a
read on the published run were invisible to it.

The bills come from the company's own `build_monthly_bills` with a scripted read feed: one account
read in January 2023 and then estimated for 11 months (C1), another for 12 (C2), a third for 13
(C3), which still writes one row: the register counts runs, not bills past the year. The register reads
only those bills. Mutations, each run and reverted: the trigger at 11 or 13, or `>=` in place of
`==` (one row per bill past the year), each reds the single assertion.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass

from company.billing.monthly_bill_assembly import build_monthly_bills
from company.billing.read_duty_register import read_duty_register

# Months 2023-01 .. 2024-03. Each account is read in its first month and then estimated for RUN
# months, then read again.
MONTHS = [(2023, m) for m in range(1, 13)] + [(2024, m) for m in range(1, 4)]
RUN = {"C1": 11, "C2": 12, "C3": 13}


def _records():
    out = []
    for cid in RUN:
        for yr, mo in MONTHS:
            days = calendar.monthrange(yr, mo)[1]
            out.extend({
                "customer_id": cid,
                "settlement_date": f"{yr}-{mo:02d}-{d:02d}",
                "settlement_period": 1,
                "consumption_kwh": 10.0,
                "unit_rate_gbp_per_mwh": 200.0,
                "revenue_gbp": 0.01 * 200.0 + 0.5,
                "standing_charge_gbp": 0.5,
                "wholesale_cost_gbp": 0.0,
                "margin_gbp": 0.0,
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
        index = MONTHS.index((int(period_end[:4]), int(period_end[5:7])))
        if 1 <= index <= RUN[customer_id]:
            return _Read("estimated", None, consecutive + 1)
        return _Read("actual", None, 0)

    def final_read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        return _Read("actual", None, 0)


def test_a_run_of_eleven_writes_no_row_and_a_run_of_twelve_or_more_writes_one_at_its_twelfth():
    rows = read_duty_register(build_monthly_bills(_records(), _Feed()))
    assert [(r["account_id"], r["date"], r["duty_applies"]) for r in rows] == [
        ("C2", "2024-01-31", True), ("C3", "2024-01-31", True)]
