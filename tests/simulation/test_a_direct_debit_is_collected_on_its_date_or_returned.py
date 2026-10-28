"""A direct debit is collected on its due date or returned; it never succeeds weeks late.

The defect: every domestic credit bill took one outcome draw whose "paid late" leg (3-90 days by
stress tier) a DD took too, so 181 accounts on the 1a02c46116 book had DDs collected 31 to 45 days
after their due date with no return. Under Bacs a collection is taken on its date or comes back
through ARUDD (`docs/market_research/payments_and_direct_debit_2026-10-25.md`, "A DD is never
late").
"""
from datetime import date

from simulation.arrears_engine import DD_METHOD, PAY_ON_RECEIPT_METHOD, payment_outcome
from simulation.payment_behaviour_source import (
    DIRECT_DEBIT,
    STANDING_ORDER,
    generate_payment_event,
)
from simulation.rng_substream import substream

_STRESSES = ("low", "moderate", "high")
_DRAWS = 300


def _events(method: str, stress: str):
    return [generate_payment_event(f"DDT{i}", 1300, date(2016, 3, 20), 80.0, stress, method)
            for i in range(_DRAWS)]


def test_a_dd_bill_is_paid_on_its_due_date_or_failed():
    late = [(s, e.customer_id, e.days_late) for s in _STRESSES for e in _events(DIRECT_DEBIT, s)
            if e.result == "success" and e.days_late > 0]
    assert not late, f"{len(late)} DD bills collected late with no return, e.g. {late[:3]}"


def test_the_late_leg_can_still_be_taken_off_dd():
    # The guard is on the method, not on lateness: a standing-order payer at MODERATE stress is
    # still late, so the test above cannot pass by zeroing every delay.
    late = [e for e in _events(STANDING_ORDER, "moderate")
            if e.result == "success" and e.days_late > 0]
    assert late


def test_the_method_moves_only_when_a_bill_is_paid_not_whether():
    for s in _STRESSES:
        dd = [e.result for e in _events(DIRECT_DEBIT, s)]
        so = [e.result for e in _events(STANDING_ORDER, s)]
        assert dd == so, s


def test_the_engines_own_draw_never_lates_a_dd():
    for stress in ("LOW", "MODERATE", "HIGH"):
        dd = [payment_outcome(DD_METHOD, stress, substream("test_dd", f"dd::{i}", 7))
              for i in range(_DRAWS)]
        por = [payment_outcome(PAY_ON_RECEIPT_METHOD, stress, substream("test_dd", f"dd::{i}", 7))
               for i in range(_DRAWS)]
        assert all(d == 0 for o, d in dd if o == "success"), stress
        assert [o for o, _ in dd] == [o for o, _ in por], stress
        if stress != "LOW":
            assert any(d > 0 for o, d in por if o == "success"), stress


def test_a_declared_population_can_still_hold_late_dds():
    # The H27 harness's calibration book declares late DDs (`HARNESS_BOOK_DD_NEVER_LATE`); the
    # override must reach the draw, or that book silently becomes the world's.
    late = [e for e in (generate_payment_event(f"DDT{i}", 1300, date(2016, 3, 20), 80.0,
                                               "moderate", DIRECT_DEBIT, dd_never_late=False)
                        for i in range(_DRAWS))
            if e.result == "success" and e.days_late > 0]
    assert late
