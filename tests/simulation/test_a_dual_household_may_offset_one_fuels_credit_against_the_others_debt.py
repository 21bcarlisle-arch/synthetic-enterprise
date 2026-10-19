"""A dual household's credit on one fuel is set against its debt on the other (SLC 27.8D, fuel page §8b).

The defect kept visible with the switch off: the DD book seeks a leg's debit at the review and the
final bill while the household's other leg holds a credit it may lawfully set off, from 22 Jan 2021.

The fixture is illustrative: monthly level DDs from March 2021, electricity bills rising £5 a
month each year against a review that resets to last year's spend (so each review finds a recent
debit), gas flat under its debit (so it carries a credit). C7 opens under its first year's bills. C1's gas credit covers its electricity
debt; C2's covers part of it; C3 has electricity only; C7 opens in 2019, so its first review falls
before the right existed. Every id is on direct debit for both fuels under the world's channel draw.

Named mutations, run 2026-10-19 in a scratch worktree and restored:
- `company.billing.dd_review.dual_fuel_offset_amount`: `min(recoverable_debit_gbp, other_leg_credit_gbp)`
  -> `recoverable_debit_gbp` (the debt cleared whatever the credit) turns the partition control,
  the credit-moved leg and two rows of the rule's table red (4 failed, 8 passed).
- `build_dd_balance_book`: `if offsets_dual_fuel_legs:` -> `if True:` (offsets taken with the switch
  off) turns both off-arm controls, the partition and the credit-moved leg red (4 failed, 8 passed).
"""
from __future__ import annotations

from datetime import date

import pytest

from company.billing.dd_review import OFFSET_RIGHT_IN_FORCE_FROM, dual_fuel_offset_amount
from company.policy.decision_policy import CURRENT_POLICY
from simulation.dd_balance_book import build_dd_balance_book


def _bills(cid, commodity, amounts, y0, m0):
    out = []
    for i, amount in enumerate(amounts):
        k = (m0 - 1) + i
        y, m = y0 + k // 12, k % 12 + 1
        out.append({"customer_id": cid, "period_start": f"{y}-{m:02d}-01",
                    "period_end": f"{y}-{m:02d}-28", "total_amount_gbp": amount,
                    "segment": "resi", "commodity": commodity})
    return out


