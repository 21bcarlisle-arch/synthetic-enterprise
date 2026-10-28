"""D48 (2026-10-22): with the annualised advance on and `bill_estimate_floors_the_gas_advance_at_nine_months`
on, a gas account annualises only an advance of nine months or more (Xoserve's AQ floor) and falls
back below it to the registry AQ (2026-10-28; the three reads before that). Electricity keeps the AA's six months.

Knowledge: docs/market_research/unbilled_energy_and_revenue_assurance.md K2, design choice 1.
Prereg: docs/staging/records/WORKER_PREREG_THE_GAS_ESTIMATE_FLOORS_THE_ADVANCE_AT_NINE_MONTHS_2026-10-22.md.
"""

from __future__ import annotations

import calendar
import dataclasses
import datetime as dt
from dataclasses import dataclass

import pytest

from company.billing import monthly_bill_assembly as M
from company.billing import unread_month_estimate as U

D = dt.date
# Seven months read (May-Nov), December estimated: an advance of 214 days, inside the AA's six
# months and outside the AQ's nine. Use far off the published shape, so the advance and the three
# reads give different Decembers.
READ = {5: 900.0, 6: 800.0, 7: 700.0, 8: 650.0, 9: 300.0, 10: 250.0, 11: 200.0}
DEC = (D(2023, 12, 1), D(2023, 12, 31))


@dataclass
class _Read:
    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int


class _Feed:
    def meter_type_for(self, customer):
        return "traditional"

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        if period_end < "2023-12":
            return _Read("actual", None, 0)
        return _Read("estimated", None, consecutive + 1)

    def final_read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        return _Read("actual", None, 0)


def _month(cid, month, kwh):
    days = calendar.monthrange(2023, month)[1]
    return [{"customer_id": cid, "settlement_date": f"2023-{month:02d}-{d:02d}",
             "settlement_period": 1, "consumption_kwh": kwh / days,
             "unit_rate_gbp_per_mwh": 60.0, "revenue_gbp": kwh / days / 1000 * 60.0 + 0.3,
             "standing_charge_gbp": 0.3, "wholesale_cost_gbp": 0.0, "margin_gbp": 0.0}
            for d in range(1, days + 1)]


def _records(cid):
    rows = [r for m, k in READ.items() for r in _month(cid, m, k)]
    return rows + _month(cid, 12, 1000.0)


def _december(monkeypatch, fuel, **kw):
    # The account's fuel is the only thing the registered point is asked for here.
    monkeypatch.setattr(M, "get_customer", lambda cid: {"commodity": fuel})
    bills = M.build_monthly_bills(_records(f"C-{fuel}"), _Feed(), annualised_advance_estimate=True,
                                  **kw)
    return next(b for b in bills if b["period_end"].startswith("2023-12"))["total_consumption_kwh"]


def _three_read(fuel):
    window = [(D(2023, m, 1), D(2023, m, calendar.monthrange(2023, m)[1]), READ[m]) for m in (9, 10, 11)]
    return U.estimate_unread_kwh(fuel, window, *DEC)


def _advance(fuel):
    reads = [(D(2023, 4, 30), 0.0), (D(2023, 11, 30), sum(READ.values()))]
    return U.annualised_advance_kwh(fuel, reads)[0] * U.profile_weight(fuel, *DEC)


def _registry(fuel):
    return U.opening_estimate_kwh(fuel, {"commodity": fuel}, *DEC)


def test_the_floor_moves_a_gas_estimate_off_a_seven_month_advance_and_onto_the_registry_aq(monkeypatch):
    """Defect caught, both ways: a floor that reaches nothing (on still bills the 214-day advance),
    and a floor that is always on (off already bills the registry figure). Below the AQ's nine
    months the company's own reads establish no annual figure, so the registry's stands (2026-10-28,
    E1: it used to be the three reads). The branch is asserted takeable first: the advance, the
    three reads and the registry figure must all differ on this account."""
    assert abs(_advance("gas") - _three_read("gas")) > 10.0
    assert abs(_registry("gas") - _three_read("gas")) > 10.0
    assert abs(_registry("gas") - _advance("gas")) > 10.0
    assert _december(monkeypatch, "gas") == pytest.approx(_advance("gas"), abs=0.01)
    assert _december(monkeypatch, "gas", gas_advance_floor_nine_months=True) == pytest.approx(
        _registry("gas"), abs=0.01)


def test_the_floor_leaves_electricity_on_the_six_month_advance(monkeypatch):
    """Defect caught: the gas floor applied to every fuel, which the AA's six months does not ask."""
    assert _december(monkeypatch, "electricity", gas_advance_floor_nine_months=True) == pytest.approx(
        _advance("electricity"), abs=0.01)


def test_the_floor_is_nine_months_and_a_gas_advance_of_nine_months_is_still_annualised():
    """Defect caught: a floor at the wrong length, or one that refuses the AQ's own nine months."""
    assert U.GAS_AQ_MIN_ADVANCE_DAYS == 273
    nine = [(D(2023, 1, 1), 0.0), (D(2023, 10, 1), 5_000.0)]
    assert U.annualised_advance_kwh("gas", nine, min_advance_days=U.GAS_AQ_MIN_ADVANCE_DAYS)
    short = [(D(2023, 1, 1), 0.0), (D(2023, 9, 30), 5_000.0)]
    assert U.annualised_advance_kwh("gas", short, min_advance_days=U.GAS_AQ_MIN_ADVANCE_DAYS) is None
    assert U.annualised_advance_kwh("gas", short) is not None


def test_the_run_takes_the_floor_from_the_policy_and_the_standing_policy_leaves_it_off():
    from simulation.run_phase2b import CURRENT_POLICY
    from simulation.run_phase4c_on_phase2b import gas_advance_floor_request

    assert gas_advance_floor_request(CURRENT_POLICY) is False
    on = dataclasses.replace(CURRENT_POLICY, bill_estimate_floors_the_gas_advance_at_nine_months=True)
    assert gas_advance_floor_request(on) is True
