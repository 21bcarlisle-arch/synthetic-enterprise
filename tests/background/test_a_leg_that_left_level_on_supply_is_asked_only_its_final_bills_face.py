"""A leg that left level DD while still supplied is asked its final bill's face, never a level debit.

The defect this names (home_moves.md s.8.8f choice 33; SEAT_FINDING_PROS_2023_0338G_IS_NOT_N29_A_LEG_
THAT_LEFT_LEVEL_ON_SUPPLY_IS_ASKED_THE_LEVEL_DEBIT_AT_ITS_FINAL_BILL_2026-11-26.md): the debit half of a
level leaver's final bill was gated on "has EVER presented a level collection". PROS-2023-0338 left level
in Jan 2024, paid on receipt, and moved out in Nov 2024. Each fuel's final bill asked the October bill,
issued and not yet paid, again as "the scheme's debit". The household paid it twice and both legs were
refunded the excess: the one closing refund outside its class on the 001e4f680a book. s.8.8f: the final
bill is the closing demand of a leg that leaves level AT that bill; a leg that left on supply (S7) gets
the 28-day closing statement, and only that.

Both sides of the partition are asserted at once, so the gate cannot be satisfied by never asking.
"""
from __future__ import annotations

from datetime import date

import pytest

import background.live_payment_triad as lpt
import simulation.household_budget as household_budget
from background.live_payment_triad import LivePaymentTriad
from simulation.arrears_engine import PAY_ON_RECEIPT_METHOD
from simulation.payment_behaviour_source import DIRECT_DEBIT


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
    return date.fromordinal(date(y + m // 12, m % 12 + 1, 1).toordinal() - 1)


def _bill(t, cid, y, m, face, *, level_gbp=None, moved_out=False):
    month = f"{y}-{m:02d}"
    end = _month_end(y, m)
    t.record_period(
        customer_id=cid, due_date=date(y + m // 12, m % 12 + 1, 14), bill_month=month,
        period_end=end.isoformat(), amount_gbp=face, income_stress_value="low", segment="resi",
        moved_out_on=date.fromordinal(end.toordinal() + 1).isoformat() if moved_out else None,
        level_collection=({"month": month, "collection_date": f"{month}-05",
                           "amount_gbp": level_gbp} if level_gbp is not None else None))
    return lpt._period_index_for(month)


def _leaver(cid, *, leaves_level_first):
    """Three months billed 60 on a 30 level amount (90 short), then either two more level months or
    two months paid on receipt, then a final bill of 50."""
    t = LivePaymentTriad()
    method = {"now": DIRECT_DEBIT}
    t._method_for = lambda c, fuel="electricity": method["now"]
    for y, m in [(2024, 7), (2024, 8), (2024, 9)]:
        _bill(t, cid, y, m, 60.00, level_gbp=30.00)
    if leaves_level_first:
        method["now"] = PAY_ON_RECEIPT_METHOD
    for y, m in [(2024, 10), (2024, 11)]:
        _bill(t, cid, y, m, 60.00, level_gbp=None if leaves_level_first else 30.00)
    final = _bill(t, cid, 2024, 12, 50.00, moved_out=True)
    return t.final_month_nets()["rows"][-1], final


def test_a_leg_that_left_level_on_supply_is_asked_its_face(asked):
    """S7 then a move: the ledger is in debit, but the final bill asks 50, and the row says why."""
    row, final = _leaver("LEFT-ON-SUPPLY", leaves_level_first=True)
    assert row["ever_level"] and not row["on_level_at_final"]
    assert row["ledger_balance_gbp"] > 0.005, "the fixture must hold a debit for the gate to refuse"
    assert row["debit_asked_gbp"] == pytest.approx(0.0)
    assert asked[("LEFT-ON-SUPPLY", final)] == pytest.approx(50.00)


def test_a_leg_on_level_at_its_final_bill_is_still_asked_the_debit(asked):
    """The other side of the partition: five months 30 short on level leave 150; the final asks 200."""
    row, final = _leaver("ON-LEVEL", leaves_level_first=False)
    assert row["on_level_at_final"]
    assert row["debit_asked_gbp"] == pytest.approx(150.00)
    assert asked[("ON-LEVEL", final)] == pytest.approx(200.00)