N = 48
RISING = [40.0 + 5 * (i // 12) for i in range(N)]
BILLS = (_bills("C1", "electricity", RISING, 2021, 3) + _bills("C1g", "gas", [50.0] * N, 2021, 3)
         + _bills("C2", "electricity", RISING, 2021, 3) + _bills("C2g", "gas", [50.0] * N, 2021, 3)
         + _bills("C3", "electricity", RISING, 2021, 3)
         + _bills("C7", "electricity", RISING, 2019, 6) + _bills("C7g", "gas", [50.0] * N, 2019, 6))
OPENING = {"C1": 40.0, "C1g": 70.0, "C2": 40.0, "C2g": 52.0, "C3": 40.0, "C7": 35.0, "C7g": 70.0}
CLOSED = {"C1", "C1g"}


def _book(seek, offsets, bills=BILLS, closed=CLOSED):
    return build_dd_balance_book(bills, OPENING, closed, seek_balance_at_review=seek,
                                 offsets_dual_fuel_legs=offsets)


def _view(book):
    return (book.serialise(), book.bar_actions, book.review_step_ups, book.back_billing_accounts,
            {c: [p.balance_gbp for p in pts] for c, pts in book.trajectories.items()})


def test_the_switch_stands_off_on_the_standing_policy():
    assert CURRENT_POLICY.dd_review_offsets_dual_fuel_legs is False


@pytest.mark.parametrize("seek", [False, True])
def test_off_each_leg_is_booked_as_if_its_household_had_no_other_fuel(seek):
    """Off, the book is the book as it was: a leg's balances, bars and step-ups do not depend on
    whether its household holds the other fuel, and the summary carries no offset figure."""
    both = _book(seek, False)
    assert _view(both) == _view(build_dd_balance_book(BILLS, OPENING, CLOSED,
                                                      seek_balance_at_review=seek))
    assert "dual_fuel_offsets_gbp" not in both.summary() and both.dual_fuel_offsets == []
    for leg in ("C1", "C1g", "C2", "C2g", "C7", "C7g"):
        alone = _book(seek, False, [b for b in BILLS if b["customer_id"] == leg])
        assert [p.balance_gbp for p in alone.trajectories[leg]] == \
            [p.balance_gbp for p in both.trajectories[leg]]
        assert [r for r in both.review_step_ups if r["customer_id"] == leg] == alone.review_step_ups


def test_the_partition_on_offsets_in_full_in_part_at_the_final_bill_and_never_before_the_right():
    """One control over every branch: a review leg covered in full is not stepped up, one covered in
    part is stepped up on the rest only, a closed leg's final bill is offset, a review before 22 Jan
    2021 seeks the debit as before, and a single-fuel leg is booked exactly as with the switch off."""
    off, on = _book(True, False), _book(True, True)
    steps = {(r["customer_id"], r["date"]): r["step_up_gbp"] for r in on.review_step_ups}
    steps_off = {(r["customer_id"], r["date"]): r["step_up_gbp"] for r in off.review_step_ups}
    made = {(r["debit_leg"], r["action"], r["date"]): r["offset_gbp"] for r in on.dual_fuel_offsets}
    in_full = ("C1", "2023-03-01")
    in_part = ("C2", "2023-03-01")
    before_right = [k for k in steps_off if k[0] == "C7" and date.fromisoformat(k[1])
                    < OFFSET_RIGHT_IN_FORCE_FROM]
    assert (made[("C1", "review", "2023-03-01")] == 60.0 and in_full in steps_off
            and in_full not in steps
            and 0.0 < steps[in_part] < steps_off[in_part]
            and made[("C1", "final_bill", "2025-02-28")] > 0.0
            and before_right and all(steps[k] == steps_off[k] for k in before_right)
            and not any(k[0] == "C7" and k[2] < OFFSET_RIGHT_IN_FORCE_FROM.isoformat() for k in made)
            and [p.balance_gbp for p in on.trajectories["C3"]]
            == [p.balance_gbp for p in off.trajectories["C3"]]), (made, steps, steps_off)
    assert on.summary()["n_dual_fuel_offsets"] == len(on.dual_fuel_offsets) > 0


def test_on_an_offset_moves_the_credit_it_spends_and_no_more():
    """The credit leg pays exactly what the debit leg is relieved of: at the bill after a review
    offset, the gas leg sits that much lower than with the switch off."""
    off, on = _book(True, False, closed=set()), _book(True, True, closed=set())
    first = next(r for r in on.dual_fuel_offsets if r["debit_leg"] == "C2")
    i = next(i for i, p in enumerate(off.trajectories["C2g"]) if p.month == first["date"][:7])
    drop = off.trajectories["C2g"][i].balance_gbp - on.trajectories["C2g"][i].balance_gbp
    assert drop == pytest.approx(first["offset_gbp"]) and first["offset_gbp"] == 24.0


@pytest.mark.parametrize("args, expected", [
    ((100.0, 60.0, date(2023, 3, 1), True), 60.0),
    ((40.0, 60.0, date(2023, 3, 1), True), 40.0),
    ((100.0, 60.0, date(2023, 3, 1), False), 0.0),
    ((100.0, 60.0, date(2021, 1, 21), True), 0.0),
    ((100.0, 60.0, date(2021, 1, 22), True), 60.0),
    ((0.0, 60.0, date(2023, 3, 1), True), 0.0),
    ((100.0, 0.0, date(2023, 3, 1), True), 0.0),
])
def test_the_offset_is_the_smaller_side_from_the_day_the_right_began(args, expected):
    assert dual_fuel_offset_amount(*args) == expected
