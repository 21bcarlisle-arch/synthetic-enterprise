"""A level leaver's final bill asks its face plus the debit the scheme left, less what SLC 21BA bars.

The defect this names (D5, docs/market_research/home_moves.md s.8.8f): the world's final bill for a
level leaver asked only its face, so a debit the schedule left was never asked by any document, and
the desk opened a journey on it (SYN-2016-024g: 5.87 after a 24.83 final bill; INV_OVERDUE_WITHIN_
BALANCE 4 and INV_OVERDUE_WITHIN_PAGE_BALANCE 7 on the f7e17b1316 book). SLC 27.17 and 31H.12: the
final bill states the one balance and is the closing demand, collected by the existing mandate.
The branch is behind `FINAL_BILL_ASKS_THE_LEVEL_DEBIT`, ON since the page and the runner read the same ask
(17 Nov 2026); `test_the_shipped_world_asks_the_debit` reds if it is switched off again.
"""
from __future__ import annotations

from datetime import date

import pytest

import background.live_payment_triad as lpt
import simulation.household_budget as household_budget
from background.live_payment_triad import LivePaymentTriad
from simulation.payment_behaviour_source import DIRECT_DEBIT

#: The switch as shipped, read before any fixture patches it.
SHIPPED = lpt.FINAL_BILL_ASKS_THE_LEVEL_DEBIT


@pytest.fixture
def asked(monkeypatch):
    """Every amount the world presented, keyed by (leg, month index), every draw collected."""
    monkeypatch.setattr(household_budget, "BUDGET_DECIDES_PAYMENT", False)
    monkeypatch.setattr(lpt.early_contact, "EARLY_CONTACT_SHARE", 0.0)
    monkeypatch.setattr(lpt, "later_settlement_date", lambda event, segment="resi": None)
    monkeypatch.setattr(lpt, "FINAL_BILL_ASKS_THE_LEVEL_DEBIT", True)
    real = lpt.generate_payment_event
    seen: dict = {}

    def draw(cid, period_index, due, amount, stress, method, **kw):
        seen[(cid, period_index)] = amount
        ev = real(cid, period_index, due, amount, stress, method, **kw)
        return lpt.dataclasses.replace(ev, result="success", days_late=0,
                                       payment_date=due.isoformat(), dd_failure_reason=None)
    monkeypatch.setattr(lpt, "generate_payment_event", draw)
    return seen


