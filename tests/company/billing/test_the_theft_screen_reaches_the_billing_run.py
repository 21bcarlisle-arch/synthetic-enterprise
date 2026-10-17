"""W2_36: the company's monthly billing run calls the theft screen on every account (§4b).

Driven through the company's own `build_monthly_bills` with a scripted read feed, so a billing run
that stops reaching `screen_billing_run`, `empty_period_flags` or `boundary_read_status` reds here
rather than leaving the screen's own tests green over a rule nothing calls.
"""

from __future__ import annotations

import calendar
from dataclasses import dataclass

import pytest

from company.billing.monthly_bill_assembly import build_monthly_bills

USE_KWH = 300.0


def _month(cid, year, month, kwh, void=False, unit_rate=200.0, sc_per_day=0.50):
    days = calendar.monthrange(year, month)[1]
    rows = []
    for d in range(1, days + 1):
        revenue = (kwh / days / 1000) * unit_rate + sc_per_day
        rows.append({
            "customer_id": cid, "settlement_date": f"{year}-{month:02d}-{d:02d}",
            "settlement_period": 1, "consumption_kwh": kwh / days,
            "unit_rate_gbp_per_mwh": unit_rate, "revenue_gbp": revenue,
            "standing_charge_gbp": sc_per_day, "wholesale_cost_gbp": 0.0, "margin_gbp": 0.0,
            **({"void_owner_charge_gbp": revenue} if void else {}),
        })
    return rows


@dataclass
class _Read:
    status: str
    estimated_consumption_kwh: float | None
    consecutive_estimated_count: int


class _EveryMonthRead:
    def meter_type_for(self, customer):
        return "smart"

    def read_for(self, customer_id, period_end, meter_type, true_kwh, consecutive):
        return _Read("actual", None, 0)

    final_read_for = read_for


def _book():
    """C1: named, used for three months, then empty for two (two leads). C2: an owner's void month.
    C3: opens on 2020-07-01 at C1's meter point, on C1's actual closing read, and is empty."""
    rows = []
    for m, kwh in [(1, USE_KWH), (2, USE_KWH), (3, USE_KWH), (4, 0.0), (5, 0.0), (6, USE_KWH)]:
        rows += _month("C1", 2020, m, kwh)
    rows += _month("C2", 2020, 1, USE_KWH) + _month("C2", 2020, 2, 0.0, void=True)
    rows += _month("C2", 2020, 3, USE_KWH)
    rows += _month("C3", 2020, 7, 0.0) + _month("C3", 2020, 8, USE_KWH)
    return rows


def _run(screen=True, links=None):
    out = [] if screen else None
    bills = build_monthly_bills(_book(), _EveryMonthRead(), theft_screen_out=out,
                                tenancy_links=links)
    return bills, out


def test_the_billing_run_records_each_flag_with_the_act_the_page_names():
    """Defect: the billing run stops calling the screen, files a void as a lead, prices a lead from
    nothing, or the switch-off run's bills move when the screen is switched on."""
    bills, flags = _run(links={"C3": "C1"})
    by = {(f["customer_id"], f["span_start"]): f for f in flags}
    # The whole partition is reached before any leg is graded.
    assert {f["act"] for f in flags} == {"refer_for_investigation", "bill_the_void"}, flags
    lead = by[("C1", "2020-04-01")]
    # A read every month makes each empty month its own span.
    assert lead["status"] == "investigate" and lead["periods"] == 1
    # RPCoP Appendix 7 §1.1: the account's own level before the change, per day, over the span.
    daily = 3 * USE_KWH / (31 + 29 + 31)
    assert lead["assessment_method"] == "prior_history"
    assert lead["assessed_unrecorded_kwh"] == pytest.approx(daily * 30, abs=0.1)
    # Priced at the account's own billed commodity rate, read off its bills.
    own = [b for b in bills if b["customer_id"] == "C1"]
    rate = sum(b["commodity_amount_gbp"] for b in own) / sum(b["total_consumption_kwh"] for b in own)
    assert lead["assessed_value_gbp"] == pytest.approx(lead["assessed_unrecorded_kwh"] * rate, abs=0.01)
    assert "21BA.2(c)" in lead["act_text"] and "12A.11(g)" in lead["act_text"]
    void = by[("C2", "2020-02-01")]
    assert void["status"] == "void" and void["assessed_unrecorded_kwh"] == 0.0
    # The incoming account's first span is judged because C1's closing read was actual.
    opening = by[("C3", "2020-07-01")]
    assert opening["opening_read_status"] == "actual" and opening["status"] == "investigate"
    # Unlinked, the same account's first span is not judged at all.
    assert not [f for f in _run()[1] if f["customer_id"] == "C3"]
    # Switch off: no screen, and not one bill differs.
    assert _run(screen=False) == (bills, None)
