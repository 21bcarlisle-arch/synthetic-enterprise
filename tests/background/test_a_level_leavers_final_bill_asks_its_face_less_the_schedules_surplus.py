"""A level leaver's final bill asks its face less the surplus the schedule left on the leg.

The defect this names (`docs/staging/SEAT_FINDING_A_LEVEL_LEAVERS_FINAL_BILL_IS_NETTED_ON_THE_PAGE_
AND_COLLECTED_AT_FACE_BY_THE_WORLD_2026-11-12.md`): the page nets a level leaver's closing credit
against its final bill (home_moves.md s.8.8c choice 14), while the world took the final month off the
schedule and asked the bill's whole face, because its waiting credit held credit-bill excess only.
On 6fe7827ab2: 195 legs, GBP 4,715.67 of final bills the page said the credit covered and the desk
counted as cash. SLC 31H.12 and 27.17: the final bill states the one balance and asks the rest.
"""
from __future__ import annotations

from datetime import date

import pytest

import background.live_payment_triad as lpt
import simulation.household_budget as household_budget
from background.live_payment_triad import LivePaymentTriad
from simulation.payment_behaviour_source import DIRECT_DEBIT

# Three summer months at GBP 30 on a GBP 60 level amount: GBP 90 over-collected by the final month.
SUMMER = [
    ("2025-01", "2025-01-31", date(2025, 2, 14), 30.00),
    ("2025-02", "2025-02-28", date(2025, 3, 14), 30.00),
    ("2025-03", "2025-03-31", date(2025, 4, 14), 30.00),
]


@pytest.fixture
def asked(monkeypatch):
    """Every amount the world presented, keyed by month index, with every draw collected."""
    monkeypatch.setattr(household_budget, "BUDGET_DECIDES_PAYMENT", False)
    monkeypatch.setattr(lpt.early_contact, "EARLY_CONTACT_SHARE", 0.0)
    monkeypatch.setattr(lpt, "later_settlement_date", lambda event, segment="resi": None)
    real = lpt.generate_payment_event
    seen: dict = {}

    def draw(cid, period_index, due, amount, stress, method, **kw):
        seen[(cid, period_index)] = amount
        ev = real(cid, period_index, due, amount, stress, method, **kw)
        return lpt.dataclasses.replace(ev, result="success", days_late=0,
                                       payment_date=due.isoformat(), dd_failure_reason=None)
    monkeypatch.setattr(lpt, "generate_payment_event", draw)
    return seen


def _leave(cid, final_face, *, on_level=True):
    t = LivePaymentTriad()
    t._method_for = lambda c, fuel="electricity": DIRECT_DEBIT
    for month, period_end, due, bill in SUMMER:
        t.record_period(
            customer_id=cid, due_date=due, bill_month=month, period_end=period_end,
            amount_gbp=bill, income_stress_value="low", segment="resi",
            level_collection={"month": month, "collection_date": f"{month}-05", "amount_gbp": 60.00}
            if on_level else None)
    t.record_period(
        customer_id=cid, due_date=date(2025, 5, 14), bill_month="2025-04",
        period_end="2025-04-30", amount_gbp=final_face, income_stress_value="low",
        segment="resi", moved_out_on="2025-05-01",
        level_collection={"month": "2025-04", "collection_date": "2025-04-05", "amount_gbp": 60.00}
        if on_level else None)
    return t


FINAL = lpt._period_index_for("2025-04")


def test_the_final_bill_asks_its_face_less_the_surplus(asked):
    _leave("LVL-PART", 120.00)
    assert asked[("LVL-PART", FINAL)] == pytest.approx(30.00)


def test_a_surplus_that_covers_the_final_bill_presents_nothing(asked):
    t = _leave("LVL-ALL", 50.00)
    assert asked[("LVL-ALL", FINAL)] == pytest.approx(0.00)
    assert t._records[-1].result == "success"


def test_a_leg_never_on_level_still_asks_the_face(asked):
    """The control the branch needs: off the schedule there is no surplus, so the face is asked,
    and the months before were paid at face too, so the ledger holds no credit to net."""
    _leave("FACE", 50.00, on_level=False)
    assert asked[("FACE", FINAL)] == pytest.approx(50.00)


def test_a_credit_bill_on_the_level_leg_comes_off_the_final_bill_too(asked):
    """LEVEL_DD map s.9.7: 6 of the 25 page nettings (GBP 315.55, SYN-2016-037, -225, -333, -444, -482)
    draw credit-bill credit, not level surplus. The run posts a credit bill as a GBP 0 face plus a credit
    note (`run_phase2b`: `credit_gbp=max(0, -ask)`), which the leg's ledger balance reads, so the final
    bill nets both: GBP 90 of surplus and the GBP 25 credit note come off a GBP 150 face."""
    t = LivePaymentTriad()
    t._method_for = lambda c, fuel="electricity": DIRECT_DEBIT
    for month, period_end, due, bill in SUMMER:
        t.record_period(
            customer_id="LVL-CB", due_date=due, bill_month=month, period_end=period_end,
            amount_gbp=bill, income_stress_value="low", segment="resi",
            level_collection={"month": month, "collection_date": f"{month}-05", "amount_gbp": 60.00})
    t.record_period(
        customer_id="LVL-CB", due_date=date(2025, 5, 14), bill_month="2025-04",
        period_end="2025-04-30", amount_gbp=0.0, credit_gbp=25.00, income_stress_value="low",
        segment="resi",
        level_collection={"month": "2025-04", "collection_date": "2025-04-05", "amount_gbp": 60.00})
    t.record_period(
        customer_id="LVL-CB", due_date=date(2025, 6, 14), bill_month="2025-05",
        period_end="2025-05-31", amount_gbp=300.00, income_stress_value="low", segment="resi",
        moved_out_on="2025-06-01",
        level_collection={"month": "2025-05", "collection_date": "2025-05-05", "amount_gbp": 60.00})
    # Surplus: 4 x 60 collected against 90 billed -> 150; plus the 25 credit note -> 175 off 300.
    assert asked[("LVL-CB", lpt._period_index_for("2025-05"))] == pytest.approx(125.00)