def _month_end(y, m):
    return date(y + m // 12, m % 12 + 1, 1).toordinal() - 1


def _leave(cid, months, final_face, *, level_gbp=30.00, bill_gbp=60.00, on_level=True):
    """`months` winter months billed at `bill_gbp` on a `level_gbp` level amount, then a final bill."""
    t = LivePaymentTriad()
    t._method_for = lambda c, fuel="electricity": DIRECT_DEBIT
    for y, m in months:
        month = f"{y}-{m:02d}"
        end = date.fromordinal(_month_end(y, m))
        t.record_period(
            customer_id=cid, due_date=date(y + m // 12, m % 12 + 1, 14), bill_month=month,
            period_end=end.isoformat(), amount_gbp=bill_gbp, income_stress_value="low",
            segment="resi",
            level_collection={"month": month, "collection_date": f"{month}-05",
                              "amount_gbp": level_gbp} if on_level else None)
    y, m = months[-1][0] + (months[-1][1] // 12), months[-1][1] % 12 + 1
    month = f"{y}-{m:02d}"
    end = date.fromordinal(_month_end(y, m))
    t.record_period(
        customer_id=cid, due_date=date(y + m // 12, m % 12 + 1, 14), bill_month=month,
        period_end=end.isoformat(), amount_gbp=final_face, income_stress_value="low",
        segment="resi", moved_out_on=date.fromordinal(end.toordinal() + 1).isoformat(),
        level_collection={"month": month, "collection_date": f"{month}-05",
                          "amount_gbp": level_gbp} if on_level else None)
    return t, lpt._period_index_for(month)


RECENT = [(2024, 11), (2024, 12), (2025, 1)]


def test_the_final_bill_asks_its_face_plus_the_schemes_debit(asked):
    """Three months billed 60 against a 30 level amount leave 90 on the ledger; the final bill of 50
    asks 140, and the row the run records says so. The first assertion is the branch firing at all."""
    t, final = _leave("LVL-DEBIT", RECENT, 50.00)
    row = t.final_month_nets()["rows"][-1]
    assert row["debit_asked_gbp"] == pytest.approx(90.00)
    assert asked[("LVL-DEBIT", final)] == pytest.approx(140.00)
    assert row["debit_barred_gbp"] == pytest.approx(0.0)


def test_a_shortfall_from_energy_used_over_a_year_before_is_barred(asked):
    """SLC 21BA at the final bill, a charge recovery action: 2019's 90 shortfall is for energy used
    more than 12 months before a 2021 final bill, so none of it is asked, and the face still is."""
    months = [(2019, 1), (2019, 2), (2019, 3)] + [(2019, m) for m in range(4, 13)] + [
        (2020, m) for m in range(1, 13)] + [(2021, 1)]
    # From April 2019 the level amount meets the bill exactly, so only Jan-Mar 2019 fell short.
    t = LivePaymentTriad()
    t._method_for = lambda c, fuel="electricity": DIRECT_DEBIT
    for y, m in months:
        month = f"{y}-{m:02d}"
        end = date.fromordinal(_month_end(y, m))
        t.record_period(
            customer_id="LVL-OLD", due_date=date(y + m // 12, m % 12 + 1, 14), bill_month=month,
            period_end=end.isoformat(), amount_gbp=60.00 if (y, m) < (2019, 4) else 30.00,
            income_stress_value="low", segment="resi",
            level_collection={"month": month, "collection_date": f"{month}-05", "amount_gbp": 30.00})
    t.record_period(
        customer_id="LVL-OLD", due_date=date(2021, 3, 14), bill_month="2021-02",
        period_end="2021-02-28", amount_gbp=30.00, income_stress_value="low", segment="resi",
        moved_out_on="2021-03-01",
        level_collection={"month": "2021-02", "collection_date": "2021-02-05", "amount_gbp": 30.00})
    row = t.final_month_nets()["rows"][-1]
    assert row["ledger_balance_gbp"] == pytest.approx(90.00)
    assert row["debit_barred_gbp"] == pytest.approx(90.00)
    assert asked[("LVL-OLD", lpt._period_index_for("2021-02"))] == pytest.approx(30.00)


def test_a_leg_never_on_level_asks_its_face(asked):
    _t, final = _leave("FACE-ONLY", RECENT, 50.00, on_level=False)
    assert asked[("FACE-ONLY", final)] == pytest.approx(50.00)


def test_the_shipped_world_asks_the_debit(asked, monkeypatch):
    """The shipped switch, not the fixture's: a level leaver's final bill on the world as it runs asks
    the scheme's debit (D5 switch-on). The page's close and the runner's choice 27 read this ask."""
    monkeypatch.setattr(lpt, "FINAL_BILL_ASKS_THE_LEVEL_DEBIT", SHIPPED)
    t, final = _leave("LVL-SHIP", RECENT, 50.00)
    assert t.final_month_nets()["rows"][-1]["debit_asked_gbp"] == pytest.approx(90.00)
    assert asked[("LVL-SHIP", final)] == pytest.approx(140.00)


def test_switched_off_the_final_bill_asks_only_its_face(asked, monkeypatch):
    """The state every book before the 17 Nov switch-on was in: the reverse, if the switch goes off."""
    monkeypatch.setattr(lpt, "FINAL_BILL_ASKS_THE_LEVEL_DEBIT", False)
    t, final = _leave("LVL-OFF", RECENT, 50.00)
    assert asked[("LVL-OFF", final)] == pytest.approx(50.00)
    assert t.final_month_nets()["rows"][-1]["debit_asked_gbp"] == pytest.approx(0.0)


def test_the_desk_is_told_what_the_final_bill_asked(asked):
    """Choice 27: the desk reads the ask, not the face, so a collected ask leaves nothing to dun."""
    t, final = _leave("LVL-DESK", RECENT, 50.00)
    ref = f"LVL-DESK::{final}"
    assert t._consumer.collections_journeys.asked_of(ref, 50.00) == pytest.approx(140.00)
