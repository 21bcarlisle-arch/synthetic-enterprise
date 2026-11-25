"""D48 (2026-11-25): with `same_period_estimate` on, an unread month is billed first from the account's
own read advance over the same calendar period in an earlier year. Off, the switch reaches nothing.

Knowledge: docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md s.5b.
Pre-registration: docs/staging/records/SEAT_PREREG_D48_THE_ESTIMATE_READS_THE_SAME_PERIOD_FIRST_2026-11-25.md.
"""

from __future__ import annotations

import calendar
import datetime as dt
from dataclasses import dataclass

import pytest

from company.billing import monthly_bill_assembly as M
from company.billing import unread_month_estimate as U

D = dt.date
# An electrically heated home: winter is five times its summer. The class shape is far flatter, so
# an annual figure spread on it bills this home's summer at several times what it uses.
USE = {1: 1500.0, 2: 1300.0, 3: 1100.0, 4: 700.0, 5: 400.0, 6: 250.0, 7: 240.0, 8: 260.0,
       9: 450.0, 10: 800.0, 11: 1200.0, 12: 1450.0}
JUNE_2023 = "2023-06"


@dataclass
class _Read:
    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int


class _Feed:
    """Every month read until June 2023, which is not."""

    def meter_type_for(self, customer):
        return "traditional"

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        if period_end.startswith(JUNE_2023):
            return _Read("estimated", None, consecutive + 1)
        return _Read("actual", None, 0)

    def final_read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        return _Read("actual", None, 0)


def _month(year, month, kwh):
    days = calendar.monthrange(year, month)[1]
    return [{"customer_id": "C1", "settlement_date": f"{year}-{month:02d}-{d:02d}",
             "settlement_period": 1, "consumption_kwh": kwh / days,
             "unit_rate_gbp_per_mwh": 200.0, "revenue_gbp": kwh / days / 1000 * 200.0 + 0.5,
             "standing_charge_gbp": 0.5, "wholesale_cost_gbp": 0.0, "margin_gbp": 0.0}
            for d in range(1, days + 1)]


def _records():
    return ([r for m in range(1, 13) for r in _month(2022, m, USE[m])]
            + [r for m in range(1, 8) for r in _month(2023, m, USE[m])])


def _bills(monkeypatch, **switch):
    monkeypatch.setattr(M, "get_customer", lambda cid: {
        "commodity": "electricity", "registered_profile_class": 1, "eac_kwh": 9_000.0})
    return M.build_monthly_bills(_records(), _Feed(), annualised_advance_estimate=True,
                                 bsc_blend_spar=0.5, **switch)


def _june(bills):
    return next(b for b in bills if b["period_end"].startswith(JUNE_2023))["total_consumption_kwh"]


def test_on_bills_last_junes_read_and_off_bills_the_class_shape(monkeypatch):
    """Defect caught: a switch that reaches nothing (on bills the class shape) and a route that does
    not read the held June (on differs from June 2022's own advance). The branch is asserted
    takeable first: on and off differ by more than the home's whole June."""
    off, on = _june(_bills(monkeypatch)), _june(_bills(monkeypatch, same_period_estimate=True))
    assert off - on > USE[6], (off, on)
    # June 2022 and June 2023 carry the same profile weight, so the shaped estimate is the read.
    assert on == pytest.approx(USE[6], abs=0.01)


def test_the_off_arm_is_bit_identical_and_never_asks_for_history(monkeypatch):
    """Defect caught: the off arm moving at all. Off and the switch omitted print the same bills,
    and with the history lookup made to raise, off still bills: it never consulted it."""
    omitted = _bills(monkeypatch)
    off = _bills(monkeypatch, same_period_estimate=False)
    assert off == omitted

    def _asked(*_a, **_k):
        raise AssertionError("the off arm read the account's history")

    monkeypatch.setattr(M, "same_period_advance", _asked)
    assert _bills(monkeypatch, same_period_estimate=False) == omitted


def test_the_same_period_advance_takes_the_nearest_year_and_refuses_an_annual_span():
    """Defect caught: an annual advance taken as a season (it would be the class shape again), and a
    two-year-old season preferred over last year's."""
    june = (D(2023, 6, 1), D(2023, 6, 30))
    last_year = (D(2022, 5, 1), D(2022, 7, 31), 700.0)
    two_back = (D(2021, 6, 1), D(2021, 6, 30), 200.0)
    annual = (D(2022, 1, 1), D(2022, 12, 31), 9000.0)
    assert U.same_period_advance([two_back, last_year, annual], *june) == last_year
    assert U.same_period_advance([two_back, annual], *june) == two_back
    assert U.same_period_advance([annual], *june) is None
    # Covering under half the shifted period is not the same period.
    assert U.same_period_advance([(D(2022, 3, 1), D(2022, 6, 10), 900.0)], *june) is None
