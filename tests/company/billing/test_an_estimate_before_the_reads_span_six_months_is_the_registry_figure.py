"""E1 (2026-10-28): an estimate set from too short a span of the company's own reads is the registry's.

Defect (SEAT_FINDING_THE_PRINTED_REGISTER_FIX_EXPOSES_ESTIMATES_FROM_ONE_READ_AND_PRINTS_6436_OPENING_
READS_NOBODY_TOOK_2026-10-28.md, E1): after an occupier's short first month, every later estimate
scaled from that one advance. OCC-f6813bf9f05eg gas: 138 kWh in Oct 2016, then eight estimates
totalling about 1,890 kWh against about 8,065 on the meter (8 of 13 breached runs). The published
method annualises an advance only between reads "at least 6 months apart" (DESNZ on the BSC's AA;
Xoserve's AQ, 9-36 months); "an EAC is used where two such meter readings are not available". So
until the reads span that, the estimate is the registry figure spread by the shape, as before the
first read. Knowledge: docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md §7.
"""

from __future__ import annotations

import calendar
import datetime as dt
from dataclasses import dataclass

import pytest

from company.billing import monthly_bill_assembly as M
from company.billing import unread_month_estimate as U
from company.interfaces.supply_book import registered_point

D = dt.date


@dataclass
class _Read:
    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int


class _Feed:
    """Actual reads up to and including `last_read`, estimated after it."""

    def __init__(self, last_read):
        self.last_read = last_read

    def meter_type_for(self, customer):
        return "traditional"

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        if period_end[:7] <= self.last_read:
            return _Read("actual", None, 0)
        return _Read("estimated", None, consecutive + 1)

    def final_read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        return _Read("actual", None, 0)


def _month(cid, year, month, kwh):
    days = calendar.monthrange(year, month)[1]
    return [{"customer_id": cid, "settlement_date": f"{year}-{month:02d}-{d:02d}",
             "settlement_period": 1, "consumption_kwh": kwh / days,
             "unit_rate_gbp_per_mwh": 200.0, "revenue_gbp": kwh / days / 1000 * 200.0 + 0.5,
             "standing_charge_gbp": 0.5, "wholesale_cost_gbp": 0.0, "margin_gbp": 0.0}
            for d in range(1, days + 1)]


def _estimates(first_month, last_read):
    """Supplied from `first_month` of 2023 to December, a short 40 kWh first read, 400 kWh a month."""
    rows = []
    for m in range(first_month, 13):
        rows += _month("C1", 2023, m, 40.0 if m == first_month else 400.0)
    bills = M.build_monthly_bills(rows, _Feed(last_read))
    return {b["period_end"][:7]: b for b in bills if b["billing_basis"] == "estimated"}


def test_one_short_read_sets_no_estimate_and_the_registry_figure_is_billed():
    """Read once (a 40 kWh first month), estimated for two months after: each estimate is the
    registry figure over the month, not the 40 kWh scaled. The branch is asserted takeable: the
    one-read window gives a different number, or this proves nothing."""
    est = _estimates(9, "2023-09")
    for month in ("2023-10", "2023-11"):
        start = D(2023, int(month[5:]), 1)
        end = D(2023, start.month, calendar.monthrange(2023, start.month)[1])
        registry = U.opening_estimate_kwh("electricity", registered_point("C1"), start, end)
        one_read = U.estimate_unread_kwh(
            "electricity", [(D(2023, 9, 1), D(2023, 9, 30), 40.0)], start, end)
        assert abs(registry - one_read) > 10.0, (registry, one_read)
        assert est[month]["total_consumption_kwh"] == pytest.approx(registry, abs=0.01), month


def test_once_the_reads_span_six_months_the_companys_own_reads_set_the_estimate():
    """The other side of the gate: read March to September, the December estimate is the trailing
    window's, not the registry's (a gate that always refused the reads passes the test above)."""
    est = _estimates(3, "2023-11")
    dec = (D(2023, 12, 1), D(2023, 12, 31))
    window = [(D(2023, m, 1), D(2023, m, calendar.monthrange(2023, m)[1]), 400.0) for m in (9, 10, 11)]
    own = U.estimate_unread_kwh("electricity", window, *dec)
    registry = U.opening_estimate_kwh("electricity", registered_point("C1"), *dec)
    assert abs(own - registry) > 10.0
    assert est["2023-12"]["total_consumption_kwh"] == pytest.approx(own, abs=0.01)
