"""D48 (2026-10-22): with `bill_estimate_reads_the_annualised_advance` on, an unread month is billed
from the annual rate the account's own register reads imply, not the latest three monthly reads.

One-variable table and prereg:
docs/staging/records/WORKER_PREREG_THE_BILL_ESTIMATE_READS_THE_ANNUALISED_ADVANCE_2026-10-22.md.
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
# A year of reads with a 6:1 winter-to-summer swing, steeper than the published shape: the three
# reads before December (Sep-Nov) set a level the year's advance does not.
YEAR = {(2022, 12): 900.0, (2023, 1): 950.0, (2023, 2): 800.0, (2023, 3): 600.0, (2023, 4): 400.0,
        (2023, 5): 250.0, (2023, 6): 160.0, (2023, 7): 150.0, (2023, 8): 170.0, (2023, 9): 230.0,
        (2023, 10): 420.0, (2023, 11): 700.0}
DEC = (D(2023, 12, 1), D(2023, 12, 31))


@dataclass
class _Read:
    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int


class _Feed:
    """Every month read for C1 (a year) and C2 (three months) until December, estimated after."""

    def meter_type_for(self, customer):
        return "traditional"

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        if period_end < "2023-12":
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


def _records():
    rows = [r for (y, m), k in YEAR.items() for r in _month("C1", y, m, k)]
    rows += _month("C1", 2023, 12, 1000.0)
    for m in (9, 10, 11):
        rows += _month("C2", 2023, m, YEAR[(2023, m)])
    return rows + _month("C2", 2023, 12, 1000.0)


def _december(bills, cid):
    return next(b for b in bills if b["customer_id"] == cid and b["period_end"].startswith("2023-12"))


def _three_read(cid):
    window = [(D(2023, m, 1), D(2023, m, calendar.monthrange(2023, m)[1]), YEAR[(2023, m)])
              for m in (9, 10, 11)]
    return U.estimate_unread_kwh("electricity", window, *DEC)


def test_switched_on_the_estimate_is_the_annualised_advance_and_off_it_is_the_three_reads():
    """Defect caught, both ways: a switch that reaches nothing (on bills the three reads), and a
    switch that leaks into the standing policy's bills (off bills anything else). The branch is
    asserted takeable first: on and off must differ on an account with a year of reads."""
    off = _december(M.build_monthly_bills(_records(), _Feed()), "C1")["total_consumption_kwh"]
    on = _december(M.build_monthly_bills(_records(), _Feed(), annualised_advance_estimate=True),
                   "C1")["total_consumption_kwh"]
    assert abs(on - off) > 10.0, (on, off)
    assert off == pytest.approx(_three_read("C1"), abs=0.01)
    # The register opens at 0 the day before supply and closes on 30 Nov after a year's use.
    reads = [(D(2022, 11, 30), 0.0), (D(2023, 11, 30), sum(YEAR.values()))]
    annual = U.annualised_advance_kwh("electricity", reads)[0]
    assert on == pytest.approx(annual * U.profile_weight("electricity", *DEC), abs=0.01)


def test_switched_on_the_estimate_stops_matching_when_the_advance_is_not_read(monkeypatch):
    """The control the direction item names: if the estimate stops reading the annualised advance
    with the field on, this reds. A planted annual rate must be the one billed."""
    monkeypatch.setattr(M, "annualised_advance_kwh",
                        lambda fuel, reads: (12_000.0, reads[0][0], reads[-1][0]))
    on = _december(M.build_monthly_bills(_records(), _Feed(), annualised_advance_estimate=True),
                   "C1")["total_consumption_kwh"]
    assert on == pytest.approx(12_000.0 * U.profile_weight("electricity", *DEC), abs=0.01)


def test_with_no_advance_of_half_a_year_the_switch_falls_back_to_the_three_reads():
    """Defect caught: an advance under 182 days annualised (or a zero billed) where the published
    AA asks for reads at least six months apart. C2 has three months of reads."""
    on = _december(M.build_monthly_bills(_records(), _Feed(), annualised_advance_estimate=True),
                   "C2")["total_consumption_kwh"]
    assert on == pytest.approx(_three_read("C2"), abs=0.01)


def test_the_run_takes_the_switch_from_the_policy_and_the_standing_policy_turns_it_on():
    """Defect: the default reverts to off, and the standing run bills unread months from the last
    three reads again -- undoing a switch-on whose pre-registered rule was met (7e31d8f70) and
    which the director's ruling of 23 Oct made the machine's to turn on (canon G9). A revert is a
    new pre-registration, not an edit to this default.

    MUTATION (must fire): set the dataclass default back to False (the field-default leg reds), or
    make `annualised_estimate_request` ignore the policy (one of the two request legs reds)."""
    from company.policy.decision_policy import DecisionPolicy
    from simulation.run_phase2b import CURRENT_POLICY
    from simulation.run_phase4c_on_phase2b import annualised_estimate_request

    default = {f.name: f.default for f in dataclasses.fields(DecisionPolicy)}
    assert default["bill_estimate_reads_the_annualised_advance"] is True
    assert annualised_estimate_request(CURRENT_POLICY) is True
    assert annualised_estimate_request(None) is True
    off = dataclasses.replace(CURRENT_POLICY, bill_estimate_reads_the_annualised_advance=False)
    assert annualised_estimate_request(off) is False
