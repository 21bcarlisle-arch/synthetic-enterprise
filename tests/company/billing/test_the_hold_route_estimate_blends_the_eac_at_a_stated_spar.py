"""D48 (2026-11-19): with `bill_estimate_blends_the_eac_at_spar` set, a hold-route electricity month
is billed from the BSC-blended EAC (Annex S-2 4.3.7), not the registry figure. The hold route is an
actual read held and reads spanning under 182 days. SPAR is a GAP, carried as a range.

Knowledge: docs/market_research/how_a_supplier_shapes_an_estimate_for_an_unread_month.md s8.
Pre-registrations: docs/staging/records/SEAT_PREREG_D48_THE_ELECTRICITY_RESIDUAL_BY_ESTIMATE_ROUTE_2026-11-19.md,
docs/staging/records/SEAT_PREREG_D48_E1_BREACHES_AT_EACH_SPAR_2026-11-19.md.
"""

from __future__ import annotations

import calendar
import datetime as dt
from dataclasses import dataclass

import pytest

from company.billing import monthly_bill_assembly as M
from company.billing import unread_month_estimate as U

D = dt.date
REGISTRY_EAC = 6_000.0
# Three read months whose use annualises to about a third of the registry EAC: C6's shape, a held
# read the hold sets aside.
READS = {9: 150.0, 10: 170.0, 11: 190.0}
DEC = (D(2023, 12, 1), D(2023, 12, 31))
LOW, HIGH = U.SPAR_WEIGHT_RATE_STATED_RANGE


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
             "unit_rate_gbp_per_mwh": 200.0, "revenue_gbp": kwh / days / 1000 * 200.0 + 0.5,
             "standing_charge_gbp": 0.5, "wholesale_cost_gbp": 0.0, "margin_gbp": 0.0}
            for d in range(1, days + 1)]


def _records(cid="C1"):
    rows = [r for m, k in READS.items() for r in _month(cid, m, k)]
    return rows + _month(cid, 12, 300.0)


def _point(profile_class=1, commodity="electricity"):
    return {"commodity": commodity, "registered_profile_class": profile_class,
            "eac_kwh": REGISTRY_EAC, "aq_kwh": REGISTRY_EAC}


def _december(monkeypatch, point=None, **switch):
    monkeypatch.setattr(M, "get_customer", lambda cid: point or _point())
    bills = M.build_monthly_bills(_records(), _Feed(), **switch)
    return next(b for b in bills if b["period_end"].startswith("2023-12"))["total_consumption_kwh"]


def _by_hand(spar):
    eac = REGISTRY_EAC
    for m, kwh in READS.items():
        fyc = U.profile_weight("electricity", D(2023, m, 1), D(2023, m, calendar.monthrange(2023, m)[1]))
        w = min(1.0, fyc * spar)
        eac = w * kwh / fyc + (1 - w) * eac
    return eac * U.profile_weight("electricity", *DEC)


def test_the_blend_is_taken_at_both_ends_of_the_range_and_off_it_is_the_hold(monkeypatch):
    """Defect caught, every way at once: a switch that reaches nothing (both ends bill the hold), a
    switch that leaks into the standing policy (off bills anything but the registry figure), and a
    blend that does not follow 4.3.7 (either end differs from the formula done by hand). The branch
    is asserted takeable first: both ends differ from the hold, and from each other."""
    hold = _december(monkeypatch)
    low, high = (_december(monkeypatch, bsc_blend_spar=s) for s in (LOW, HIGH))
    assert hold == pytest.approx(REGISTRY_EAC * U.profile_weight("electricity", *DEC), abs=0.01)
    assert hold - low > 10.0 and low - high > 10.0, (hold, low, high)
    assert low == pytest.approx(_by_hand(LOW), abs=0.01)
    assert high == pytest.approx(_by_hand(HIGH), abs=0.01)


def test_the_blend_moves_only_pc1_and_pc3_electricity(monkeypatch):
    """Defect caught: the blend reaching PC2 (estimated per register, a separate question) or gas
    (the AQ is not smoothed by 4.3.7). Keyed to the property: on and off agree off the scope."""
    for point in (_point(profile_class=2), _point(commodity="gas", profile_class=None)):
        assert _december(monkeypatch, point, bsc_blend_spar=HIGH) == pytest.approx(
            _december(monkeypatch, point), abs=0.01)
    assert _december(monkeypatch, _point(profile_class=3), bsc_blend_spar=HIGH) == pytest.approx(
        _by_hand(HIGH), abs=0.01)


@pytest.mark.parametrize("spar", [0.0, LOW - 0.01, HIGH + 0.01, float("inf")])
def test_a_spar_outside_the_stated_range_is_refused_with_its_reason(monkeypatch, spar):
    """Defect caught: a point SPAR picked outside the evidence. SPAR 0 is the hold and infinity
    re-opens E1, so both are refused by name, at the door, before any month is billed."""
    with pytest.raises(ValueError, match="stated range"):
        _december(monkeypatch, bsc_blend_spar=spar)


def test_the_standing_policy_blends_at_the_end_of_the_range_that_claims_least():
    """Defect: the standing policy bills on a SPAR the evidence does not support, or on a point
    inside the range that claims more than the least (F11). Since 2026-11-20 it is the range's
    low end, and the hold stays reachable as None."""
    import dataclasses

    from company.billing.unread_month_estimate import SPAR_WEIGHT_RATE_STATED_RANGE
    from company.policy.decision_policy import DecisionPolicy
    from simulation.run_phase2b import CURRENT_POLICY
    from simulation.run_phase4c_on_phase2b import bsc_blend_spar_request

    field = {f.name: f for f in dataclasses.fields(DecisionPolicy)}["bill_estimate_blends_the_eac_at_spar"]
    assert field.default == min(SPAR_WEIGHT_RATE_STATED_RANGE)
    assert bsc_blend_spar_request(CURRENT_POLICY) == min(SPAR_WEIGHT_RATE_STATED_RANGE)
    assert bsc_blend_spar_request(None) == min(SPAR_WEIGHT_RATE_STATED_RANGE)
    hold = dataclasses.replace(CURRENT_POLICY, bill_estimate_blends_the_eac_at_spar=None)
    assert bsc_blend_spar_request(hold) is None
